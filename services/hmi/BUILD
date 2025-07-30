load("@ai_intrinsic_sdks//intrinsic/assets/services/build_defs:services.bzl", "intrinsic_service")
load("@container_structure_test//:defs.bzl", "container_structure_test")
load("@io_bazel_rules_go//go:def.bzl", "go_binary")
load("@rules_oci//oci:defs.bzl", "oci_image", "oci_load")
load("@rules_pkg//:pkg.bzl", "pkg_tar")

filegroup(
    name = "frontend_files",
    srcs = glob(["frontend/**"]),
)

go_binary(
    name = "server",
    srcs = ["server.go"],
    data = [":frontend_files"],
    deps = [
        "@ai_intrinsic_sdks//intrinsic/assets/services/proto/v1:system_service_state_go_grpc_proto",
        "@ai_intrinsic_sdks//intrinsic/executive/proto:behavior_tree_go_proto",
        "@ai_intrinsic_sdks//intrinsic/executive/proto:executive_execution_mode_go_proto",
        "@ai_intrinsic_sdks//intrinsic/executive/proto:executive_service_go_grpc_proto",
        "@ai_intrinsic_sdks//intrinsic/executive/proto:executive_service_go_proto",
        "@ai_intrinsic_sdks//intrinsic/executive/proto:run_metadata_go_proto",
        "@ai_intrinsic_sdks//intrinsic/frontend/solution_service/proto:solution_service_go_grpc_proto",
        "@ai_intrinsic_sdks//intrinsic/frontend/solution_service/proto:solution_service_go_proto",
        "@ai_intrinsic_sdks//intrinsic/resources/proto:runtime_context_go_proto",
        "@ai_intrinsic_sdks//intrinsic/util/proto:protoio",
        "@com_google_cloud_go_longrunning//autogen/longrunningpb",
        "@io_bazel_rules_go//go/runfiles",
        "@org_golang_google_grpc//:go_default_library",
        "@org_golang_google_grpc//credentials/insecure",
        "@org_golang_google_protobuf//encoding/protojson",
        "@org_golang_google_protobuf//proto",
    ],
)

pkg_tar(
    name = "server_layer",
    srcs = [":server"],
    extension = "tar.gz",
    include_runfiles = True,
    strip_prefix = "/",
)

oci_image(
    name = "hmi_image",
    base = "@distroless_base",
    entrypoint = ["/services/hmi/server_/server"],
    tars = [":server_layer"],
)

oci_load(
    name = "hmi_tarball",
    image = ":hmi_image",
    repo_tags = ["hmi:latest"],
)

filegroup(
    name = "hmi_tarball.tar",
    srcs = [":hmi_tarball"],
    output_group = "tarball",
)

container_structure_test(
    name = "hmi_tarball_test",
    configs = ["testdata/image_files.yaml"],
    driver = "tar",
    image = ":hmi_tarball.tar",
)

intrinsic_service(
    name = "hmi_service",
    images = [":hmi_tarball.tar"],
    manifest = "manifest.textproto",
)
