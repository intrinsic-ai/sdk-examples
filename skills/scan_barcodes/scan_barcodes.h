#ifndef SCAN_BARCODES_SCAN_BARCODES_H_
#define SCAN_BARCODES_SCAN_BARCODES_H_

#include <memory>
#include <string>
#include <utility>

#include "absl/status/statusor.h"
#include "intrinsic/perception/service/proto/camera_server.pb.h"
#include "intrinsic/perception/service/proto/camera_server.grpc.pb.h"
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
  absl::StatusOr<std::unique_ptr<google::protobuf::Message>>
  Execute(const intrinsic::skills::ExecuteRequest& request,
          intrinsic::skills::ExecuteContext& context) override;

 private:
  absl::Status
  ConnectToCamera(
    const intrinsic_proto::resources::ResourceGrpcConnectionInfo& grpc_info,
    const intrinsic_proto::perception::CameraConfig& camera_config,
    std::unique_ptr<intrinsic_proto::perception::CameraServer::Stub>* camera_stub,
    std::string* camera_handle);

  absl::StatusOr<intrinsic_proto::perception::CaptureResult>
  CaptureImage(
    const intrinsic_proto::resources::ResourceGrpcConnectionInfo& grpc_info,
    intrinsic_proto::perception::CameraServer::Stub* camera_stub,
    const std::string& camera_handle);

  absl::StatusOr<std::unique_ptr<::com::example::ScanBarcodesResult>>
  ConvertToResultProto(
    const std::vector<std::string>& decoded_data,
    const std::vector<std::string>& decoded_types,
    const std::vector<cv::Point2f>& detected_corners);

  cv::barcode::BarcodeDetector detector_;
};

}  // namespace scan_barcodes

#endif  // SCAN_BARCODES_SCAN_BARCODES_H_
