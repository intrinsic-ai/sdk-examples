#include "say_skill.h"

#include <memory>

#include "absl/log/log.h"
#include "absl/status/status.h"
#include "absl/status/statusor.h"
#include "absl/synchronization/notification.h"
#include "intrinsic/skills/cc/skill_utils.h"
#include "intrinsic/skills/proto/skill_service.pb.h"
#include "intrinsic/util/status/status_macros.h"
#include "skills/say_skill/say_skill.pb.h"

namespace say_skill {

using ::com::example::SaySkillParams;

using ::intrinsic::skills::ExecuteContext;
using ::intrinsic::skills::ExecuteRequest;
using ::intrinsic::skills::SkillInterface;

// -----------------------------------------------------------------------------
// Skill signature.
// -----------------------------------------------------------------------------

std::unique_ptr<SkillInterface> SaySkill::CreateSkill() {
  return std::make_unique<SaySkill>();
}

// -----------------------------------------------------------------------------
// Skill execution.
// -----------------------------------------------------------------------------

absl::StatusOr<std::unique_ptr<google::protobuf::Message>> SaySkill::Execute(
    const ExecuteRequest& request, ExecuteContext& context) {
  // Get parameters.
  INTR_ASSIGN_OR_RETURN(auto params, request.params<SaySkillParams>());

  context.canceller().Ready();
  if (context.canceller().Wait(absl::Milliseconds(params.wait_ms()))) {
    LOG(INFO) << "say_skill_cc was canceled!";
    return absl::CancelledError("say_skill_cc was canceled.");
  }

  LOG(INFO) << params.text();

  return nullptr;
}
}  // namespace say_skill
