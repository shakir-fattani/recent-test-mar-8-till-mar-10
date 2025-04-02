import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from core.config import settings
from api.api import api_router
from api.v1.endpoints import health
from db.init_db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic (previously in @app.on_event("startup"))
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
    
    logger.info("Application startup complete")
    yield  # This is where the application runs
    
    # Shutdown logic (previously in @app.on_event("shutdown"))
    logger.info("Shutting down application")

# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Backend API for the application",
    version="1.0.0",
    lifespan=lifespan,
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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
