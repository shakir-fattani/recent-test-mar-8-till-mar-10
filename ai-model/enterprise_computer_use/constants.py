"""Constants for the computer use"""

from enum import StrEnum


class APIProvider(StrEnum):
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OPENAI = "openai"
    BEDROCK = "bedrock"  # TODO: Remove
    VERTEX = "vertex"  # TODO: Remove
