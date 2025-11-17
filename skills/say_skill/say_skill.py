"""Contains the skill say_skill_py."""

from absl import logging
from intrinsic.skills.python import skill_interface
from intrinsic.util.decorators import overrides


class SaySkill(skill_interface.Skill):
  """Implementation of the say_skill_py skill."""

  def __init__(self) -> None:
    pass

  @overrides(skill_interface.Skill)
  def execute(
      self,
      request: skill_interface.ExecuteRequest,
      context: skill_interface.ExecuteContext,
  ) -> None:

    context.canceller.ready()
    if context.canceller.wait(request.params.wait_ms / 1000.0):
      raise skill_interface.SkillCancelledError(f"say_skill_cc was cancelled.")

    logging.info(request.params.text)
