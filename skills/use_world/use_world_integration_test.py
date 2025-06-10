#!/usr/bin/env python3
import argparse

from intrinsic.solutions import behavior_tree as bt
from intrinsic.solutions import deployments


def run_integration_test(args):
  solution = deployments.connect_to_selected_solution()

  executive = solution.executive
  resources = solution.resources
  skills = solution.skills
  world = solution.world

  input("""Follow these instructions to test the use_world skill:
    1. Create a solution, and set it as your target solution in VS Code
    2. Add to Scene: basler_camera named "basler_camera"
    3. Add to Scene: ur3e_hardware_module named "robot"
    4. Add to Scene: ur_realtime_control_service named "robot_controller"
    5. Sideload the use_world skill into your solution
Hit [Enter] when ready""")

  skills.update()

  camera = resources.basler_camera
  robot_controller = resources.robot_controller

  camera_obj = world.get_object("basler_camera")
  robot_obj = world.get_object("robot")

  if args.python:
    use_world = skills.com.example.use_world_py(
        camera=camera,
        robot=robot_controller,
        object_ref=robot_obj,
        frame_ref=robot_obj.get_frame("flange"),
        transform_node_ref=robot_obj.get_frame("flange"),
    )
  else:
    use_world = skills.com.example.use_world_cc(
        camera=camera,
        robot=robot_controller,
        object_ref=robot_obj,
        frame_ref=robot_obj.get_frame("flange"),
        transform_node_ref=robot_obj.get_frame("flange"),
    )

  tree = bt.BehaviorTree(
      name="UseWorld Integration Test",
      root=bt.Sequence([
          bt.Task(action=use_world, name="Use World"),
      ]),
  )

  executive.run(tree)
  print("Executing use_world skill succeeded!")


def parse_arguments():
  parser = argparse.ArgumentParser()
  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument("--python", action="store_true", help="Test Python skill")
  group.add_argument("--cpp", action="store_true", help="Test C++ skill")
  return parser.parse_args()


if __name__ == "__main__":
  args = parse_arguments()
  run_integration_test(args)
