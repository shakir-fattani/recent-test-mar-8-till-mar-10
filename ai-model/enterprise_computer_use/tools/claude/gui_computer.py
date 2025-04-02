"""GUI Computer tool implementation."""

import asyncio
import base64
from enum import StrEnum
from pathlib import Path
from typing import ClassVar, Literal, TypedDict
from uuid import uuid4

import pyautogui  # type: ignore
from PIL import Image  # type: ignore

from enterprise_computer_use.tools.base import BaseTool, ToolError, ToolResult

# Configure PyAutoGUI safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1  # Add small delay between actions

OUTPUT_DIR = "/tmp/outputs"
TYPING_DELAY_MS = 0.012  # PyAutoGUI uses seconds instead of ms
TYPING_GROUP_SIZE = 50

Action = Literal[
    "key",
    "type",
    "mouse_move",
    "left_click",
    "left_click_drag",
    "right_click",
    "middle_click",
    "double_click",
    "screenshot",
    "cursor_position",
]


class Resolution(TypedDict):
    width: int
    height: int


# Same scaling targets as computer.py
MAX_SCALING_TARGETS: dict[str, Resolution] = {
    "XGA": Resolution(width=1024, height=768),
    "WXGA": Resolution(width=1280, height=800),
    "FWXGA": Resolution(width=1366, height=768),
}


class ScalingSource(StrEnum):
    COMPUTER = "computer"
    API = "api"


class ComputerToolOptions(TypedDict):
    display_height_px: int
    display_width_px: int
    display_number: int | None


class GUIComputerTool(BaseTool):
    name: ClassVar[Literal["computer"]] = "computer"
    api_type: Literal["computer_20241022"] = "computer_20241022"
    width: int
    height: int
    display_num: int | None

    _screenshot_delay = 2.0
    _scaling_enabled = True

    def __init__(self):
        super().__init__()
        # Get screen size from PyAutoGUI
        self.width, self.height = pyautogui.size()
        self.display_num = None  # PyAutoGUI handles multi-monitor differently

    @property
    def options(self) -> ComputerToolOptions:
        width, height = self.scale_coordinates(
            ScalingSource.COMPUTER, self.width, self.height
        )
        return {
            "display_width_px": width,
            "display_height_px": height,
            "display_number": self.display_num,
        }

    def to_params(self, **kwargs):
        return {"name": self.name, "type": self.api_type, **self.options}

    async def __call__(
        self,
        *,
        action: Action,
        text: str | None = None,
        coordinate: tuple[int, int] | None = None,
        **kwargs,
    ):
        try:
            if action in ("mouse_move", "left_click_drag"):
                if coordinate is None:
                    raise ToolError(f"coordinate is required for {action}")
                if text is not None:
                    raise ToolError(f"text is not accepted for {action}")

                x, y = self.scale_coordinates(
                    ScalingSource.API, coordinate[0], coordinate[1]
                )

                if action == "mouse_move":
                    pyautogui.moveTo(x, y)
                elif action == "left_click_drag":
                    pyautogui.dragTo(x, y, button="left")

                return await self.take_screenshot_result()

            if action in ("key", "type"):
                if text is None:
                    raise ToolError(f"text is required for {action}")
                if coordinate is not None:
                    raise ToolError(f"coordinate is not accepted for {action}")

                if action == "key":
                    pyautogui.press(text)
                elif action == "type":
                    pyautogui.write(text, interval=TYPING_DELAY_MS)

                return await self.take_screenshot_result()

            if action in (
                "left_click",
                "right_click",
                "middle_click",
                "double_click",
            ):
                if text is not None or coordinate is not None:
                    raise ToolError(f"No parameters accepted for {action}")

                button = {
                    "left_click": "left",
                    "right_click": "right",
                    "middle_click": "middle",
                }

                if action == "double_click":
                    pyautogui.doubleClick()
                else:
                    pyautogui.click(button=button.get(action, "left"))

                return await self.take_screenshot_result()

            if action == "screenshot":
                return await self.screenshot()

            if action == "cursor_position":
                x, y = pyautogui.position()
                x, y = self.scale_coordinates(ScalingSource.COMPUTER, x, y)
                return ToolResult(output=f"X={x},Y={y}")

            raise ToolError(f"Invalid action: {action}")

        except pyautogui.FailSafeException as err:
            raise ToolError(
                "Mouse hit failsafe corner - operation aborted"
            ) from err

    async def screenshot(self) -> ToolResult:
        """Take a screenshot and return it as base64."""
        output_dir = Path(OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"screenshot_{uuid4().hex}.png"

        # Take screenshot using PyAutoGUI
        screenshot = pyautogui.screenshot()

        if self._scaling_enabled:
            x, y = self.scale_coordinates(
                ScalingSource.COMPUTER, self.width, self.height
            )
            screenshot = screenshot.resize((x, y), Image.Resampling.LANCZOS)

        # Save and encode
        screenshot.save(path)
        return ToolResult(
            base64_image=base64.b64encode(path.read_bytes()).decode()
        )

    async def take_screenshot_result(self) -> ToolResult:
        """Helper to take a screenshot after an action."""
        await asyncio.sleep(self._screenshot_delay)
        return await self.screenshot()

    def scale_coordinates(
        self, source: ScalingSource, x: float, y: float
    ) -> tuple[int, int]:
        """Scale coordinates to a target maximum resolution."""
        if not self._scaling_enabled:
            return int(x), int(y)
        ratio = self.width / self.height
        target_dimension = None
        for dimension in MAX_SCALING_TARGETS.values():
            if abs(dimension["width"] / dimension["height"] - ratio) < 0.02:
                if dimension["width"] < self.width:
                    target_dimension = dimension
                break
        if target_dimension is None:
            return int(x), int(y)

        x_scaling_factor = target_dimension["width"] / self.width
        y_scaling_factor = target_dimension["height"] / self.height

        if source == ScalingSource.API:
            if x > self.width or y > self.height:
                raise ToolError(f"Coordinates {x}, {y} are out of bounds")
            return round(x / x_scaling_factor), round(y / y_scaling_factor)
        return round(x * x_scaling_factor), round(y * y_scaling_factor)
