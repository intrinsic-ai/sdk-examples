package main

import (
	"encoding/json"
	"flag"
	"fmt"
	rcpb "intrinsic/resources/proto/runtime_context_go_proto"
	"intrinsic/util/proto/protoio"
	"log"
	"net/http"
	"path"
	"strings"
	"text/template"

	"google.golang.org/grpc"

	esvcgrpcpb "intrinsic/executive/proto/executive_service_go_grpc_proto"
	ssvcgrpcpb "intrinsic/frontend/solution_service/proto/solution_service_go_grpc_proto"

	lropb "cloud.google.com/go/longrunning/autogen/longrunningpb"
	"github.com/bazelbuild/rules_go/go/tools/bazel"

	"github.com/bazelbuild/rules_go/go/runfiles"
	"google.golang.org/grpc/credentials/insecure"
)

const (
	packageDir    = "services/angular-hmi/angular-app/dist/hmi-angular/browser/"
	indexFilePath = packageDir + "index.html"
	// defaultRuntimeContextPath is the well-known location for the runtime config
	// inside on-prem devices.
	defaultRuntimeContextPath = "/etc/intrinsic/runtime_config.pb"
	// defaultBaseURLFormat will work correctly when the on-prem device is reached
	// at the root path in a browser (most common). It is used to populate a
	// <base> tag in HTML. This ensures that relative URLs are resolved correctly.
	defaultBaseURLFormat = "/ext/services/%s/"
)

// Providing these values as flags allows for local testing. The README
// describes how this works in more detail.
var (
	runtimeContextPath = flag.String("runtime_context_path", defaultRuntimeContextPath, "Path to the runtime context binary proto.")
	baseURLFormat      = flag.String("base_url_fmt", defaultBaseURLFormat, "Go format string for the base URL of the HMI. Supports exactly one %s for the name of the service. Must end with a trailing slash.")
	ingressAddress     = flag.String("ingress_address", "istio-ingressgateway.app-ingress.svc.cluster.local:80", "Address used to connect to services.")
)

func solutionStatus(w http.ResponseWriter, r *http.Request, client ssvcgrpcpb.SolutionServiceClient) {
	listBtReq := &ssvcgrpcpb.GetStatusRequest{}
	response, err := client.GetStatus(r.Context(), listBtReq)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(fmt.Sprintf("Failed to list operations: %v", err)))
	}
	_returnResponse(w, r, response)
}

func listOperations(w http.ResponseWriter, r *http.Request, client esvcgrpcpb.ExecutiveServiceClient) {
	response, err := client.ListOperations(r.Context(), &lropb.ListOperationsRequest{
		PageSize: 1,
	})
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(fmt.Sprintf("Failed to list operations: %v", err)))
	}
	_returnResponse(w, r, response.GetOperations())
}

func _returnResponse(w http.ResponseWriter, r *http.Request, output any) {
	// Marshal the proto response to JSON.
	b, err := json.Marshal(output)
	if err != nil {
		if err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(fmt.Sprintf("Failed to encode response: %v", err)))
		}
	}
	w.Header().Set("content-type", "application/json")
	w.Write(b)
}

func serveIndexFile(w http.ResponseWriter, r *http.Request, t *template.Template, filesURL string) {
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	if err := t.Execute(w, map[string]any{
		"BaseURL": filesURL,
	}); err != nil {
		log.Fatalf("Failed to execute index.html template: %v", err)
		http.Error(w, "Failed to generate index.html", http.StatusInternalServerError)
		return
	}
}

func main() {
	fmt.Println("Angular HMI service")
	// Parse the flag definitions at the top from the command line. This enables
	// local testing scenarios.
	flag.Parse()

	filesRoot, err := bazel.RunfilesPath()
	if err != nil {
		// Runfiles are placed relative to the container root when running there.
		filesRoot = "/"
	}
	rc := new(rcpb.RuntimeContext)
	if strings.HasSuffix(*runtimeContextPath, ".txtpb") || strings.HasSuffix(*runtimeContextPath, ".textproto") {
		if err := protoio.ReadTextProto(*runtimeContextPath, rc); err != nil {
			log.Fatalf("Failed to read runtime context: %v", err)
		}
	} else {
		if err := protoio.ReadBinaryProto(*runtimeContextPath, rc); err != nil {
			log.Fatalf("Failed to read runtime context: %v", err)
		}
	}
	address := fmt.Sprintf(":%d", rc.GetHttpPort())
	baseURL := fmt.Sprintf(*baseURLFormat, rc.GetName())

	frontendDir, err := runfiles.Rlocation("_main/services/angular-hmi/angular-app/dist/hmi-angular/browser/")
	if err != nil {
		// When running outside of a cluster Rlocation() fails
		// This allows local testing for faster development
		frontendDir = "services/angular-hmi/angular-app/dist/hmi-angular/browser/"
	}

	// filesURL must be prepended to each file we try to access
	filesURL := path.Join(filesRoot, frontendDir)

	conn, err := grpc.NewClient(*ingressAddress, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("Failed to create client connection: %v", err)
	}
	executiveClient := esvcgrpcpb.NewExecutiveServiceClient(conn)
	solutionClient := ssvcgrpcpb.NewSolutionServiceClient(conn)
	indexTemplate, err := template.ParseFiles(path.Join(filesURL, "/index.html"))

	serveFunc := func(response http.ResponseWriter, request *http.Request) {
		// Handle the request to '/' to avoid the server handling
		// all request even for static files in index.html
		if request.URL.Path == "/" || request.URL.Path == "/index.html" {
			serveIndexFile(response, request, indexTemplate, baseURL)
			return
		}

		// Handling endpoints feel free to add as much as you need
		switch request.URL.Path {
		case "/api/executive/operations":
			listOperations(response, request, executiveClient)
			return
		case "/api/solution/status":
			solutionStatus(response, request, solutionClient)
			return
		}

		// Handling static files like the ones in index.html
		f, err := http.Dir(path.Join(filesRoot, frontendDir)).Open(request.URL.Path)
		if err != nil {
			http.NotFound(response, request)
			return
		}
		defer f.Close()
		http.ServeFile(response, request, path.Join(filesURL, request.URL.Path))
	}

	log.Printf("Listening at %s", address)

	handler := http.Handler(http.HandlerFunc(serveFunc))
	if err := http.ListenAndServe(address, handler); err != nil {
		log.Fatalf("Failed to start HTTP server: %v", err)
	}
}
