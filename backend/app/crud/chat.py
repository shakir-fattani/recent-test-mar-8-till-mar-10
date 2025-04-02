import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload # type: ignore
from sqlalchemy import desc # type: ignore

from models.chat import Chat, ChatHistory


def create_chat(
    db: Session, 
    user_id: int,
    initial_message: Optional[str] = None,
    initial_role: str = "user"
) -> Chat:
    """Create a new chat for a user, optionally with an initial message."""
    # Create chat
    db_chat = Chat(user_id=user_id)
    db.add(db_chat)
    db.flush()  # Flush to get the chat_id without committing transaction
    
    # Add initial message if provided
    if initial_message:
        db_history = ChatHistory(
            chat_id=db_chat.chat_id,
            role=initial_role,
            message=initial_message,
            extra_data={}
        )
        db.add(db_history)
    
    db.commit()
    db.refresh(db_chat)
    return db_chat


def get_all_chats_by_user_id(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Get all chats for a user, including the first history entry for each chat.
    Returns a list of dicts with chat info and first_message.
    """
    # Get all chats for the user
    chats = db.query(Chat).filter(Chat.user_id == user_id).order_by(
        desc(Chat.updated_at)
    ).offset(skip).limit(limit).all()
    
    result = []
    for chat in chats:
        # Get the first message in the chat history (chronologically)
        first_history = db.query(ChatHistory).filter(
            ChatHistory.chat_id == chat.chat_id
        ).order_by(ChatHistory.created_at).first()
        
        # Create a dict with chat and first message
        chat_info = {
            "chat_id": chat.chat_id,
            "user_id": chat.user_id,
            "created_at": chat.created_at,
            "updated_at": chat.updated_at,
            "first_message": first_history.message if first_history else "",
            "first_role": first_history.role if first_history else ""
        }
        result.append(chat_info)
    
    return result


def get_chat_by_id_with_history(
    db: Session, 
    chat_id: uuid.UUID,
    user_id: int
) -> Optional[Chat]:
    """Get a specific chat with all its history ordered by creation time."""
    db_chat = db.query(Chat).filter(
        Chat.chat_id == chat_id,
    ).options(
        joinedload(Chat.history)
    ).first()

    if not db_chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if db_chat.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this chat")
    return db_chat



def add_chat_history(
    db: Session,
    chat_id: uuid.UUID,
    role: str,
    message: str,
    extra_data: Optional[Dict[str, Any]] = None
) -> ChatHistory:
    """Add a new message to a chat's history."""
    # Create history entry
    db_history = ChatHistory(
        chat_id=chat_id,
        role=role,
        message=message,
        extra_data=extra_data or {}
    )
    db.add(db_history)
    
    # Update the chat's updated_at timestamp
    chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()
    if chat:
        # The updated_at will be updated automatically due to onupdate=func.now()
        db.add(chat)
    
    db.commit()
    db.refresh(db_history)
    return db_history


def delete_chat(
    db: Session, 
    chat_id: uuid.UUID
) -> bool:
    """Delete a chat and all its history."""
    chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()
    if not chat:
        return False
    
    db.delete(chat)
    db.commit()
    return True


def get_chat_history(
    db: Session,
    chat_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100
) -> List[ChatHistory]:
    """Get chat history entries for a specific chat."""
    return db.query(ChatHistory).filter(
        ChatHistory.chat_id == chat_id
    ).order_by(
        ChatHistory.created_at
    ).offset(skip).limit(limit).all()
