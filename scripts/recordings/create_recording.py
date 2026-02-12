import datetime
import time

from absl import app
from absl import flags
from absl import logging
from google.protobuf import empty_pb2
from google.protobuf import timestamp_pb2
from intrinsic.logging.proto import bag_metadata_pb2
from intrinsic.logging.proto import logger_service_pb2
from intrinsic.logging.proto import logger_service_pb2_grpc
from intrinsic.solutions import deployments

BagStatusEnum = bag_metadata_pb2.BagStatus.BagStatusEnum

# How often to poll for recording status updates.
POLLING_INTERVAL_SECONDS = 10

FLAGS = flags.FLAGS
flags.DEFINE_string(
    "org",
    None,
    "The organization ID, with project suffix, e.g. org@project.",
    required=True,
)
flags.DEFINE_string(
    "cluster",
    None,
    "The cluster name or solution ID.",
    required=True,
)


def check_recordings_supported(
    stub: logger_service_pb2_grpc.DataLoggerStub,
) -> None:
  """Checks if recordings are supported on the target cluster."""
  try:
    if not stub.RecordingsSupported(empty_pb2.Empty()):
      raise RuntimeError("Recordings not supported on this cluster.")
  except Exception as e:
    raise RuntimeError(
        f"Error checking if recordings are supported: {e}"
    ) from e


def create_recording(
    stub: logger_service_pb2_grpc.DataLoggerStub,
    start_time: datetime.datetime | None = None,
    end_time: datetime.datetime | None = None,
    description: str = "",
    event_sources: list[str] | None = None,
) -> logger_service_pb2.CreateLocalRecordingResponse:
  """
  Creates a recording.

  Constraints:
    - Recording duration cannot exceed 10 minutes.
    - Recording start time cannot be more than 24 hours in the past, as logs are
      only retained for 24 hours.

  Args:
      stub: The DataLoggerStub instance.
      start_time: The start time of the recording. Defaults to 1 minute ago.
      end_time: The end time of the recording. Defaults to now.
      description: A description for the recording. Defaults to an empty string.
      event_sources: A list of event source regex patterns to record. Defaults
        to [".*"].

  Returns:
      A CreateLocalRecordingResponse protobuf message.
  """
  if start_time is None:
    start_time = datetime.datetime.now() - datetime.timedelta(minutes=1)
  if end_time is None:
    end_time = datetime.datetime.now()

  if (end_time - start_time) > datetime.timedelta(minutes=10):
    raise ValueError("Recording duration cannot exceed 10 minutes.")
  if start_time < datetime.datetime.now() - datetime.timedelta(hours=24):
    raise ValueError(
        "Recording start time cannot be more than 24 hours in the past"
    )

  if event_sources is None:
    event_sources = [".*"]

  start_time_pb = timestamp_pb2.Timestamp()
  start_time_pb.FromDatetime(start_time)

  end_time_pb = timestamp_pb2.Timestamp()
  end_time_pb.FromDatetime(end_time)

  return stub.CreateLocalRecording(
      logger_service_pb2.CreateLocalRecordingRequest(
          start_time=start_time_pb,
          end_time=end_time_pb,
          description=description,
          event_sources_to_record=list(event_sources),
      )
  )


def wait_for_recording_to_upload(
    stub: logger_service_pb2_grpc.DataLoggerStub,
    recording_id: str,
    timeout: datetime.timedelta = datetime.timedelta(minutes=5),
) -> None:
  """Periodically polls the status of a recording until it is fully uploaded."""
  upload_start_time = None  # Will be set when upload starts

  while True:
    # Check for timeout only after the upload has started
    if upload_start_time and (
        datetime.datetime.now() - upload_start_time > timeout
    ):
      logging.error(
          "Timed out waiting for recording `%s` to upload.", recording_id
      )
      return

    try:
      list_resp = stub.ListLocalRecordings(
          logger_service_pb2.ListLocalRecordingsRequest(bag_ids=[recording_id])
      )
    except Exception as e:
      logging.error("Error polling recording status: %s", e)
      time.sleep(POLLING_INTERVAL_SECONDS)
      continue

    if not list_resp.bags:
      logging.error("Recording `%s` not found.", recording_id)
      return

    recording = list_resp.bags[0]
    status = recording.status.status

    # Start the timer when the status is no longer UPLOAD_PENDING
    if upload_start_time is None and status != BagStatusEnum.UPLOAD_PENDING:
      upload_start_time = datetime.datetime.now()

    if log_recording_upload_status(recording):
      return

    time.sleep(POLLING_INTERVAL_SECONDS)


def log_recording_upload_status(
    recording: bag_metadata_pb2.BagMetadata,
) -> bool:
  """Logs the current upload status of a recording."""

  recording_id = recording.bag_id
  status = recording.status.status
  status_str = BagStatusEnum.Name(status)
  log_prefix = (
      f"Waiting for recording `{recording_id}` to be uploaded by cluster:"
  )

  match status:
    case BagStatusEnum.UPLOAD_PENDING:
      logging.info("%s [%s]", log_prefix, status_str)
    case BagStatusEnum.UPLOADING:
      if recording.total_bytes > 0:
        percentage = (
            recording.total_uploaded_bytes / recording.total_bytes
        ) * 100
        logging.info("%s [%s - %.2f%%]", log_prefix, status_str, percentage)
      else:
        logging.info("%s [%s - calculating size...]", log_prefix, status_str)
    case BagStatusEnum.UPLOADED | BagStatusEnum.COMPLETED:
      logging.info(
          "[COMPLETE] Recording `%s` successfully uploaded.", recording_id
      )
      return True
    case BagStatusEnum.UNCOMPLETABLE | BagStatusEnum.FAILED:
      logging.error(
          "Recording `%s` failed to upload with status: %s. Reason: %s",
          recording_id,
          status_str,
          recording.status.reason,
      )
      return True
    case _:
      logging.info("%s [%s]", log_prefix, status_str)
  return False


def main(argv):
  """Creates a recording and polls for its status."""
  del argv  # Unused.
  solution = deployments.connect(
      org=FLAGS.org,
      # Use cluster name or solution_id
      # solution=solution_id,
      cluster=FLAGS.cluster,
  )
  channel = solution.grpc_channel
  logger_stub = logger_service_pb2_grpc.DataLoggerStub(channel)

  check_recordings_supported(logger_stub)

  now = datetime.datetime.now()
  start_time = now - datetime.timedelta(minutes=1)
  end_time = now

  resp: logger_service_pb2.CreateLocalRecordingResponse = create_recording(
      logger_stub,
      start_time,
      end_time,
      f"Example recording {start_time} to {end_time}",
  )

  if resp.bag and resp.bag.bag_id:
    logging.info("Successfully created recording with ID: %s", resp.bag.bag_id)
    wait_for_recording_to_upload(logger_stub, resp.bag.bag_id)
  else:
    logging.error("No bag created.")


if __name__ == "__main__":
  app.run(main)
