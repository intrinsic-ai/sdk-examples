#ifndef SKILLS_STOP_STOPWATCH_STOP_STOPWATCH_H_
#define SKILLS_STOP_STOPWATCH_STOP_STOPWATCH_H_

#include <memory>
#include <string>
#include <utility>

#include "absl/container/flat_hash_map.h"
#include "absl/status/statusor.h"
#include "google/protobuf/message.h"
#include "intrinsic/skills/cc/skill_interface.h"

namespace skills::stop_stopwatch {

class StopStopwatch : public intrinsic::skills::SkillInterface {
 public:
  // Factory method to create an instance of the skill.
  static std::unique_ptr<intrinsic::skills::SkillInterface> CreateSkill();

  // Returns the resources required for running this skill.
  absl::StatusOr<intrinsic_proto::skills::Footprint> GetFootprint(
      const intrinsic::skills::GetFootprintRequest& request,
      intrinsic::skills::GetFootprintContext& context) const override;

  // Previews the expected outcome of executing the skill.
  absl::StatusOr<std::unique_ptr<::google::protobuf::Message>> Preview(
      const intrinsic::skills::PreviewRequest& request,
      intrinsic::skills::PreviewContext& context) override;

  // Called once each time the skill is executed in a process.
  absl::StatusOr<std::unique_ptr<google::protobuf::Message>> Execute(
      const intrinsic::skills::ExecuteRequest& request,
      intrinsic::skills::ExecuteContext& context) override;
};

}  // namespace skills::stop_stopwatch

#endif  // SKILLS_STOP_STOPWATCH_STOP_STOPWATCH_H_
