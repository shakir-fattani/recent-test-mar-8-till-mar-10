from fastapi import APIRouter # type: ignore

from api.v1.endpoints import auth, users, health, chat, files

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(chat.router, prefix="/chats", tags=["chats"])
api_router.include_router(files.router, prefix="/files", tags=["files"])

# Add more routers here as needed for different features
