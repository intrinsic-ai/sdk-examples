import unittest

from intrinsic.skills.testing import skill_test_utils as stu
from services.stopwatch import stopwatch_service_pb2 as stopwatch_proto
from services.stopwatch import stopwatch_service_pb2_grpc as stopwatch_grpc
from skills.start_stopwatch.start_stopwatch import StartStopwatch
from skills.start_stopwatch.start_stopwatch_pb2 import StartStopwatchParams


class FakeStopwatchServicer(stopwatch_grpc.StopwatchServiceServicer):

  def Start(self, request, context):
    response = stopwatch_proto.StartResponse()
    response.success = True
    return response


class StartStopwatchTest(unittest.TestCase):

  def test_execute(self):
    skill = StartStopwatch()
    server, handle = stu.make_grpc_server_with_resource_handle(
        "stopwatch_service"
    )
    stopwatch_grpc.add_StopwatchServiceServicer_to_server(
        FakeStopwatchServicer(), server
    )
    server.start()

    params = StartStopwatchParams()

    context = stu.make_test_execute_context(
        resource_handles={handle.name: handle},
    )
    request = stu.make_test_execute_request(params)

    with self.assertLogs() as log_output:
      skill.execute(request, context)

    output = log_output[0][3].message
    self.assertEqual(output, "Successfully started the stopwatch")


if __name__ == "__main__":
  unittest.main()
