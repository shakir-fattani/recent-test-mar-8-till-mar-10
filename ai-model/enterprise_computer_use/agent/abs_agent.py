"""Abstract class for an agent."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class AbsAgent(ABC):
    """Abstract class for an agent."""

    @abstractmethod
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize the agent.

        Args:
            api_key: Optional API key for the model service
            **kwargs: Additional model-specific initialization parameters
        """

    @abstractmethod
    def _preprocess(
        self, messages: list[dict[str, Any]], **kwargs
    ) -> list[dict[str, Any]]:
        """Preprocess the messages."""

    @abstractmethod
    def _postprocess(
        self, messages: list[dict[str, Any]], **kwargs
    ) -> dict[str, Any]:
        """Postprocess the messages."""

    @abstractmethod
    def configure(self, **kwargs):
        """Configure agent parameters"""

    @abstractmethod
    def predict(self, observation: dict) -> dict[str, Any]:
        """Generate action from environment observation"""
