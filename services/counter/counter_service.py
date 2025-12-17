#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor
import logging
import sys
import threading

import grpc
from intrinsic.resources.proto import runtime_context_pb2
from services.counter import counter_service_pb2 as counter_proto
from services.counter import counter_service_pb2_grpc as counter_grpc
from intrinsic.platform.pubsub.python import pubsub
from google.protobuf import wrappers_pb2
from pybind11_abseil.status import StatusNotOk

logger = logging.getLogger(__name__)

def WrapIntValue(idx: int) -> wrappers_pb2.Int64Value:
  """Generate a dummy message deterministically, with populated members."""
  msg = wrappers_pb2.Int64Value()
  msg.value = idx
  return msg

def MakeKey(counter_name: str) -> str:
  return f"demo_counters/{counter_name}"

class CounterServicer(counter_grpc.CounterServiceServicer):

  def __init__(self):
    self.pubsub_instance = pubsub.PubSub()
    self.kvstore = self.pubsub_instance.KeyValueStore()

  def Create(
      self,
      request: counter_proto.CreateRequest,
      context: grpc.ServicerContext,
  ) -> counter_proto.CreateResponse:
    
    key = MakeKey(request.counter_name)
    try:      
      logging.info(f"Setting value of {key} to 0")
      self.kvstore.Set(key, WrapIntValue(0))
    except StatusNotOk as e:
      logging.error(f"Failed to set value of {key}: {e.status.message}")
      context.abort(grpc.StatusCode.INTERNAL, "failed to create counter")

    response = counter_proto.CreateResponse()
    return response
  
  def Increment(
      self,
      request: counter_proto.IncrementRequest,
      context: grpc.ServicerContext,
  ) -> counter_proto.IncrementResponse:
    response = counter_proto.IncrementResponse()
    return response
  
  def Get(
      self,
      request: counter_proto.GetRequest,
      context: grpc.ServicerContext,
  ) -> counter_proto.GetResponse:
    key = MakeKey(request.counter_name)
    try:
      logging.info(f"Getting value for key {key}")
      any_msg = self.kvstore.Get(key)
      msg = wrappers_pb2.Int64Value()
      any_msg.Unpack(msg)
      logging.info(f"Got {msg.value}")
    except StatusNotOk as e:
      context.abort(
        grpc.StatusCode.INTERNAL,
        f"failed to get value for counter {request.counter_name}: {e.status.code}, {e.status.message}")

    response = counter_proto.GetResponse()
    response.current_value = msg.value
    return response  


  def GetCurrentValues(
      self,
      request: counter_proto.GetCurrentValuesRequest,
      context: grpc.ServicerContext,
  ) -> counter_proto.GetCurrentValuesResponse:    
    response = counter_proto.GetCurrentValuesResponse()
    cv = threading.Condition()

    def kv_callback(key, wrapped_value):
      msg = wrappers_pb2.Int64Value()
      wrapped_value.Unpack(msg)
      logging.info(f"Got {key} , {msg.value}")
      response_item = response.values.add()
      response_item.counter_name = key
      response_item.current_value = msg.value
      logging.info("Exiting kv_callback")


    def done_callback(key):
      logging.info("All values have been fetched")
      with cv:
        cv.notify()
      logging.info("Notified waiting threads")

    def do_get_all(key):    
      logging.info(f"Calling GetAll({key})")
      query = self.kvstore.GetAll(key, kv_callback, done_callback)
      logging.info("Waiting until all values are fetched")
      with cv:
        cv.wait()
      logging.info("Done waiting for all values")

    key = MakeKey("**")
    worker_thread = threading.Thread(target=do_get_all, args=(key,))
    worker_thread.start()

    logging.info("Waiting for the worker thread")
    worker_thread.join()
    logging.info("Done waiting for the worker thread")

    return response


def get_runtime_context():
  with open('/etc/intrinsic/runtime_config.pb', 'rb') as fin:
    return runtime_context_pb2.RuntimeContext.FromString(fin.read())


def make_grpc_server(port):
  server = grpc.server(
      ThreadPoolExecutor(),
      options=(('grpc.so_reuseport', 0),),
  )

  counter_grpc.add_CounterServiceServicer_to_server(
      CounterServicer(), server
  )
  endpoint = f'[::]:{port}'
  added_port = server.add_insecure_port(endpoint)
  if added_port != port:
    raise RuntimeError(f'Failed to use port {port}')
  return server


def main():
  context = get_runtime_context()

  logging.info(f'Starting Counter service on port: {context.port}')

  server = make_grpc_server(context.port)
  server.start()

  logging.info('--------------------------------')
  logging.info(f'-- Counter service listening on port {context.port}')
  logging.info('--------------------------------')

  server.wait_for_termination()


if __name__ == '__main__':
  logging.basicConfig(stream=sys.stderr, level=logging.INFO)
  main()
