"""A script to generate and get a URL to visualize that recording."""

import datetime
import time
from typing import Optional
import uuid

from absl import app
from absl import flags
from absl import logging
from google.protobuf import timestamp_pb2
import grpc
from intrinsic.kubernetes.vmpool.manager.api.v1 import lease_api_pb2
from intrinsic.kubernetes.vmpool.manager.api.v1 import lease_api_pb2_grpc
from intrinsic.logging.proto import bag_packager_service_pb2_grpc
from intrinsic.logging.proto import replay_service_pb2
from intrinsic.logging.proto import replay_service_pb2_grpc
from intrinsic.solutions import auth
from intrinsic.solutions import dialerutil
from scripts.recordings import recording_lib

FLAGS = flags.FLAGS

_ORG = flags.DEFINE_string(
    "org",
    None,
    "The organization ID.",
    required=True,
)
_RECORDING_ID = flags.DEFINE_string(
    "recording_id",
    None,
    "The ID of the recording to generate and visualize.",
    required=True,
)
_DURATION_SECS = flags.DEFINE_integer(
    "duration",
    3600,
    "The duration of the VM lease in seconds.",
)

# Constants
_VM_POOL = ""
_LEASE_RETRY_COUNT = 5
_LEASE_RETRY_DELAY_SECS = 20


def request_lease(
    lease_client: lease_api_pb2_grpc.VMPoolLeaseServiceStub,
    duration: datetime.timedelta,
    pool: str,
    service_tag: str,
    reservation_id: Optional[str] = None,
) -> lease_api_pb2.Lease:
  """Requests a lease from a pre-existing pool."""
  if not reservation_id:
    reservation_id = str(uuid.uuid4())

  for _ in range(_LEASE_RETRY_COUNT):
    try:
      expires = timestamp_pb2.Timestamp()
      expires.FromDatetime(
          datetime.datetime.now(datetime.timezone.utc) + duration
      )
      req = lease_api_pb2.LeaseRequest(
          pool=pool,
          expires=expires,
          service_tag=service_tag,
          reservation_id=reservation_id,
      )
      lease_response = lease_client.Lease(req)
      logging.info("Successfully leased VM: %s", lease_response.lease.instance)
      return lease_response.lease
    except grpc.RpcError as e:
      if e.code() == grpc.StatusCode.PERMISSION_DENIED:
        raise RuntimeError(
            "Lease request failed: Your API key might have expired."
        ) from e
      if e.code() == grpc.StatusCode.UNAUTHENTICATED:
        raise RuntimeError(
            "Lease request failed: Please ensure you are logged in."
        ) from e

      logging.warning(
          "Lease request did not succeed yet, retrying in %ds: %s",
          _LEASE_RETRY_DELAY_SECS,
          e.details(),
      )
      time.sleep(_LEASE_RETRY_DELAY_SECS)
  raise RuntimeError("Failed to acquire lease after multiple retries.")


def connect_and_request_visualization(
    org_info: auth.OrgInfo, lease: lease_api_pb2.Lease, recording_id: str
) -> Optional[str]:
  """Connects to the leased VM and requests a visualization URL."""
  try:
    with dialerutil.create_channel_from_cluster(
        org_info=org_info, cluster=lease.instance
    ) as vm_channel:
      logging.info(
          "Connecting to replay service on cluster '%s'", lease.instance
      )
      replay_client = replay_service_pb2_grpc.ReplayStub(vm_channel)
      req = replay_service_pb2.VisualizeRecordingRequest(
          recording_id=recording_id,
      )
      resp = replay_client.VisualizeRecording(req)
      return resp.url
  except grpc.RpcError as e:
    logging.error("Error communicating with replay service: %s", e)
    return None


def main(argv):
  """Main function to generate a recording and fetch its visualization URL."""
  if len(argv) > 1:
    raise app.UsageError("Too many command-line arguments.")

  org_info = auth.parse_info_from_string(_ORG.value)
  recording_id = _RECORDING_ID.value

  # Establish a connection to the shared cloud gRPC services.
  channel = dialerutil.create_channel_from_org(org_info)
  bag_packager_client = bag_packager_service_pb2_grpc.BagPackagerStub(channel)

  # Get, or generate the recording and wait for it to complete.
  initial_response = recording_lib.get_recording(
      bag_packager_client, recording_id, with_url=False
  )
  if initial_response is None:
    logging.error("Recording with id %s does not exist.", recording_id)
    return
  if not recording_lib.is_recording_generated(initial_response):
    recording_lib.generate_recording(
        bag_packager_client,
        recording_id,
        org_info,
    )
    recording_lib.wait_for_recording_to_generate(
        bag_packager_client,
        recording_id,
    )
  generated_recording_id = recording_id

  logging.info("Retrieved recording ID: %s", generated_recording_id)

  if not recording_id:
    logging.error("Could not obtain recording ID. Aborting.")
    return

  # Lease a VM for visualization.
  lease_client = lease_api_pb2_grpc.VMPoolLeaseServiceStub(channel)
  lease_duration = datetime.timedelta(seconds=_DURATION_SECS.value)
  lease = request_lease(
      lease_client=lease_client,
      duration=lease_duration,
      pool=_VM_POOL,
      service_tag="generate_and_visualize_recording",
  )

  if not lease:
    logging.error("Failed to acquire VM lease. Aborting.")
    return

  logging.info(
      "VM instance '%s' leased from pool '%s'.", lease.instance, lease.pool
  )

  # Connect to the leased VM and get the visualization URL.
  url = connect_and_request_visualization(
      org_info, lease, generated_recording_id
  )

  if not url:
    return

  lease_expires = lease.expires.ToDatetime().replace(
      tzinfo=datetime.timezone.utc
  )
  expires_in = lease_expires - datetime.datetime.now(datetime.timezone.utc)

  print(f"\nVisualization created successfully for recording {recording_id}")
  print(
      f"- Visualization valid for {expires_in}, expires at"
      f" {lease_expires.isoformat()}"
  )
  print(
      "\nData will load into the visualization over the next few minutes."
      " You will know it is done when data stops appearing in the timeline."
  )
  # ANSI color codes: Blue background, White text
  print(f"\n\033[44m\033[97mLink to visualization: {url}\033[0m\n")


if __name__ == "__main__":
  app.run(main)
