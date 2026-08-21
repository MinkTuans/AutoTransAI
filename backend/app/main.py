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

    # Register Audio Providers
    from app.providers.audio.edge_tts_provider import EdgeTTSProvider
    from app.providers.audio.google_tts_provider import GoogleCloudTTSProvider
    from app.providers.audio.elevenlabs_provider import ElevenLabsAudioProvider

    registry.register_audio(EdgeTTSProvider())
    registry.register_audio(GoogleCloudTTSProvider())
    registry.register_audio(ElevenLabsAudioProvider())

    # Register Video Providers
    from app.providers.video.local_provider import LocalVideoProvider
    from app.providers.video.kling_provider import KlingVideoProvider
    from app.providers.video.fal_provider import FalVideoProvider

    registry.register_video(LocalVideoProvider())
    registry.register_video(KlingVideoProvider())
    registry.register_video(FalVideoProvider())

    # Register LLM Providers
    from app.providers.llm.gemini_provider import GeminiLLMProvider

    registry.register_llm(GeminiLLMProvider())

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

# Mount Static Files for local media serving
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.DATA_DIR), name="media")



@app.get("/")
async def root():
    return {
        "name": "WorkflowVdAi",
        "version": "0.1.0",
        "status": "running",
    }
