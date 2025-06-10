"""A skill that connects to a camera resource and scans all visible barcodes using OpenCV."""

# [START import_typing]
from typing import List

# [END import_typing]

from absl import logging

# [START import_cv2]
import cv2

# [END import_cv2]
# [START import_numpy]
import numpy as np

# [END import_numpy]

# [START import_cameras]
from intrinsic.perception.python.camera import cameras

# [END import_cameras]
from intrinsic.skills.python import skill_interface
from intrinsic.util.decorators import overrides

from skills.scan_barcodes import scan_barcodes_pb2

# [START camera_slot_constant]
# Camera slot name; make sure this matches the skill manifest.
CAMERA_EQUIPMENT_SLOT: str = "camera"
# [END camera_slot_constant]


# [START convert_barcode_type_to_proto]
def convert_barcode_type_to_proto(
    barcode_type: int,
) -> scan_barcodes_pb2.BarcodeType:
  """Convert cv2 barcode type to BarcodeType proto."""
  if barcode_type == "EAN_8":
    return scan_barcodes_pb2.BARCODE_EAN_8
  elif barcode_type == "EAN_13":
    return scan_barcodes_pb2.BARCODE_EAN_13
  elif barcode_type == "UPC_A":
    return scan_barcodes_pb2.BARCODE_UPC_A
  elif barcode_type == "UPC_E":
    return scan_barcodes_pb2.BARCODE_UPC_E
  elif barcode_type == "UPC_EAN_EXTENSION":
    return scan_barcodes_pb2.BARCODE_UPC_EAN_EXTENSION
  else:
    return scan_barcodes_pb2.BARCODE_UNSPECIFIED
  # [END convert_barcode_type_to_proto]


# [START barcode_detector]
class ScanBarcodes(skill_interface.Skill):
  """Skill that connects to a camera resource and scans all visible barcodes using OpenCV."""

  detector: cv2.barcode.BarcodeDetector

  def __init__(self) -> None:
    super().__init__()
    self.detector = cv2.barcode.BarcodeDetector()
    # [END barcode_detector]

  # [START access_equipment]
  @overrides(skill_interface.Skill)
  def execute(
      self,
      request: skill_interface.ExecuteRequest[
          scan_barcodes_pb2.ScanBarcodesParams
      ],
      context: skill_interface.ExecuteContext,
  ) -> scan_barcodes_pb2.ScanBarcodesResult:
    # Get camera.
    camera = cameras.Camera.create(context, CAMERA_EQUIPMENT_SLOT)
    # [END access_equipment]

    # [START call_capture]
    # Capture from the camera and get the first sensor image as a numpy array.
    sensor_image = camera.capture()
    img = sensor_image.array
    # [END call_capture]

    # [START run_detector]
    # Run the detector and check results.
    (
        ok,
        decoded_data,
        decoded_types,
        detected_corners,
    ) = self.detector.detectAndDecodeWithType(img)
    # [END run_detector]

    # [START call_convert_to_result_proto]
    # Convert result and return.
    result = self.convert_to_result_proto(
        ok, decoded_data, decoded_types, detected_corners
    )
    # [END call_convert_to_result_proto]

    logging.info("ScanBarcodesResult: %s", result)

    # [START execute_result]
    return result
    # [END execute_result]

  # [START convert_to_result_proto]
  def convert_to_result_proto(
      self,
      ok: bool,
      decoded_data: List[str],
      decoded_types: List[int],
      detected_corners: np.ndarray,
  ) -> scan_barcodes_pb2.ScanBarcodesResult:
    if not ok:
      return scan_barcodes_pb2.ScanBarcodesResult()

    barcodes: List[scan_barcodes_pb2.Barcode] = []
    for i, barcode_type in enumerate(decoded_types):
      barcode_data = decoded_data[i]
      barcode_corners = detected_corners[i]

      corners: List[scan_barcodes_pb2.Corner] = []
      for barcode_corner in barcode_corners:
        corner = scan_barcodes_pb2.Corner(
            x=barcode_corner[0],
            y=barcode_corner[1],
        )
        corners.append(corner)

      barcode = scan_barcodes_pb2.Barcode(
          type=convert_barcode_type_to_proto(barcode_type),
          data=barcode_data,
          corners=corners,
      )
      barcodes.append(barcode)

    return scan_barcodes_pb2.ScanBarcodesResult(barcodes=barcodes)

  # [END convert_to_result_proto]
