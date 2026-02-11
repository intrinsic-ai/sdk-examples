import traceback

from absl import logging
from intrinsic.solutions import behavior_tree as bt
from intrinsic.solutions import deployments
from services.point_storage import point_storage_service_pb2 as point_storage_proto
from skills.points_crud import points_crud_pb2


def verify_result_type(
    result: points_crud_pb2.PointsCrudResult, want: str
) -> bool:
  got = result.WhichOneof("result")
  if got != want:
    logging.error("Skill returned result of type %s, want %s", got, want)
    return False
  return True


def verify_num_points(result: points_crud_pb2.GetAllResult, n: int) -> bool:
  if len(result.items) != n:
    logging.error("Got %d, want %d", len(result.items), n)
    return False
  return True


def verify_coordinates(
    named_pt: point_storage_proto.NamedPoint,
    x: float,
    y: float,
    z: float,
) -> bool:
  pt = named_pt.point
  if pt.x != x or pt.y != y or pt.z != z:
    logging.error(
        "Got point %s at (%f, %f, %f), want (%f, %f, %f)",
        named_pt.name,
        pt.x,
        pt.y,
        pt.z,
        x,
        y,
        z,
    )
    return False
  return True


def run_points_crud_sequence(org_name, solution_id):
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

    crud_skill = skills["com.example.points_crud"]
    point_storage_service = resources.point_storage_service

    put_point_a_action = crud_skill(
        point_storage_service=point_storage_service,
        put=points_crud_pb2.PutParams(
            point_name="A",
            coordinates=point_storage_proto.Point(x=1.0, y=2.0, z=3.0),
        ),
    )

    put_point_b_action = crud_skill(
        point_storage_service=point_storage_service,
        put=points_crud_pb2.PutParams(
            point_name="B",
            coordinates=point_storage_proto.Point(x=10.0, y=20.0, z=30.0),
        ),
    )

    get_point_a_action = crud_skill(
        point_storage_service=point_storage_service,
        get=points_crud_pb2.GetParams(point_name="A"),
    )

    update_point_a_action = crud_skill(
        point_storage_service=point_storage_service,
        update=points_crud_pb2.UpdateParams(
            point_name="A",
            offset=point_storage_proto.Point(x=10.0, y=1.0, z=2.0),
        ),
    )

    get_all_action = crud_skill(
        point_storage_service=point_storage_service,
        get_all=points_crud_pb2.GetAllParams(),
    )

    delete_point_a_action = crud_skill(
        point_storage_service=point_storage_service,
        delete=points_crud_pb2.DeleteParams(
            point_name="A",
        ),
    )

    delete_point_b_action = crud_skill(
        point_storage_service=point_storage_service,
        delete=points_crud_pb2.DeleteParams(
            point_name="B",
        ),
    )

    get_none_action = crud_skill(
        point_storage_service=point_storage_service,
        get_all=points_crud_pb2.GetAllParams(),
    )

    tree = bt.BehaviorTree(
        name="Populate point storage",
        root=bt.Sequence([
            bt.Task(action=put_point_a_action, name="Add point A"),
            bt.Task(action=put_point_b_action, name="Add point B"),
            bt.Task(action=get_point_a_action, name="Get point A"),
            bt.Task(action=update_point_a_action, name="Update point A"),
            bt.Task(action=get_all_action, name="Get all points 1"),
            bt.Task(action=delete_point_a_action, name="Delete point A"),
            bt.Task(action=delete_point_b_action, name="Delete point B"),
            bt.Task(action=get_none_action, name="Get all points 2"),
        ]),
    )

    logging.info("Executing behavior tree")
    solution.executive.run(tree)

    logging.info("Checking result of the PUT A action")
    put_a_result = solution.executive.get_value(put_point_a_action.result)
    if not verify_coordinates(put_a_result.put.point, 1.0, 2.0, 3.0):
      return 1
    logging.info("Got point A at expected coordinates")

    logging.info("Checking result of the PUT B action")
    put_b_result = solution.executive.get_value(put_point_b_action.result)
    if not verify_coordinates(put_b_result.put.point, 10.0, 20.0, 30.0):
      return 1
    logging.info("Got point B at expected coordinates")

    logging.info("Checking result of the GET action")
    get_result = solution.executive.get_value(get_point_a_action.result)
    if not verify_coordinates(get_result.get.point, 1.0, 2.0, 3.0):
      return 1
    logging.info("Got point A with coordinates (1, 2, 3), as expected")

    logging.info("Checking result of UPDATE action")
    update_result = solution.executive.get_value(update_point_a_action.result)
    if not verify_coordinates(
        update_result.update.updated_point, 11.0, 3.0, 5.0
    ):
      return 1
    logging.info("Got point A with coordinates (11, 3, 5), as expected")

    logging.info("Checking result of GET ALL action")
    get_all_result = solution.executive.get_value(get_all_action.result)
    if not verify_num_points(get_all_result.get_all, 2):
      return 1
    found_points = {}
    for item in get_all_result.get_all.items:
      found_points[item.name] = item
    if "A" not in found_points:
      logging.error("Point A is missing")
      return 1
    if "B" not in found_points:
      logging.error("Point B is missing")
      return 1
    if not verify_coordinates(found_points["A"], 11.0, 3.0, 5.0):
      return 1
    if not verify_coordinates(found_points["B"], 10.0, 20.0, 30.0):
      return 1
    logging.info("Got points A and B at expected coordinates")

    logging.info("Checking result of DELETE A action")
    delete_a_action_result = solution.executive.get_value(
        delete_point_a_action.result
    )
    if not verify_result_type(delete_a_action_result, "delete"):
      return 1
    logging.info("Got expected response")

    logging.info("Checking result of DELETE B action")
    delete_b_action_result = solution.executive.get_value(
        delete_point_b_action.result
    )
    if not verify_result_type(delete_b_action_result, "delete"):
      return 1
    logging.info("Got expected response")

    logging.info("Checking result of the final GET ALL action")
    get_none_result = solution.executive.get_value(get_none_action.result)

    # We've just deleted all points, so the result should be empty.
    if not verify_num_points(get_none_result.get_all, 0):
      return 1
    logging.info("Got 0 points, as expected")

    return 0
  except Exception as e:
    logging.exception(e)

    return 1
