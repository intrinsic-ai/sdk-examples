"""Contains the skill read_joint_positions_from_opcua_equipment.

This skill connects to an opcua_equipment which has been configured with
variables that represent the joint positions of a 6-axis robot arm, where
joints 1-6 are matched to signal names lrAxis1 - lrAxis6.

It is also assumed that the opcua_equipment has been configured with a "Get"
command that retreives the values of the variables and returns them as an
array of double values.

The signal names of these variables, as well as the rest of the configuration
of the opcua_equipment can be found in the accompanying `example_opcua_equipment_config.pbtxt`
file. This configuration must be uploaded to the equipment via Flowstate
before the skill can communicate with the equipment properly.

For more information about configuring OPCUA equipment, refer to
https://developers.intrinsic.ai/guides/workcell_design/adding_new_hardware?hl=en#opcua-equipment.

"""

from absl import logging
import grpc
from intrinsic.icon.proto import joint_space_pb2
from intrinsic.skills.python import skill_interface
from intrinsic.util.decorators import overrides
from intrinsic.hardware.opcua_equipment import opcua_equipment_service_pb2
from intrinsic.hardware.opcua_equipment import opcua_equipment_service_pb2_grpc
from skills.read_joint_positions_from_opcua_equipment import (
    read_joint_positions_from_opcua_equipment_pb2,
)

_EQUIPMENT_SLOT = "opcua_equipment"

OpcuaEquipmentServiceStub = (
    opcua_equipment_service_pb2_grpc.OpcuaEquipmentServiceStub
)
ControlRequest = opcua_equipment_service_pb2.ControlRequest
GetStatusRequest = opcua_equipment_service_pb2.GetStatusRequest


class ReadJointPositionsFromOpcuaEquipment(skill_interface.Skill):
  """Implementation of the read_joint_positions_from_opcua_equipment skill."""

  @overrides(skill_interface.Skill)
  def execute(
      self,
      request: skill_interface.ExecuteRequest[
          read_joint_positions_from_opcua_equipment_pb2.ReadJointPositionsFromOpcuaEquipmentParams
      ],
      context: skill_interface.ExecuteContext,
  ) -> (
      read_joint_positions_from_opcua_equipment_pb2.ReadJointPositionsFromOpcuaEquipmentResult
  ):
    resource_handle = context.resource_handles[_EQUIPMENT_SLOT]

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
      # Send a GetStatusRequest containing a "Get" command that returns the joint position values.
      res: opcua_equipment_service_pb2.GetStatusResponse = stub.GetStatus(
          GetStatusRequest(command="Get"), **connection_params
      )
      logging.info("Status values: \n%s", res.status)

    # Extract the axes values and package into a JointVec before returning the result.
    output_jp = []
    for ax in range(1, 7):
      output_jp.append(res.status[f"lrAxis{ax}"].double_value)

    return read_joint_positions_from_opcua_equipment_pb2.ReadJointPositionsFromOpcuaEquipmentResult(
        joint_positions=joint_space_pb2.JointVec(joints=output_jp)
    )
