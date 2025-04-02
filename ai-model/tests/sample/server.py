import os
import sys
from concurrent import futures

import grpc

sys.path.append(
    os.path.join((os.path.dirname(os.path.abspath(__file__))), "..", "..")
)

import enterprise_computer_use.objects.computer_use_message_pb2 as computer_use_message_pb2
import enterprise_computer_use.objects.computer_use_pb2_grpc as computer_use_pb2_grpc


class ComputerUseServer(computer_use_pb2_grpc.ComputerUseProtoServicer):
    def step(self, request, context):
        # Simple implementation - just echo back the request
        response = computer_use_message_pb2.ComputerUseMessageProto()
        response.header.status = 200
        response.header.message = "Step executed successfully"
        return response

    def reset(self, request, context):
        response = computer_use_message_pb2.ComputerUseMessageProto()
        response.header.status = 200
        response.header.message = "Environment reset"
        return response


def serve():
    # Increase max message size to 10MB (10 * 1024 * 1024 bytes)
    options = [
        ("grpc.max_receive_message_length", 10 * 1024 * 1024),
        ("grpc.max_send_message_length", 10 * 1024 * 1024),
    ]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), options=options
    )
    computer_use_pb2_grpc.add_ComputerUseProtoServicer_to_server(
        ComputerUseServer(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
