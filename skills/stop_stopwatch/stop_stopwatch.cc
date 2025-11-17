#include "stop_stopwatch.h"

#include <memory>
#include <string>

#include "absl/container/flat_hash_map.h"
#include "absl/log/log.h"
#include "absl/status/status.h"
#include "absl/status/statusor.h"
#include "google/protobuf/message.h"
#include "grpcpp/channel.h"
#include "grpcpp/create_channel.h"
#include "intrinsic/skills/cc/skill_utils.h"
#include "intrinsic/util/status/status_macros.h"
#include "intrinsic/util/status/status_macros_grpc.h"
#include "services/stopwatch/stopwatch_service.grpc.pb.h"
#include "services/stopwatch/stopwatch_service.pb.h"
#include "skills/stop_stopwatch/stop_stopwatch.pb.h"

namespace skills::stop_stopwatch {

using ::com::example::StopStopwatchParams;

using ::intrinsic::skills::ExecuteContext;
using ::intrinsic::skills::ExecuteRequest;
using ::intrinsic::skills::GetFootprintContext;
using ::intrinsic::skills::GetFootprintRequest;
using ::intrinsic::skills::PreviewContext;
using ::intrinsic::skills::PreviewRequest;
using ::intrinsic::skills::SkillInterface;
using ::intrinsic::skills::SkillProjectInterface;

std::unique_ptr<::stopwatch::StopwatchService::Stub> MakeGrpcStub(
    intrinsic_proto::resources::ResourceHandle handle) {
  const std::string& address = handle.connection_info().grpc().address();
  std::shared_ptr<grpc::Channel> channel =
      ::grpc::CreateChannel(address, grpc::InsecureChannelCredentials());
  return ::stopwatch::StopwatchService::NewStub(channel);
}

std::unique_ptr<::grpc::ClientContext> MakeClientContext(
    intrinsic_proto::resources::ResourceHandle handle) {
  const std::string& instance =
      handle.connection_info().grpc().server_instance();
  auto ctx = std::make_unique<::grpc::ClientContext>();
  ctx->AddMetadata("x-resource-instance-name", instance);
  return ctx;
}

std::unique_ptr<SkillInterface> StopStopwatch::CreateSkill() {
  return std::make_unique<StopStopwatch>();
}

absl::StatusOr<intrinsic_proto::skills::Footprint> StopStopwatch::GetFootprint(
    const GetFootprintRequest& request, GetFootprintContext& context) const {
  intrinsic_proto::skills::Footprint result;
  result.set_lock_the_universe(true);
  return std::move(result);
}

absl::StatusOr<std::unique_ptr<::google::protobuf::Message>>
StopStopwatch::Preview(const PreviewRequest& request, PreviewContext& context) {
  return absl::UnimplementedError("Skill has not implemented `Preview`.");
}

absl::StatusOr<std::unique_ptr<google::protobuf::Message>>
StopStopwatch::Execute(const ExecuteRequest& request, ExecuteContext& context) {
  INTR_ASSIGN_OR_RETURN(intrinsic_proto::resources::ResourceHandle handle,
                        context.equipment().GetHandle("stopwatch_service"));

  auto stub = MakeGrpcStub(handle);
  auto ctx = MakeClientContext(handle);
  ::stopwatch::StopRequest stop_request;
  ::stopwatch::StopResponse stop_response;
  INTR_RETURN_IF_ERROR_GRPC(
      stub->Stop(ctx.get(), stop_request, &stop_response));

  LOG(INFO) << "Time elapsed: " << stop_response.time_elapsed();

  auto return_value = std::make_unique<com::example::StopStopwatchResult>();
  return_value->set_time_elapsed(stop_response.time_elapsed());
  return return_value;
}

}  // namespace skills::stop_stopwatch
