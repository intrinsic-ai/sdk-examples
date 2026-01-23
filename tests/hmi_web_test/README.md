# HMI Web Client (Generated SDK Demo)

This project demonstrates a browser-based HMI client that connects to the Intrinsic Executive Service using the **OpenAPI Auto-Generated TypeScript**.

## Architecture

The connection flows through a local proxy to bypass CORS(Cross-Origin Resource Sharing) and reach the Kubernetes cluster securely:

1.  **Browser (HMI)**: Sends HTTP requests to `/http-gateway/...`
2.  **Vite Proxy**: Forwards requests from `localhost:5173` → `localhost:17081`.
3.  **inctl Tunnel**: Securely tunnels requests from `localhost:17081` → **Remote Cluster**.
4.  **Executive Service**: Receives the command and control the solution.

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

### Step 1: Open the Tunnel (Terminal 1)

You must keep this terminal open to maintain the connection to the solution.

```bash
inctl cluster k8s configure--cluster <YOUR_CLUSTER_NAME> --org <YOUR_ORG>
```

```bash
inctl cluster port-forward --cluster <YOUR_CLUSTER_NAME> --org <YOUR_ORG>
```

### Step 2: Start the Web Server (Terminal 2)

Start the local development server.

```bash
npm run dev
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
