import types
import unittest
from unittest.mock import create_autospec

from intrinsic.skills.python import skill_canceller
from intrinsic.skills.python import skill_interface
from skills.say_skill.say_skill import SaySkill
from skills.say_skill.say_skill_pb2 import SaySkillParams


class SaySkillTest(unittest.TestCase):

  def make_execute_context(self):
    fake_context = create_autospec(
        spec=skill_interface.ExecuteContext, spec_set=True, instance=True
    )

    canceller = skill_canceller.SkillCancellationManager(ready_timeout=30.0)
    fake_context.canceller = canceller
    return fake_context

  def test_logs_correct_message(self):
    dut_skill = SaySkill()
    fake_request = skill_interface.ExecuteRequest(
        params=SaySkillParams(text="Hello world!", wait_ms=0)
    )

    fake_context = self.make_execute_context()

    # Call execute and verify the log output
    with self.assertLogs() as log_output:
      dut_skill.execute(fake_request, fake_context)
    output = log_output[0][0].message
    self.assertEqual(output, "Hello world!")

  def test_can_be_cancelled(self):
    dut_skill = SaySkill()
    fake_request = skill_interface.ExecuteRequest(
        params=SaySkillParams(text="Hello world!", wait_ms=1000)
    )

    fake_context = self.make_execute_context()

    # Monkey patch canceller to to immediately cancel itself
    original_ready = fake_context.canceller.ready

    def ready_then_cancel(self):
      original_ready()
      self.cancel()

    fake_context.canceller.ready = types.MethodType(
        ready_then_cancel, fake_context.canceller
    )

    with self.assertRaises(skill_interface.SkillCancelledError):
      dut_skill.execute(fake_request, fake_context)


if __name__ == "__main__":
  unittest.main()
