#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor
import logging
import sys
import threading

import grpc
from intrinsic.resources.proto import runtime_context_pb2
from services.points_storage import points_storage_service_pb2 as points_storage_proto
from services.points_storage import points_storage_service_pb2_grpc as points_storage_grpc
from intrinsic.platform.pubsub.python import pubsub
from google.protobuf import wrappers_pb2
from pybind11_abseil.status import StatusNotOk
from datetime import timedelta

logger = logging.getLogger(__name__)


def MakeKey(point_name: str) -> str:
  return f"points/{point_name}"

class PointsStorageServicer(points_storage_grpc.PointsStorageServiceServicer):

  def __init__(self):
    self.pubsub_instance = pubsub.PubSub()
    self.kvstore = self.pubsub_instance.KeyValueStore()

  def Store(
      self,
      request: points_storage_proto.StorePointRequest,
      context: grpc.ServicerContext,
  ) -> points_storage_proto.StorePointResponse:
    key = MakeKey(request.name)
    try:      
      logging.info(f"Setting value of {key} to ({request.point.x}, {request.point.y}, {request.point.z})")
      self.kvstore.Set(key, request.point)
    except StatusNotOk as e:
      logging.error(f"Failed to set value of {key}: {e.status.message}")
      context.abort(grpc.StatusCode.INTERNAL, f"failed to store point {request.name}: {e.status.message}")

    response = points_storage_proto.StorePointResponse()
    return response
  
  def Get(
      self,
      request: points_storage_proto.GetPointRequest,
      context: grpc.ServicerContext,
  ) -> points_storage_proto.GetPointResponse:
    response = points_storage_proto.GetPointResponse()
    key = MakeKey(request.name)
    try:
      logging.info(f"Getting value for key {key}")
      any_msg = self.kvstore.Get(key)
      pt = points_storage_proto.Point()
      any_msg.Unpack(pt)
      logging.info(f"Got ({pt.x}, {pt.y}, {pt.z})")
      response.point.CopyFrom(pt)
    except StatusNotOk as e:
      context.abort(
        grpc.StatusCode.INTERNAL,
        f"failed to get point {request.name}: {e.status.code}, {e.status.message}")
    
    return response  
  
  def GetAll(
      self,
      request: points_storage_proto.GetAllPointsRequest,
      context: grpc.ServicerContext,
  ) -> points_storage_proto.GetAllPointsResponse:
    response = points_storage_proto.GetAllPointsResponse()
    key = MakeKey("**")
    try:
      all_points = self.kvstore.GetAllSynchronous(key)
      logging.info(f"Got {len(all_points)} points:")
      for key, wrapped_point in all_points.items():
        response_item = response.items.add()
        response_item.name = key
        pt = points_storage_proto.Point()
        wrapped_point.Unpack(pt)
        response_item.point.CopyFrom(pt)
        logging.info(f"- ({pt.x}, {pt.y}, {pt.z})")      
    except StatusNotOk as e:
      context.abort(
          grpc.StatusCode.INTERNAL,
          f"failed to get all points: {e.status.code}, {e.status.message}")
      
    return response
  
  def Delete(
      self,
      request: points_storage_proto.DeleteRequest,
      context: grpc.ServicerContext,
  ) -> points_storage_proto.DeleteResponse:
    key = MakeKey(request.name)
    try:      
      logging.info(f"Deleting value for {key}")
      self.kvstore.Delete(key)
    except StatusNotOk as e:
      logging.error(f"Failed to delete value for {key}: {e.status.message}")
      context.abort(grpc.StatusCode.INTERNAL, f"failed to delete point {request.name}: {e.status.message}")

    response = points_storage_proto.DeleteResponse()
    return response


def get_runtime_context():
  with open('/etc/intrinsic/runtime_config.pb', 'rb') as fin:
    return runtime_context_pb2.RuntimeContext.FromString(fin.read())


def make_grpc_server(port):
  server = grpc.server(
      ThreadPoolExecutor(),
      options=(('grpc.so_reuseport', 0),),
  )

  points_storage_grpc.add_PointsStorageServiceServicer_to_server(
      PointsStorageServicer(), server
  )
  endpoint = f'[::]:{port}'
  added_port = server.add_insecure_port(endpoint)
  if added_port != port:
    raise RuntimeError(f'Failed to use port {port}')
  return server


def main():
  context = get_runtime_context()

  logging.info(f'Starting Points storage service on port: {context.port}')

  server = make_grpc_server(context.port)
  server.start()

  logging.info('--------------------------------')
  logging.info(f'-- Points storage service listening on port {context.port}')
  logging.info('--------------------------------')

  server.wait_for_termination()


if __name__ == '__main__':
  logging.basicConfig(stream=sys.stderr, level=logging.INFO)
  main()
