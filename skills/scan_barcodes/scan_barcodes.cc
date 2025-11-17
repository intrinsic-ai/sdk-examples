#include "scan_barcodes.h"

#include <chrono>
#include <memory>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include "absl/log/log.h"
#include "absl/status/status.h"
#include "absl/status/statusor.h"
#include "intrinsic/connect/cc/grpc/channel.h"
#include "intrinsic/perception/proto/v1/camera_config.pb.h"
#include "intrinsic/perception/proto/v1/camera_service.grpc.pb.h"
#include "intrinsic/skills/cc/skill_utils.h"
#include "intrinsic/skills/proto/skill_service.pb.h"
#include "intrinsic/util/status/status_conversion_grpc.h"
#include "intrinsic/util/status/status_macros.h"
#include "opencv2/core/mat.hpp"
#include "skills/scan_barcodes/scan_barcodes.pb.h"

namespace scan_barcodes {

using ::com::example::BarcodeType;
using ::com::example::ScanBarcodesParams;
using ::com::example::ScanBarcodesResult;

using ::intrinsic::connect::WaitForChannelConnected;
using ::intrinsic::skills::EquipmentPack;
using ::intrinsic::skills::ExecuteContext;
using ::intrinsic::skills::ExecuteRequest;
using ::intrinsic::skills::SkillInterface;

BarcodeType ConvertBarcodeTypeToProto(std::string_view type) {
  // Strings from
  // https://github.com/opencv/opencv/blob/
  // e8f94182f577894410cc59d5d20979dff69d8878/modules/objdetect/src/
  // barcode_decoder/abs_decoder.hpp#L46-L51
  if (type == "EAN_8") {
    return BarcodeType::BARCODE_EAN_8;
  } else if (type == "EAN_13") {
    return BarcodeType::BARCODE_EAN_13;
  } else if (type == "UPC_E") {
    return BarcodeType::BARCODE_UPC_E;
  } else if (type == "UPC_A") {
    return BarcodeType::BARCODE_UPC_A;
  } else if (type == "UPC_EAN_EXTENSION") {
    return BarcodeType::BARCODE_UPC_EAN_EXTENSION;
  }

  return BarcodeType::BARCODE_UNSPECIFIED;
}

// -----------------------------------------------------------------------------
// Skill signature.
// -----------------------------------------------------------------------------

std::unique_ptr<SkillInterface> ScanBarcodes::CreateSkill() {
  return std::make_unique<ScanBarcodes>();
}

// -----------------------------------------------------------------------------
// Skill execution.
// -----------------------------------------------------------------------------

absl::StatusOr<std::unique_ptr<google::protobuf::Message>>
ScanBarcodes::Execute(const ExecuteRequest& request, ExecuteContext& context) {
  // Get parameters.
  INTR_ASSIGN_OR_RETURN(auto params, request.params<ScanBarcodesParams>());

  // Get equipment.
  const EquipmentPack equipment_pack = context.equipment();
  INTR_ASSIGN_OR_RETURN(const auto camera_equipment,
                        equipment_pack.GetHandle(kCameraSlot));

  intrinsic_proto::perception::v1::CameraConfig camera_config;
  camera_equipment.resource_data()
      .at("CameraConfig")
      .contents()
      .UnpackTo(&camera_config);

  // Connect to the camera over gRPC.
  INTR_ASSIGN_OR_RETURN(
      std::unique_ptr<intrinsic_proto::perception::v1::CameraService::Stub>
          camera_stub,
      CreateCameraStub(camera_equipment.connection_info().grpc()));

  // Get a capture result from the camera.
  INTR_ASSIGN_OR_RETURN(
      intrinsic_proto::perception::v1::CaptureResult capture_result,
      Capture(camera_config, camera_equipment.connection_info().grpc(),
              *camera_stub));

  if (capture_result.sensor_images().size() != 1) {
    return absl::UnknownError("Expected camera to provide exactly 1 image");
  }

  // Convert to cv::Mat.
  auto image_buffer = capture_result.sensor_images().at(0).buffer();

  auto img = cv::Mat(
      image_buffer.dimensions().rows(), image_buffer.dimensions().cols(),
      CV_8UC3,  // Barcode detector requires unsigned data
      // Need unsigned data with no const so it can implicitly cast to void*
      const_cast<unsigned char*>(
          reinterpret_cast<const unsigned char*>(image_buffer.data().c_str())));

  // Do the detection.
  std::vector<cv::Point2f> detected_corners;
  std::vector<std::string> decoded_type;
  std::vector<std::string> decoded_data;

  try {
    detector_.detectAndDecodeWithType(img, decoded_data, decoded_type,
                                      detected_corners);
  } catch (const cv::Exception& e) {
    LOG(ERROR) << e.what();
    return absl::UnknownError(e.what());
  }

  INTR_ASSIGN_OR_RETURN(
      std::unique_ptr<ScanBarcodesResult> result,
      ConvertToResultProto(decoded_data, decoded_type, detected_corners));

  LOG(INFO) << "Detected " << decoded_data.size() << " barcode(s).";
  return result;
}

absl::StatusOr<
    std::unique_ptr<intrinsic_proto::perception::v1::CameraService::Stub>>
ScanBarcodes::CreateCameraStub(
    const intrinsic_proto::resources::ResourceGrpcConnectionInfo& grpc_info) {
  // Connect to the provided camera.
  const std::string camera_grpc_address = grpc_info.address();
  const std::string camera_server_instance = grpc_info.server_instance();

  grpc::ChannelArguments options;
  constexpr int kMaxReceiveMessageSize{
      -1};  // Put no limit on the size of a message we can receive.
  options.SetMaxReceiveMessageSize(kMaxReceiveMessageSize);
  auto camera_channel = grpc::CreateCustomChannel(
      camera_grpc_address, grpc::InsecureChannelCredentials(), options);

  INTR_RETURN_IF_ERROR(WaitForChannelConnected(
      camera_server_instance, camera_channel, absl::InfiniteFuture()));

  return intrinsic_proto::perception::v1::CameraService::NewStub(
      camera_channel);
}

absl::StatusOr<intrinsic_proto::perception::v1::CaptureResult>
ScanBarcodes::Capture(
    const intrinsic_proto::perception::v1::CameraConfig& camera_config,
    const intrinsic_proto::resources::ResourceGrpcConnectionInfo& grpc_info,
    intrinsic_proto::perception::v1::CameraService::Stub& camera_stub) {
  const std::string camera_server_instance = grpc_info.server_instance();

  auto client_context = std::make_unique<grpc::ClientContext>();
  constexpr const auto kCameraClientTimeout = std::chrono::seconds(5);
  client_context->set_deadline(std::chrono::system_clock::now() +
                               kCameraClientTimeout);
  if (!camera_server_instance.empty()) {
    client_context->AddMetadata("x-resource-instance-name",
                                camera_server_instance);
  }

  intrinsic_proto::perception::v1::CaptureRequest request;
  *request.mutable_camera_config() = camera_config;
  request.mutable_timeout()->set_seconds(5);
  intrinsic_proto::perception::v1::CaptureResponse response;
  INTR_RETURN_IF_ERROR(intrinsic::ToAbslStatus(
      camera_stub.Capture(client_context.get(), request, &response)));
  return std::move(*response.mutable_capture_result());
}

absl::StatusOr<std::unique_ptr<ScanBarcodesResult>>
ScanBarcodes::ConvertToResultProto(
    const std::vector<std::string>& decoded_data,
    const std::vector<std::string>& decoded_types,
    const std::vector<cv::Point2f>& detected_corners) {
  auto result = std::make_unique<ScanBarcodesResult>();

  constexpr int kNumCorners = 4;

  if (decoded_data.size() != decoded_types.size() ||
      (kNumCorners * decoded_types.size()) != detected_corners.size()) {
    LOG(ERROR)
        << "Internal error: barcode detection data had inconsistent sizes."
        << " Please report this as a bug with this skill.";
    return absl::InternalError("barcode detection data had inconsistent sizes");
  }

  for (int d = 0; d < decoded_types.size(); ++d) {
    std::string_view barcode_data = decoded_data.at(d);
    std::string_view barcode_type = decoded_types.at(d);
    auto corners_iter = detected_corners.begin() + (d * kNumCorners);

    ::com::example::Barcode* barcode = result->add_barcodes();
    barcode->set_type(ConvertBarcodeTypeToProto(barcode_type));
    barcode->set_data(barcode_data);

    ::com::example::Corner* corner = barcode->add_corners();

    for (int c = 0; c < kNumCorners; ++c) {
      const cv::Point2f& point = *(corners_iter + c);
      corner->set_x(point.x);
      corner->set_y(point.y);
    }
  }

  return result;
}

}  // namespace scan_barcodes
