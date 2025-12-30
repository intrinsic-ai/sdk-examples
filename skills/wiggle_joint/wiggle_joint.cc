#include "wiggle_joint.h"

#include <memory>
#include <string>
#include <utility>

#include "absl/log/log.h"
#include "absl/status/status.h"
#include "absl/status/statusor.h"
#include "skills/wiggle_joint/wiggle_joint.pb.h"
// [START wiggle_joint_includes]
#include "intrinsic/icon/actions/point_to_point_move_info.h"
#include "intrinsic/icon/cc_client/client.h"
#include "intrinsic/icon/cc_client/client_utils.h"
#include "intrinsic/icon/cc_client/session.h"
#include "intrinsic/icon/equipment/channel_factory.h"
#include "intrinsic/icon/equipment/equipment_utils.h"
// [END wiggle_joint_includes]
#include "intrinsic/skills/cc/skill_utils.h"
#include "intrinsic/skills/proto/skill_service.pb.h"
#include "intrinsic/util/status/status_macros.h"

namespace wiggle_joint {

using ::com::example::WiggleJointParams;

// [START wiggle_joint_using_directives_p1]
using ::intrinsic_proto::icon::PartJointState;
using ::intrinsic_proto::icon::PartStatus;
// [END wiggle_joint_using_directives_p1]
using ::intrinsic::skills::ExecuteRequest;
using ::intrinsic_proto::skills::ExecuteResult;
// [START wiggle_joint_using_directives_p2]
using ::intrinsic::icon::Action;
using ::intrinsic::icon::ActionDescriptor;
using ::intrinsic::icon::ActionInstanceId;
using ::intrinsic::icon::ConnectToIconEquipment;
using ::intrinsic::icon::CreatePointToPointMoveFixedParams;
using ::intrinsic::icon::DefaultChannelFactory;
using ::intrinsic::icon::IconEquipment;
using ::intrinsic::icon::IsDone;
using ::intrinsic::icon::IsGreaterThanOrEqual;
using ::intrinsic::icon::IsTrue;
using ::intrinsic::icon::PointToPointMoveInfo;
using ::intrinsic::icon::ReactionDescriptor;
using ::intrinsic::skills::EquipmentPack;
// [END wiggle_joint_using_directives_p2]
using ::intrinsic::skills::ExecuteContext;
using ::intrinsic::skills::SkillInterface;

// [START wiggle_joint_using_directives_p3]
using IconClient = ::intrinsic::icon::Client;
using IconSession = ::intrinsic::icon::Session;
// [END wiggle_joint_using_directives_p3]
// -----------------------------------------------------------------------------
// Skill signature.
// -----------------------------------------------------------------------------

std::unique_ptr<SkillInterface> WiggleJoint::CreateSkill() {
  return std::make_unique<WiggleJoint>();
}

// -----------------------------------------------------------------------------
// Skill execution.
// -----------------------------------------------------------------------------

absl::StatusOr<std::unique_ptr<google::protobuf::Message>> WiggleJoint::Execute(
    const ExecuteRequest& request, ExecuteContext& context) {
  // Get parameters.
  INTR_ASSIGN_OR_RETURN(auto params, request.params<WiggleJointParams>());

  // [START access_equipment]
  const EquipmentPack equipment_pack = context.equipment();
  INTR_ASSIGN_OR_RETURN(const auto equipment,
                        equipment_pack.GetHandle(kRobotSlot));
  // [END access_equipment]
  // [START connect_to_robot]
  INTR_ASSIGN_OR_RETURN(IconEquipment icon_equipment,
                        ConnectToIconEquipment(equipment_pack, kRobotSlot,
                                               DefaultChannelFactory()));
  IconClient icon_client(icon_equipment.channel);
  // [END connect_to_robot]
  // [START get_robot_info]
  INTR_ASSIGN_OR_RETURN(auto robot_config, icon_client.GetConfig());

  const std::string part_name = icon_equipment.position_part_name.value();
  INTR_ASSIGN_OR_RETURN(intrinsic_proto::icon::GenericPartConfig part_config,
                        robot_config.GetGenericPartConfig(part_name));

  INTR_ASSIGN_OR_RETURN(const PartStatus part_status,
                        icon_client.GetSinglePartStatus(part_name));
  // [END get_robot_info]
  // [START parameter_validation]
  if (params.joint_number() < 0 ||
      params.joint_number() >= part_status.joint_states_size()) {
    return absl::FailedPreconditionError(
        absl::StrCat("Joint ", params.joint_number(),
                     " does not exist on: ", equipment.name()));
  }
  // [END parameter_validation]
  // [START describe_movement_goals]
  const double five_degrees = 0.0872665;  // Radians
  const double joint_target_pose =
      part_status.joint_states(params.joint_number()).position_sensed() +
      five_degrees;

  std::vector<double> original_positions;
  std::vector<double> first_goal_positions;
  std::vector<double> zero_velocity;
  for (size_t i = 0; i < part_status.joint_states_size(); ++i) {
    const double cur_pos = part_status.joint_states(i).position_sensed();
    if (params.joint_number() == i) {
      first_goal_positions.push_back(joint_target_pose);
    } else {
      first_goal_positions.push_back(cur_pos);
    }
    original_positions.push_back(cur_pos);
    zero_velocity.push_back(0);
  }
  // [END describe_movement_goals]

  // [START start_icon_session]
  // Start an icon session
  INTR_ASSIGN_OR_RETURN(
      std::unique_ptr<IconSession> icon_session,
      IconSession::Start(icon_equipment.channel, {std::string(part_name)}));
  // [END start_icon_session]

  // [START icon_constants]
  const ActionInstanceId kFirstMoveId(1);
  const ActionInstanceId kSecondMoveId(2);
  const double kTimeoutSeconds = 2;
  // [END icon_constants]

  // [START first_icon_action]
  ActionDescriptor first_move =
      // [START first_icon_action_id_and_goal]
      ActionDescriptor(PointToPointMoveInfo::kActionTypeName, kFirstMoveId,
                       part_name)
          .WithFixedParams(CreatePointToPointMoveFixedParams(
              first_goal_positions, zero_velocity))
          // [END first_icon_action_id_and_goal]
          // [START first_icon_action_when_done]
          .WithReaction(
              ReactionDescriptor(IsDone()).WithRealtimeActionOnCondition(
                  kSecondMoveId))
          // [END first_icon_action_when_done]
          // [START first_icon_action_when_timeout]
          .WithReaction(ReactionDescriptor(
                            IsGreaterThanOrEqual(
                                PointToPointMoveInfo::kSetpointDoneForSeconds,
                                kTimeoutSeconds))
                            // This nonrealtime callback prints a message if the
                            // joint motion fails to settle within a timeout.
                            .WithWatcherOnCondition([&icon_session]() {
                              LOG(ERROR) << "Failed to reach Goal";
                              icon_session->QuitWatcherLoop();
                            }));
  // [END first_icon_action_when_timeout]
  // [END first_icon_action]
  // [START second_icon_action]
  ActionDescriptor second_move =
      ActionDescriptor(PointToPointMoveInfo::kActionTypeName, kSecondMoveId,
                       part_name)
          .WithFixedParams(CreatePointToPointMoveFixedParams(original_positions,
                                                             zero_velocity))
          .WithReaction(
              ReactionDescriptor(IsTrue(PointToPointMoveInfo::kIsSettled))
                  .WithWatcherOnCondition([&icon_session]() {
                    LOG(INFO) << "Finished moving joint.";
                    icon_session->QuitWatcherLoop();
                  }))
          .WithReaction(ReactionDescriptor(
                            IsGreaterThanOrEqual(
                                PointToPointMoveInfo::kSetpointDoneForSeconds,
                                kTimeoutSeconds))
                            // This nonrealtime callback prints a message if the
                            // joint motion fails to settle within a timeout.
                            .WithWatcherOnCondition([&icon_session]() {
                              LOG(ERROR) << "Failed to reach Goal";
                              icon_session->QuitWatcherLoop();
                            }));
  // [END second_icon_action]

  // [START add_icon_actions]
  INTR_ASSIGN_OR_RETURN(auto actions,
                        icon_session->AddActions({first_move, second_move}));
  // [END add_icon_actions]

  // [START move_the_robot]
  LOG(INFO) << "Starting Wiggle.";
  INTR_RETURN_IF_ERROR(icon_session->StartActions({actions.front()}));
  INTR_RETURN_IF_ERROR(icon_session->RunWatcherLoop());
  LOG(INFO) << "Finished Wiggle.";
  // [END move_the_robot]

  return nullptr;
}
}  // namespace wiggle_joint
