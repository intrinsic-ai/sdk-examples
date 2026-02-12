# HMI

This example implements a service-based HMI for Flowstate.

> [!IMPORTANT]
> This HMI service is based on the ["Create an HMI service"](https://flowstate.intrinsic.ai/docs/assets/create_new_assets/create_services/implement_service_scenarios/create_hmi_service/) guide in the Flowstate documentation.

## Features

* Frontend: Angular
* Backend: Golang

## Prerequisites

* Angular CLI

For this example you need to [install Angular CLI](https://angular.dev/tools/cli/setup-local#install-the-angular-cli) in order to build the frontend. Since the application is quite simple there are no minimal version requirementes, as long as you are able to build the project with `ng build` you should be fine.

## Test locally

> [!WARNING]
> Local testing requires setup that is only suitable for advanced users.
> Please refer to [this README](../hmi/README.md) for more details since the process remains the same.

It's possible to test the HMI locally without the necessity of leasing a vm which not only saves time but also costs.
In a nutshell you have to provide a runtime context when running the HMI server.

If your ingress is at `workcell.lan:17080` and the runtime context file is `services/static-angular/local/runtime_context.txtpb` relative to the current directory, then you can start a working local version of the HMI server using this command:

```sh
bazel run //services/static-angular:server -- \
  --ingress_address="workcell.lan:17080" \
  --runtime_context_path="$(pwd)/services/static-angular/local/runtime_context.txtpb" \
  --base_url_fmt="/"
```

The `base_url_fmt` is a format string that determines how HTTP requests made by the HMI frontend are routed.
This will depend on how you intend to access the HMI.
A single `/` is sufficient for the most common case where you access the HMI at `workcell.lan:{port}`.
The placeholder `{port}` is the `http_port` from the local runtime context.

> [!NOTE]
> The value of `--base_url_fmt` must end with a `/`.

> [!NOTE]
> The value of `--ingress_address` must be accessible for your browser. In other words it needs to know how to translate it to an IP.
> If you are running a solution you should be fine using the provided address and no special considerations to take into account.
> On the other hand just make sure to use an address the browser knows how to translate. If you are running Linux you can easily add a new entry to `/etc/hosts` file mapping whatever value you used as `ingress_address`, for example: `127.0.0.1    workcell.lan`. Alternative you can just use the keyword `localhost` which your system already knows how to translate.

You can now make changes to the HMI implementation and simply re-run the above command to see them immediately reflected locally.

> [!IMPORTANT]
> If you made changes to the frontend remember to run `ng build` inside `services/static-angular/angular-app/` in order to regenerate the files.

## Install the HMI to a solution

To install the service to a running solution you use `inctl`.

> [!NOTE]
> Remember to [authenticate with your organization](https://flowstate.intrinsic.ai/docs/guides/build_with_code/connect_to_an_organization/#authenticate-with-your-organization)

1. First build the service

```sh
bazel build //services/static-angular:static_angular_service
```

It should generate a `.tar` ready to be deployed, take note of the output location for next step.

1. Now install it in your running solution

```sh
inctl asset install bazel-bin/services/static-angular/static_angular_service.bundle.tar --org=ORGANIZATION_NAME --address="workcell.lan:17080"
```
