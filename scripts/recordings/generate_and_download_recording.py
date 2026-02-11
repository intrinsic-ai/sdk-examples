"""A script to generate and retrieve a recording's download URL."""

import sys

from absl import app
from absl import flags
from absl import logging
from intrinsic.logging.proto import bag_packager_service_pb2_grpc
from intrinsic.util.grpc import auth
from intrinsic.util.grpc import dialerutil
from scripts.recordings import recording_lib

_ORG = flags.DEFINE_string(
    "org",
    None,
    "The organization ID, with project suffix, e.g. org@project.",
    required=True,
)
_RECORDING_ID = flags.DEFINE_string(
    "recording_id", None, "The ID of the recording to process.", required=True
)


def main(argv) -> None:
  del argv  # Unused.

  org_info = auth.parse_info_from_string(_ORG.value)
  channel = dialerutil.create_channel_from_org(org_info)
  stub = bag_packager_service_pb2_grpc.BagPackagerStub(channel)
  recording_id = _RECORDING_ID.value

  try:
    initial_response = recording_lib.get_recording(
        stub, recording_id, with_url=False
    )
    if initial_response is None:
      logging.error("Recording with id %s does not exist.", recording_id)
      sys.exit(1)
    if not recording_lib.is_recording_generated(initial_response):
      recording_lib.generate_recording(stub, recording_id, org_info)

    # Fetch the recording details again to get the URL.
    final_response = recording_lib.get_recording(
        stub, recording_id, with_url=True
    )
    if final_response and final_response.url:
      logging.info("Signed URL: %s", final_response.url)
    else:
      logging.error("Failed to retrieve download URL after generation.")
      sys.exit(1)

  except RuntimeError as e:
    logging.error(e)
    sys.exit(1)


if __name__ == "__main__":
  app.run(main)
