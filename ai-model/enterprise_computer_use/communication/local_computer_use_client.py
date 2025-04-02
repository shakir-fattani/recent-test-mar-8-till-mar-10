import logging
from typing import Any, Callable, Optional

from enterprise_computer_use.tools import ToolCollection, ToolResult
from enterprise_computer_use.tools.claude import (
    BashTool,
    EditTool,
    GUIComputerTool,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
)


class LocalComputerUseClient:
    def __init__(
        self,
        output_callback: Callable[[dict[str, Any]], None],
        tool_output_callback: Callable[[ToolResult, str], None],
        address: str = "localhost",
    ):
        self.output_callback = output_callback
        self.tool_output_callback = tool_output_callback
        self.messages = []

        # Initialize tools directly
        self.tool_collection = ToolCollection(
            GUIComputerTool(),
            BashTool(),
            EditTool(),
        )

    async def step(
        self, action: dict[str, Any]
    ) -> tuple[dict, float, bool, bool, dict]:
        # 1. Process incoming action and tool calls
        tool_calls = action.get("tool_calls", [])
        self.messages.append(self._format_message("assistant", tool_calls))

        # Process each tool call through the output callback
        for content_block in tool_calls:
            self.output_callback(content_block)

        # 2. Execute tools directly and collect results
        tool_results = []
        for tool_call in tool_calls:
            if tool_call["type"] == "tool_use":
                result = await self.tool_collection.run(
                    name=tool_call["name"],
                    tool_input=tool_call["input"],
                )
                tool_results.append(
                    self._make_api_tool_result(result, tool_call["id"])
                )

                # Call tool output callback
                self.tool_output_callback(result, tool_call["id"])

        # 3. Prepare observation
        obs = {"messages": self.messages}
        if tool_results:
            self.messages.append({"content": tool_results, "role": "user"})
            terminated = False
        else:
            terminated = True

        # 4. Return step results
        return (
            obs,  # observation
            0.0,  # reward (not used in this implementation)
            terminated,  # terminated
            False,  # truncated
            {},  # info
        )

    async def reset(self, options: Optional[dict] = None) -> tuple[dict, dict]:
        if options:
            self.messages = options.get("initial_messages", [])
        else:
            self.messages = []

        return {"messages": self.messages}, {}

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

    def _make_api_tool_result(
        self, result: ToolResult, tool_use_id: str
    ) -> dict[str, Any]:
        """Convert a ToolResult to API format.

        Args:
            result: Tool execution result
            tool_use_id: ID of the tool use request

        Returns:
            Formatted tool result
        """
        tool_result_content = []
        is_error = False

        if result.error:
            is_error = True
            tool_result_content = self._maybe_prepend_system_tool_result(
                result, result.error
            )
        else:
            if result.output:
                tool_result_content.append(
                    {
                        "type": "text",
                        "text": self._maybe_prepend_system_tool_result(
                            result, result.output
                        ),
                    }
                )
            if result.base64_image:
                tool_result_content.append(
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": result.base64_image,
                        },
                    }
                )

        return {
            "type": "tool_result",
            "content": tool_result_content,
            "tool_use_id": tool_use_id,
            "is_error": is_error,
        }

    def _maybe_prepend_system_tool_result(
        self, result: ToolResult, result_text: str
    ) -> str:
        """Add system message to tool result if present.

        Args:
            result: Tool execution result
            result_text: Text output from tool

        Returns:
            Text with optional system message prepended
        """
        if result.system:
            return f"<system>{result.system}</system>\n{result_text}"
        return result_text

    async def close(self):
        """Cleanup method (kept for API compatibility)"""
