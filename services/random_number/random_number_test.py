import unittest
import portpicker

import grpc
from grpc.framework.foundation import logging_pool

from services.random_number import random_number
from services.random_number import random_number_pb2 as rand_num_proto
from services.random_number import random_number_pb2_grpc as random_num_grpc


class RandomNumberTest(unittest.TestCase):
  """Tests the Random Number Service.
  The first two requests should succeed and the 3rd request should fail.
  """

  def test_get_random_number(self):
    stub = self._make_test_stub()

    # first request
    request = rand_num_proto.RandomNumberRequest(
        range_start=2,
        range_end=15,
    )
    response = stub.GetRandomNumber(request)
    self.assertTrue(request.range_start <= response.result <= request.range_end)

    # second request
    request.range_start = 4
    request.range_end = 8
    response = stub.GetRandomNumber(request)
    self.assertTrue(request.range_start <= response.result <= request.range_end)

    # third request should fail
    with self.assertRaises(grpc.RpcError):
      response = stub.GetRandomNumber(request)

  def _make_test_stub(self):
    port = portpicker.pick_unused_port()
    server_pool = logging_pool.pool(max_workers=1)
    server = grpc.server(server_pool)
    server.add_insecure_port(f"[::]:{port}")
    server.start()

    servicer = random_number.RandomNumberServicer()

    random_num_grpc.add_RandomNumberServiceServicer_to_server(servicer, server)

    channel = grpc.secure_channel(
        f"localhost:{port}", grpc.local_channel_credentials()
    )
    stub = random_num_grpc.RandomNumberServiceStub(channel)

    def teardown():
      channel.close()
      server.stop(None)

    self.addCleanup(teardown)

    return stub


if __name__ == "__main__":
  unittest.main()
