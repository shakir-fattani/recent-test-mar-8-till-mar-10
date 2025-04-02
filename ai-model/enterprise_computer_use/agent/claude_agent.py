"""Claude agent implementation."""

from typing import Any, Optional, cast

from anthropic import (
    Anthropic,
    AnthropicBedrock,
    AnthropicVertex,
    APIError,
    APIResponseValidationError,
    APIStatusError,
)
from anthropic.types.beta import (
    BetaTextBlock,
    BetaTextBlockParam,
    BetaToolUseBlockParam,
)

from enterprise_computer_use.agent.abs_agent import AbsAgent
from enterprise_computer_use.constants import APIProvider

COMPUTER_USE_BETA_FLAG = "computer-use-2024-10-22"
PROMPT_CACHING_BETA_FLAG = "prompt-caching-2024-07-31"


class ClaudeAgent(AbsAgent):
    """Claude agent implementation."""

    PROVIDER = APIProvider.ANTHROPIC
    ENABLE_PROMPT_CACHING = True

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize the Claude agent.

        Args:
            api_key: Anthropic API key
            **kwargs: Additional initialization parameters
        """
        super().__init__()
        self.client = Anthropic(api_key=api_key)

    def configure(self, **kwargs):
        self.max_tokens = kwargs.get("max_tokens", 4096)
        self.model = kwargs.get("model")
        self.api_response_callback = kwargs.get("api_response_callback")
        self.image_truncation = kwargs.get("image_truncation")
        self.system_prompt = kwargs.get("system_prompt")
        self.tool_collection = kwargs.get("tool_collection")

    def predict(self, observation: dict) -> dict[str, Any]:
        """Process observation into action using Claude API"""
        messages = self._preprocess(
            observation["messages"],
            only_n_most_recent_images=self.image_truncation,
        )

        try:
            raw_response = self.client.beta.messages.with_raw_response.create(
                max_tokens=self.max_tokens,
                messages=messages,  # type: ignore
                model=self.model,  # type: ignore
                system=self._get_system_block(self.system_prompt),  # type: ignore
                tools=self.tool_collection.to_params(model="claude"),  # type: ignore
                betas=self._get_beta_flags(),
            )
        except (APIStatusError, APIResponseValidationError) as e:
            self.api_response_callback(e.request, e.response, e)  # type: ignore
            return {}  # add tool_result_content
        except APIError as e:
            self.api_response_callback(e.request, e.body, e)  # type: ignore
            return {}  # add tool_result_content

        self.api_response_callback(  # type: ignore
            raw_response.http_response.request, raw_response.http_response, None
        )

        return self._postprocess(
            messages=messages, response=raw_response.parse()
        )

    def _postprocess(
        self, messages: list[dict[str, Any]], **kwargs
    ) -> dict[str, Any]:
        """Postprocess the response."""
        response = kwargs.get("response")
        tool_calls: list[dict[str, Any]] = []
        for block in response.content:  # type: ignore
            if isinstance(block, BetaTextBlock):
                tool_calls.append({"type": "text", "text": block.text})
            else:
                tool_calls.append(
                    cast(BetaToolUseBlockParam, block.model_dump())  # type: ignore
                )

        return {"tool_calls": tool_calls}

    def _preprocess(
        self, messages: list[dict[str, Any]], **kwargs
    ) -> list[dict[str, Any]]:
        """Preprocess the messages."""
        only_n_most_recent_images = kwargs.get(
            "only_n_most_recent_images", None
        )
        image_truncation_threshold = only_n_most_recent_images or 0

        if self.ENABLE_PROMPT_CACHING:
            self._inject_prompt_caching(messages)
            # Because cached reads are 10% of the price, we don't think it's
            # ever sensible to break the cache by truncating images
            only_n_most_recent_images = 0

        if only_n_most_recent_images:
            self._maybe_filter_to_n_most_recent_images(
                messages,
                only_n_most_recent_images,
                min_removal_threshold=image_truncation_threshold,
            )

        return messages

    def _get_system_block(self, system_prompt: str) -> list[BetaTextBlockParam]:
        """Get system block with appropriate cache control."""
        if self.ENABLE_PROMPT_CACHING:
            return [
                BetaTextBlockParam(
                    type="text",
                    text=system_prompt,
                    cache_control={"type": "ephemeral"},
                )
            ]
        else:
            return [BetaTextBlockParam(type="text", text=system_prompt)]

    def _get_beta_flags(self):
        betas = [COMPUTER_USE_BETA_FLAG]
        if self.ENABLE_PROMPT_CACHING:
            betas.append(PROMPT_CACHING_BETA_FLAG)
        return betas

    def _inject_prompt_caching(self, messages: list[dict[str, Any]]):
        """
        Set cache breakpoints for the 3 most recent turns
        one cache breakpoint is left for tools/system prompt, to be shared
        across sessions
        """

        breakpoints_remaining = 3
        for message in reversed(messages):
            if message["role"] == "user" and isinstance(
                content := message["content"], list
            ):
                if breakpoints_remaining:
                    breakpoints_remaining -= 1
                    content[-1]["cache_control"] = {"type": "ephemeral"}
                else:
                    content[-1].pop("cache_control", None)
                    # we'll only every have one extra turn per loop
                    break

    def _maybe_filter_to_n_most_recent_images(
        self,
        messages: list[dict[str, Any]],
        images_to_keep: int,
        min_removal_threshold: int,
    ):
        """
        With the assumption that images are screenshots that are of diminishing value as
        the conversation progresses, remove all but the final `images_to_keep` tool_result
        images in place, with a chunk of min_removal_threshold to reduce the amount we
        break the implicit prompt cache.
        """
        if images_to_keep is None:
            return messages

        tool_result_blocks = cast(
            list[dict[str, Any]],
            [
                item
                for message in messages
                for item in (
                    message["content"]
                    if isinstance(message["content"], list)
                    else []
                )
                if isinstance(item, dict) and item.get("type") == "tool_result"
            ],
        )

        total_images = sum(
            1
            for tool_result in tool_result_blocks
            for content in tool_result.get("content", [])
            if isinstance(content, dict) and content.get("type") == "image"
        )

        images_to_remove = total_images - images_to_keep
        # for better cache behavior, we want to remove in chunks
        images_to_remove -= images_to_remove % min_removal_threshold

        for tool_result in tool_result_blocks:
            if isinstance(tool_result.get("content"), list):
                new_content = []
                for content in tool_result.get("content", []):
                    if (
                        isinstance(content, dict)
                        and content.get("type") == "image"
                    ):
                        if images_to_remove > 0:
                            images_to_remove -= 1
                            continue
                    new_content.append(content)
                tool_result["content"] = new_content


class BedrockClaudeAgent(ClaudeAgent):
    """Bedrock Claude agent implementation.

    Bedrock Claude is a bit different than the standard Claude agent, so we
    override the default behavior here especially for prompt caching.
    """

    PROVIDER = APIProvider.BEDROCK
    ENABLE_PROMPT_CACHING = False

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize the Bedrock Claude agent.

        Args:
            api_key: Not used for Bedrock (uses AWS credentials instead)
            **kwargs: Additional initialization parameters
        """
        super(AbsAgent, self).__init__()  # Skip ClaudeAgent's __init__
        self.client = AnthropicBedrock()


class VertexClaudeAgent(ClaudeAgent):
    """Vertex Claude agent implementation.

    Vertex Claude is a bit different than the standard Claude agent, so we
    override the default behavior here especially for prompt caching.
    """

    PROVIDER = APIProvider.VERTEX
    ENABLE_PROMPT_CACHING = False

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize the Vertex Claude agent.

        Args:
            api_key: Not used for Vertex (uses AWS credentials instead)
            **kwargs: Additional initialization parameters
        """
        super(AbsAgent, self).__init__()  # Skip ClaudeAgent's __init__
        self.client = AnthropicVertex()
