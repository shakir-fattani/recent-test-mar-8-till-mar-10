import logging
from typing import Any, cast

import gymnasium as gym
from anthropic.types.beta import BetaImageBlockParam, BetaTextBlockParam

from enterprise_computer_use.tools import ToolCollection, ToolResult

logger = logging.getLogger(__name__)


class ComputerUseEnv(gym.Env):
    """Gym environment for computer use tasks with tool interaction."""

    metadata = {"render_modes": ["human"]}

    def __init__(
        self,
        tool_collection: ToolCollection,
        max_steps: int = 50,
    ):
        super().__init__()
        self.tool_collection = tool_collection
        self.max_steps = max_steps
        self.tool_results = []  # Initialize tool results storage
        self.step_count = 0

        # Define action/observation spaces
        self.action_space = gym.spaces.Dict(
            {
                "tool_calls": gym.spaces.Sequence(
                    gym.spaces.Dict(
                        {
                            "name": gym.spaces.Text(max_length=50),
                            "input": gym.spaces.Dict(
                                {}
                            ),  # Adjust based on actual tool inputs
                        }
                    )
                )
            }
        )

        self.observation_space = gym.spaces.Dict(
            {
                "step_count": gym.spaces.Discrete(self.max_steps),
                "tool_results": gym.spaces.Sequence(
                    gym.spaces.Dict(
                        {
                            "type": gym.spaces.Text(max_length=20),
                            "content": gym.spaces.Sequence(
                                gym.spaces.Text(max_length=5000)
                            ),
                            "tool_use_id": gym.spaces.Text(max_length=50),
                            "is_error": gym.spaces.Discrete(2),
                        }
                    )
                ),
            }
        )

        # Reset the environment and loop will reset it again
        self.reset()

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[dict, dict]:
        super().reset(seed=seed)
        self.tool_results = []  # Reset tool results on new episode

        self.step_count = 0

        return self._get_obs(), self._get_info()

    async def step(self, action: dict) -> tuple[dict, float, bool, bool, dict]:  # type: ignore
        """Execute tool calls and return new observation

        This override the gym with async method.
        """

        tool_calls = action.get("tool_calls", [])
        tool_outputs: list[dict[str, Any]] = []

        # Computer use environment executes tool calls
        for content_block in tool_calls:
            if content_block["type"] == "tool_use":
                result = await self.tool_collection.run(
                    name=content_block["name"],
                    tool_input=cast(dict[str, Any], content_block["input"]),
                )
                tool_outputs.append(
                    self._make_api_tool_result(result, content_block["id"])
                )

        self.tool_results = tool_outputs  # Update current tool results
        self.step_count += 1

        # Append tool results to messages
        terminated = True
        if tool_outputs:
            terminated = False

        truncated = self.step_count >= self.max_steps

        return (
            self._get_obs(),
            0.0,
            terminated,
            truncated,
            self._get_info(),  # Return standardized info format
        )

    def _get_obs(self) -> dict[str, Any]:
        return {
            "step_count": self.step_count,
            "tool_results": self.tool_results,
        }

    def _get_info(self) -> dict:
        """Return current environment state metadata"""
        return {
            "available_tools": list(self.tool_collection.tool_map.keys()),
        }

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
        """Convert an agent ToolResult to an API ToolResultBlockParam."""
        tool_result_content: (
            list[BetaTextBlockParam | BetaImageBlockParam] | str
        ) = []
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
    ):
        if result.system:
            result_text = f"<system>{result.system}</system>\n{result_text}"
        return result_text
