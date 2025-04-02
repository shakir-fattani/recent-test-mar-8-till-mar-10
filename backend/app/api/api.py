from fastapi import APIRouter

from api.v1.endpoints import auth, users, health

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Add more routers here as needed for different features
