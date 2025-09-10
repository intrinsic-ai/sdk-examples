# HMI (Python)

This example implements a service-based HMI for Flowstate.
The hmi service is written using Python.
The frontend uses HTML and JavaScript to create a very simple UI.
> [!IMPORTANT]
> This HMI service is based on the ["Create an HMI service"](https://flowstate.intrinsic.ai/docs/assets/create_new_assets/create_services/implement_service_scenarios/create_hmi_service/) guide in the Flowstate documentation.
> Follows the steps in the guide to install the HMI service in your solution.

## Features

* Queries the loaded process from the executive service

## Install the HMI to a solution

To install the service to a running solution you use `inctl`.

> [!NOTE]
> Remember to [authenticate with your organization](https://flowstate.intrinsic.ai/docs/guides/build_with_code/connect_to_an_organization/#authenticate-with-your-organization)

1. First build the service

```sh
bazel build //services/hmi_python:hmi_service
```

It should generate a `.tar` ready to be deployed, take note of the output location for next step.

2. Now install it in your running solution

```sh
inctl service install bazel-bin/services/hmi_python/hmi_service.bundle.tar --org=ORGANIZATION_NAME --address="workcell.lan:17080"
```
