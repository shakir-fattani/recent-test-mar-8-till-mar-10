"""OpenAI agent implementation."""

import json
import logging
from typing import Any, Optional, cast

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam

from enterprise_computer_use.agent.abs_agent import AbsAgent
from enterprise_computer_use.constants import APIProvider

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
)


# TODO: Mocking a request and response is a hack.
# We should use httpx to make the request and response.
class MockRequest:
    """Mock httpx.Request for OpenAI API calls."""

    def __init__(self, method: str, url: str, headers: dict, content: str):
        self.method = method
        self.url = url
        self.headers = headers
        self.content = content

    def read(self) -> bytes:
        """Return content as bytes for compatibility with httpx.Request."""
        return self.content.encode("utf-8")


class MockResponse:
    """Mock httpx.Response for OpenAI API calls."""

    def __init__(self, status_code: int, headers: dict, content: Any):
        self.status_code = status_code
        self.headers = headers
        self.content = content


class OpenAIAgent(AbsAgent):
    """OpenAI agent implementation."""

    PROVIDER = APIProvider.OPENAI
    ENABLE_PROMPT_CACHING = True

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize the OpenAI agent.

        Args:
            api_key: OpenAI API key
            **kwargs: Additional initialization parameters
        """
        super().__init__()
        self.client = OpenAI(api_key=api_key)

    def configure(self, **kwargs):
        self.max_tokens = kwargs.get("max_tokens", 4096)
        if "model" not in kwargs:
            raise ValueError("OpenAI model must be specified")
        self.model = kwargs["model"]
        self.api_response_callback = kwargs.get("api_response_callback")
        self.image_truncation = kwargs.get("image_truncation")
        self.system_prompt = kwargs.get("system_prompt")
        self.tool_collection = kwargs.get("tool_collection")

    def _preprocess(
        self, messages: list[dict[str, Any]], **kwargs
    ) -> list[dict[str, Any]]:
        """Preprocess messages for OpenAI."""
        # Add system prompt as first message if not already present
        formatted_messages = []
        if self.system_prompt:
            formatted_messages.append(
                {"role": "system", "content": self.system_prompt}
            )

        # Add conversation history
        for message in messages:
            formatted_messages.append(
                self._format_message(message["role"], message["content"])
            )
        return formatted_messages

    def _postprocess(
        self,
        messages: list[dict[str, Any]],
        **kwargs,
    ) -> dict[str, Any]:
        """Postprocess messages and handle tool interactions.

        Args:
            messages: Current message history
            **kwargs: Additional arguments including:
                - raw_response: Raw response from the model
                - tool_collection: Collection of available tools
                - output_callback: Callback for model outputs
                - tool_output_callback: Callback for tool outputs

        Returns:
            Tuple of (updated messages, tool result content)
        """
        action_response = kwargs.get("raw_response")
        if not action_response:
            raise ValueError("Missing required arguments")

        # Parse and convert response
        tool_result_content = []
        message = action_response.choices[0].message

        # Handle text content if present
        if message.content:
            tool_result_content.append(
                {"type": "text", "text": message.content}
            )

        # Handle tool calls
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_use = {
                    "type": "tool_use",
                    "id": tool_call.id,
                    "name": tool_call.function.name,
                    "input": json.loads(tool_call.function.arguments),
                }
                tool_result_content.append(tool_use)

        logger.info(f"Tool result content: {tool_result_content}")

        return {"tool_calls": tool_result_content}

    def predict(self, observation: dict) -> dict[str, Any]:
        """Process observation into action using Claude API"""
        messages = self._preprocess(
            observation["messages"],
            only_n_most_recent_images=self.image_truncation,
        )

        try:
            # Step 1: Tool Selection
            formatted_tools = self._format_tool_selection_tools()

            tool_selection_response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                tools=cast(list[ChatCompletionToolParam], formatted_tools),
                messages=cast(list[ChatCompletionMessageParam], messages),
                tool_choice="auto",
            )  # type: ignore

            logger.info(
                f"Tool selection response: {tool_selection_response.choices[0].message}"
            )

            tool_calls = tool_selection_response.choices[0].message.tool_calls
            if not tool_calls:
                raise ValueError("No tool was selected by the model")

            selected_tool_str = tool_calls[0].function.arguments
            selected_tool = json.loads(selected_tool_str)["tool_name"]
            logger.info(f"Selected tool: {selected_tool}")

            if selected_tool != "computer":
                raise ValueError("Only 'computer' tool is supported")

            computer_action_tools = self._format_action_tools(selected_tool)

            # Step 2: Action Execution
            action_request = MockRequest(
                method="POST",
                url="https://api.openai.com/v1/chat/completions",
                headers={"Authorization": "REDACTED"},
                content=str(
                    {
                        "model": self.model,
                        "messages": messages,
                        "tools": computer_action_tools,
                        "max_tokens": self.max_tokens,
                    }
                ),
            )

            action_response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                tools=cast(
                    list[ChatCompletionToolParam], computer_action_tools
                ),
                messages=cast(list[ChatCompletionMessageParam], messages),
                tool_choice="auto",
            )  # type: ignore
            logger.info(
                f"Action response: {action_response.choices[0].message}"
            )
            logger.info(
                f"Action response tool calls: {action_response.choices[0].message.tool_calls}"
            )

            # Create mock response object
            mock_response = MockResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                content=action_response,
            )

            if self.api_response_callback:
                self.api_response_callback(action_request, mock_response, None)

            logger.info("Finished API Response Callback. Starting Postprocess")

            return self._postprocess(
                messages,
                raw_response=action_response,
            )

        except Exception as e:
            # Create mock request for error case
            mock_request = MockRequest(
                method="POST",
                url="https://api.openai.com/v1/chat/completions",
                headers={"Authorization": "REDACTED"},
                content=str({"error": str(e)}),
            )

            mock_response = MockResponse(
                status_code=500,
                headers={"Content-Type": "application/json"},
                content=str(e),
            )
            logger.error(f"Error: {e}")
            if self.api_response_callback:
                self.api_response_callback(mock_request, mock_response, e)
            return self._postprocess(messages, raw_response=mock_response)

    def _format_message(self, role: str, content: Any) -> dict[str, Any]:
        """Format message for OpenAI.

        Args:
            role: Message role (user/assistant)
            content: Message content

        Returns:
            Formatted message for OpenAI
        """
        if isinstance(content, str):
            return {"role": role, "content": content}

        formatted_parts = []
        for item in content:
            if item["type"] == "text":
                formatted_parts.append(
                    {
                        "type": "text",
                        "text": item["text"],
                    }
                )
            elif item["type"] == "tool_result":
                if isinstance(item["content"], str):
                    formatted_parts.append(item["content"])
                else:
                    for content_item in item["content"]:
                        if content_item["type"] == "text":
                            formatted_parts.append(
                                {
                                    "type": "text",
                                    "text": "\n".join(content_item["text"]),
                                }
                            )
                        elif content_item["type"] == "image":
                            formatted_parts.append(
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{content_item['source']['data']}",
                                    },
                                }
                            )
        return {"role": role, "content": formatted_parts}

    def _format_tool_selection_tools(self) -> list[dict[str, Any]]:
        """Format tools for the tool selection step.

        Returns:
            list of tools in OpenAI format for tool selection
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "tool_selector",
                    "description": "Select a tool to use based on the user's request. Do not give rhetorical questions back, and only give the tool name.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tool_name": {
                                "type": "string",
                                "enum": [
                                    "computer",
                                    "bash",
                                    "str_replace_editor",
                                ],
                                "description": "The tool to use for the task",
                            },
                        },
                        "required": ["tool_name"],
                        "additionalProperties": False,
                    },
                    "examples": [
                        "Select 'computer' for GUI interactions like clicking, typing, or screenshots",
                        "Select 'bash' for terminal commands and file operations",
                        "Select 'str_replace_editor' for text editing tasks",
                    ],
                    "strict": True,
                },
            }
        ]

    def _format_action_tools(self, selected_tool: str) -> list[dict[str, Any]]:
        """Format detailed action parameters for the selected tool.

        Args:
            selected_tool: The name of the selected tool

        Returns:
            list containing the detailed tool specification in OpenAI format
        """
        tool_specifications = {
            "computer": {
                "name": "computer",
                "description": "Control computer actions like clicking, typing, scrolling, and taking screenshots. If you have no specific knowledge about current screen, take a screenshot first. If you need to provide coordinates, make sure it is an accurate coordinate, and in the format [x, y].",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": [
                                "screenshot",
                                "mouse_move",
                                "left_click",
                                "right_click",
                                "type",
                                "key",
                                "scroll",
                            ],
                            "description": "The action to perform on the computer",
                        },
                        "coordinate": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "X,Y coordinates for mouse actions [x, y]",
                        },
                        "text": {
                            "type": "string",
                            "description": "Text to type or key to press",
                        },
                        "scroll_amount": {
                            "type": "number",
                            "description": "Amount to scroll (positive for down, negative for up)",
                        },
                    },
                    "required": ["action"],
                    "dependencies": {
                        "mouse_move": ["coordinate"],
                        "left_click": ["coordinate"],
                        "right_click": ["coordinate"],
                        "type": ["text"],
                        "key": ["text"],
                        "scroll": ["scroll_amount"],
                    },
                    "additionalProperties": False,
                },
            },
            "bash": {
                "name": "bash",
                "description": "Execute bash commands in the terminal. Returns command output or error messages.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The bash command to execute",
                        }
                    },
                    "required": ["command"],
                },
            },
            "str_replace_editor": {
                "name": "str_replace_editor",
                "description": "Edit text content using string replacement. Useful for modifying files or text content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "old_text": {
                            "type": "string",
                            "description": "Text to be replaced",
                        },
                        "new_text": {
                            "type": "string",
                            "description": "Replacement text",
                        },
                    },
                    "required": ["old_text", "new_text"],
                },
            },
        }

        tool_spec = tool_specifications.get(selected_tool)
        if not tool_spec:
            raise ValueError(f"Unknown tool: {selected_tool}")

        return [
            {
                "type": "function",
                "function": {
                    "name": tool_spec["name"],
                    "description": tool_spec["description"],
                    "parameters": tool_spec["parameters"],
                    "strict": False,
                },
            }
        ]
