import unittest
from unittest.mock import create_autospec
from unittest.mock import patch

import grpc
from grpc.framework.foundation import logging_pool

from intrinsic.skills.python import skill_interface
from intrinsic.hardware.gpio.v1.signal_pb2 import SignalValue
from intrinsic.hardware.opcua_equipment import opcua_equipment_service_pb2
from intrinsic.hardware.opcua_equipment import (
    opcua_equipment_service_pb2_grpc,
)
from intrinsic.resources.proto import resource_handle_pb2
from skills.read_joint_positions_from_opcua_equipment import (
    read_joint_positions_from_opcua_equipment,
    read_joint_positions_from_opcua_equipment_pb2,
)

ReadJointPositionsFromOpcuaEquipment = (
    read_joint_positions_from_opcua_equipment.ReadJointPositionsFromOpcuaEquipment
)
MOCK_SERVICE_ADDR = "localhost"
MOCK_SERVICE_INSTANCE = "test_service"
EXPECTED_JOINT_POSITIONS = {
    "lrAxis1": SignalValue(double_value=1.0),
    "lrAxis2": SignalValue(double_value=2.0),
    "lrAxis3": SignalValue(double_value=3.0),
    "lrAxis4": SignalValue(double_value=4.0),
    "lrAxis5": SignalValue(double_value=5.0),
    "lrAxis6": SignalValue(double_value=6.0),
}


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


class TestingReadJointPositionsFromOpcuaEquipmentServiceServicer(
    opcua_equipment_service_pb2_grpc.OpcuaEquipmentServiceServicer
):
    """A servicer for testing the ReadJointPositionsFromOpcuaEquipment skill."""

    def GetStatus(
        self,
        request: opcua_equipment_service_pb2.GetStatusRequest,
        context: grpc.ServicerContext,
    ) -> opcua_equipment_service_pb2.GetStatusResponse:
        return opcua_equipment_service_pb2.GetStatusResponse(
            status=EXPECTED_JOINT_POSITIONS,
        )


class ReadJointPositionsFromOpcuaEquipmentTest(unittest.TestCase):
    def make_execute_context_with_resource_handles(self, resource_handles):
        mock_context = create_autospec(
            spec=skill_interface.ExecuteContext, spec_set=True, instance=True
        )
        mock_context.resource_handles = resource_handles
        return mock_context

    def setUp(self) -> None:
        self._server, self._port = _make_local_testing_server()
        self._servicer = TestingReadJointPositionsFromOpcuaEquipmentServiceServicer()
        opcua_equipment_service_pb2_grpc.add_OpcuaEquipmentServiceServicer_to_server(
            self._servicer, self._server
        )

        self._skill = ReadJointPositionsFromOpcuaEquipment()
        self._resource_handles = {
            read_joint_positions_from_opcua_equipment._EQUIPMENT_SLOT: (
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
            )
        }

    def tearDown(self) -> None:
        self._server.stop(grace=None)

    def test_execute(self):
        mock_request = skill_interface.ExecuteRequest(
            params=read_joint_positions_from_opcua_equipment_pb2.ReadJointPositionsFromOpcuaEquipmentParams()
        )

        mock_context = self.make_execute_context_with_resource_handles(
            self._resource_handles
        )

        result = self._skill.execute(mock_request, mock_context)

        self.assertTrue(
            isinstance(
                result,
                read_joint_positions_from_opcua_equipment_pb2.ReadJointPositionsFromOpcuaEquipmentResult,
            )
        )
        for ax in range(0, 6):
            self.assertEqual(
                result.joint_positions.joints[ax],
                EXPECTED_JOINT_POSITIONS[f"lrAxis{ax+1}"].double_value,
            )


if __name__ == "__main__":
    unittest.main()
