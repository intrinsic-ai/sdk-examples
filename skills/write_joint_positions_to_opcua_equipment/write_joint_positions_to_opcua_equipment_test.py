import unittest
from unittest.mock import create_autospec
from unittest.mock import patch

import grpc
from grpc.framework.foundation import logging_pool

from intrinsic.icon.proto.v1 import service_pb2
from intrinsic.icon.python import icon_api
from intrinsic.skills.python import skill_interface
from intrinsic.hardware.opcua_equipment import opcua_equipment_service_pb2
from intrinsic.hardware.opcua_equipment import (
    opcua_equipment_service_pb2_grpc,
)
from intrinsic.resources.proto import resource_handle_pb2
from skills.write_joint_positions_to_opcua_equipment import (
    write_joint_positions_to_opcua_equipment,
    write_joint_positions_to_opcua_equipment_pb2,
)

WriteJointPositionsToOpcuaEquipment = (
    write_joint_positions_to_opcua_equipment.WriteJointPositionsToOpcuaEquipment
)
MOCK_SERVICE_ADDR = "localhost"
MOCK_SERVICE_INSTANCE = "test_service"

EXPECTED_JOINT_POSITIONS = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
STORED_JOINT_POSITIONS = []


def _make_local_testing_server() -> tuple[grpc.Server, int]:
  """Makes a local server for testing.

  The server is started before returning.

  Returns:
    A tuple (server, port), where `server` is the local server, and `port` is
    the port on which the local server is listening.
  """
  port = 12345

  server_pool = logging_pool.pool(max_workers=25)
  server = grpc.server(server_pool)
  server.add_secure_port(f"[::]:{port}", grpc.local_server_credentials())
  server.start()

  return server, port


class TestingWriteJointPositionsToOpcuaEquipmentServiceServicer(
    opcua_equipment_service_pb2_grpc.OpcuaEquipmentServiceServicer
):
  """A servicer for testing the WriteJointPositionsToOpcuaEquipment skill."""

  def Control(
      self,
      request: opcua_equipment_service_pb2.ControlRequest,
      context: grpc.ServicerContext,
  ) -> opcua_equipment_service_pb2.ControlResponse:
    for ax in range(1, 7):
      STORED_JOINT_POSITIONS.append(
          request.user_input[f"lrAxis{ax}"].double_value
      )

    return opcua_equipment_service_pb2.ControlResponse(
        success=True,
    )


class WriteJointPositionsToOpcuaEquipmentTest(unittest.TestCase):

  def make_execute_context_with_resource_handles(self, resource_handles):
    mock_context = create_autospec(
        spec=skill_interface.ExecuteContext, spec_set=True, instance=True
    )
    mock_context.resource_handles = resource_handles
    return mock_context

  def setUp(self) -> None:
    self._server, self._port = _make_local_testing_server()
    self._servicer = TestingWriteJointPositionsToOpcuaEquipmentServiceServicer()
    opcua_equipment_service_pb2_grpc.add_OpcuaEquipmentServiceServicer_to_server(
        self._servicer, self._server
    )
    self.equipment_utils_patcher = patch(
        "skills.write_joint_positions_to_opcua_equipment.write_joint_positions_to_opcua_equipment.equipment_utils",
        spec_set=True,
        autospec=True,
    )
    self.mock_equipment_utils = self.equipment_utils_patcher.start()
    self.mock_icon_client = create_autospec(
        spec=icon_api.Client, spec_set=True, instance=True
    )
    self.mock_equipment_utils.init_icon_client.return_value = (
        self.mock_icon_client
    )

    self.mock_equipment_utils.get_position_part_name.return_value = "arm"
    fake_status_resp = service_pb2.GetStatusResponse()

    # Set the mock robot arm to the expected joint positions.
    for ax in EXPECTED_JOINT_POSITIONS:
      fake_status_resp.part_status["arm"].joint_states.add().position_sensed = (
          ax
      )
    self.mock_icon_client.get_status.return_value = fake_status_resp

    self._skill = WriteJointPositionsToOpcuaEquipment()
    self._resource_handles = {
        write_joint_positions_to_opcua_equipment._EQUIPMENT_SLOT: (
            resource_handle_pb2.ResourceHandle(
                connection_info=resource_handle_pb2.ResourceConnectionInfo(
                    grpc=resource_handle_pb2.ResourceGrpcConnectionInfo(
                        address=f"{MOCK_SERVICE_ADDR}:{self._port}",
                        server_instance=MOCK_SERVICE_INSTANCE,
                    )
                ),
                resource_data=None,
                name="test_equipment",
            )
        ),
        # Add a placeholder for the robot slot.
        write_joint_positions_to_opcua_equipment._ROBOT_SLOT: (
            resource_handle_pb2.ResourceHandle()
        ),
    }

  def tearDown(self) -> None:
    self._server.stop(grace=None)

  def test_execute(self):
    mock_request = skill_interface.ExecuteRequest(
        params=write_joint_positions_to_opcua_equipment_pb2.WriteJointPositionsToOpcuaEquipmentParams()
    )

    mock_context = self.make_execute_context_with_resource_handles(
        self._resource_handles
    )

    self._skill.execute(mock_request, mock_context)

    # Ensure that the joint positions stored by the skill is as expected.
    self.assertEqual(
        STORED_JOINT_POSITIONS,
        EXPECTED_JOINT_POSITIONS,
    )


if __name__ == "__main__":
  unittest.main()
