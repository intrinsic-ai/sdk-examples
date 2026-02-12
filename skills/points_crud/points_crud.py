"""Contains the points_crud skill."""

from absl import logging
import grpc
from intrinsic.skills.python import skill_interface
from intrinsic.util.decorators import overrides
from intrinsic.util.grpc import connection
from intrinsic.util.grpc import interceptor
from services.point_storage import point_storage_service_pb2 as point_storage_proto
from services.point_storage import point_storage_service_pb2_grpc as point_storage_grpc
from skills.points_crud import points_crud_pb2


def make_grpc_stub(resource_handle):
  logging.info("Address: %s", resource_handle.connection_info.grpc.address)
  logging.info(
      "Server Instance: %s",
      resource_handle.connection_info.grpc.server_instance,
  )
  logging.info("Header: %s", resource_handle.connection_info.grpc.header)

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
  return point_storage_grpc.PointStorageServiceStub(intercepted_channel)


class PointsCrud(skill_interface.Skill):
  """Implementation of the points_crud skill."""

  def put(self, stub, name: str, x: float, y: float, z: float):
    logging.info("Storing point (%f, %f, %f) under the name %s", x, y, z, name)
    request = point_storage_proto.PutRequest()
    request.name = name
    request.point.x = x
    request.point.y = y
    request.point.z = z
    stub.Put(request)
    logging.info("Point %s has been stored", name)

  def get_point_by_name(self, stub, name: str) -> point_storage_proto.Point:
    logging.info("Fetching point %s", name)
    request = point_storage_proto.GetRequest()
    request.name = name
    try:
      response = stub.Get(request)
      pt = response.point
      logging.info("Got (%f, %f, %f)", pt.x, pt.y, pt.z)
      return pt
    except grpc.RpcError as e:
      self.log_rpc_error(e)
      raise RuntimeError(f"Failed to read point {name}") from e

  def get(self, stub, name: str) -> points_crud_pb2.PointsCrudResult:
    pt = self.get_point_by_name(stub, name)
    result = points_crud_pb2.PointsCrudResult(
        get=points_crud_pb2.GetResult(
            point=point_storage_proto.NamedPoint(name=name, point=pt)
        )
    )
    return result

  def log_rpc_error(self, e: grpc.RpcError):
    logging.error("Got an error %s: %s", e.code(), e.details())

  @overrides(skill_interface.Skill)
  def execute(
      self,
      request: skill_interface.ExecuteRequest[points_crud_pb2.PointsCrudParams],
      context: skill_interface.ExecuteContext,
  ) -> points_crud_pb2.PointsCrudResult:
    params = request.params
    operation = params.WhichOneof("operation")
    logging.info("--- Invoking the skill with parameters = %s ---", params)
    stub = make_grpc_stub(context.resource_handles["point_storage_service"])

    match operation:
      case "put":
        pt_name = params.put.point_name
        coords = params.put.coordinates
        try:
          self.put(stub, pt_name, coords.x, coords.y, coords.z)
        except grpc.RpcError as e:
          self.log_rpc_error(e)
          raise RuntimeError(f"Failed to store point {pt_name}") from e
        result = points_crud_pb2.PointsCrudResult(
            put=points_crud_pb2.PutResult(
                point=point_storage_proto.NamedPoint(
                    name=pt_name,
                    point=self.get_point_by_name(stub, pt_name),
                )
            )
        )
        return result

      case "get":
        return self.get(stub, params.get.point_name)

      case "get_all":
        logging.info("Fetching all points")
        request = point_storage_proto.GetAllRequest()

        try:
          response = stub.GetAll(request)
        except grpc.RpcError as e:
          self.log_rpc_error(e)
          raise RuntimeError("Failed to get all points") from e

        ret = points_crud_pb2.PointsCrudResult(
            get_all=points_crud_pb2.GetAllResult()
        )
        get_all_result = ret.get_all
        logging.info("Got %d points", len(response.items))
        for item in response.items:
          pt = item.point
          logging.info("- Point %s: (%f, %f, %f)", item.name, pt.x, pt.y, pt.z)
          get_all_result.items.append(item)
        return ret

      case "update":
        pt_name = params.update.point_name
        offset = params.update.offset
        pt = self.get_point_by_name(stub, pt_name)
        try:
          logging.info(
              "Moving point %s by (%f, %f, %f)",
              pt_name,
              offset.x,
              offset.y,
              offset.z,
          )
          self.put(
              stub,
              pt_name,
              pt.x + offset.x,
              pt.y + offset.y,
              pt.z + offset.z,
          )
        except grpc.RpcError as e:
          self.log_rpc_error(e)
          raise RuntimeError(f"Failed to store updated point {pt_name}") from e

        logging.info(
            "Fetching point %s to confirm that it has been updated", pt_name
        )
        result = points_crud_pb2.PointsCrudResult(
            update=points_crud_pb2.UpdateResult(
                updated_point=point_storage_proto.NamedPoint(
                    name=pt_name,
                    point=self.get_point_by_name(stub, pt_name),
                )
            )
        )
        return result

      case "delete":
        pt_name = params.delete.point_name
        try:
          logging.info("Deleting point %s", pt_name)
          request = point_storage_proto.DeleteRequest(name=pt_name)
          stub.Delete(request)
          logging.info("Point %s has been deleted", pt_name)
        except grpc.RpcError as e:
          self.log_rpc_error(e)
          raise RuntimeError(f"Failed to delete point {pt_name}") from e

        result = points_crud_pb2.PointsCrudResult(
            delete=points_crud_pb2.DeleteResult()
        )
        return result

      case _:
        raise ValueError(f"Unknown operation {params.op}")
