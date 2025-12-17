"""Contains the skill counter_demo."""

from absl import logging
import grpc
from intrinsic.skills.python import proto_utils
from intrinsic.skills.python import skill_interface
from intrinsic.util.decorators import overrides
from intrinsic.util.grpc import connection
from intrinsic.util.grpc import interceptor
from services.counter import counter_service_pb2 as counter_demo_proto
from services.counter import counter_service_pb2_grpc as counter_demo_grpc
from skills.counter_demo import counter_demo_pb2


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
  return counter_demo_grpc.CounterServiceStub(intercepted_channel)


class CounterDemo(skill_interface.Skill):
  """Implementation of the counter demo skill."""

  @overrides(skill_interface.Skill)
  def execute(
      self,
      request: skill_interface.ExecuteRequest[
          counter_demo_pb2.CounterDemoParams
      ],
      context: skill_interface.ExecuteContext,
  ) -> None:
    stub = make_grpc_stub(context.resource_handles["counter_service"])

    counter_name = "some_counter"

    logging.info(f"--- Creating a counter {counter_name} ---")
    create_counter_request = counter_demo_proto.CreateRequest()
    create_counter_request.counter_name = counter_name
    response = stub.Create(create_counter_request)
    logging.info(f"Got a response: {response}")

    logging.info(f"--- Getting a value of {counter_name} ---")
    get_counter_request = counter_demo_proto.GetRequest()
    get_counter_request.counter_name = counter_name
    response = stub.Get(get_counter_request)
    logging.info(f"Got {response.current_value}")

    logging.info(f"--- Getting all counters ---")
    request = counter_demo_proto.GetCurrentValuesRequest()
    response = stub.GetCurrentValues(request)
    logging.info(f"Got {len(response.values)} counters:")
    for item in response.values:
      logging.info(f"- {item.counter_name} , {item.current_value}")
    
