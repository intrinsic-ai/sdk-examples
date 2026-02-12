from typing import Dict
from typing import List
import unittest

import grpc
from intrinsic.skills.testing import skill_test_utils as stu
from intrinsic.solutions.testing import compare
from services.point_storage import point_storage_service_pb2 as point_storage_proto
from services.point_storage import point_storage_service_pb2_grpc as point_storage_grpc
from skills.points_crud import points_crud
from skills.points_crud import points_crud_pb2

_POINT_A = point_storage_proto.Point(x=1.0, y=2.0, z=3.0)
_POINT_B = point_storage_proto.Point(x=10.0, y=20.0, z=30.0)

_INITIAL_STATE = {
    "A": _POINT_A,
    "B": _POINT_B,
}


class SuccessfulFakePointStorageServicer(
    point_storage_grpc.PointStorageServiceServicer
):
  """Fake implementation of the point storage service.

  Designed to test successful invocations of the skill.
  Stores all data in memory.
  """

  def __init__(self, initial_state: Dict[str, point_storage_proto.Point]):
    # Copying initial_state because tests may modify it.
    self._data = initial_state.copy()

  def Put(
      self,
      request: point_storage_proto.PutRequest,
      context: grpc.ServicerContext,
  ) -> point_storage_proto.PutResponse:
    self._data[request.name] = request.point
    return point_storage_proto.PutResponse()

  def Get(
      self,
      request: point_storage_proto.GetRequest,
      context: grpc.ServicerContext,
  ) -> point_storage_proto.GetResponse:
    return point_storage_proto.GetResponse(point=self._data[request.name])

  def GetAll(
      self,
      request: point_storage_proto.GetAllRequest,
      context: grpc.ServicerContext,
  ) -> point_storage_proto.GetAllResponse:
    response = point_storage_proto.GetAllResponse()
    for k, v in self._data.items():
      response.items.append(point_storage_proto.NamedPoint(name=k, point=v))
    return response

  def Delete(
      self,
      request: point_storage_proto.DeleteRequest,
      context: grpc.ServicerContext,
  ) -> point_storage_proto.DeleteResponse:
    if request.name in self._data:
      del self._data[request.name]
    return point_storage_proto.DeleteResponse()


class FailingFakePointStorageServicer(
    point_storage_grpc.PointStorageServiceServicer
):
  """Fake implementation of the point storage service that always fails."""

  def Put(
      self,
      request: point_storage_proto.PutRequest,
      context: grpc.ServicerContext,
  ) -> point_storage_proto.PutResponse:
    context.abort(
        grpc.StatusCode.INTERNAL, f"Failed to store point {request.name}"
    )

  def Get(
      self,
      request: point_storage_proto.GetRequest,
      context: grpc.ServicerContext,
  ) -> point_storage_proto.GetResponse:
    context.abort(grpc.StatusCode.NOT_FOUND, f"Point {request.name} not found")

  def GetAll(
      self,
      request: point_storage_proto.GetAllRequest,
      context: grpc.ServicerContext,
  ) -> point_storage_proto.GetAllResponse:
    context.abort(grpc.StatusCode.INTERNAL, "Failed to read all points")

  def Delete(
      self,
      request: point_storage_proto.DeleteRequest,
      context: grpc.ServicerContext,
  ) -> point_storage_proto.DeleteResponse:
    context.abort(
        grpc.StatusCode.INTERNAL, f"Failed to delete point {request.name}"
    )


class PointsCrudTest(unittest.TestCase):

  def run_test(
      self,
      initial_state: Dict[str, point_storage_proto.Point],
      params: points_crud_pb2.PointsCrudParams,
      expected_result: points_crud_pb2.PointsCrudResult,
      failure_message: str,
  ):
    """Executes the skill in success and failure modes.

    The skill is executed twice. On the first run, it receives a successful
    response from the point storage service. On the second run, it receives an
    error.

    Args:
      initial_state - data that will be added to the KV storage at the beginning
        of the test.
      params - skill execution parameters.
      expected_result - the value that the skill is expected to return
        if it succeeds.
      failure_message - message in the exception that the skill is expected to
        throw if it fails.
    """
    for should_succeed in [True, False]:
      skill = points_crud.PointsCrud()
      server, handle = stu.make_grpc_server_with_resource_handle(
          "point_storage_service"
      )
      if should_succeed:
        servicer = SuccessfulFakePointStorageServicer(initial_state)
      else:
        servicer = FailingFakePointStorageServicer()
      point_storage_grpc.add_PointStorageServiceServicer_to_server(
          servicer,
          server,
      )
      server.start()
      context = stu.make_test_execute_context(
          resource_handles={handle.name: handle},
      )

      request = stu.make_test_execute_request(params)
      if should_succeed:
        result = skill.execute(request, context)
        compare.assertProto2SameElements(self, result, expected_result)
      else:
        with self.assertRaisesRegex(RuntimeError, failure_message):
          skill.execute(request, context)

  def test_put(self):
    params = points_crud_pb2.PointsCrudParams(
        put=points_crud_pb2.PutParams(point_name="A", coordinates=_POINT_A)
    )
    expected_result = points_crud_pb2.PointsCrudResult(
        put=points_crud_pb2.PutResult(
            point=point_storage_proto.NamedPoint(name="A", point=_POINT_A)
        )
    )
    self.run_test(
        initial_state={},
        params=params,
        expected_result=expected_result,
        failure_message="Failed to store point",
    )

  def test_get(self):
    params = points_crud_pb2.PointsCrudParams(
        get=points_crud_pb2.GetParams(point_name="A")
    )
    expected_result = points_crud_pb2.PointsCrudResult(
        get=points_crud_pb2.GetResult(
            point=point_storage_proto.NamedPoint(name="A", point=_POINT_A)
        )
    )
    self.run_test(
        initial_state=_INITIAL_STATE,
        params=params,
        expected_result=expected_result,
        failure_message="Failed to read point A",
    )

  def test_get_all(self):
    params = points_crud_pb2.PointsCrudParams(
        get_all=points_crud_pb2.GetAllParams()
    )
    expected_result = points_crud_pb2.PointsCrudResult(
        get_all=points_crud_pb2.GetAllResult(
            items=[
                point_storage_proto.NamedPoint(name="A", point=_POINT_A),
                point_storage_proto.NamedPoint(name="B", point=_POINT_B),
            ]
        )
    )
    self.run_test(
        initial_state=_INITIAL_STATE,
        params=params,
        expected_result=expected_result,
        failure_message="Failed to get all points",
    )

  def test_update(self):
    params = points_crud_pb2.PointsCrudParams(
        update=points_crud_pb2.UpdateParams(
            point_name="A",
            offset=point_storage_proto.Point(x=10.0, y=-2.0, z=12.0),
        )
    )
    expected_result = points_crud_pb2.PointsCrudResult(
        update=points_crud_pb2.UpdateResult(
            updated_point=point_storage_proto.NamedPoint(
                name="A",
                point=point_storage_proto.Point(x=11.0, y=0.0, z=15.0),
            )
        )
    )
    self.run_test(
        initial_state=_INITIAL_STATE,
        params=params,
        expected_result=expected_result,
        failure_message="Failed to read point",
    )

  def test_delete(self):
    params = points_crud_pb2.PointsCrudParams(
        delete=points_crud_pb2.DeleteParams(point_name="A")
    )
    expected_result = points_crud_pb2.PointsCrudResult(
        delete=points_crud_pb2.DeleteResult()
    )
    self.run_test(
        initial_state=_INITIAL_STATE,
        params=params,
        expected_result=expected_result,
        failure_message="Failed to delete point A",
    )


if __name__ == "__main__":
  unittest.main()
