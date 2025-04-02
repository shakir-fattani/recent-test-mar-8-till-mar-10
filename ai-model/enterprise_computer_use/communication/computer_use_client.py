import logging
from typing import Any, Callable, Optional

import grpc

from enterprise_computer_use.communication.serialization import (
    deserialize_dict,
    serialize_dict,
)
from enterprise_computer_use.objects.computer_use_message_pb2 import (
    ComputerUseMessageProto,
)
from enterprise_computer_use.objects.computer_use_pb2_grpc import (
    ComputerUseProtoStub,
)
from enterprise_computer_use.tools import ToolResult

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
)


class ComputerUseClient:
    def __init__(
        self,
        output_callback: Callable[[dict[str, Any]], None],
        tool_output_callback: Callable[[ToolResult, str], None],
        address: str = "localhost",
        port: int = 50051,
    ):
        logger.info(f"Connecting to grpc server at {address}:{port}")
        # Increase max message size to 10MB (10 * 1024 * 1024 bytes)
        options = [
            ("grpc.max_receive_message_length", 10 * 1024 * 1024),
            ("grpc.max_send_message_length", 10 * 1024 * 1024),
        ]
        self.channel = grpc.aio.insecure_channel(
            f"{address}:{port}", options=options
        )
        self.stub = ComputerUseProtoStub(self.channel)
        self.output_callback = output_callback
        self.tool_output_callback = tool_output_callback
        self.messages = []  # Add message storage

    async def step(
        self, action: dict[str, Any]
    ) -> tuple[dict, float, bool, bool, dict]:
        # 1. Process incoming action and tool calls
        tool_calls = action.get("tool_calls", [])
        self.messages.append(self._format_message("assistant", tool_calls))

        # Process each tool call through the output callback
        for content_block in tool_calls:
            self.output_callback(content_block)

        # 2. Make RPC call to server
        request = ComputerUseMessageProto()
        request.dataMsg.data = serialize_dict(action)
        response = await self.stub.step(request)
        response_dict = deserialize_dict(response.dataMsg.data)

        # 3. Process server response and tool results
        tool_results = response_dict["obs"].get("tool_results", [])

        # Handle individual tool results
        for tool_result in tool_results:
            if tool_result["content"]:  # Check if content list is not empty
                self.tool_output_callback(
                    tool_result["content"][0], tool_result["tool_use_id"]
                )

        # If we have tool results, add them to conversation and continue
        if tool_results:
            self.messages.append({"content": tool_results, "role": "user"})
            response_dict["terminated"] = False

        # 4. Prepare final observation
        response_dict["obs"]["messages"] = self.messages

        # 5. Return step results
        return (
            response_dict["obs"],
            response_dict["reward"],
            response_dict["terminated"],
            response_dict["truncated"],
            response_dict["info"],
        )

    async def reset(self, options: Optional[dict] = None) -> tuple[dict, dict]:
        request = ComputerUseMessageProto()
        if options:
            request.dataMsg.data = serialize_dict(options)
            self.messages = options.get("initial_messages", [])

        response = await self.stub.reset(request)
        raw_obs = deserialize_dict(response.dataMsg.data)

        raw_obs["messages"] = self.messages
        return raw_obs, {}

    def _format_message(self, role: str, content: Any) -> dict[str, Any]:
        """Format message for Claude.

        Args:
            role: Message role (user/assistant)
            content: Message content

        Returns:
            Formatted message for Claude
        """
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        return {"role": role, "content": content}

    async def close(self):
        await self.channel.close()
