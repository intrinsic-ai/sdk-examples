#ifndef USE_WORLD_USE_WORLD_H_
#define USE_WORLD_USE_WORLD_H_

#include <memory>

#include "absl/status/statusor.h"
#include "intrinsic/math/pose3.h"
#include "intrinsic/skills/cc/skill_interface.h"
#include "intrinsic/skills/proto/skill_service.pb.h"

namespace use_world {

class UseWorld : public intrinsic::skills::SkillInterface {
 public:
  static constexpr char kRobotSlot[] = "robot";
  static constexpr char kCameraSlot[] = "camera";

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

}  // namespace use_world

#endif  // USE_WORLD_USE_WORLD_H_
