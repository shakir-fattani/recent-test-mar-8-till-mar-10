from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException # type: ignore
from sqlalchemy.orm import Session # type: ignore

from api.deps import get_db
from core.config import settings
from core.security import create_access_token
from crud.user import authenticate_user, create_user, get_user_by_email, get_user_by_username
from schemas.token import Token
from schemas.user import User, UserCreate

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    username: str = Body(...),
    password: str = Body(...)
) -> Any:
    """
    JSON based token login, get an access token for future requests
    """
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/register", response_model=User)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user
    """
    user = get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    
    user = get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    
    user = create_user(db, user_in=user_in)
    return user
