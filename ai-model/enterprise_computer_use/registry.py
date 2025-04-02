from dataclasses import dataclass
from enum import Enum
from typing import Callable

from enterprise_computer_use.tools import ToolCollection


class OSType(Enum):
    """The environment type of the computer use task."""

    MAC = "mac"
    LINUX = "linux"


class ProjectType(Enum):
    """The project type of the computer use task."""

    COMPUTER_USE = "computer_use"
    CLAUDE_COMPUTER_USE = "claude_computer_use"
    AIRTABLE_COMPUTER_USE = "airtable_computer_use"
    PLANNER_GROUNDING_COMPUTER_USE = "planner_grounding_computer_use"
    CONCUR_COMPUTER_USE = "concur_computer_use"


@dataclass
class Config:
    """The configuration for the computer use task."""

    tool_collection: ToolCollection
    system_prompt: str
    client_factory: Callable


class Registry:
    """The registry for the computer use task."""

    _store = {}

    @classmethod
    def register(cls, os: OSType, project: ProjectType):
        def decorator(fn):
            key = f"{os.value}_{project.value}"
            cls._store[key] = fn()
            return fn

        return decorator

    @classmethod
    def get_config(cls, os: OSType, project: ProjectType) -> Config:
        return cls._store[f"{os.value}_{project.value}"]
