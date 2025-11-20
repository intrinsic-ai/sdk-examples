# Data assets: Frontend

## Step 0: Setup your organization and solution

Export some variables related to the organization in order to build and install your data asset.

```bash
export INTRINSIC_ORG=intrinsic@intrinsic-prod-us
export INTRINSIC_SOLUTION=9999ffff-9999-ffff-9999-ffff9999ffff_BRANCH
```

## Step 1: Build your HMI as a data asset

First, you use a build rule (e.g., in Bazel) to define your data asset, which packages your static files into a versioned bundle. 
Then, you use `inctl data install` to publish this bundle to the catalog.


  ```bash
  bazel build //data_assets/platform_http_server/frontend_{x}:{intrinsic_data_name}
  ```

For example, `bazel build //data_assets/platform_http_server/frontend_2:hello_world_data_2`

## Step 2: Install the data asset to your solution

Use `inctl data install` with the local bundle file to install the data asset into your running solution. This makes the files available on the local filesystem where the Generic HMI Service can access them.

  ```bash
  inctl data install bazel-bin/data_assets/platform_http_server/frontend_x/{intrinsic_data_name}.bundle.tar --solution YOUR_SOLUTION_ID
  ```
For example, `inctl data install bazel-bin/data_assets/platform_http_server/frontend_2/hello_world_data_2.bundle.tar --solution 1a23456b-78c9-0123-4de5-6f7g89h01i23_BRANCH`

**NOTE**: There is an example of a service that uses those data assets. Follow the guide [here](../../services/platform_http_server/README.md).
