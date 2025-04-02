"""Gemini agent implementation."""

from collections.abc import Callable
from typing import Any, Optional

from enterprise_computer_use.agent.abs_agent import AbsAgent
from enterprise_computer_use.tools import ToolCollection, ToolResult


class GeminiAgent(AbsAgent):
    """Gemini agent implementation."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize the Gemini agent.

        Args:
            api_key: Google API key
            **kwargs: Additional initialization parameters
        """
        super().__init__()
        raise NotImplementedError("Gemini agent not yet implemented")

    async def generate(
        self,
        max_tokens: int,
        messages: list[dict[str, Any]],
        model: str,
        system_prompt: str,
        tool_collection: ToolCollection,
        api_response_callback: Callable[[Any, Any, Optional[Exception]], None],
        output_callback: Callable[[dict[str, Any]], None],  # type: ignore
        tool_output_callback: Callable[[ToolResult, str], None],
        **kwargs,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Generate a response using Gemini.

        Args:
            max_tokens: Maximum tokens to generate
            messages: Conversation history
            tools: Available tools
            system_prompt: System prompt
            **kwargs: Additional parameters for Gemini API

        Returns:
            Gemini API response as dictionary
        """
        raise NotImplementedError("Gemini agent not yet implemented")
