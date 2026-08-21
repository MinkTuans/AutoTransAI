"""
FastAPI application entry point.

Initializes the app, registers providers, and mounts routes.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.core import setup_logging, get_logger
from app.database import init_db
from app.api.routes import projects, providers, system
from app.providers.registry import get_registry
from app.providers.audio.edge_tts_provider import EdgeTTSProvider

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    # Setup logging
    setup_logging(log_level="DEBUG" if settings.DEBUG else "INFO")
    logger = get_logger("app.main")
    logger.info("Starting WorkflowVdAi backend")

    # Ensure data directories exist
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Register providers
    registry = get_registry()

    # Always register Edge TTS (free, no API key needed)
    registry.register_audio(EdgeTTSProvider())

    # Register additional providers based on configured API keys
    # (Video and LLM providers will be registered when implemented)

    logger.info(
        "Providers registered",
        audio=len(registry.list_audio()),
        video=len(registry.list_video()),
        llm=len(registry.list_llm()),
    )

    # Detect interrupted projects on startup
    logger.info("WorkflowVdAi backend ready", port=settings.PORT)

    yield

    # Shutdown
    logger.info("Shutting down WorkflowVdAi backend")


app = FastAPI(
    title="WorkflowVdAi",
    description="Local-first Script-to-Video Production Pipeline",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(projects.router)
app.include_router(providers.router)
app.include_router(system.router)


@app.get("/")
async def root():
    return {
        "name": "WorkflowVdAi",
        "version": "0.1.0",
        "status": "running",
    }
