#!/usr/bin/env python3
"""
This script works as the binary for a generic, data-asset-driven HMI server.
It discovers installed data assets, unpacks their content into memory, serves one
specified in a config file, and supports hot-reloading by swapping which
in-memory asset is active. It uses the Flask web framework to provide robust request handling
and to enforce security-enhancing HTTP headers on all response.

This server also implements the gRPC ServiceState servicer, allowing its lifecycle
(enable/disable) to be managed by Flowstate, in addition to HTTP endpoints.
"""

from concurrent import futures
import json
import logging
import mimetypes
import os
import pathlib
import sys
import threading

from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
import grpc
from intrinsic.assets.data.proto.v1 import referenced_data_struct_pb2
# Intrinsic-specific imports
from intrinsic.assets.services.proto.v1 import service_state_pb2 as state_proto
from intrinsic.assets.services.proto.v1 import service_state_pb2_grpc as state_grpc
from intrinsic.resources.proto import runtime_context_pb2
from services.platform_http_server import data_asset_utils
from services.platform_http_server import platform_http_server_pb2
from waitress import serve

app = Flask(__name__)
update_lock = threading.Lock()
_SERVICE_STATE = {}


def get_runtime_context():
  """Reads the runtime context protobuf to get dynamic configuration like the port."""
  if not os.path.exists("/etc/intrinsic/runtime_config.pb"):
    logging.warning(
        "Runtime context not found. Using default port 8080 for local testing."
    )
    return None
  with open("/etc/intrinsic/runtime_config.pb", "rb") as fin:
    return runtime_context_pb2.RuntimeContext.FromString(fin.read())


def load_assets_to_memory():
  """Discovers all installed data assets and unpacks them into a dictionary."""
  data_asset_service = data_asset_utils.DataAssetsService()
  available_assets = data_asset_service.list_data_assets()

  if not available_assets:
    logging.critical("No installed data assets found. Server cannot start.")
    sys.exit(1)

  logging.info(
      f"Found {len(available_assets)} installed data assets. Unpacking to"
      " memory..."
  )

  all_assets_content = {}
  for asset in available_assets:
    asset_id = f"{asset.metadata.id_version.id.package}.{asset.metadata.id_version.id.name}"

    # Check if the asset's data is of the expected type.
    if "ReferencedDataStruct" in asset.data.type_url:
      rds = referenced_data_struct_pb2.ReferencedDataStruct()
      asset.data.Unpack(rds)

      content_map = {
          filename: data_value.referenced_data_value.inlined
          for filename, data_value in rds.fields.items()
      }

      for filename, content in content_map.items():
        logging.info(
            f"  - Loaded '{filename}' ({len(content)} bytes) into memory for"
            f" asset '{asset_id}'."
        )

      all_assets_content[asset_id] = content_map
    else:
      logging.warning(
          f"Skipping asset '{asset_id}' with unexpected data type:"
          f" {asset.data.type_url}"
      )
  return all_assets_content


def _reload_assets_and_enable_service():
  """
  Helper to reload all data assets from disk and set the service state to ENABLED.
  """
  logging.info("Reloading all data assets from disk...")
  all_assets_content = load_assets_to_memory()
  app.config["ALL_ASSETS_CONTENT"] = all_assets_content
  _SERVICE_STATE["state_code"] = state_proto.SelfState.STATE_CODE_ENABLED
  logging.info("Asset reload complete. Service is now ENABLED.")


class PlatformHttpServicer(state_grpc.ServiceStateServicer):
  """Implements the gRPC ServiceState servicer for the HMI server."""

  def GetState(self, request, context):
    """Returns the current state of the service."""
    with update_lock:
      return state_proto.SelfState(state_code=_SERVICE_STATE["state_code"])

  def Enable(self, request, context):
    """Enables the service via gRPC call."""
    with update_lock:
      _reload_assets_and_enable_service()
    logging.info("Service has been enabled via gRPC.")
    return state_proto.EnableResponse()

  def Disable(self, request, context):
    """Disables the service via gRPC call."""
    with update_lock:
      _SERVICE_STATE["state_code"] = state_proto.SelfState.STATE_CODE_DISABLED
    logging.info("Service has been disabled via gRPC.")
    return state_proto.DisableResponse()


@app.after_request
def add_security_headers(response):
  """
  Applies security-enhancing headers to every outgoing response.
  This helps to mitigate common web vulnerabilities.
  """
  # Prevents clickjacking attacks.
  response.headers["X-Frame-Options"] = "SAMEORIGIN"
  # Prevents browsers from MIME-sniffing the content type.
  response.headers["X-Content-Type-Options"] = "nosniff"
  # A robust Content Security Policy to prevent XSS.
  response.headers["Content-Security-Policy"] = "default-src 'self'"
  # Controls how much referrer information is sent.
  response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
  return response


@app.route("/enable", methods=["POST"])
def enable_service():
  """Enables the service, allowing it to serve files."""
  with update_lock:
    _reload_assets_and_enable_service()
  logging.info("Service has been enabled via HTTP.")
  return jsonify({"status": "ENABLED"}), 200


@app.route("/disable", methods=["POST"])
def disable_service():
  """Disables the service, preventing it from serving files."""
  with update_lock:
    _SERVICE_STATE["state_code"] = state_proto.SelfState.STATE_CODE_DISABLED
  logging.info("Service has been disabled via HTTP.")
  return jsonify({"status": "DISABLED"}), 200


@app.route("/status", methods=["GET"])
def get_status():
  """Returns the current state of the service (ENABLED or DISABLED)."""
  with update_lock:
    state_code = _SERVICE_STATE.get("state_code")
    status_str = state_proto.SelfState.StateCode.Name(state_code)
  return jsonify({"status": status_str}), 200


@app.route("/reconfigure", methods=["POST"])
def handle_reconfigure():
  """
  Handles POST requests for hot-reloading the active data asset.
  Expects a JSON payload: {"data_asset_id": "new.asset.id"}
  """
  try:
    data = request.get_json()
    if not data:
      return jsonify({"error": "Request must be valid JSON"}), 400

    new_asset_id = data.get("data_asset_id")
    if not new_asset_id:
      return jsonify({"error": "Missing 'data_asset_id' in request body"}), 400

    logging.info(f"Hot reload triggered for asset: {new_asset_id}")

    all_assets = app.config["ALL_ASSETS_CONTENT"]
    if new_asset_id not in all_assets:
      logging.error(f"Asset '{new_asset_id}' not found in memory.")
      return jsonify({"error": f"Asset '{new_asset_id}' not found"}), 404

    # Atomically swap the active asset ID using the lock.
    with update_lock:
      app.config["ACTIVE_ASSET_ID"] = new_asset_id

    logging.info(f"Successfully reconfigured to serve asset '{new_asset_id}'.")
    return jsonify({"status": "ok"}), 200

  except Exception as e:
    logging.error(f"Reconfiguration failed: {e}", exc_info=True)
    return jsonify({"error": "Internal Server Error"}), 500


@app.route("/")
@app.route("/<path:filepath>")
def serve_file(filepath=None):
  """
  Handles GET requests by looking up the path in the active in-memory asset.
  If the root path '/' is requested, it serves 'index.html' if available.
  """
  path = filepath

  with update_lock:
    if (
        _SERVICE_STATE.get("state_code")
        == state_proto.SelfState.STATE_CODE_DISABLED
    ):
      logging.warning("Request received while service is disabled.")
      return jsonify({"error": "Service is disabled."}), 503
    active_id = app.config["ACTIVE_ASSET_ID"]
    active_content = app.config["ALL_ASSETS_CONTENT"].get(active_id, {})

  if not path:
    for index_file in ["index.html", "hello_world.html"]:
      if index_file in active_content:
        path = index_file
        break

  if not path:
    logging.warning("No index file found to serve for root request.")
    return "File Not Found", 404

  content_bytes = active_content.get(path)

  if content_bytes:
    mime_type, _ = mimetypes.guess_type(path)
    if mime_type and ("\r" in mime_type or "\n" in mime_type):
      logging.error(
          f"Invalid characters detected in mime type for path: {path}"
      )
      return "Bad Request", 400

    # Create a Flask Response object to send the file content.
    return Response(
        content_bytes, mimetype=mime_type or "application/octet-stream"
    )
  else:
    logging.warning(f"File not found in memory: {path}")
    return "File Not Found", 404


def main():
  """Main function to discover assets, unpack them to memory, and run the server."""
  # Discover all installed data assets using the utility service.
  all_assets_content = load_assets_to_memory()
  # Read the configuration to determine which asset to load initially.
  context = get_runtime_context()
  config = platform_http_server_pb2.PlatformHttpServerConfig()
  context.config.Unpack(config)
  initial_asset_id = config.data_asset_id

  if not initial_asset_id:
    logging.critical("Config file is missing 'data_asset_id'.")
    sys.exit(1)

  # Validate that the configured initial asset was found and unpacked.
  if initial_asset_id not in all_assets_content:
    logging.critical(
        f"Initial asset '{initial_asset_id}' from config was not found "
        "or failed to unpack."
    )
    sys.exit(1)

  http_port = context.http_port if context else 8080
  if context and hasattr(context, "grpc_port"):
    grpc_port = context.grpc_port
  else:
    grpc_port = 9090
    logging.warning(
        "gRPC port not found in runtime context. Defaulting to 9090."
    )
  logging.info(f"HTTP port set to: {http_port}")

  _SERVICE_STATE["state_code"] = state_proto.SelfState.STATE_CODE_ENABLED

  # Set the initial configuration for the Flask app.
  app.config["ALL_ASSETS_CONTENT"] = all_assets_content
  app.config["ACTIVE_ASSET_ID"] = initial_asset_id

  grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  state_grpc.add_ServiceStateServicer_to_server(
      PlatformHttpServicer(), grpc_server
  )
  grpc_server.add_insecure_port(f"[::]:{grpc_port}")
  grpc_thread = threading.Thread(target=grpc_server.start, daemon=True)
  grpc_thread.start()
  logging.info(f"gRPC ServiceState server started on port {grpc_port}.")

  logging.info(f"Starting in-memory HMI server on port {http_port}...")
  logging.info(f"Serving initial content from asset '{initial_asset_id}'")
  logging.info(f"Service state is initially 'ENABLED'")
  serve(app, host="0.0.0.0", port=http_port)


if __name__ == "__main__":
  logging.basicConfig(
      stream=sys.stderr,
      level=logging.INFO,
      format="%(asctime)s - %(levelname)s - %(message)s",
  )
  main()
