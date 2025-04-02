import logging
import os
import sys

import grpc

sys.path.append(
    os.path.join((os.path.dirname(os.path.abspath(__file__))), "..", "..")
)

import enterprise_computer_use.objects.computer_use_message_pb2 as computer_use_message_pb2
import enterprise_computer_use.objects.computer_use_pb2_grpc as computer_use_pb2_grpc

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
)


def run_client():
    # Create channel and stub
    channel = grpc.insecure_channel("localhost:50051")
    stub = computer_use_pb2_grpc.ComputerUseProtoStub(channel)

    # Create a simple request
    request = computer_use_message_pb2.ComputerUseMessageProto()
    request.header.status = 0
    request.header.message = "Test request"

    try:
        # Test step method
        logger.info("Calling step method...")
        response = stub.step(request)
        logger.info(f"Step response: {response.header.message}")

        # Test reset method
        logger.info("\nCalling reset method...")
        response = stub.reset(request)
        logger.info(f"Reset response: {response.header.message}")

    except grpc.RpcError as e:
        logger.error(f"RPC failed: {e}")


if __name__ == "__main__":
    run_client()
