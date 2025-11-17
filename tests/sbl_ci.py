import argparse

from intrinsic.solutions import behavior_tree as bt
from intrinsic.solutions import deployments


def run_stopwatch_sequence(
    org_name,
    solution_id,
):
  """
  Connects to a solution, configure the skills and services,
  and execute the sequence of start_stopwatch and stop_stopwatch.
  Returns 0 if the execution was succesfull, 1 is there was an error.
  """
  try:
    print("Connecting to the solution...")
    solution = deployments.connect(
        org=org_name,
        solution=solution_id,
    )
    skills = solution.skills
    resources = solution.resources
    skills.update()
    resources.update()

    start_skill = skills["com.example.start_stopwatch"]
    stop_skill = skills["com.example.stop_stopwatch"]
    stopwatch_service = resources.stopwatch_service

    print(
        "\nConfiguring the behavior tree for the start_stopwatch and"
        " stop_stopwatch"
    )

    start_action = start_skill(stopwatch_service=stopwatch_service)
    stop_action = stop_skill(stopwatch_service=stopwatch_service)

    tree = bt.BehaviorTree(
        name="Stopwatch Sequence",
        root=bt.Sequence([
            bt.Task(action=start_action, name="Start stopwatch"),
            bt.Task(action=stop_action, name="Stop stopwatch"),
        ]),
    )

    print("Executing behavior tree")
    solution.executive.run(tree)

    time_elapsed = solution.executive.get_value(stop_action.result).time_elapsed
    print(f"\nStopwatch stopped. Time elapsed: {time_elapsed} seconds.")

    if time_elapsed > 0:
      print(
          "The stopwatch started and stop succesfully and registered the time!"
      )
      return 0
    else:
      print("Warning: Time elapsed is not greater than 0. Something was wrong.")
      return 1

  except Exception as e:
    print(f"\n It was an error during the execution: {e}")
    return 1


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      description="Run CI journey for Intrinsic solution."
  )
  parser.add_argument(
      "--org",
      required=True,
      help="Intrinsic organization name (e.g., intrinsic@intrinsic-prod-us)",
  )
  parser.add_argument(
      "--solution-id", required=True, help="Intrinsic solution ID"
  )
  args = parser.parse_args()

  exit_code = run_stopwatch_sequence(
      org_name=args.org, solution_id=args.solution_id
  )
  exit(exit_code)
