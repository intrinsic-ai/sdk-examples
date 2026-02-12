#include "stop_stopwatch.h"

#include <gtest/gtest.h>

#include "absl/status/status_matchers.h"
#include "intrinsic/skills/testing/skill_test_utils.h"
#include "services/stopwatch/stopwatch_service.grpc.pb.h"
#include "services/stopwatch/stopwatch_service.pb.h"
#include "skills/stop_stopwatch/stop_stopwatch.pb.h"

using ::intrinsic::skills::EquipmentPack;
using ::intrinsic::skills::ExecuteContext;
using ::intrinsic::skills::ExecuteRequest;
using ::intrinsic::skills::GetFootprintContext;
using ::intrinsic::skills::GetFootprintRequest;
using ::intrinsic::skills::PreviewContext;
using ::intrinsic::skills::PreviewRequest;
using ::intrinsic::skills::SkillTestFactory;

using ::com::example::StopStopwatchParams;

using skills::stop_stopwatch::StopStopwatch;

class FakeStopwatchService : public stopwatch::StopwatchService::Service {
 public:
  grpc::Status Stop(grpc::ServerContext* context,
                    const ::stopwatch::StopRequest* request,
                    ::stopwatch::StopResponse* response) override {
    response->set_time_elapsed(42);
    return grpc::Status::OK;
  }
};

TEST(SaySkillTest, GetFootprint) {
  auto skill = StopStopwatch::CreateSkill();

  // Set parameters
  StopStopwatchParams params;

  auto skill_test_factory = SkillTestFactory();
  FakeStopwatchService service;
  auto handle = skill_test_factory.RunService(&service);
  EquipmentPack equipment_pack;
  ASSERT_THAT(equipment_pack.Add("stopwatch_service", handle),
              ::absl_testing::IsOk());

  GetFootprintRequest request =
      skill_test_factory.MakeGetFootprintRequest(params);
  std::unique_ptr<GetFootprintContext> context =
      skill_test_factory.MakeGetFootprintContext({
          .equipment_pack = equipment_pack,
      });

  auto result = skill->GetFootprint(request, *context);

  ASSERT_TRUE(result.ok());
  EXPECT_TRUE(result->lock_the_universe());
}

TEST(SaySkillTest, Preview) {
  auto skill = StopStopwatch::CreateSkill();

  // Set parameters
  StopStopwatchParams params;

  auto skill_test_factory = SkillTestFactory();
  FakeStopwatchService service;
  auto handle = skill_test_factory.RunService(&service);
  EquipmentPack equipment_pack;
  ASSERT_THAT(equipment_pack.Add("stopwatch_service", handle),
              ::absl_testing::IsOk());

  PreviewRequest request = skill_test_factory.MakePreviewRequest(params);
  std::unique_ptr<PreviewContext> context =
      skill_test_factory.MakePreviewContext({
          .equipment_pack = equipment_pack,
      });

  auto result = skill->Preview(request, *context);

  ASSERT_TRUE(absl::IsUnimplemented(result.status()));
}

TEST(SaySkillTest, Execute) {
  auto skill = StopStopwatch::CreateSkill();

  // Set parameters
  StopStopwatchParams params;

  auto skill_test_factory = SkillTestFactory();
  FakeStopwatchService service;
  auto handle = skill_test_factory.RunService(&service);
  EquipmentPack equipment_pack;
  ASSERT_THAT(equipment_pack.Add("stopwatch_service", handle),
              ::absl_testing::IsOk());

  ExecuteRequest request = skill_test_factory.MakeExecuteRequest(params);
  std::unique_ptr<ExecuteContext> context =
      skill_test_factory.MakeExecuteContext({
          .equipment_pack = equipment_pack,
      });

  auto result = skill->Execute(request, *context);
  ASSERT_TRUE(result.ok());

  auto return_value =
      google::protobuf::DownCastMessage<com::example::StopStopwatchResult>(
          result->get());
  ASSERT_NE(return_value, nullptr);
  EXPECT_EQ(42, return_value->time_elapsed());
}
