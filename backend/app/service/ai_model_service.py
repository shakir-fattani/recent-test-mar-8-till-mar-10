import requests
from typing import List, Dict, Any, Optional
import os
import logging

logger = logging.getLogger(__name__)

class ChatMessage:
    """Represents a message in a chat conversation."""
    def __init__(self, role: str, content: str, extra: Dict[str, Any] = {}):
        self.role = role
        self.content = content
        self.extra = extra
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content
        }


def extract_new_messages(api_response: Dict[str, Any]) -> List[ChatMessage]:
    """
    Extract messages marked with isNew: True from the API response.
    
    Args:
        api_response: Response dictionary from the AI model API
        
    Returns:
        List of ChatMessage objects created from new messages
    """
    new_messages = []
    
    if not api_response or not isinstance(api_response, dict):
        logger.warning("Invalid API response format")
        return new_messages
    
    # Extract messages from the response - adjust this based on the actual response structure
    messages = api_response.get("messages", [])
    
    # Filter for messages with isNew: True and convert to ChatMessage objects
    for message in messages:
        if isinstance(message, dict) and message.get("isNew") is True:
            new_messages.append(
                ChatMessage(
                    role=message.get("role", "assistant"),
                    content=message.get("content", ""),
                    extra=message.get("extra", {})
                )
            )
    
    return new_messages


def send_message_to_ai_model(messages: List[ChatMessage]) -> Optional[Dict[str, Any]]:
    """
    Sends messages to AI model and gets a response.
    
    Args:
        messages: List of ChatMessage objects
        
    Returns:
        Response from AI model or None if request failed
    """
    ai_model_base_url = os.environ.get("AI_MODEL_BASE_URL")
    if not ai_model_base_url:
        logger.error("AI_MODEL_BASE_URL environment variable not set")
        return None
    
    url = f"{ai_model_base_url}/send_message"
    
    try:
        payload = {
            "messages": [message.to_dict() for message in messages]
        }
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception for non-2xx status codes
        
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error calling AI model: {str(e)}")
        return None
