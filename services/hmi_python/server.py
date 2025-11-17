"""This script works as the binary for the HMI server."""

#!/usr/bin/env python3

from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
import logging
import pathlib
import sys

from google.longrunning.operations_pb2 import ListOperationsRequest  # type: ignore
from google.protobuf import json_format
import grpc
from intrinsic.executive.proto import executive_service_pb2_grpc
from intrinsic.resources.proto import runtime_context_pb2

logger = logging.getLogger(__name__)

GRPC_INGRESS_ADDRESS = "istio-ingressgateway.app-ingress.svc.cluster.local:80"


def get_runtime_context():
  with open("/etc/intrinsic/runtime_config.pb", "rb") as fin:
    return runtime_context_pb2.RuntimeContext.FromString(fin.read())


def create_executive_stub(connect_timeout: float):
  channel = grpc.insecure_channel(GRPC_INGRESS_ADDRESS)
  grpc.channel_ready_future(channel).result(timeout=connect_timeout)
  return executive_service_pb2_grpc.ExecutiveServiceStub(channel)


class MyHandler(SimpleHTTPRequestHandler):
  """Handler for the HMI server."""

  def __init__(
      self,
      *args,
      **kwargs,
  ):
    # Resolve PWD to create frontend_directory.
    self.frontend_directory = (
        str(pathlib.Path(__file__).parent.resolve()) + "/frontend"
    )
    logging.info(f"Root Direcory: {self.frontend_directory}")
    super().__init__(*args, directory=self.frontend_directory, **kwargs)

  def do_GET(self):

    if self.path == "/":
      # Serving of HTML file.
      self.path = "/index.html"
      with open(self.frontend_directory + self.path, "r") as f:
        file_content = f.read()
      self.send_response(200)
      self.send_header("Content-type", "text/html")
      self.end_headers()
      self.wfile.write(bytes(file_content, encoding="utf-8"))

    elif self.path == "/api/executive/operations":
      # Lists all active operations in the executive.
      executive = create_executive_stub(60)
      response_proto = executive.ListOperations(request=ListOperationsRequest())
      for operation in response_proto.operations:
        operation.ClearField("metadata")
      response_json = json_format.MessageToJson(response_proto)
      logging.info("Operations in the executive: %s", response_json)
      self.send_response(200)
      self.send_header("Content-type", "application/json")
      self.end_headers()
      self.wfile.write(response_json.encode())

    else:
      # Serve other static files as usual.
      super().do_GET()


def main():
  context = get_runtime_context()
  http_port = context.http_port
  logging.info(f" HTTP port provided by runtime context: {http_port}")

  logging.info(f" Creating HTTP server.")
  http_server = HTTPServer(
      server_address=("", http_port), RequestHandlerClass=MyHandler
  )
  logging.info(f" Starting HTTP server.")
  http_server.serve_forever()


if __name__ == "__main__":
  logging.basicConfig(stream=sys.stderr, level=logging.INFO)
  main()
