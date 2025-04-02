"""Tools for the Claude API. Do not use unless you are using the Claude API.
Do not add any tools here unless you are using the Claude API.
"""

import logging
import os

from enterprise_computer_use.tools.claude.bash import BashTool
from enterprise_computer_use.tools.claude.computer import ComputerTool
from enterprise_computer_use.tools.claude.edit import EditTool

logger = logging.getLogger(__name__)

# Initialize GUIComputerTool as None by default
GUIComputerTool = None

# Only import GUIComputerTool if DISPLAY environment variable is set
if "DISPLAY" in os.environ:
    try:
        from enterprise_computer_use.tools.claude.gui_computer import (
            GUIComputerTool,
        )
    except ImportError as e:
        logger.warning(f"Warning: Could not import GUIComputerTool: {e}")

__ALL__ = [
    BashTool,
    ComputerTool,
    EditTool,
    GUIComputerTool,
]
