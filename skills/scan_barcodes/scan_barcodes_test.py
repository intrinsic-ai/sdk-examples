import unittest
from unittest.mock import create_autospec
from unittest.mock import patch

import cv2
import numpy as np

try:
  from rules_python.python.runfiles import runfiles
except ImportError:
  # https://github.com/bazelbuild/rules_python/issues/1679
  from python.runfiles import runfiles

from intrinsic.perception.python.camera.cameras import Camera
from intrinsic.perception.python.camera.data_classes import SensorImage
from intrinsic.skills.python import skill_interface

from skills.scan_barcodes.scan_barcodes import ScanBarcodes
from skills.scan_barcodes import scan_barcodes_pb2


class ScanBarcodesTest(unittest.TestCase):

  def make_execute_context(self):
    mock_context = create_autospec(
        spec=skill_interface.ExecuteContext, spec_set=True, instance=True
    )

    return mock_context

  def load_test_image(self, name) -> np.ndarray:
    r = runfiles.Create()

    path = r.Rlocation("examples/skills/scan_barcodes/test/" + name)
    img = cv2.imread(path)
    return img

  def setUp(self) -> None:
    self.camera_creator_patcher = patch(
        "intrinsic.perception.python.camera.cameras.Camera",
        spec_set=True,
        autospec=True,
    )
    self.mock_camera_class = self.camera_creator_patcher.start()
    self.mock_camera = create_autospec(
        spec=Camera, spec_set=True, instance=True
    )
    self.mock_camera_class.create.return_value = self.mock_camera

  def tearDown(self) -> None:
    self.camera_creator_patcher.stop()

  def test_no_barcodes(self):
    dut_skill = ScanBarcodes()
    mock_request = skill_interface.ExecuteRequest(
        params=scan_barcodes_pb2.ScanBarcodesParams()
    )

    mock_context = self.make_execute_context()

    black_buffer = np.ndarray(
        shape=(1216, 1936, 3),
        dtype=np.uint8,
        buffer=bytes([0] * (1216 * 1936 * 3)),
    )
    black_image = create_autospec(
        spec=SensorImage, spec_set=True, instance=True
    )
    black_image.array = black_buffer
    self.mock_camera.capture.return_value = black_image

    result = dut_skill.execute(mock_request, mock_context)
    self.assertTrue(isinstance(result, scan_barcodes_pb2.ScanBarcodesResult))
    self.assertEqual(len(result.barcodes), 0)

  def test_one_barcode(self):
    dut_skill = ScanBarcodes()
    mock_request = skill_interface.ExecuteRequest(
        params=scan_barcodes_pb2.ScanBarcodesParams()
    )

    mock_context = self.make_execute_context()

    test_image = create_autospec(spec=SensorImage, spec_set=True, instance=True)
    test_image.array = self.load_test_image("EAN-8_0123456.png")
    self.mock_camera.capture.return_value = test_image

    result = dut_skill.execute(mock_request, mock_context)
    self.assertTrue(isinstance(result, scan_barcodes_pb2.ScanBarcodesResult))
    self.assertEqual(1, len(result.barcodes))
    self.assertEqual(scan_barcodes_pb2.BARCODE_EAN_8, result.barcodes[0].type)
    self.assertEqual("01234565", result.barcodes[0].data)


if __name__ == "__main__":
  unittest.main()
