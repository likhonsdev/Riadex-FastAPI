from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
import os
import sys

# Add the api directory to Python path for absolute imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from infrastructure.config import get_settings
from presentation.routers.sessions import router as sessions_router
from presentation.routers.chat import router as chat_router
from presentation.routers.tools import router as tools_router
from infrastructure.logging import setup_logging
from infrastructure.database import init_database, close_database
from infrastructure.redis_client import redis_client

settings = get_settings()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    logger.info("FastAPI application starting up")
    await init_database()
    await redis_client.connect()
    yield
    # Shutdown
    logger.info("FastAPI application shutting down")
    await close_database()
    await redis_client.close()

app = FastAPI(
    title="Riadex FastAPI Backend",
    description="A complete FastAPI + DDD backend scaffold with SSE chat and Gemini-through-OpenAI compatibility",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions_router, prefix="/api/v1", tags=["sessions"])
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
app.include_router(tools_router, prefix="/api/v1", tags=["tools"])

@app.get("/")
async def root():
    return {"message": "Riadex FastAPI Backend is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# For Vercel serverless deployment
handler = app
</Vercel>
