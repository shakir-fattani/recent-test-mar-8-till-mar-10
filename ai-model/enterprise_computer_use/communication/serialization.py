import json
from typing import Any


def serialize_dict(data: dict[str, Any]) -> bytes:
    """Serialize dictionary to bytes using JSON encoding."""
    return json.dumps(data).encode("utf-8")


def deserialize_dict(data: bytes) -> dict[str, Any]:
    """Deserialize bytes to dictionary using JSON decoding."""
    try:
        return json.loads(data.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to deserialize data: {e}") from e


def clean_message_string(message: str) -> str:
    """Clean message string by replacing enum references."""
    message = message.replace("<Sender.USER: 'user'>", "'user'")
    message = message.replace("<Sender.ASSISTANT: 'assistant'>", "'assistant'")
    return message
