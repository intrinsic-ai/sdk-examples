# HMI (Go)

This example implements a service-based HMI for Flowstate.
The hmi service is written using Go.
The frontend uses HTML and JavaScript to create a very simple UI.
> [!IMPORTANT]
> This HMI service is based on the ["Create an HMI service"](https://flowstate.intrinsic.ai/docs/assets/create_new_assets/create_services/implement_service_scenarios/create_hmi_service/) guide in the Flowstate documentation.
> Follows the steps in the guide to install the HMI service in your solution.

## Features

* start a pre-defined process
* stop execution
* pause/resume execution
* view execution status (inluding errors)
* query and modify the state of service instances in a solution

## Test locally

> [!WARNING]
> Local testing requires setup that is only suitable for advanced users.

In order to test the HMI, it can be run locally (i.e. outside of a cluster, not as a service).
This enables testing the HMI without needing to install it on the cluster with `inctl`.
This should drastically increase iteration speed during development.

You need to perform some preparation before running the HMI locally.

### Create runtime context

The HMI relies on a `intrinsic_proto.config.RuntimeContext` proto for some configuration (e.g. the HTTP port to listen on).
This context will be available as a binary proto from a file when the HMI is installed as a service.
However, local environments will not have a runtime context file.
You must create a local runtime context with some test data.
Since managing a binary proto locally is not very easy, you will be using the text format for protocol buffers.
An example file is provided in `local/runtime_context.txtpb` that can be used as is or modified to fit your needs.

> [!IMPORTANT]
> Ensure the proto file has the `.txtpb` extension if you want to provide a proto in text rather than binary format.

The path to the proto file must be provided to the service at startup through the `--runtime_context_path` flag.

### Run the HMI server

You can now start the HMI locally.
Local configuration is provided using flags.
If your ingress is at `workcell.lan:17080` and the runtime context file is `services/hmi/local/runtime_context.txtpb` relative to the current directory, then you can start a working local version of the HMI server using this command:

```sh
bazel run //services/hmi:server -- \
  --ingress_address="workcell.lan:17080" \
  --runtime_context_path="$(pwd)/services/hmi/local/runtime_context.txtpb" \
  --base_url_fmt="/"
```

The `base_url_fmt` is a format string that determines how HTTP requests made by the HMI frontend are routed.
This will depend on how you intend to access the HMI.
A single `/` is sufficient for the most common case where you access the HMI at `workcell.lan:{port}`.
The placeholder `{port}` is the `http_port` from the local runtime context.

> [!NOTE]
> The value of `--base_url_fmt` must end with a `/`.
You can use the `%s` format string placeholder exactly once and it will be replaced by the service name you chose when adding the service to the solution.

You can now make changes to the HMI implementation and simply re-run the above command to see them immediately reflected locally.
