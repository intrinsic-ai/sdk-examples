import argparse

from absl import logging
from tests.points_crud_sbl_ci_test import run_points_crud_sequence
from tests.stopwatch_sbl_ci_test import run_stopwatch_sequence

if __name__ == "__main__":
  logging.set_verbosity(logging.INFO)
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

  tests = [run_stopwatch_sequence, run_points_crud_sequence]
  workflow_exit_code = 0

  for test in tests:
    test_name = test.__name__
    logging.info("===== Starting %s =====", test_name)
    test_exit_code = test(org_name=args.org, solution_id=args.solution_id)
    if test_exit_code != 0:
      workflow_exit_code = 1
      test_result = "FAILED"
    else:
      test_result = "SUCCEEDED"
    logging.info("===== %s %s =====", test_name, test_result)

  exit(workflow_exit_code)
