# HMI Web Client (Generated SDK Demo)

This project demonstrates a browser-based HMI client that connects to the Intrinsic Executive Service using the **OpenAPI Auto-Generated TypeScript**.

## Architecture

The connection flows through a local proxy to bypass CORS (Cross-Origin Resource Sharing) and reach the Kubernetes cluster securely:

1. **Browser (HMI)**: Sends HTTP requests to `localhost:5173/http-gateway/...`
2. **Vite Proxy**: Intercepts the request, injects the **Authentication Token**, and forwards it securely to `flowstate.intrinsic.ai`.
3. **Executive Service**: Receives the command inside the remote cluster and controls the solution.

## Prerequisites

- **Node.js** (v18 or higher)
- **inctl** (configured for your workcell)

## Setup

1.  **Install Dependencies**

    ```bash
    npm install
    ```

    _Note: Ensure your `.npmrc` is configured to use the public registry or your internal mirror._

2.  **Generate the client code**
    This project does not commit the generated client code. You must build it from the `openapi.yaml` file:
    ```bash
    npm run generate
    ```
    Ensure the `src/generated` folder is created.

## How to Run

This application connects via the secure Flowstate Web Proxy. You must provide your credentials and target URL via environment variables.

### Step 1: Get your Configuration

You need a fresh Access Token and the specific URL of your cluster.

1.  **Generate an Access Token:**

    ```bash
    export TOKEN=$(inctl auth print-access-token --org <YOUR_ORG>)
    ```

2.  **Set the Target URL:**
    Replace <ENV> with your name of the org (e.g., intrinsic-prod-us) and <CLUSTER_ID> with your specific cluster name (e.g., vmp-...).

    ```bash
    export URL="https://flowstate.intrinsic.ai/web-proxy-onprem/<ENV>/<YOUR_CLUSTER_ID>"
    ```

### Step 2: Start the Web Server

Run the development server with the variables injected:

```bash
HMI_SERVER_URL=$URL HMI_AUTH_TOKEN=$TOKEN npm run dev
```

### Step 3: Run the Test

1. Open your browser to the URL shown (usually http://localhost:5173).

2. Open the Developer Console (F12) to see network details (optional).

3. Click the **Run HMI Test Sequence button.**

## What the Test Does

The runTestSequence function performs a cycle:

1. Safety Cleanup: Checks for operations (stuck in RUNNING state) and attempts to delete them.

2. Check for Existing Behavior Trees: Queries the Solution Service for available Behavior Trees:
   - Success: Downloads the real tree (e.g., main.bt.pb).
   - Failure: Auto-generates a "Manual Fallback" tree in memory.

3. Creates a new Operation using the chosen tree.

4. Start the Execution: Sends the StartOperation command.

5. Check status: Polls the status to confirm the state.
