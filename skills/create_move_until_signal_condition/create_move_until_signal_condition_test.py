import unittest
from unittest.mock import create_autospec

from intrinsic.icon.python import icon_api
from intrinsic.skills.python import skill_interface
from skills.create_move_until_signal_condition import create_move_until_signal_condition
from skills.create_move_until_signal_condition import create_move_until_signal_condition_pb2


class CreateMoveUntilSignalConditionTest(unittest.TestCase):

  def make_execute_context(self):
    mock_context = create_autospec(
        spec=skill_interface.ExecuteContext, spec_set=True, instance=True
    )

  def test_execute(self):
    skill = create_move_until_signal_condition.CreateMoveUntilSignalCondition()
    params = (
        create_move_until_signal_condition_pb2.CreateMoveUntilSignalParams()
    )
    params.icon_part_name = "test_part"
    params.analog_input_block_name = "test_block"
    params.signal_index = 0
    params.upperLimit = 10.0

    request = skill_interface.ExecuteRequest(params)

    result = skill.execute(request, self.make_execute_context())

    expected_condition = icon_api.Condition.is_greater_than(
        icon_api.StateVariablePath.ADIO.analog_input(
            part_name="test_part",
            block_name="test_block",
            signal_index=0,
        ),
        10.0,
    )

    self.assertEqual(result.result, expected_condition.proto)

  def test_execute_with_different_values(self):
    skill = create_move_until_signal_condition.CreateMoveUntilSignalCondition()
    params = (
        create_move_until_signal_condition_pb2.CreateMoveUntilSignalParams()
    )
    params.icon_part_name = "another_part"
    params.analog_input_block_name = "another_block"
    params.signal_index = 1
    params.upperLimit = 25.5
    request = skill_interface.ExecuteRequest(params)

    result = skill.execute(request, self.make_execute_context())

    expected_condition = icon_api.Condition.is_greater_than(
        icon_api.StateVariablePath.ADIO.analog_input(
            part_name="another_part",
            block_name="another_block",
            signal_index=1,
        ),
        25.5,
    )

    self.assertEqual(result.result, expected_condition.proto)


if __name__ == "__main__":
  unittest.main()
