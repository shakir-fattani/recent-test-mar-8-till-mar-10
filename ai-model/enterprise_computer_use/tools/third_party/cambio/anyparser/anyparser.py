"""AnyParser tool for parsing PDF/Image to text"""

import os
from typing import Any, ClassVar, Literal

from any_parser import AnyParser as AnyParserSDK

from enterprise_computer_use.tools.base import BaseTool, CLIResult, ToolError


class AnyParserTool(BaseTool):
    """
    AnyParser tool for parsing PDF/Image to text in markdown format.

    Available commands:
        - parse: Parse PDF/Image to text in markdown format
    """

    name: ClassVar[Literal["anyparser"]] = "anyparser"

    def __init__(self):
        """Initialize AnyParser tool."""
        self.api_key = os.getenv("CAMBIO_API_KEY")
        if not self.api_key:
            raise ToolError("CAMBIO_API_KEY environment variable not set")
        self.parser = AnyParserSDK(api_key=self.api_key)
        super().__init__()

    async def __call__(
        self, *, command: Literal["parse"], filepath: str, **kwargs
    ) -> CLIResult:
        """
        Execute AnyParser operations for parsing PDF/Image to text in markdown format.
        Args:
            command: The operation to perform (parse)
            filepath: Path to the local file to parse

        Returns:
            CLIResult containing parsed text output or error
        """
        try:
            if command == "parse":
                markdown, _ = self.parser.parse(file_path=filepath)
                return CLIResult(output=f"Parsed content: {markdown}")

        except Exception as e:
            raise ToolError(f"AnyParser operation failed: {str(e)}") from e

    def to_params(self, **kwargs) -> dict[str, Any]:
        """Convert tool to function parameters for LLM."""
        return {
            "name": self.name,
            "description": self.__class__.__doc__,
            "input_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "enum": ["parse"],
                        "description": "The parsing operation to perform",
                    },
                    "filepath": {
                        "type": "string",
                        "description": "Path to the local file to parse",
                    },
                },
                "required": ["command", "filepath"],
            },
        }
