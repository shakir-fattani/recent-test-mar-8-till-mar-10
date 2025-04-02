import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException # type: ignore
from sqlalchemy.orm import Session # type: ignore

from service.ai_model_service import send_message_to_ai_model, ChatMessage, extract_new_messages
from api.deps import get_db, get_current_user
from crud import chat as chat_crud
from models.user import User
from schemas.chat import (
    ChatCreate, 
    ChatResponse, 
    ChatWithHistoryResponse, 
    ChatHistoryCreate, 
    ChatHistoryResponse,
    ChatListItem
)

router = APIRouter()

def process_messages_with_ai_model(db: Session, chat_id: str, user_id: int) -> List[ChatMessage]:
    """Send messages to the AI model and process the response."""
    db_chat = chat_crud.get_chat_by_id_with_history(db=db, chat_id=chat_id, user_id=user_id)

    msg = [ChatMessage(role=m.role, content=m.message) for m in db_chat.history]
    api_response = send_message_to_ai_model(msg)
    new_messages = extract_new_messages(api_response)
 
    # Add each new message to the chat history
    for message in new_messages:
        chat_crud.add_chat_history(
            db=db,
            chat_id=chat_id,
            role=message.role,
            message=message.content,
            extra_data=message.extra
        )

    return chat_crud.get_chat_by_id_with_history(db=db, chat_id=chat_id, user_id=user_id)

# @router.post("/", response_model=ChatResponse)
@router.post("/")
def create_chat(
    chat_in: ChatCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new chat for the current user."""
    db_chat = chat_crud.create_chat(
        db=db, 
        user_id=current_user.id,
        initial_message=chat_in.initial_message,
        initial_role=chat_in.initial_role
    )

    return process_messages_with_ai_model(db, db_chat.chat_id, current_user.id)


@router.get("/", response_model=List[ChatListItem])
def get_user_chats(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all chats for the current user with first message preview."""
    chats = chat_crud.get_all_chats_by_user_id(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return chats


@router.get("/{chat_id}")
def get_chat_with_history(
    chat_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific chat with all its history."""
    db_chat = chat_crud.get_chat_by_id_with_history(db=db, chat_id=chat_id, user_id=current_user.id)

    return db_chat


@router.post("/{chat_id}/history", )
def add_message_to_chat(
    chat_id: uuid.UUID,
    message_in: ChatHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a new message to a chat's history."""
    # First verify the chat belongs to the current user
    _ = chat_crud.get_chat_by_id_with_history(db=db, chat_id=chat_id, user_id=current_user.id)
    # Add the message to chat history
    _ = chat_crud.add_chat_history(
        db=db,
        chat_id=chat_id,
        role=message_in.role,
        message=message_in.message,
        extra_data=message_in.extra_data
    )
    return process_messages_with_ai_model(db, chat_id, current_user.id)

@router.delete("/{chat_id}", response_model=bool)
def delete_chat(
    chat_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a chat and all its history."""
    # First verify the chat belongs to the current user
    db_chat = chat_crud.get_chat_by_id_with_history(db=db, chat_id=chat_id, user_id=current_user.id)
    # Delete the chat
    success = chat_crud.delete_chat(db=db, chat_id=chat_id)
    return success
