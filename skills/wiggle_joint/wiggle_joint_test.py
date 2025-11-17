import unittest
from unittest.mock import create_autospec
from unittest.mock import patch

from intrinsic.icon.proto.v1 import service_pb2
from intrinsic.icon.python import icon_api
from intrinsic.skills.python import skill_interface
from skills.wiggle_joint.wiggle_joint import WiggleJoint
from skills.wiggle_joint.wiggle_joint_pb2 import WiggleJointParams


class WiggleJointTest(unittest.TestCase):

  def make_execute_context(self):
    mock_context = create_autospec(
        spec=skill_interface.ExecuteContext, spec_set=True, instance=True
    )

    return mock_context

  def setUp(self) -> None:
    self.equipment_utils_patcher = patch(
        "skills.wiggle_joint.wiggle_joint.equipment_utils",
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
    self.event_flag_class_patcher = patch(
        "intrinsic.icon.python.icon_api.EventFlag", spec_set=True, autospec=True
    )
    self.mock_event_flag = create_autospec(
        spec=icon_api.EventFlag, spec_set=True, instance=True
    )
    self.mock_event_flag_class = self.event_flag_class_patcher.start()
    self.mock_event_flag_class.return_value = self.mock_event_flag

  def tearDown(self) -> None:
    self.event_flag_class_patcher.stop()
    self.equipment_utils_patcher.stop()

  def test_logs_success_message(self):
    dut_skill = WiggleJoint()
    mock_request = skill_interface.ExecuteRequest(params=WiggleJointParams())

    mock_context = self.make_execute_context()

    self.mock_equipment_utils.get_position_part_name.return_value = "arm"
    fake_status_resp = service_pb2.GetStatusResponse()
    fake_status_resp.part_status["arm"].joint_states.add()
    self.mock_icon_client.get_status.return_value = fake_status_resp

    with self.assertLogs() as log_output:
      dut_skill.execute(mock_request, mock_context)
    self.assertIn("movement is complete", log_output[0][-1].message)

    self.mock_event_flag.wait.assert_called_once()


if __name__ == "__main__":
  unittest.main()
