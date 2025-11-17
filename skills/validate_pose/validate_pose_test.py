import unittest
from unittest.mock import create_autospec

from intrinsic.math.python.pose3 import Pose3
from intrinsic.math.python.quaternion import Quaternion
from intrinsic.math.python.rotation3 import Rotation3
from intrinsic.skills.python import skill_interface
from skills.validate_pose.validate_pose import ValidatePose
from skills.validate_pose.validate_pose_pb2 import ValidatePoseParams


class ValidatePoseTest(unittest.TestCase):

  def make_execute_context(self):
    fake_context = create_autospec(
        spec=skill_interface.ExecuteContext, spec_set=True, instance=True
    )

    return fake_context

  def test_pose_in_tolerance(self):
    dut_skill = ValidatePose()
    fake_request = skill_interface.ExecuteRequest(
        params=ValidatePoseParams(
            position_tolerance=1.0, rotation_tolerance=0.25
        )
    )

    fake_context = self.make_execute_context()
    fake_context.object_world.get_transform.return_value = Pose3()

    dut_skill.execute(fake_request, fake_context)

    fake_context.object_world.get_transform.assert_called_once()

  def test_position_not_in_tolerance(self):
    dut_skill = ValidatePose()
    fake_request = skill_interface.ExecuteRequest(
        params=ValidatePoseParams(
            position_tolerance=1.0, rotation_tolerance=0.25
        )
    )

    fake_context = self.make_execute_context()
    fake_context.object_world.get_transform.return_value = Pose3(
        translation=(1, 2, 3)
    )

    with self.assertRaises(ValueError):
      dut_skill.execute(fake_request, fake_context)

    fake_context.object_world.get_transform.assert_called_once()

  def test_rotation_not_in_tolerance(self):
    dut_skill = ValidatePose()
    fake_request = skill_interface.ExecuteRequest(
        params=ValidatePoseParams(
            position_tolerance=1.0, rotation_tolerance=0.25
        )
    )

    fake_context = self.make_execute_context()
    fake_context.object_world.get_transform.return_value = Pose3(
        rotation=Rotation3(quat=Quaternion((0, 0, 1, 0)))
    )

    with self.assertRaises(ValueError):
      dut_skill.execute(fake_request, fake_context)

    fake_context.object_world.get_transform.assert_called_once()


if __name__ == '__main__':
  unittest.main()
