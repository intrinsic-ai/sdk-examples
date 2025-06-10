#!/usr/bin/env python3

import unittest

from intrinsic.solutions import behavior_tree as bt
from intrinsic.solutions import deployments


class TestStopwatch(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.solution = deployments.connect_to_selected_solution()
    need_skills = [
        'com.example.start_stopwatch',
        'com.example.stop_stopwatch_py',
    ]
    need_services = [('com.example.stopwatch_service', 'stopwatch')]
    for skill_id in need_skills:
      input(f'Please install the skill {skill_id} into the target solution')
    for service_id, name in need_services:
      input(
          f'Please install the service {service_id} into the target solution,'
          f' then add an instance named "{name}"'
      )
    cls.solution.skills.update()
    cls.solution.resources.update()
    cls.start_skill = cls.solution.skills.com.example.start_stopwatch
    cls.stop_skill = cls.solution.skills.com.example.stop_stopwatch
    cls.stopwatch_service = cls.solution.resources.stopwatch

  def test_start_stop_stopwatch(self):
    start_skill = self.start_skill(stopwatch_service=self.stopwatch_service)
    stop_skill = self.stop_skill(stopwatch_service=self.stopwatch_service)
    tree = bt.BehaviorTree(
        name='StopStopwatch Integration Test',
        root=bt.Sequence([
            bt.Task(action=start_skill, name='Start stopwatch'),
            bt.Task(action=stop_skill, name='Stop stopwatch'),
        ]),
    )
    self.solution.executive.run(tree)

    self.assertGreater(
        self.solution.executive.get_value(stop_skill.result).time_elapsed, 0
    )


if __name__ == '__main__':
  unittest.main()
