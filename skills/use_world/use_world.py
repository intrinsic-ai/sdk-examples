"""Example skill demonstrating how to use the world service in skills."""

from typing import cast

from absl import logging

from intrinsic.math.python import data_types
from intrinsic.skills.proto import skill_service_pb2
from intrinsic.skills.python import proto_utils
from intrinsic.skills.python import skill_interface
from intrinsic.util.decorators import overrides
from intrinsic.world.python import object_world_client
from intrinsic.world.python import object_world_resources

from skills.use_world import use_world_pb2

ROBOT_EQUIPMENT_SLOT: str = "robot"
CAMERA_EQUIPMENT_SLOT: str = "camera"


class UseWorld(skill_interface.Skill):
  """Example skill demonstrating how to use the world service in skills.

  Queries information from the world and makes some world updates.
  """

  @overrides(skill_interface.Skill)
  def execute(
      self,
      request: skill_service_pb2.ExecuteRequest,
      context: skill_interface.ExecuteContext,
  ) -> None:
    # Get connection to world service.
    world: object_world_client.ObjectWorldClient = context.object_world

    # Unpack equipment handles.
    camera_handle = context.resource_handles[CAMERA_EQUIPMENT_SLOT]
    robot_handle = context.resource_handles[ROBOT_EQUIPMENT_SLOT]

    # Resolve ObjectReference.
    obj: object_world_resources.WorldObject = world.get_object(
        request.params.object_ref
    )

    # Resolve FrameReference.
    frame: object_world_resources.Frame = world.get_frame(
        request.params.frame_ref
    )

    # Resolve TransformNodeReference, obtaining an instance of either
    # WorldObject or Frame.
    obj_or_frame: object_world_resources.TransformNode = (
        world.get_transform_node(request.params.transform_node_ref)
    )

    logging.info(obj.name)
    logging.info(obj.parent_t_this)

    logging.info(frame.name)
    logging.info(frame.object_name)
    logging.info(frame.parent_t_this)

    logging.info(obj_or_frame.id)
    logging.info(obj_or_frame.parent_t_this)

    # Equipment handles can be used in place of world references.
    camera_obj: object_world_resources.WorldObject = world.get_object(
        camera_handle
    )

    # If we know that an object is a robot, we can also get it as a
    # KinematicObject which has additional properties.
    robot_kinematic_obj: object_world_resources.KinematicObject = (
        world.get_kinematic_object(robot_handle)
    )

    logging.info(robot_kinematic_obj.joint_positions)

    # Update the robot joints, operating on the robot in the belief world.
    # Note the values in this example are valid only for a UR3e robot.
    world.update_joint_positions(
        robot_kinematic_obj, [1, -1.725, 1.111, -1.219, -1.523, 3.14]
    )

    # WorldObject representing the world origin. Always present.
    root_object = cast(object_world_resources.WorldObject, world.root)

    # Every camera has a frame called "sensor" which represents the origin of
    # the camera sensor (as opposed to the camera object itself representing the
    # origin of the cameras geometry).
    sensor_frame = cast(object_world_resources.Frame, camera_obj.sensor)

    # Every robot has a frame called "flange" which represents the flange of a
    # robot arm according to the ISO 9787 standard.
    flange_frame = cast(
        object_world_resources.Frame, robot_kinematic_obj.flange
    )

    logging.info(root_object)
    logging.info(sensor_frame)
    logging.info(flange_frame)

    root_t_obj = world.get_transform(root_object, obj)
    obj_t_frame = world.get_transform(obj, frame)
    robot_t_sensor = world.get_transform(robot_kinematic_obj, camera_obj.sensor)
    sensor_t_obj = world.get_transform(camera_obj.sensor, obj)

    logging.info(root_t_obj)
    logging.info(obj_t_frame)
    logging.info(robot_t_sensor)
    logging.info(sensor_t_obj)

    world.update_transform(
        world.root, obj, data_types.Pose3(translation=[1.0, 2.0, 3.0])
    )

    # Prints: Pose3(...old pose...)
    logging.info(obj.parent_t_this)

    # Get a fresh snapshot of the object ('obj' is just a local snapshot and
    # does not get updated automatically!).
    obj_new = world.get_object(request.params.object_ref)

    # Prints: Pose3(Rotation3([0i + 0j + 0k + 1]),[1. 2. 3.])
    logging.info(obj_new.parent_t_this)

    # Assume the following world structure:
    #
    #        'world.root' (WorldObject)
    #           /    \
    #      robot     'obj' (WorldObject)
    #        /
    #   'camera' (WorldObject)
    #       |
    # 'camera.sensor' (Frame)

    # Pretend the pose came from detecting the object in an image from the
    # camera.
    observed_sensor_t_obj = data_types.Pose3(translation=[-1.0, -2.0, -3.0])

    # Update root_t_obj (= 'obj.parent_t_this') such that sensor_t_obj becomes
    # equal to 'observed_sensor_t_obj'. The chain of transforms from the root
    # object to the sensor object will not be modified, i.e., we are just moving
    # the object 'obj' and not the camera or the robot.
    world.update_transform(
        node_a=camera_obj.sensor,
        node_b=obj,
        a_t_b=observed_sensor_t_obj,
        # Supports any node on the path from 'node_a' to 'node_b'.
        node_to_update=obj,
    )
