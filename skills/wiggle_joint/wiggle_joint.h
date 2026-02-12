#ifndef WIGGLE_JOINT_WIGGLE_JOINT_H_
#define WIGGLE_JOINT_WIGGLE_JOINT_H_

#include <memory>

#include "absl/status/statusor.h"
#include "intrinsic/skills/cc/skill_interface.h"
#include "intrinsic/skills/proto/skill_service.pb.h"

namespace wiggle_joint {

class WiggleJoint : public intrinsic::skills::SkillInterface {
 public:
  // [START robot_slot]
  static constexpr char kRobotSlot[] = "robot";
  // [END robot_slot]
  // ---------------------------------------------------------------------------
  // Skill signature (see intrinsic::skills::SkillSignatureInterface)
  // ---------------------------------------------------------------------------

  // Factory method to create an instance of the skill.
  static std::unique_ptr<intrinsic::skills::SkillInterface> CreateSkill();

  // ---------------------------------------------------------------------------
  // Skill execution (see intrinsic::skills::SkillExecuteInterface)
  // ---------------------------------------------------------------------------

  // Called once each time the skill is executed in a process.
  absl::StatusOr<std::unique_ptr<google::protobuf::Message>> Execute(
      const intrinsic::skills::ExecuteRequest& request,
      intrinsic::skills::ExecuteContext& context) override;
};

}  // namespace wiggle_joint

#endif  // WIGGLE_JOINT_WIGGLE_JOINT_H_
