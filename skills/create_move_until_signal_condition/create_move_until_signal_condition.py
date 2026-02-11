"""Example skill that creates an icon_api.Condition to be linked to a move_robot skill."""

from absl import logging
from intrinsic.icon.python import icon_api
from intrinsic.skills.python import skill_interface
from intrinsic.util.decorators import overrides
from skills.create_move_until_signal_condition import create_move_until_signal_condition_pb2


class CreateMoveUntilSignalCondition(skill_interface.Skill):
  """
  Skill that creates a CreateMoveUntilSignalCondition based on the input param.
  The output of this skill can be `linked` to the `move_until_signal_condition` input of the `move_robot` skill
  (see https://flowstate.intrinsic.ai/docs/guides/develop_a_process/add_nodes/add_skills/manage_data_flow/#manage-data-flow-links).
  In production it would most likely query a service for the required parameters.
  """

  @overrides(skill_interface.Skill)
  def execute(
      self,
      request: skill_interface.ExecuteRequest[
          create_move_until_signal_condition_pb2.CreateMoveUntilSignalParams
      ],
      #  ExecuteContext is not used in this example, because the skill consits of a single operation and can not be aborted.
      _: skill_interface.ExecuteContext,
  ) -> create_move_until_signal_condition_pb2.CreateMoveUntilSignalResult:
    params = request.params
    # A real skill would connect to the ICON instance and check that the params are valid.
    logging.info("CreateMoveUntilSignalCondition upperLimit: %s", params)

    # Uses a helper to simply working with Conditions instead of a plain proto.
    # https://flowstate.intrinsic.ai/docs/apis/client_libraries/icon_library/python_client_api/#reactions
    # https://flowstate.intrinsic.ai/docs/apis/client_libraries/skills_sdk/references/python/intrinsic/icon/python/icon_api/Condition/
    # Conditions can be chained e.g. using `reactions.Condition.all_of(``
    condition = icon_api.Condition.is_greater_than(
        icon_api.StateVariablePath.ADIO.analog_input(
            part_name=params.icon_part_name,
            block_name=params.analog_input_block_name,
            signal_index=params.signal_index,
        ),
        params.upperLimit,
    )

    return create_move_until_signal_condition_pb2.CreateMoveUntilSignalResult(
        result=condition.proto
    )
