"""A helper library for handling recordings."""

import time
from typing import Optional

from absl import logging
import grpc
from intrinsic.logging.proto import bag_packager_service_pb2
from intrinsic.logging.proto import bag_packager_service_pb2_grpc
from intrinsic.util.grpc import auth

_GENERATE_RETRY_COUNT = 10
_GENERATE_RETRY_DELAY_SECS = 30


def get_recording(
    client: bag_packager_service_pb2_grpc.BagPackagerStub,
    recording_id: str,
    with_url: bool,
) -> Optional[bag_packager_service_pb2.GetBagResponse]:
  """Retrieves recording details, handling NOT_FOUND errors."""
  try:
    return client.GetBag(
        bag_packager_service_pb2.GetBagRequest(
            bag_id=recording_id, with_url=with_url
        )
    )
  except grpc.RpcError as e:
    if e.code() == grpc.StatusCode.NOT_FOUND:
      return None
    raise


def is_recording_generated(
    response: Optional[bag_packager_service_pb2.GetBagResponse],
) -> bool:
  """Checks if a recording has a generated bag file."""
  return (
      response is not None
      and response.bag.bag_file is not None
      and response.bag.bag_file.file_path
  )


def wait_for_recording_to_generate(
    stub: bag_packager_service_pb2_grpc.BagPackagerStub, recording_id: str
) -> None:
  """Waits for a recording to be generated, with polling."""
  logging.info("Waiting for recording %s to be generated...", recording_id)
  for _ in range(_GENERATE_RETRY_COUNT):
    logging.info("Still generating...")
    # Poll without requesting the URL to be efficient.
    get_resp = get_recording(stub, recording_id, with_url=False)
    if is_recording_generated(get_resp):
      logging.info("Generated recording file for recording ID %s", recording_id)
      return
    time.sleep(_GENERATE_RETRY_DELAY_SECS)
  raise RuntimeError(
      f"Failed to generate recording with id {recording_id} after 10 retries."
  )


def generate_recording(
    stub: bag_packager_service_pb2_grpc.BagPackagerStub,
    recording_id: str,
    org_info: auth.OrgInfo,
) -> Optional[bag_packager_service_pb2.BagRecord]:
  """Ensures a recording is generated, handling timeouts and polling."""
  logging.info("Starting generation of recording with id %s...", recording_id)
  generate_req = bag_packager_service_pb2.GenerateBagRequest(
      bag_id=recording_id,
      organization_id=org_info.organization,
  )

  try:
    response = stub.GenerateBag(generate_req)
    logging.info("Generated recording file for recording ID %s", recording_id)
    return response.bag
  except grpc.RpcError as e:
    if e.code() != grpc.StatusCode.DEADLINE_EXCEEDED:
      raise RuntimeError(f"Error generating bag: {e}") from e

    wait_for_recording_to_generate(stub, recording_id)
    response = get_recording(stub, recording_id, with_url=False)

    return response.bag if response else None
