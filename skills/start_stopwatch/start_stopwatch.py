"""Contains the skill start_stopwatch."""

from absl import logging

from intrinsic.skills.python import proto_utils
from intrinsic.skills.python import skill_interface
from intrinsic.util.decorators import overrides

from skills.start_stopwatch import start_stopwatch_pb2
import grpc
from intrinsic.util.grpc import connection
from intrinsic.util.grpc import interceptor
from services.stopwatch import stopwatch_service_pb2 as stopwatch_proto
from services.stopwatch import stopwatch_service_pb2_grpc as stopwatch_grpc


def make_grpc_stub(resource_handle):
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
  return stopwatch_grpc.StopwatchServiceStub(intercepted_channel)


class StartStopwatch(skill_interface.Skill):
  """Implementation of the start_stopwatch skill."""

  @overrides(skill_interface.Skill)
  def execute(
      self,
      request: skill_interface.ExecuteRequest[
          start_stopwatch_pb2.StartStopwatchParams
      ],
      context: skill_interface.ExecuteContext,
  ) -> None:
    stub = make_grpc_stub(context.resource_handles["stopwatch_service"])

    response = stub.Start(stopwatch_proto.StartRequest())
    if response.success:
      logging.info("Successfully started the stopwatch")
    else:
      logging.error(f"Failed to start the stopwatch: {response.error}")
