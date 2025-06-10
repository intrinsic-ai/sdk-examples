#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor
import logging
import sys
import time

import grpc
from intrinsic.resources.proto import runtime_context_pb2

from services.stopwatch import stopwatch_service_pb2 as stopwatch_proto
from services.stopwatch import stopwatch_service_pb2_grpc as stopwatch_grpc


logger = logging.getLogger(__name__)


class StopwatchServicer(stopwatch_grpc.StopwatchServiceServicer):

  def __init__(self):
    self._start_time = None

  def Start(
      self,
      request: stopwatch_proto.StartRequest,
      context: grpc.ServicerContext,
  ) -> stopwatch_proto.StartResponse:
    response = stopwatch_proto.StartResponse()
    if self._start_time is None:
      self._start_time = time.monotonic()
      logging.info(f'Starting stopwatch {self._start_time}')
      response.success = True
    else:
      response.success = False
      response.error = 'Cannot start stopwatch because it is already started'
      logging.error(response.error)
    return response

  def Stop(
      self,
      request: stopwatch_proto.StopRequest,
      context: grpc.ServicerContext,
  ) -> stopwatch_proto.StopResponse:
    response = stopwatch_proto.StopResponse()
    if self._start_time is not None:
      response.time_elapsed = time.monotonic() - self._start_time
      self._start_time = None
      logging.info(f'Stopping stopwatch {response.time_elapsed}')
      response.success = True
    else:
      response.success = False
      response.error = 'Cannot stop stopwatch because it is not started'
      logging.error(response.error)
    return response


def get_runtime_context():
  with open('/etc/intrinsic/runtime_config.pb', 'rb') as fin:
    return runtime_context_pb2.RuntimeContext.FromString(fin.read())


def make_grpc_server(port):
  server = grpc.server(
      ThreadPoolExecutor(),
      options=(('grpc.so_reuseport', 0),),
  )

  stopwatch_grpc.add_StopwatchServiceServicer_to_server(
      StopwatchServicer(), server
  )
  endpoint = f'[::]:{port}'
  added_port = server.add_insecure_port(endpoint)
  if added_port != port:
    raise RuntimeError(f'Failed to use port {port}')
  return server


def main():
  context = get_runtime_context()

  logging.info(f'Starting Stopwatch service on port: {context.port}')

  server = make_grpc_server(context.port)
  server.start()

  logging.info('--------------------------------')
  logging.info(f'-- Stopwatch service listening on port {context.port}')
  logging.info('--------------------------------')

  server.wait_for_termination()


if __name__ == '__main__':
  logging.basicConfig(stream=sys.stderr, level=logging.INFO)
  main()
