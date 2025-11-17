#!/usr/bin/env python3
from concurrent import futures
import logging
import sys

import grpc
from intrinsic.assets.services.proto.v1 import service_state_pb2_grpc as state_grpc
from intrinsic.resources.proto import runtime_context_pb2
from services.random_number import random_number
from services.random_number import random_number_pb2_grpc as random_num_grpc


def _get_runtime_context():
  with open('/etc/intrinsic/runtime_config.pb', 'rb') as fin:
    return runtime_context_pb2.RuntimeContext.FromString(fin.read())


def _make_grpc_server(port: int):
  server = grpc.server(
      futures.ThreadPoolExecutor(),
      options=(('grpc.so_reuseport', 0),),
  )
  servicer = random_number.RandomNumberServicer()
  random_num_grpc.add_RandomNumberServiceServicer_to_server(servicer, server)
  state_grpc.add_ServiceStateServicer_to_server(servicer, server)
  endpoint = f'[::]:{port}'
  added_port = server.add_insecure_port(endpoint)
  if added_port != port:
    raise RuntimeError(f'Failed to use port {port}')
  return server


def main():
  context = _get_runtime_context()

  logging.info(f'Starting Random Number Service on port: {context.port}')

  server = _make_grpc_server(context.port)
  server.start()

  logging.info('---------------------------------------------------------')
  logging.info(f'-- Random Number Service listening on port {context.port}')
  logging.info('---------------------------------------------------------')

  server.wait_for_termination()


if __name__ == '__main__':
  logging.basicConfig(stream=sys.stderr, level=logging.INFO)
  main()
