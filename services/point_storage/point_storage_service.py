#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor
import logging
import sys

import grpc
from intrinsic.platform.pubsub.python import pubsub
from intrinsic.resources.proto import runtime_context_pb2
from services.point_storage import point_storage_service_pb2 as point_storage_proto
from services.point_storage import point_storage_service_pb2_grpc as point_storage_grpc

logger = logging.getLogger(__name__)


def make_key(point_name: str) -> str:
  return f"ai.intrinsic/points/{point_name}"


class PointStorageServicer(point_storage_grpc.PointStorageServiceServicer):
  """Implementation of the Point storage service."""

  def __init__(self):
    self.pubsub_instance = pubsub.PubSub()
    self.kvstore = self.pubsub_instance.KeyValueStore()

  def Put(
      self,
      request: point_storage_proto.PutRequest,
      context: grpc.ServicerContext,
  ) -> point_storage_proto.PutResponse:
    key = make_key(request.name)
    try:
      pt = request.point
      logging.info("Setting value of %s to (%f, %f, %f)", key, pt.x, pt.y, pt.z)
      self.kvstore.Set(key, pt)
      return point_storage_proto.PutResponse()
    except RuntimeError as e:
      logging.error("Caught runtime error %s", e)
      context.abort(
          grpc.StatusCode.INTERNAL,
          f"failed to store point {request.name}: {e}",
      )

  def Get(
      self,
      request: point_storage_proto.GetRequest,
      context: grpc.ServicerContext,
  ) -> point_storage_proto.GetResponse:
    key = make_key(request.name)
    try:
      logging.info("Getting value for key %s", key)
      any_msg = self.kvstore.Get(key)
      pt = point_storage_proto.Point()
      any_msg.Unpack(pt)
      logging.info("Got (%f, %f, %f)", pt.x, pt.y, pt.z)
      return point_storage_proto.GetResponse(point=pt)
    except RuntimeError as e:
      if "NOT_FOUND" in str(e):
        logging.error("Key %s not found", key)
        context.abort(
            grpc.StatusCode.NOT_FOUND,
            f"point {request.name} not found",
        )
      else:
        logging.error("Failed to get point %s: %s", request.name, e)
        context.abort(
            grpc.StatusCode.INTERNAL,
            str(e),
        )

  def GetAll(
      self,
      request: point_storage_proto.GetAllRequest,
      context: grpc.ServicerContext,
  ) -> point_storage_proto.GetAllResponse:
    key = make_key("**")
    try:
      all_points = self.kvstore.GetAllSynchronous(key)
      logging.info("Got %d points", len(all_points))
      response = point_storage_proto.GetAllResponse()
      for key, wrapped_point in all_points.items():
        pt = point_storage_proto.Point()
        wrapped_point.Unpack(pt)
        response.items.append(
            point_storage_proto.NamedPoint(
                name=key.replace("kv_store/ai.intrinsic/points/", ""), point=pt
            )
        )
        logging.info("- (%f, %f, %f)", pt.x, pt.y, pt.z)
      return response
    except RuntimeError as e:
      logging.error("Failed to get all points matching %s: %s", key, e)
      context.abort(
          grpc.StatusCode.INTERNAL,
          str(e),
      )

  def Delete(
      self,
      request: point_storage_proto.DeleteRequest,
      context: grpc.ServicerContext,
  ) -> point_storage_proto.DeleteResponse:
    key = make_key(request.name)
    try:
      logging.info("Deleting value for %s", key)
      self.kvstore.Delete(key)
      return point_storage_proto.DeleteResponse()
    except RuntimeError as e:
      logging.error("Failed to delete point %s: %s", request.name, e)
      context.abort(
          grpc.StatusCode.INTERNAL,
          str(e),
      )


def get_runtime_context():
  with open("/etc/intrinsic/runtime_config.pb", "rb") as fin:
    return runtime_context_pb2.RuntimeContext.FromString(fin.read())


def make_grpc_server(port):
  server = grpc.server(
      ThreadPoolExecutor(),
      options=(("grpc.so_reuseport", 0),),
  )

  point_storage_grpc.add_PointStorageServiceServicer_to_server(
      PointStorageServicer(), server
  )
  endpoint = f"[::]:{port}"
  added_port = server.add_insecure_port(endpoint)
  if added_port != port:
    raise RuntimeError(f"Failed to use port {port}")
  return server


def main():
  context = get_runtime_context()

  logging.info("Starting Point storage service on port: %d", context.port)

  server = make_grpc_server(context.port)
  server.start()

  logging.info("--------------------------------")
  logging.info("-- Point storage service listening on port %d", context.port)
  logging.info("--------------------------------")

  server.wait_for_termination()


if __name__ == "__main__":
  logging.basicConfig(stream=sys.stderr, level=logging.INFO)
  main()
