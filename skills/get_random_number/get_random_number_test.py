import unittest

import grpc

from intrinsic.skills.testing import skill_test_utils as stu

from skills.get_random_number import get_random_number
from skills.get_random_number import get_random_number_pb2 as get_rand_num_proto
from services.random_number import random_number_pb2 as rand_num_proto
from services.random_number import random_number_pb2_grpc as rand_num_grpc

class FakeRandomNumberServicer(rand_num_grpc.RandomNumberServiceServicer):
    """Fake Random Number Service that instead of returning random numbers,
       will add the two numbers together and the result will be the sum
       to test the ranges are being sent through and looking at the result.
    """

    def GetRandomNumber(
        self,
        request: rand_num_proto.RandomNumberRequest,
        context: grpc.ServicerContext,
    ) -> rand_num_proto.RandomNumberResponse:
        return rand_num_proto.RandomNumberResponse(result=request.range_start + request.range_end)
    

class GetRandomNumberTest(unittest.TestCase):

    def test_execute(self):
        skill = get_random_number.GetRandomNumber()
        server, handle = stu.make_grpc_server_with_resource_handle("random_number_service")
        rand_num_grpc.add_RandomNumberServiceServicer_to_server(FakeRandomNumberServicer(), server)
        server.start()
        context = stu.make_test_execute_context(
            resource_handles={handle.name: handle},
        )

        params = get_rand_num_proto.GetRandomNumberParams()
        params.range_start = 1
        params.range_end = 2
        request = stu.make_test_execute_request(params)
        result = skill.execute(request, context)
        self.assertEqual(result.result, 3)

        params.range_start = 3
        params.range_end = 5
        request = stu.make_test_execute_request(params)
        result = skill.execute(request, context)
        self.assertEqual(result.result, 8)

if __name__ == '__main__':
    unittest.main()
