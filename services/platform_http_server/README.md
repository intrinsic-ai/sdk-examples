# Platform HTTP Server Service (Python)

This service is a reusable, generic web server for the Flowstate platform.
Its purpose is to host static web content (like an HMI, dashboard, or documentation) that is packaged and delivered as an Intrinsic Data Asset.

This approach decouples the web content from the server binary, allowing HMI developers to update their user interfaces without needing to rebuild or reinstall the entire service.

The workflow is separated into two parts: a one-time installation of this service, and the ongoing management of the HMI content via data assets.

## Content management workflow & usage

Once the service is running, your primary workflow is managing the HMI content through the `inctl data` command. You do not need to rebuild or reinstall the service to update the HMI.

### Step 0: Setup your organization and solution

Export some variables related to the organization in order to build and install you data asset.

```bash
export INTRINSIC_ORG=intrinsic@intrinsic-prod-us
export INTRINSIC_SOLUTION=9999ffff-9999-ffff-9999-ffff9999ffff_BRANCH
```

### Step 1: Build and install your HMI as a data asset

Follow the guide under the *data_assets/platform_http_server* directory, [here](../../data_assets/platform_http_server/README.md) to build and install your data asset.

### Step 2: Configure the service (for initial Load)

The service's `config/default_config_values.textproto` file determines which asset to load on startup.
To load your HMI for the first time, you would set the initial asset ID.

`config/default_config_values.textproto:`

```bash
[type.googleapis.com/platform_http_server.PlatformHttpServerConfig] {
    data_asset_id: "ai.intrinsic.hello_world"
  }
```

When the platform http server starts, it will read this config and immediately serve the content from that asset.

## Service installation (one-time setup)

Before you can serve content, you need to build and install this platform http server into your solution.

  1. **Build the service bundle:**
  This command packages the Python server into a deployable `.tar` bundle.

  ```bash
  bazel build //services/platform_http_server:platform_http_server
  ```

  1. **Install the service into your solution:**
  Use inctl to install the service bundle into a running solution.

  ```bash
  inctl asset install bazel-bin/services/platform_http_server/platform_http_server.bundle.tar --org=ORGANIZATION_NAME 
  ```

  1. **Add your service:**

    * Find the *Services* tab on the right side.
    * Select *Add service*. The Platform HTTP Server service you just installed should be shown in the list with the display name from metadata in the service manifest.
    * Select the Platform HTTP Server service and click Add.
    * You will be prompted for a service name. This can be any unique identifier you like. Use the name *platform_http_server*.
    * Select Apply to add the Platform HTTP Server to the solution. This should be very quick.

  You can add it too with inctl:

  ```bash
  inctl service add ai.intrinsic.platform_http_server --org=ORGANIZATION_NAME 
  ```

The platform http server will start up and should now be available.

Once installed, the service will be running and ready to serve content.

### Access the platform http server

  1. On your browser, paste the desired url. It should follow this format:

  ```bash
  https://flowstate.intrinsic.ai/content/projects/<PROJECT>/uis/onprem/clusters/<CLUSTER>/api/resourceinstances/<SERVICE_NAME>/
  ```

## Updating the platform http server content

There are two primary workflows for updating the HMI content live without rebuilding the service.

### Approach 1: In-Place update with Disable/Enable

This is the recommended approach for deploying a new version of the same HMI.
The server will automatically detect and load the new content when it is re-enabled.

#### Step 1: Disable the Service

Temporarily disable the service to prepare for the update.
You can do it through the Service manager dialog (File -> Service Manager) and untoggle the enable button.

#### Step 2: Build and install the updated data asset

Build the new version of your HMI data asset and install it.
Note that the asset name (e.g., `ai.intrinsic.hello_world`) remains the same, but its content is updated.

  ```bash
  bazel build //data_assets/platform_http_server/frontend_1:hello_world_data
  ```

  ```bash
  inctl data install bazel-bin/data_assets/platform_http_server/frontend_1/hello_world_data.bundle.tar  --solution YOUR_SOLUTION_ID
  ```

#### Step 3: Enable the service

Re-enable the service. This action triggers the server to automatically re-scan the disk, discover the newly installed asset version, and load its content into memory. You can do it through the Service manager dialog (File -> Service Manager) and toggle the enable button.

#### Step 4: Verify the update

Refresh your browser. The HMI should now be serving the updated content.

### Approach 2: Live hot-reload with a new asset

This approach is useful when you want to switch between completely different HMIs (e.g., for A/B testing or diagnostics) without an intermediate disabled state.

#### Step 1: Build and install a new, different date asset

Build and install a second data asset with a unique name (e.g., `ai.intrinsic.hello_world_2`). Follow the guide under the *data_assets/platform_http_server* directory, [here](../../data_assets/platform_http_server/README.md)

#### Step 2: Restart your service

In order to get the previous data asset updated, the server needs to be restarted. Run the following command and wait for a minute. Or restart it from the Service Manager.

```bash
  inctl service state restart hmi
```

#### Step 3: Update the live HMI (hot reload)

To update the HMI, send a POST request to the service's /reconfigure endpoint to trigger a live update.

**NOTE**: This is only available with the intermediate step of `inctl cluster port-forward`.

1. Run the following command for getting the port:

  ```bash
  inctl cluster port-forward --cluster="vmp-0123-abc4d56e"
  ```
1. On your browser, run:

  ```bash
  http://localhost:17081/api/resourceinstances/hmi/
  ```

1. *Use curl to tell the service to load the new version*

```bash
curl -X POST http://<hmi-service-address>:<port>/reconfigure \
     -H "Content-Type: application/json" \
     -d '{"data_asset_id": "ai.intrinsic.hello_world_2"}'
```

Then, manually refresh the page of your localhost and the one from the flowstate, e.g: `https://flowstate.intrinsic.ai/content/projects/giza-workcells/uis/onprem/clusters/vmp-0123-abc4d56e/api/resourceinstances/hmi/` and the server will immediately switch to serving the new content without reinstalling.


## Running the test locally

This project includes a comprehensive test suite (`test_server.py`) for the Platform HTTP Server. The tests validate the HTTP file serving logic, hot-reloading capabilities, lifecycle management, and gRPC service integration.

### What is tested?
* Asset Serving: Verifies that HTML, CSS, JS, and binary files (images/fonts) are served correctly from memory with the proper MIME types.
* Security Headers: Ensures essential headers like Content-Security-Policy and X-Frame-Options are present on every response.
* Hot Reloading: Tests the `/reconfigure` endpoint to confirm the server can switch active data assets on the fly without restarting.
* Lifecycle Management: Validates the `/enable` and `/disable` endpoints, ensuring the server rejects requests when disabled (HTTP 503).
* gRPC Integration: Adds the Intrinsic SDK protobufs to verify the gRPC GetState, Enable, and Disable RPCs function correctly.

### How to Run the Tests
You can run the tests using bazel:

```
bazel test //services/platform_http_server:test_server
```

To see detailed output (including logs and print statements) regardless of pass/fail status:
```
bazel test //services/platform_http_server:test_server --test_output=all
```
