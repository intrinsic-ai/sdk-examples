# Examples for manipulating recordings

This directory contains examples for creating, downloading, and visualizing [solution recordings](https://flowstate.intrinsic.ai/docs/operate/store_transmit_and_access_data/structured_logging/solution_recordings/) using the Python Intrinsic SDK (SDK).

### Setup

* Initialize bazel workspace: ```inctl bazel init --sdk_repository=https://github.com/intrinsic-ai/sdk.git```

### Create recording

Creates a recording on the target cluster.

```bash
bazel run create_recording_py -- --org <ORG_ID> --cluster <CLUSTER_NAME>
```

### Generate and download recording

Generates an MCAP file for a recording and provides a download URL.

```bash
bazel run generate_and_download_recording_py -- --org <ORG_ID> --recording_id <RECORDING_ID>
```

### Generate and visualize recording

Generates a recording and creates a visualization session to view it in the browser.

```bash
bazel run generate_and_visualize_recording_py -- --org <ORG_ID> --recording_id <RECORDING_ID>
```
