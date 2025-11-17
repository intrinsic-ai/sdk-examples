import unittest
from unittest.mock import create_autospec

from intrinsic.skills.python import skill_interface
from skills.use_world.use_world import UseWorld
from skills.use_world.use_world_pb2 import UseWorldParams


class UseWorldTest(unittest.TestCase):

  def make_execute_context(self):
    fake_context = create_autospec(
        spec=skill_interface.ExecuteContext, spec_set=True, instance=True
    )

    return fake_context

  def test_logs_correct_message(self):
    dut_skill = UseWorld()
    fake_request = skill_interface.ExecuteRequest(params=UseWorldParams())

    fake_context = self.make_execute_context()

    # Call execute and make sure it outputs stuff
    with self.assertLogs() as log_output:
      dut_skill.execute(fake_request, fake_context)
    # pass if there are more than 5 (arbitrary) log statements
    self.assertGreater(len(log_output[0]), 5)

    fake_context.object_world.update_transform.assert_called()


if __name__ == '__main__':
  unittest.main()
