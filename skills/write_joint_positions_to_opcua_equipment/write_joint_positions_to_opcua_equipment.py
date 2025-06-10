"""Contains the skill write_joint_positions_to_opcua_equipment.

This skill connects to an opcua_equipment which has been configured with
variables that represent the joint positions of a 6-axis robot arm, where
joints 1-6 are matched to signal names lrAxis1 - lrAxis6.

It is also assumed that the opcua_equipment has been configured with a "Write"
command that writes the an array of double values to the variables on the opcua_equipment.

The skill reads the current sensed joint positions of the robot arm, and writes them to the
opcua_equipment.

The signal names of these variables, as well as the rest of the configuration
of the opcua_equipment can be found in the accompanying `example_opcua_equipment_config.pbtxt`
file. This configuration must be uploaded to the equipment via Flowstate
before the skill can communicate with the equipment properly.

For more information about configuring OPCUA equipment, refer to
https://developers.intrinsic.ai/guides/workcell_design/adding_new_hardware?hl=en#opcua-equipment.
"""

from absl import logging
import grpc
from intrinsic.icon.equipment import equipment_utils
from intrinsic.skills.python import skill_interface
from intrinsic.util.decorators import overrides
from intrinsic.hardware.opcua_equipment import opcua_equipment_service_pb2
from intrinsic.hardware.opcua_equipment import opcua_equipment_service_pb2_grpc
from intrinsic.hardware.gpio.v1.signal_pb2 import SignalValue
from skills.write_joint_positions_to_opcua_equipment import (
    write_joint_positions_to_opcua_equipment_pb2,
)

_EQUIPMENT_SLOT = "opcua_equipment"
_ROBOT_SLOT = "robot"

OpcuaEquipmentServiceStub = (
    opcua_equipment_service_pb2_grpc.OpcuaEquipmentServiceStub
)
ControlRequest = opcua_equipment_service_pb2.ControlRequest
GetStatusRequest = opcua_equipment_service_pb2.GetStatusRequest


class WriteJointPositionsToOpcuaEquipment(skill_interface.Skill):
  """Implementation of the write_joint_positions_to_opcua_equipment skill."""

  @overrides(skill_interface.Skill)
  def execute(
      self,
      request: skill_interface.ExecuteRequest[
          write_joint_positions_to_opcua_equipment_pb2.WriteJointPositionsToOpcuaEquipmentParams
      ],
      context: skill_interface.ExecuteContext,
  ) -> None:
    resource_handle = context.resource_handles[_EQUIPMENT_SLOT]

    # Get the current sensed robot joint positions from ICON.
    icon_equipment = context.resource_handles[_ROBOT_SLOT]
    icon_client = equipment_utils.init_icon_client(icon_equipment)

    part_name = equipment_utils.get_position_part_name(icon_equipment)
    part_status = icon_client.get_status().part_status[part_name]

    current_joint_positions = [
        joint_state.position_sensed for joint_state in part_status.joint_states
    ]

    logging.info(f"Current joint positions: {current_joint_positions}")

    logging.info(
        "Connecting to equipment at %s:%s",
        resource_handle.connection_info.grpc.address,
        resource_handle.connection_info.grpc.server_instance,
    )
    with grpc.insecure_channel(
        resource_handle.connection_info.grpc.address
    ) as channel:
      stub = OpcuaEquipmentServiceStub(channel)
      connection_params = {
          "metadata": [(
              "x-resource-instance-name",
              resource_handle.connection_info.grpc.server_instance,
          )]
      }

      # Store the sensed joint positions in a dict and send a "Write" control request
      # to the opcua_equipment.
      joint_position_map = {}
      for ax in range(1, 7):
        joint_position_map[f"lrAxis{ax}"] = SignalValue(
            double_value=current_joint_positions[ax - 1]
        )

      res: opcua_equipment_service_pb2.ControlResponse = stub.Control(
          ControlRequest(
              command="Write",
              user_input=joint_position_map,
          ),
          **connection_params,
      )
      logging.info("Status: \n%s", res.success)

    if not res.success:
      raise RuntimeError("Failed to write joint positions.")
