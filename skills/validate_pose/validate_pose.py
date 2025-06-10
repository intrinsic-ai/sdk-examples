"""Contains the skill validate_pose."""

import numpy

from absl import logging

from intrinsic.skills.python import skill_interface
from intrinsic.util.decorators import overrides
from intrinsic.world.python import object_world_client

from skills.validate_pose import validate_pose_pb2


class ValidatePose(skill_interface.Skill):
  """Implementation of the validate_pose skill."""

  @overrides(skill_interface.Skill)
  def execute(
      self,
      request: skill_interface.ExecuteRequest[
          validate_pose_pb2.ValidatePoseParams
      ],
      context: skill_interface.ExecuteContext,
  ) -> None:
    logging.info('Input parameters: %s', request.params)

    # Perform validation.
    world: object_world_client.ObjectWorldClient = context.object_world

    # Look up frames to compare.
    actual_object = world.get_transform_node(request.params.actual_object)
    expected_pose = world.get_transform_node(request.params.expected_pose)

    # Determine the difference between acutal and expected poses.
    diff_transform = world.get_transform(actual_object, expected_pose)
    logging.info(
        'Transform difference between actual and expected: %s', diff_transform
    )
    position_diff: float = numpy.sqrt(
        diff_transform.translation.dot(diff_transform.translation)
    )
    logging.info(f'Translation error: %s meters', position_diff)
    rotation_diff = diff_transform.rotation.angle()
    logging.info(
        f'Rotation error: %s radians (on axis %s)',
        rotation_diff,
        diff_transform.rotation.axis(),
    )

    # Return failure if anything outside tolerances.
    position_tolerance = (
        request.params.position_tolerance
        if request.params.HasField('position_tolerance')
        else 0
    )
    rotation_tolerance = (
        request.params.rotation_tolerance
        if request.params.HasField('rotation_tolerance')
        else 0
    )
    if position_diff > position_tolerance:
      raise ValueError(
          f'Translation error of {position_diff} meters exceeds tolerance of'
          f' {position_tolerance}'
      )
    if rotation_diff > rotation_tolerance:
      raise ValueError(
          f'Rotation error of {rotation_diff} radians exceeds tolerance of'
          f' {rotation_tolerance}'
      )
