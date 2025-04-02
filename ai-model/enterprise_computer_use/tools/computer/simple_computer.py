"""Computer tools for interacting with the operating system and UI."""

import asyncio
import base64
import logging
import os
import shlex
import shutil
from enum import StrEnum
from pathlib import Path
from typing import Any, ClassVar, Literal, TypedDict
from uuid import uuid4

from openai import OpenAI

from enterprise_computer_use.tools.base import BaseTool, ToolError, ToolResult

logger = logging.getLogger(__name__)

OUTPUT_DIR = "/tmp/outputs"

MAX_GROUNDING_ATTEMPTS = 3
TYPING_DELAY_MS = 12
TYPING_GROUP_SIZE = 50
MAX_RESPONSE_LEN: int = 16000

GROUNDING_PROMPT = """Output only the coordinate of one point in your response. What element matches the following task: """
TRUNCATED_MESSAGE: str = "<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>"

Action = Literal["type", "click", "screenshot", "press_key"]


class Resolution(TypedDict):
    width: int
    height: int


MAX_SCALING_TARGETS: dict[str, Resolution] = {
    "XGA": Resolution(width=1024, height=768),  # 4:3
    "WXGA": Resolution(width=1280, height=800),  # 16:10
    "FWXGA": Resolution(width=1366, height=768),  # ~16:9
}


def maybe_truncate(content: str, truncate_after: int | None = MAX_RESPONSE_LEN):
    """Truncate content and append a notice if content exceeds the specified length."""
    return (
        content
        if not truncate_after or len(content) <= truncate_after
        else content[:truncate_after] + TRUNCATED_MESSAGE
    )


async def run(
    cmd: str,
    timeout: float | None = 120.0,  # seconds
    truncate_after: int | None = MAX_RESPONSE_LEN,
):
    """Run a shell command asynchronously with a timeout."""
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=timeout
        )
        return (
            process.returncode or 0,
            maybe_truncate(stdout.decode(), truncate_after=truncate_after),
            maybe_truncate(stderr.decode(), truncate_after=truncate_after),
        )
    except asyncio.TimeoutError as exc:
        try:
            process.kill()
        except ProcessLookupError:
            pass
        raise TimeoutError(
            f"Command '{cmd}' timed out after {timeout} seconds"
        ) from exc


class ScalingSource(StrEnum):
    COMPUTER = "computer"
    API = "api"


class ComputerToolOptions(TypedDict):
    display_height_px: int
    display_width_px: int
    display_number: int | None


def chunks(s: str, chunk_size: int) -> list[str]:
    return [s[i : i + chunk_size] for i in range(0, len(s), chunk_size)]


class SimpleComputerTool(BaseTool):
    """
    A tool for interacting with computer UI and system operations.
    Supports operations like clicking, typing, pressing keys, taking screenshots.
    Always take a screenshot first before each action.

    Available commands:
        - click: Click on a UI element. When describing the element to click, provide a detailed description including:
            - The exact text/label of the element
            - Its location on screen (e.g. "top right", "bottom left")
            - Any nearby elements or text that help identify it uniquely
            - Visual characteristics (e.g. "blue button", "search textbox")
            This helps avoid ambiguity when multiple similar elements exist.
        - type: Type text into the currently focused element, return the text need to be typed
        - press_key: Press a specific keyboard key, return the key need to be pressed
        - screenshot: Take a screenshot of the current screen
    """

    name: ClassVar[Literal["SimpleComputerTool"]] = "SimpleComputerTool"
    width: int
    height: int
    display_num: int | None

    _screenshot_delay = 2.0
    _scaling_enabled = True

    def __init__(self):
        """Initialize Computer tool."""
        super().__init__()
        self.width = int(os.getenv("WIDTH") or 0)
        self.height = int(os.getenv("HEIGHT") or 0)
        assert self.width and self.height, "WIDTH, HEIGHT must be set"
        if (display_num := os.getenv("DISPLAY_NUM")) is not None:
            self.display_num = int(display_num)
            self._display_prefix = f"DISPLAY=:{self.display_num} "
        else:
            self.display_num = None
            self._display_prefix = ""

        self.xdotool = f"{self._display_prefix}xdotool"
        self.grounding_model = OpenAI(
            base_url=os.getenv("GROUNDING_MODEL_URL"),
            api_key="empty",
        )

    def _get_grounding_coordinates(self, text: str) -> tuple[int, int]:
        # Get the latest screenshot from the output directory
        output_dir = Path(OUTPUT_DIR)
        screenshots = list(output_dir.glob("screenshot_*.png"))
        if not screenshots:
            raise ToolError("No screenshots found in output directory")
        latest_screenshot = max(screenshots, key=lambda p: p.stat().st_mtime)

        # Read and encode the latest screenshot
        screenshot_base64 = base64.b64encode(
            latest_screenshot.read_bytes()
        ).decode("utf-8")

        grounding_response = None
        for attempt in range(MAX_GROUNDING_ATTEMPTS):
            try:
                grounding_response = (
                    self.grounding_model.chat.completions.create(
                        model="ui-tars",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64,{screenshot_base64}"
                                        },
                                    },
                                    {
                                        "type": "text",
                                        "text": GROUNDING_PROMPT + text,
                                    },
                                ],
                            },
                        ],
                        frequency_penalty=1,
                        max_tokens=128,
                    )
                    .choices[0]
                    .message.content
                )
                logger.info("grounding_response: %s", grounding_response)

                if grounding_response is None:
                    raise ValueError(
                        "Received empty response from grounding model"
                    )

                # Remove any parentheses and split by comma
                coords = grounding_response.strip("()").split(",")
                if len(coords) != 2:
                    raise ValueError("Invalid coordinate format")

                # Convert relative coordinates (0-1000 range) to absolute coordinates
                x_relative = int(coords[0].strip())
                y_relative = int(coords[1].strip())

                # Calculate absolute coordinates based on screen dimensions
                # This is required for UI-TARS model's response
                x_absolute = round(self.width * x_relative / 1000)
                y_absolute = round(self.height * y_relative / 1000)

                return (x_absolute, y_absolute)

            except (ValueError, IndexError) as e:
                if attempt == MAX_GROUNDING_ATTEMPTS - 1:
                    raise ToolError(
                        f"Failed to parse coordinates after {MAX_GROUNDING_ATTEMPTS} attempts. Last response: {grounding_response}"
                    ) from e
                logger.warning(
                    f"Attempt {attempt + 1} failed: {str(e)}. Retrying..."
                )

        # This return is needed to satisfy the return type hint
        raise ToolError("Failed to get coordinates after all attempts")

    async def __call__(
        self,
        *,
        command: Literal["click", "type", "press_key", "screenshot"],
        text: str,
        **kwargs,
    ):
        logger.info(f"Running {command} with text: {text}")
        if text is None:
            raise ToolError(f"text is required for {command} action")
        if command == "screenshot":
            return await self.screenshot()
        if command == "click":
            x, y = self._get_grounding_coordinates(text)
            return await self.shell(
                f"{self.xdotool} mousemove --sync {x} {y} click 1"
            )
        elif command == "type":
            results: list[ToolResult] = []
            for chunk in chunks(text, TYPING_GROUP_SIZE):
                cmd = f"{self.xdotool} type --delay {TYPING_DELAY_MS} -- {shlex.quote(chunk)}"
                results.append(await self.shell(cmd, take_screenshot=False))
            screenshot_base64 = (await self.screenshot()).base64_image
            return ToolResult(
                output=text,
                error="".join(result.error or "" for result in results),
                base64_image=screenshot_base64,
            )
        elif command == "press_key":
            return await self.shell(f"{self.xdotool} key -- {text}")
        else:
            raise ToolError(f"Invalid command: {command}")

    def to_params(self, **kwargs) -> dict[str, Any]:
        """Convert tool to function parameters for LLM."""
        model = kwargs.get("model")
        if model == "claude":
            return {
                "name": self.name,
                "description": self.__class__.__doc__,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The computer operation to perform",
                            "enum": [
                                "click",
                                "type",
                                "press_key",
                                "screenshot",
                            ],
                        },
                        "text": {
                            "type": "string",
                            "description": "Description of what to do for the command (e.g. element to click, text to type, key to press). If clicking, return the concise description of the element to click on, not the coordinates.",
                        },
                    },
                    "required": ["command", "text"],
                },
            }

        # Add a catch-all return or raise an exception
        raise ValueError(
            f"Model {model} is in SUPPORTED_MODELS but has no implementation"
        )

    async def screenshot(self):
        """Take a screenshot of the current screen and return the base64 encoded image."""
        output_dir = Path(OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"screenshot_{uuid4().hex}.png"

        # Try gnome-screenshot first
        if shutil.which("gnome-screenshot"):
            screenshot_cmd = (
                f"{self._display_prefix}gnome-screenshot -f {path} -p"
            )
        else:
            # Fall back to scrot if gnome-screenshot isn't available
            screenshot_cmd = f"{self._display_prefix}scrot -p {path}"

        result = await self.shell(screenshot_cmd, take_screenshot=False)
        if self._scaling_enabled:
            x, y = self.scale_coordinates(
                ScalingSource.COMPUTER, self.width, self.height
            )
            await self.shell(
                f"convert {path} -resize {x}x{y}! {path}", take_screenshot=False
            )

        if path.exists():
            return result.replace(
                base64_image=base64.b64encode(path.read_bytes()).decode()
            )
        raise ToolError(f"Failed to take screenshot: {result.error}")

    async def shell(self, command: str, take_screenshot=True) -> ToolResult:
        """Run a shell command and return the output, error, and optionally a screenshot."""
        _, stdout, stderr = await run(command)
        base64_image = None

        if take_screenshot:
            # delay to let things settle before taking a screenshot
            await asyncio.sleep(self._screenshot_delay)
            base64_image = (await self.screenshot()).base64_image

        return ToolResult(
            output=stdout, error=stderr, base64_image=base64_image
        )

    def scale_coordinates(self, source: ScalingSource, x: int, y: int):
        """Scale coordinates to a target maximum resolution."""
        if not self._scaling_enabled:
            return x, y
        ratio = self.width / self.height
        target_dimension = None
        for dimension in MAX_SCALING_TARGETS.values():
            # allow some error in the aspect ratio - not ratios are exactly 16:9
            if abs(dimension["width"] / dimension["height"] - ratio) < 0.02:
                if dimension["width"] < self.width:
                    target_dimension = dimension
                break
        if target_dimension is None:
            return x, y
        # should be less than 1
        x_scaling_factor = target_dimension["width"] / self.width
        y_scaling_factor = target_dimension["height"] / self.height
        if source == ScalingSource.API:
            if x > self.width or y > self.height:
                raise ToolError(f"Coordinates {x}, {y} are out of bounds")
            # scale up
            return round(x / x_scaling_factor), round(y / y_scaling_factor)
        # scale down
        return round(x * x_scaling_factor), round(y * y_scaling_factor)
