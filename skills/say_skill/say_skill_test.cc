#include "skills/say_skill/say_skill.h"

#include <gtest/gtest.h>

#include <thread>

#include "intrinsic/skills/testing/skill_test_utils.h"
#include "skills/say_skill/say_skill.pb.h"

using ::com::example::SaySkillParams;
using ::intrinsic::skills::ExecuteContext;
using ::intrinsic::skills::ExecuteRequest;
using ::intrinsic::skills::SkillCancellationManager;
using ::intrinsic::skills::SkillTestFactory;

namespace {
TEST(SaySkillTest, Execute) {
  auto skill = say_skill::SaySkill::CreateSkill();

  // Set parameters
  SaySkillParams params;
  params.set_text("hello world");
  params.set_wait_ms(1);

  auto skill_test_factory = SkillTestFactory();
  ExecuteRequest execute_request =
      skill_test_factory.MakeExecuteRequest(params);
  std::unique_ptr<ExecuteContext> execute_context =
      skill_test_factory.MakeExecuteContext({});

  auto result = skill->Execute(execute_request, *execute_context);

  ASSERT_TRUE(result.ok());
  EXPECT_EQ(nullptr, *result);
}

TEST(SaySkillTest, ExecuteCancelled) {
  auto skill = say_skill::SaySkill::CreateSkill();

  // Set parameters
  SaySkillParams params;
  params.set_text("hello world");
  params.set_wait_ms(10000);

  SkillCancellationManager canceller(absl::Seconds(10));

  auto skill_test_factory = SkillTestFactory();
  ExecuteRequest execute_request =
      skill_test_factory.MakeExecuteRequest(params);
  std::unique_ptr<ExecuteContext> execute_context =
      skill_test_factory.MakeExecuteContext({.canceller = &canceller});

  std::thread cancel_skill([&canceller]() {
    ASSERT_TRUE(canceller.WaitForReady().ok());
    ASSERT_TRUE(canceller.Cancel().ok());
  });

  auto result = skill->Execute(execute_request, *execute_context);
  cancel_skill.join();

  EXPECT_TRUE(absl::IsCancelled(result.status()));
}
}  // namespace
