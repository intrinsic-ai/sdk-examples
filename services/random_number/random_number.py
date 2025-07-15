#!/usr/bin/env python3
import datetime
import logging
import random

import grpc
from google.protobuf import timestamp_pb2 as timestamp_proto

from intrinsic.assets.services.proto.v1 import service_state_pb2 as state_proto
from intrinsic.assets.services.proto.v1 import service_state_pb2_grpc as state_grpc
from intrinsic.util.grpc import error_handling
from intrinsic.util.status import extended_status_pb2 as ext_status_proto

from services.random_number import random_number_pb2 as random_num_proto
from services.random_number import random_number_pb2_grpc as random_num_grpc

logger = logging.getLogger(__name__)

NUM_REQUESTS_BEFORE_ERROR = 2


class RandomNumberServicer(
    random_num_grpc.RandomNumberServiceServicer, state_grpc.ServiceStateServicer
):
  """Random Number Generator Intrinsic Service to demonstrate the use and implementation of the ServiceState.
  The Service takes a start and end range of numbers and returns a randomly selected number.
  After two requests, the Service sets itself to an error state to demonstrate errors in the
  Service manager and that we expect the user to use the dialog to re-enable the Service.
  """

  def __init__(self):
    self._state = state_proto.SelfState(
        state_code=state_proto.SelfState.STATE_CODE_ENABLED,
    )

    self._curr_num_requests = 0

  def GetRandomNumber(
      self,
      request: random_num_proto.RandomNumberRequest,
      context: grpc.ServicerContext,
  ) -> random_num_proto.RandomNumberResponse:

    if self._curr_num_requests == NUM_REQUESTS_BEFORE_ERROR:
      # This is to force an error for our example.
      timestamp = timestamp_proto.Timestamp()
      timestamp.FromDatetime(datetime.datetime.now())
      self._state = state_proto.SelfState(
          state_code=state_proto.SelfState.STATE_CODE_ERROR,
          extended_status=ext_status_proto.ExtendedStatus(
              title="An error occurred.",
              user_report=ext_status_proto.ExtendedStatus.UserReport(
                  message=(
                      "We've reached the maximum number of requests. Toggle"
                      " enable to reset the number of requests."
                  )
              ),
              timestamp=timestamp,
          ),
      )

    if self._state.state_code is state_proto.SelfState.STATE_CODE_DISABLED:
      status = error_handling.make_grpc_status(
          code=grpc.StatusCode.FAILED_PRECONDITION,
          message=(
              "Cannot make calls to a disabled Service; use the Service manager"
              " to enable the Service."
          ),
          details=[],
      )
      logging.error(
          f"Cannot make calls to a disabled Service; use the Service manager to"
          f" enable the Service."
      )
      context.abort_with_status(status)
    elif self._state.state_code is state_proto.SelfState.STATE_CODE_ERROR:
      status = error_handling.make_grpc_status(
          code=grpc.StatusCode.FAILED_PRECONDITION,
          message=(
              "Cannot make calls to a Service in an error state; use the"
              " Service manager to acknowledge and reset the Service."
          ),
          details=[],
      )
      logging.error(
          f"Cannot make calls to a Service in an error state; use the Service"
          f" manager to acknowledge and reset the Service."
      )
      context.abort_with_status(status)

    self._curr_num_requests += 1

    result = random.randint(request.range_start, request.range_end)

    logging.info(f"current number of requests: {self._curr_num_requests}")
    logging.info(
        f"result: {result}; from range: ({request.range_start},"
        f" {request.range_end})"
    )

    return random_num_proto.RandomNumberResponse(result=result)

  # ServiceState implementation
  def GetState(
      self,
      request: state_proto.GetStateRequest,
      context: grpc.ServicerContext,
  ) -> state_proto.SelfState:
    return self._state

  def Enable(
      self,
      request: state_proto.EnableRequest,
      context: grpc.ServicerContext,
  ) -> state_proto.EnableResponse:
    if self._state.state_code == state_proto.SelfState.STATE_CODE_ERROR:
      logging.info("Error was acknowledged, resetting request count.")
      self._curr_num_requests = 0
    elif self._state.state_code == state_proto.SelfState.STATE_CODE_ENABLED:
      # Already enabled, do nothing.
      return state_proto.EnableResponse()

    self._state = state_proto.SelfState(
        state_code=state_proto.SelfState.STATE_CODE_ENABLED,
    )

    return state_proto.EnableResponse()

  def Disable(
      self,
      request: state_proto.DisableRequest,
      context: grpc.ServicerContext,
  ) -> state_proto.DisableResponse:
    if self._state.state_code == state_proto.SelfState.STATE_CODE_ERROR:
      raise grpc.RpcError(
          grpc.StatusCode.FailedPrecondition,
          "Cannot disable Service in error state.",
      )
    elif self._state.state_code == state_proto.SelfState.STATE_CODE_DISABLED:
      return state_proto.DisableResponse()

    self._state = state_proto.SelfState(
        state_code=state_proto.SelfState.STATE_CODE_DISABLED
    )

    return state_proto.DisableResponse()
