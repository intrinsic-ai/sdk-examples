#include "use_world.h"

#include <memory>

#include "absl/log/log.h"
#include "absl/status/status.h"
#include "absl/status/statusor.h"
#include "intrinsic/skills/cc/skill_utils.h"
#include "intrinsic/util/status/status_macros.h"
#include "intrinsic/world/objects/object_world_client.h"
#include "skills/use_world/use_world.pb.h"

namespace use_world {

using ::com::example::UseWorldParams;

using ::intrinsic::FrameName;
using ::intrinsic::Pose3d;
using ::intrinsic::eigenmath::VectorXd;
using ::intrinsic::skills::EquipmentPack;
using ::intrinsic::skills::ExecuteContext;
using ::intrinsic::skills::ExecuteRequest;
using ::intrinsic::skills::SkillInterface;
using ::intrinsic::world::Frame;
using ::intrinsic::world::KinematicObject;
using ::intrinsic::world::ObjectWorldClient;
using ::intrinsic::world::TransformNode;
using ::intrinsic::world::WorldObject;

// -----------------------------------------------------------------------------
// Skill signature.
// -----------------------------------------------------------------------------

std::unique_ptr<SkillInterface> UseWorld::CreateSkill() {
  return std::make_unique<UseWorld>();
}

// -----------------------------------------------------------------------------
// Skill execution.
// -----------------------------------------------------------------------------

absl::StatusOr<std::unique_ptr<google::protobuf::Message>> UseWorld::Execute(
    const ExecuteRequest& request, ExecuteContext& context) {
  // Get parameters.
  INTR_ASSIGN_OR_RETURN(auto params, request.params<UseWorldParams>());

  // Get connection to world service.
  ObjectWorldClient& world = context.object_world();

  // Unpack equipment handles.
  const EquipmentPack equipment_pack = context.equipment();
  INTR_ASSIGN_OR_RETURN(const auto camera_handle,
                        equipment_pack.GetHandle(kCameraSlot));
  INTR_ASSIGN_OR_RETURN(const auto robot_handle,
                        equipment_pack.GetHandle(kRobotSlot));

  // Resolve ObjectReference.
  INTR_ASSIGN_OR_RETURN(WorldObject obj, world.GetObject(params.object_ref()));

  // Resolve FrameReference.
  INTR_ASSIGN_OR_RETURN(Frame frame, world.GetFrame(params.frame_ref()));

  // Resolve TransformNodeReference, obtaining an instance of either
  // WorldObject or Frame.
  INTR_ASSIGN_OR_RETURN(TransformNode obj_or_frame,
                        world.GetTransformNode(params.transform_node_ref()));

  LOG(INFO) << obj.Name();
  LOG(INFO) << obj.ParentTThis();

  LOG(INFO) << frame.Name();
  LOG(INFO) << frame.ObjectName();
  LOG(INFO) << frame.ParentTThis();

  LOG(INFO) << obj_or_frame.Id();
  LOG(INFO) << obj_or_frame.ParentTThis();

  // Equipment handles can be used in place of world references.
  INTR_ASSIGN_OR_RETURN(WorldObject camera_obj, world.GetObject(camera_handle));

  // If we know that an object is a robot, we can also get it as a
  // KinematicObject which has additional properties.
  INTR_ASSIGN_OR_RETURN(KinematicObject robot_kinematic_obj,
                        world.GetKinematicObject(robot_handle));

  LOG(INFO) << robot_kinematic_obj.JointPositions();

  // Update the robot joints, operating on the robot in the belief world.
  // Note the values in this example are valid only for a UR3e robot.
  INTR_RETURN_IF_ERROR(world.UpdateJointPositions(
      robot_kinematic_obj,
      VectorXd{{1.0, -1.725, 1.111, -1.219, -1.523, 3.14}}));

  // WorldObject representing the world origin. Always present.
  INTR_ASSIGN_OR_RETURN(WorldObject root_object, world.GetRootObject());

  // Every camera has a frame called "sensor" which represents the origin of
  // the camera sensor (as opposed to the camera object itself representing the
  // origin of the cameras geometry).
  INTR_ASSIGN_OR_RETURN(Frame sensor_frame,
                        camera_obj.GetFrame(FrameName{"sensor"}));

  // Every robot has a frame called "flange" which represents the flange of a
  // robot arm according to the ISO 9787 standard.
  INTR_ASSIGN_OR_RETURN(Frame flange_frame,
                        robot_kinematic_obj.GetFrame(FrameName{"flange"}));

  LOG(INFO) << root_object.ObjectReference().ShortDebugString();
  LOG(INFO) << sensor_frame.FrameReference().ShortDebugString();
  LOG(INFO) << flange_frame.FrameReference().ShortDebugString();

  INTR_ASSIGN_OR_RETURN(Pose3d root_t_obj,
                        world.GetTransform(root_object, obj));
  INTR_ASSIGN_OR_RETURN(Pose3d obj_t_frame, world.GetTransform(obj, frame));
  INTR_ASSIGN_OR_RETURN(Pose3d robot_t_sensor,
                        world.GetTransform(robot_kinematic_obj, sensor_frame));
  INTR_ASSIGN_OR_RETURN(Pose3d sensor_t_obj,
                        world.GetTransform(sensor_frame, obj));

  LOG(INFO) << root_t_obj;
  LOG(INFO) << obj_t_frame;
  LOG(INFO) << robot_t_sensor;
  LOG(INFO) << sensor_t_obj;

  INTR_RETURN_IF_ERROR(world.UpdateTransform(
      root_object, obj,
      Pose3d(intrinsic::eigenmath::Quaterniond({1., 0., 0., 0.}),
             intrinsic::eigenmath::Vector3d({1.0, 2.0, 3.0}))));

  // Prints: Pose3(...old pose...)
  LOG(INFO) << obj.ParentTThis();

  // Get a fresh snapshot of the object ('obj' is just a local snapshot and
  // does not get updated automatically!).
  INTR_ASSIGN_OR_RETURN(WorldObject obj_new,
                        world.GetObject(params.object_ref()));

  // Prints: Pose3(Rotation3([0i + 0j + 0k + 1]),[1. 2. 3.])
  LOG(INFO) << obj_new.ParentTThis();

  // Assume the following world structure:
  //
  //        'world.root' (WorldObject)
  //           /    \
  //      robot     'obj' (WorldObject)
  //        /
  //   'camera' (WorldObject)
  //       |
  // 'camera.sensor' (Frame)

  // Pretend the pose came from detecting the object in an image from the
  // camera.
  Pose3d observed_sensor_t_obj =
      Pose3d(intrinsic::eigenmath::Quaterniond({1., 0., 0., 0.}),
             intrinsic::eigenmath::Vector3d({-1.0, -2.0, -3.0}));

  // Update root_t_obj (= 'obj.parent_t_this') such that sensor_t_obj becomes
  // equal to 'observed_sensor_t_obj'. The chain of transforms from the root
  // object to the sensor object will not be modified, i.e., we are just moving
  // the object 'obj' and not the camera or the robot.
  INTR_RETURN_IF_ERROR(
      world.UpdateTransform(sensor_frame, obj, obj, observed_sensor_t_obj));

  return nullptr;
}

}  // namespace use_world
