import logging
from typing import Any
from typing import Callable
from typing import List
from typing import Optional
from typing import Tuple

import grpc
from intrinsic.assets.data.proto.v1 import data_asset_pb2
from intrinsic.assets.data.proto.v1 import data_assets_pb2
from intrinsic.assets.data.proto.v1 import data_assets_pb2_grpc
from intrinsic.assets.proto import id_pb2


def create_insecure_channel(
    server_address: str,
    server_port: str,
    grpc_options: Optional[List[Tuple[str, Any]]] = None,
) -> grpc.Channel:
  """Creates an insecure gRPC channel."""
  server_endpoint = f"{server_address}:{server_port}"
  logging.info("Creating insecure channel at: %s", server_endpoint)
  channel = grpc.insecure_channel(server_endpoint, options=grpc_options)
  grpc.channel_ready_future(channel).result(timeout=10.0)
  return channel


class DataAssetsService:
  """Client for the gRPC Data Assets service.

  This class provides a Python interface to interact with the Data Assets
  service, allowing users to list and retrieve data assets.

  Attributes:
      _channel: The insecure gRPC channel used for communication.
      _stub: The gRPC stub to make API calls.
  """

  def __init__(
      self,
      address: str = "istio-ingressgateway.app-ingress.svc.cluster.local",
      port: str = "80",
      grpc_options: Optional[List[Tuple[str, Any]]] = None,
  ):
    self._channel = create_insecure_channel(address, port, grpc_options)
    self._stub = data_assets_pb2_grpc.DataAssetsStub(self._channel)

  def list_data_assets(
      self, proto_name: str | None = None
  ) -> List[data_asset_pb2.DataAsset]:
    if proto_name is None:
      list_data_assets_request = data_assets_pb2.ListDataAssetsRequest()
    else:
      list_data_assets_request = data_assets_pb2.ListDataAssetsRequest(
          strict_filter=data_assets_pb2.DataAssetFilter(
              proto_name=proto_name,
          )
      )
    response = self._stub.ListDataAssets(list_data_assets_request)
    return response.data_assets


def get_data_asset(self, package: str, name: str) -> data_asset_pb2.DataAsset:
  return self._stub.GetDataAsset(
      data_assets_pb2.GetDataAssetRequest(
          id=id_pb2.Id(package=package, name=name)
      )
  )
