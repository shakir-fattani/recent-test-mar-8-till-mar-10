import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from core.config import settings
from api.api import api_router  # Updated import path
from api.v1.endpoints import health

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Backend API for the application",
    version="1.0.0",
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(health.router, prefix="/health", tags=["health"])
# Add startup and shutdown events
@app.on_event("startup")
async def startup_event():
    # Add any startup tasks here
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # Add any cleanup tasks here
    pass

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
