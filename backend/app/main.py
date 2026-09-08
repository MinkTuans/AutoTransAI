"""
FastAPI application entry point.

Initializes the app, registers providers, and mounts routes.
"""

import sys
import asyncio

# Ensure Windows ProactorEventLoopPolicy is set for asyncio subprocess support
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

from contextlib import asynccontextmanager
from pathlib import Path


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.core import setup_logging, get_logger
from app.database import init_db
from app.providers.registry import get_registry

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    # Setup logging
    setup_logging(log_level="DEBUG" if settings.DEBUG else "INFO")
    logger = get_logger("app.main")
    logger.info("Starting AutoTransAi backend")

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
    from app.providers.llm.openai_provider import OpenAILLMProvider
    from app.providers.llm.gemini_provider import GeminiLLMProvider

    registry.register_llm(OpenAILLMProvider())
    registry.register_llm(GeminiLLMProvider())

    logger.info(
        "Providers registered",
        audio=len(registry.list_audio()),
        video=len(registry.list_video()),
        llm=len(registry.list_llm()),
    )

    # Detect interrupted projects on startup
    logger.info("AutoTransAi backend ready", port=settings.PORT)

    yield

    # Shutdown
    logger.info("Shutting down AutoTransAi backend")
    try:
        from app.api.routes.video_translator import _job_cancellation_events, signal_job_cancellation
        for job_id in list(_job_cancellation_events.keys()):
            signal_job_cancellation(job_id)
    except Exception as ex:
        logger.warning("Error signalling job cancellation during shutdown", error=str(ex))


app = FastAPI(
    title="AutoTransAi",
    description="Local-first Script-to-Video & AI Translation Pipeline",
    version="0.1.0",
    lifespan=lifespan,
)

from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi import HTTPException

# CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger = get_logger("app.main")
    logger.exception("Unhandled server error", path=request.url.path, error=str(exc))
    err_type = type(exc).__name__
    err_msg = str(exc) or "Internal server error"
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "detail": f"❌ Server Error ({err_type}): {err_msg}",
            "error_type": err_type,
            "path": request.url.path,
        },
    )

from app.api.routes import projects, providers, system, video_translator, storage, apps, video_editor, thumbnail, settings as settings_router

from app.api.routers import youtube

# Mount API routes
app.include_router(projects.router)
app.include_router(providers.router)
app.include_router(system.router)
app.include_router(video_translator.router)
app.include_router(storage.router)
app.include_router(apps.router)
app.include_router(video_editor.router)
app.include_router(thumbnail.router)
app.include_router(settings_router.router)
app.include_router(youtube.router, prefix="/api")



# Mount Static Files for local media serving
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.DATA_DIR), name="media")



@app.get("/")
async def root():
    return {
        "name": "AutoTransAi",
        "version": "0.1.0",
        "status": "running",
    }

