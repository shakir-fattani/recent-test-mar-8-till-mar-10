"""Collection classes for managing multiple tools."""

from typing import Any

from .base import BaseTool, ToolError, ToolFailure, ToolResult


class ToolCollection:
    """A collection of tools."""

    def __init__(self, *tools: BaseTool):
        """Initialize the tool collection.

        Args:
            *tools: Tools to include in the collection
        """
        self.tools = tools
        self.tool_map = {tool.name: tool for tool in tools}

    def to_params(self, **kwargs) -> list[dict[str, Any]]:
        """Convert tools to parameters for model consumption.

        Returns:
            list of tool parameter dictionaries
        """
        model = kwargs.get("model")
        return [tool.to_params(model=model) for tool in self.tools]

    async def run(self, *, name: str, tool_input: dict[str, Any]) -> ToolResult:
        """Run a tool by name with the given input.

        Args:
            name: Name of the tool to run
            tool_input: Input parameters for the tool

        Returns:
            Tool execution result

        Raises:
            ToolError: If the tool is not found or fails to execute
        """
        tool = self.tool_map.get(name)
        if not tool:
            return ToolFailure(error=f"Tool {name} is invalid")
        try:
            return await tool(**tool_input)
        except ToolError as e:
            return ToolFailure(error=e.message)
