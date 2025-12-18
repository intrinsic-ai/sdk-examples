"""Contains the points_crud skill."""

from absl import logging
import grpc
from intrinsic.skills.python import proto_utils
from intrinsic.skills.python import skill_interface
from intrinsic.util.decorators import overrides
from intrinsic.util.grpc import connection
from intrinsic.util.grpc import interceptor
from services.points_storage import points_storage_service_pb2 as points_storage_proto
from services.points_storage import points_storage_service_pb2_grpc as points_storage_grpc
from skills.points_crud import points_crud_pb2


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
  return points_storage_grpc.PointsStorageServiceStub(intercepted_channel)


class PointsCrud(skill_interface.Skill):
  """Implementation of the points_crud skill."""

  def store_point(self, stub, execution_log, name: str, x: float, y: float, z: float):
    self.log(execution_log, f"Storing point ({x}, {y}, {z}) under the name {name}")
    request = points_storage_proto.StorePointRequest()
    request.name = name
    request.point.x = x
    request.point.y = y
    request.point.z = z
    stub.Store(request)
    self.log(execution_log, f"Point {name} has been stored")

  def get_point(self, stub, execution_log, name: str):
    self.log(execution_log, f"Fetching point {name}")
    request = points_storage_proto.GetPointRequest()
    request.name = name
    response = stub.Get(request)
    pt = response.point
    self.log(execution_log, f"Got ({pt.x}, {pt.y}, {pt.z})")
    return pt
  
  def get_all_points(self, stub, execution_log):
    self.log(execution_log, "Fetching all points")
    request = points_storage_proto.GetAllPointsRequest()
    response = stub.GetAll(request)
    self.log(execution_log, f"Got {len(response.items)} points:")
    for item in response.items:
      pt = item.point
      self.log(execution_log, f"- Point {item.name}: ({pt.x}, {pt.y}, {pt.z})")
  
  def delete_point(self, stub, execution_log, name: str):
    self.log(execution_log, f"Deleting point {name}")
    request = points_storage_proto.DeleteRequest()
    request.name = name
    stub.Delete(request)
    self.log(execution_log, f"Point {name} has been deleted")

  def log(self, execution_log, message):
    logging.info(message)
    execution_log.messages.append(message)  


  @overrides(skill_interface.Skill)
  def execute(
      self,
      request: skill_interface.ExecuteRequest[
          points_crud_pb2.PointsCrudParams
      ],
      context: skill_interface.ExecuteContext,
  ) -> points_crud_pb2.PointsCrudExecutionLog:
    execution_log = points_crud_pb2.PointsCrudExecutionLog()

    params = request.params
    self.log(execution_log, f"Invoking the skill with create={params.create}, read={params.read}, update={params.update}, delete={params.delete}")
    stub = make_grpc_stub(context.resource_handles["points_storage_service"])

    if params.create:
      self.log(execution_log, "Creating two points")
      self.store_point(stub, execution_log, "A", 1.0, 2.0, 3.0)
      self.store_point(stub, execution_log, "B", 10.0, 20.0, 30.0)

    if params.read:
      self.get_point(stub, execution_log, "A")
      self.get_all_points(stub, execution_log)      

    if params.update:
      self.log(execution_log, "Moving point A by 10 units along X axis")
      pt = self.get_point(stub, execution_log, "A")
      self.store_point(stub, execution_log, "A", pt.x + 10.0, pt.y, pt.z)

      self.log(execution_log, "Fetching point A to confirm that it has been updated")
      self.get_point(stub, execution_log, "A")

    if params.delete:
      self.delete_point(stub, execution_log, "A")
      self.delete_point(stub, execution_log, "B")

      self.log(execution_log, "Fetching all points, expecting an empty list")
      self.get_all_points(stub, execution_log)
      self.log(execution_log, "Done fetching all points")

    return execution_log



    
    
