import json
import sys
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

# Classes to imitate the Protobuf/gRPC objects.


class GrpcServicer:
  """Replaces state_grpc.ServiceStateServicer for testing purposes.

  This class mocks the gRPC methods required by the service state definition
  without requiring the actual generated gRPC code.
  """

  def GetState(self, request, context):
    """Mocks the GetState RPC method."""
    pass

  def Enable(self, request, context):
    """Mocks the Enable RPC method."""
    pass

  def Disable(self, request, context):
    """Mocks the Disable RPC method."""
    pass


class StateCodeClass:
  """Replaces the StateCode Enum used in Protocol Buffers.

  Attributes:
      STATE_CODE_ENABLED (int): Integer representation of enabled state (3).
      STATE_CODE_DISABLED (int): Integer representation of disabled state (2).
  """

  STATE_CODE_ENABLED = 3
  STATE_CODE_DISABLED = 2

  @staticmethod
  def Name(code):
    """Returns the string name for a given state code.

    Args:
        code (int): The integer state code.

    Returns:
        str: The name of the state ('STATE_CODE_ENABLED' or 'STATE_CODE_DISABLED').
    """
    return "STATE_CODE_ENABLED" if code == 3 else "STATE_CODE_DISABLED"


class SelfState:
  """Replaces state_proto.SelfState.
  This class mimics the Protobuf message object, storing the state_code
  as a real integer for validation logic.

  Attributes:
      state_code (int): The current state code of the service.
  """

  # Attach the Enum to the class
  StateCode = StateCodeClass
  STATE_CODE_ENABLED = 3
  STATE_CODE_DISABLED = 2

  def __init__(self, state_code=None):
    """Initializes the SelfState mock.

    Args:
        state_code (int, optional): The initial state code. Defaults to None.
    """
    self.state_code = state_code


# Create the mock module objects
mock_state_grpc = MagicMock()
mock_state_proto = MagicMock()
mock_runtime = MagicMock()

# Inject previous classes
mock_state_grpc.ServiceStateServicer = GrpcServicer
mock_state_proto.SelfState = SelfState

sys.modules["intrinsic.assets.data.proto.v1"] = MagicMock()
sys.modules["intrinsic.assets.services.proto.v1"] = MagicMock()
sys.modules["intrinsic.assets.services.proto.v1"].service_state_pb2 = (
    mock_state_proto
)
sys.modules["intrinsic.assets.services.proto.v1"].service_state_pb2_grpc = (
    mock_state_grpc
)
sys.modules["intrinsic.resources.proto"] = MagicMock()
sys.modules["intrinsic.resources.proto"].runtime_context_pb2 = mock_runtime

from services.platform_http_server import server


@pytest.fixture
def mock_assets():
  """Creates a rich mock dictionary of assets.

  Returns:
      dict: A dictionary mimicking the asset structure where keys are asset IDs
      and values are dictionaries mapping file paths to their byte content.
  """
  return {
      "ai.intrinsic.asset1": {
          "index.html": (
              b"<!DOCTYPE html><html><body><h1>Hello World</h1></body></html>"
          ),
          "css/style.css": b"body { background-color: #f0f0f0; }",
          "js/app.js": b"console.log('App loaded');",
          "images/logo.png": b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR...",
          "assets/fonts/roboto.woff2": b"\x00\x01\x00\x00",
      },
      "ai.intrinsic.asset2": {
          "index.html": b"<html>Version 2</html>",
      },
  }


@pytest.fixture
def client(mock_assets):
  """Configures the Flask test client with mock assets.

  Sets up the testing configuration, injects the mock asset dictionary,
  and sets the initial active asset ID.

  Args:
      mock_assets (dict): The fixture containing mock asset data.

  Yields:
      flask.testing.FlaskClient: A test client for the Flask application.
  """
  server.app.config["TESTING"] = True
  server.app.config["ALL_ASSETS_CONTENT"] = mock_assets
  server.app.config["ACTIVE_ASSET_ID"] = "ai.intrinsic.asset1"

  server._SERVICE_STATE["state_code"] = 3

  with server.app.test_client() as client:
    yield client


class TestAssetServing:
  """Tests for serving static assets via the Flask server."""

  def test_serve_root_file(self, client, mock_assets):
    """Verifies that the root file (index.html) is served correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.data == mock_assets["ai.intrinsic.asset1"]["index.html"]

  def test_serve_specific_file(self, client, mock_assets):
    """Verifies that a specific file (css) can be retrieved."""
    response = client.get("/css/style.css")
    assert response.status_code == 200
    assert response.data == mock_assets["ai.intrinsic.asset1"]["css/style.css"]

  def test_file_not_found(self, client):
    """Verifies that requesting a non-existent file returns a 404 status."""
    response = client.get("/missing.jpg")
    assert response.status_code == 404

  def test_security_headers(self, client):
    """Verifies that security headers (X-Frame-Options) are present."""
    response = client.get("/")
    assert response.headers["X-Frame-Options"] == "SAMEORIGIN"


class TestContentIntegrity:
  """Tests for ensuring binary and text content is served exactly as stored."""

  def test_serve_exact_html_content(self, client, mock_assets):
    """Checks that HTML content matches the source bytes exactly."""
    response = client.get("/")
    assert response.data == mock_assets["ai.intrinsic.asset1"]["index.html"]

  def test_serve_binary_image(self, client, mock_assets):
    """Checks that binary image data matches the source bytes exactly."""
    response = client.get("/images/logo.png")
    assert (
        response.data == mock_assets["ai.intrinsic.asset1"]["images/logo.png"]
    )

  def test_serve_deeply_nested_file(self, client, mock_assets):
    """Checks that deeply nested files are resolved and served correctly."""
    response = client.get("/assets/fonts/roboto.woff2")
    assert (
        response.data
        == mock_assets["ai.intrinsic.asset1"]["assets/fonts/roboto.woff2"]
    )


class TestHotReloading:
  """Tests for the dynamic reconfiguration (hot reloading) of assets."""

  def test_reconfigure_success(self, client, mock_assets):
    """Verifies successful switching of the active asset ID."""
    assert (
        client.get("/").data == mock_assets["ai.intrinsic.asset1"]["index.html"]
    )
    payload = {"data_asset_id": "ai.intrinsic.asset2"}
    response = client.post("/reconfigure", json=payload)
    assert response.status_code == 200
    assert server.app.config["ACTIVE_ASSET_ID"] == "ai.intrinsic.asset2"
    assert (
        client.get("/").data == mock_assets["ai.intrinsic.asset2"]["index.html"]
    )

  def test_reconfigure_invalid_json(self, client):
    """Tests reconfigure behavior with a missing or malformed JSON body.

    The server wraps the request in a try/except block. When get_json() fails,
    the server catches the error and should return a 500 status code.
    """
    # 500 here because server.py wraps the request in a try/except block.
    # When get_json() fails, the server catches the error and returns 500.
    response = client.post(
        "/reconfigure",
        data="not json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 500

  def test_reconfigure_missing_key(self, client):
    """Verifies 400 Bad Request when the JSON payload is missing required keys."""
    response = client.post("/reconfigure", json={"wrong_key": "val"})
    assert response.status_code == 400

  def test_reconfigure_unknown_asset(self, client):
    """Verifies 404 Not Found when requesting a non-existent asset ID."""
    payload = {"data_asset_id": "ai.intrinsic.asset3"}
    response = client.post("/reconfigure", json=payload)
    assert response.status_code == 404


class TestLifecycle:
  """Tests for the service lifecycle endpoints (enable/disable/status)."""

  @patch(
      "services.platform_http_server.server._reload_assets_and_enable_service"
  )
  def test_disable_and_enable_http(self, mock_reload, client):
    """Tests the full disable -> status check -> enable cycle.

    Args:
        mock_reload (MagicMock): Mock for the asset reload function.
        client (flask.testing.FlaskClient): The test client.
    """
    # 1. Disable
    response = client.post("/disable")
    assert response.status_code == 200

    # 2. Verify Status
    status_resp = client.get("/status")
    assert status_resp.status_code == 200
    assert (
        "ENABLED" in status_resp.json["status"]
        or "DISABLED" in status_resp.json["status"]
    )

    # 3. Enable
    response = client.post("/enable")
    assert response.status_code == 200
    mock_reload.assert_called_once()


class TestAssetLoadingLogic:
  """Tests for the backend logic that loads assets into memory."""

  @patch(
      "services.platform_http_server.server.data_asset_utils.DataAssetsService"
  )
  def test_load_assets_to_memory(self, MockDataAssetsService):
    """Verifies that asset protos are correctly unpacked into memory.

    This test mocks the DataAssetsService and the Protobuf Unpack method
    to simulate loading an asset with specific HTML content.

    Args:
        MockDataAssetsService (MagicMock): Mock of the external data service.
    """
    mock_service = MockDataAssetsService.return_value
    mock_asset = MagicMock()
    mock_asset.metadata.id_version.id.package = "ai.intrinsic"
    mock_asset.metadata.id_version.id.name = "test_asset"
    mock_asset.data.type_url = "type.googleapis.com/ReferencedDataStruct"

    def side_effect_unpack(target_proto):
      target_proto.fields = {
          "index.html": MagicMock(
              referenced_data_value=MagicMock(inlined=b"HTML DATA")
          )
      }

    mock_asset.data.Unpack.side_effect = side_effect_unpack
    mock_service.list_data_assets.return_value = [mock_asset]

    result = server.load_assets_to_memory()
    assert "ai.intrinsic.test_asset" in result
    assert result["ai.intrinsic.test_asset"]["index.html"] == b"HTML DATA"


class TestGrpcServicer:
  """Tests for the gRPC Servicer implementation."""

  @pytest.fixture(autouse=True)
  def setup_servicer(self):
    """Sets up the servicer instance and mock context before each test."""
    # Reset Global State
    server._SERVICE_STATE["state_code"] = 2
    self.servicer = server.PlatformHttpServicer()
    self.mock_context = MagicMock()

  def test_get_state(self):
    """Verifies GetState returns the correct state code."""
    server._SERVICE_STATE["state_code"] = 3
    request = MagicMock()
    response = self.servicer.GetState(request, self.mock_context)
    assert response.state_code == 3

  @patch(
      "services.platform_http_server.server._reload_assets_and_enable_service"
  )
  def test_enable_rpc(self, mock_reload):
    """Verifies the Enable RPC triggers a reload."""
    request = MagicMock()
    self.servicer.Enable(request, self.mock_context)
    mock_reload.assert_called_once()

  def test_disable_rpc(self):
    """Verifies the Disable RPC updates the global state code."""
    server._SERVICE_STATE["state_code"] = 3
    request = MagicMock()
    self.servicer.Disable(request, self.mock_context)
    assert server._SERVICE_STATE["state_code"] == 2

  def test_concurrency_lock(self):
    """Verifies that the concurrency lock is acquired during state changes."""
    with patch("services.platform_http_server.server.update_lock") as mock_lock:
      request = MagicMock()
      self.servicer.Disable(request, self.mock_context)
      mock_lock.__enter__.assert_called()
      mock_lock.__exit__.assert_called()


if __name__ == "__main__":
  sys.exit(pytest.main(["-s", "-v", __file__]))
