#!/usr/bin/env python3

from absl import logging
import grpc

from intrinsic.skills.python import skill_interface
from intrinsic.util.decorators import overrides
from intrinsic.util.grpc import connection
from intrinsic.util.grpc import interceptor

from services.random_number import random_number_pb2 as rand_num_proto
from services.random_number import random_number_pb2_grpc as rand_num_grpc
from skills.get_random_number import get_random_number_pb2 as get_rand_num_proto


def _make_grpc_stub(resource_handle):
  logging.info(f"Address: {resource_handle.connection_info.grpc.address}")
  logging.info(
      f"Server Instance: {resource_handle.connection_info.grpc.server_instance}"
  )
  logging.info(f"Header: {resource_handle.connection_info.grpc.header}")

  # Create a gRPC channel without using TLS
  grpc_info = resource_handle.connection_info.grpc
  grpc_channel = grpc.insecure_channel(grpc_info.address)
  connection_params = connection.ConnectionParams(
      grpc_info.address, grpc_info.server_instance, grpc_info.header
  )

  intercepted_channel = grpc.intercept_channel(
      grpc_channel,
      interceptor.HeaderAdderInterceptor(connection_params.headers),
  )
  return rand_num_grpc.RandomNumberServiceStub(intercepted_channel)


class GetRandomNumber(skill_interface.Skill):
  """Get Random Number Skill used to interact with the Random Number Service.
  The skill takes a start and end range to send to the Random Number Service and returns the result from
  the Service.
  """

  @overrides(skill_interface.Skill)
  def execute(
      self,
      request: skill_interface.ExecuteRequest[
          get_rand_num_proto.GetRandomNumberParams
      ],
      context: skill_interface.ExecuteContext,
  ) -> get_rand_num_proto.GetRandomNumberResult:
    resource_handle = context.resource_handles["random_number_service"]
    stub = _make_grpc_stub(resource_handle)

    logging.info(f"Input params: {request.params}")

    try:
      service_result = stub.GetRandomNumber(
          rand_num_proto.RandomNumberRequest(
              range_start=request.params.range_start,
              range_end=request.params.range_end,
          )
      )
    except grpc.RpcError as e:
      raise skill_interface.SkillError(
          code=e.code().value[0], message=e.details()
      )

    logging.info(f"Result: {service_result.result}")

    return get_rand_num_proto.GetRandomNumberResult(
        result=service_result.result
    )
