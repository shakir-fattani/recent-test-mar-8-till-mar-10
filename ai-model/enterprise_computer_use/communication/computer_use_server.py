import json
import logging

import grpc

from enterprise_computer_use.communication.serialization import (
    clean_message_string,
    deserialize_dict,
    serialize_dict,
)
from enterprise_computer_use.env.computer_use_env import ComputerUseEnv
from enterprise_computer_use.objects.computer_use_message_pb2 import (
    ComputerUseMessageProto,
)
from enterprise_computer_use.objects.computer_use_pb2_grpc import (
    ComputerUseProtoServicer,
    add_ComputerUseProtoServicer_to_server,
)
from enterprise_computer_use.tools import ToolCollection

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
)


class ComputerUseServer(ComputerUseProtoServicer):
    def __init__(
        self,
        tool_collection: ToolCollection,
    ):
        self.env = ComputerUseEnv(tool_collection=tool_collection)

    async def step(
        self, request: ComputerUseMessageProto, context
    ) -> ComputerUseMessageProto:
        action = deserialize_dict(request.dataMsg.data)
        logger.info(f"Step Request: {action}")

        obs, reward, terminated, truncated, info = await self.env.step(action)

        response = ComputerUseMessageProto()
        response.header.status = 200
        response.dataMsg.data = serialize_dict(
            {
                "obs": obs,
                "reward": reward,
                "terminated": terminated,
                "truncated": truncated,
                "info": info,
            }
        )
        return response

    async def reset(
        self, request: ComputerUseMessageProto, context
    ) -> ComputerUseMessageProto:
        options = None
        response = ComputerUseMessageProto()

        try:
            if request.HasField("dataMsg"):
                data = request.dataMsg.data.decode()
                data = clean_message_string(data)
                options = json.loads(data)

            obs, info = self.env.reset(options=options)

            response.header.status = 200
            response.dataMsg.data = serialize_dict(obs)

        except (SyntaxError, ValueError) as e:
            logger.error(f"Failed to parse reset options: {e}")
            response.header.status = 400
            response.dataMsg.data = serialize_dict(
                {"error": f"Invalid reset options: {str(e)}"}
            )
        except Exception as e:
            logger.error(f"Error during reset: {e}")
            response.header.status = 500
            response.dataMsg.data = serialize_dict(
                {"error": "Internal server error"}
            )

        return response


async def serve(
    tool_collection: ToolCollection,
    port: int = 50051,
):
    server = grpc.aio.server()
    servicer = ComputerUseServer(tool_collection)
    add_ComputerUseProtoServicer_to_server(servicer, server)
    server.add_insecure_port(f"[::]:{port}")
    await server.start()
    await server.wait_for_termination()
