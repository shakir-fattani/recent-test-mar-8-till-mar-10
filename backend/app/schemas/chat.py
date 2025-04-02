from datetime import datetime
import uuid
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field # type: ignore


# ChatHistory schemas
class ChatHistoryBase(BaseModel):
    role: str
    message: str
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ChatHistoryCreate(ChatHistoryBase):
    pass


class ChatHistoryResponse(ChatHistoryBase):
    id: uuid.UUID
    chat_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Chat schemas
class ChatBase(BaseModel):
    pass


class ChatCreate(ChatBase):
    initial_message: Optional[str] = None
    initial_role: str = "user"


class ChatResponse(ChatBase):
    chat_id: uuid.UUID
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatWithHistoryResponse(ChatResponse):
    history: List[ChatHistoryResponse] = []


class ChatListItem(ChatResponse):
    first_message: str = ""
    first_role: str = ""
