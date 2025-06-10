import unittest

from intrinsic.skills.testing import skill_test_utils as stu

from skills.stop_stopwatch.stop_stopwatch import StopStopwatch
from skills.stop_stopwatch.stop_stopwatch_pb2 import StopStopwatchParams
from services.stopwatch import stopwatch_service_pb2 as stopwatch_proto
from services.stopwatch import stopwatch_service_pb2_grpc as stopwatch_grpc


class FakeStopwatchServicer(stopwatch_grpc.StopwatchServiceServicer):

  def Stop(self, request, context):
    response = stopwatch_proto.StopResponse()
    response.time_elapsed = 42
    response.success = True
    return response


class StopStopwatchTest(unittest.TestCase):

  def test_get_footprint(self):
    skill = StopStopwatch()
    server, handle = stu.make_grpc_server_with_resource_handle(
        "stopwatch_service"
    )
    stopwatch_grpc.add_StopwatchServiceServicer_to_server(
        FakeStopwatchServicer(), server
    )
    server.start()

    params = StopStopwatchParams()

    context = stu.make_test_get_footprint_context(
        resource_handles={handle.name: handle},
    )
    request = stu.make_test_get_footprint_request(params)

    result = skill.get_footprint(request, context)
    self.assertTrue(result.lock_the_universe)

  def test_preview(self):
    skill = StopStopwatch()
    server, handle = stu.make_grpc_server_with_resource_handle(
        "stopwatch_service"
    )
    stopwatch_grpc.add_StopwatchServiceServicer_to_server(
        FakeStopwatchServicer(), server
    )
    server.start()

    params = StopStopwatchParams()

    context = stu.make_test_preview_context(
        resource_handles={handle.name: handle},
    )
    request = stu.make_test_preview_request(params)

    # Update this test when you implement preview
    with self.assertRaises(NotImplementedError):
      skill.preview(request, context)

  def test_execute(self):
    skill = StopStopwatch()
    server, handle = stu.make_grpc_server_with_resource_handle(
        "stopwatch_service"
    )
    stopwatch_grpc.add_StopwatchServiceServicer_to_server(
        FakeStopwatchServicer(), server
    )
    server.start()

    params = StopStopwatchParams()

    context = stu.make_test_execute_context(
        resource_handles={handle.name: handle},
    )
    request = stu.make_test_execute_request(params)

    result = skill.execute(request, context)

    self.assertEqual(result.time_elapsed, 42)


if __name__ == "__main__":
  unittest.main()
