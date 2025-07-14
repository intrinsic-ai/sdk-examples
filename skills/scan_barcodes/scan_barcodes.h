#ifndef SDK_EXAMPLES_SKILLS_SCAN_BARCODES_SCAN_BARCODES_H_
#define SDK_EXAMPLES_SKILLS_SCAN_BARCODES_SCAN_BARCODES_H_

#include <memory>
#include <string>
#include <utility>
#include <vector>

#include "absl/status/statusor.h"
#include "intrinsic/perception/proto/v1/camera_service.grpc.pb.h"
#include "intrinsic/perception/proto/v1/camera_service.pb.h"
#include "intrinsic/skills/cc/skill_interface.h"
#include "intrinsic/skills/proto/skill_service.pb.h"
#include "opencv2/objdetect/barcode.hpp"
#include "skills/scan_barcodes/scan_barcodes.pb.h"

namespace scan_barcodes {

class ScanBarcodes : public intrinsic::skills::SkillInterface {
 public:
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

 private:
  absl::StatusOr<
      std::unique_ptr<intrinsic_proto::perception::v1::CameraService::Stub>>
  CreateCameraStub(
      const intrinsic_proto::resources::ResourceGrpcConnectionInfo& grpc_info);

  absl::StatusOr<intrinsic_proto::perception::v1::CaptureResult> Capture(
      const intrinsic_proto::perception::v1::CameraConfig& camera_config,
      const intrinsic_proto::resources::ResourceGrpcConnectionInfo& grpc_info,
      intrinsic_proto::perception::v1::CameraService::Stub& camera_stub);

  absl::StatusOr<std::unique_ptr<::com::example::ScanBarcodesResult>>
  ConvertToResultProto(const std::vector<std::string>& decoded_data,
                       const std::vector<std::string>& decoded_types,
                       const std::vector<cv::Point2f>& detected_corners);

  cv::barcode::BarcodeDetector detector_;
};

}  // namespace scan_barcodes

#endif  // SDK_EXAMPLES_SKILLS_SCAN_BARCODES_SCAN_BARCODES_H_
