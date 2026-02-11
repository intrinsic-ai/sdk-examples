import traceback

from absl import logging
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
    logging.info("Connecting to the solution...")
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

    logging.info(
        "Configuring the behavior tree for the start_stopwatch and"
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

    logging.info("Executing behavior tree")
    solution.executive.run(tree)

    time_elapsed = solution.executive.get_value(stop_action.result).time_elapsed
    logging.info("Stopwatch stopped. Time elapsed: %s seconds.", time_elapsed)

    if time_elapsed > 0:
      logging.info(
          "The stopwatch started and stop succesfully and registered the time!"
      )
      return 0
    else:
      logging.warning(
          "Warning: Time elapsed is not greater than 0. Something was wrong."
      )
      return 1

  except Exception as e:
    logging.exception(e)
    return 1
