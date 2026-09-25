"""Standalone HTTP API for Gemini Live speech-to-speech translation."""

from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse

from app.config import get_settings
from app.services.live_audio_translation.audio import SUPPORTED_SUFFIXES
from app.services.live_audio_translation.jobs import LiveJobManager, SessionCapacityError


router = APIRouter(prefix="/api/live-audio-translations", tags=["live-audio-translation"])
MAX_UPLOAD_BYTES = 25 * 1024 * 1024


def get_live_manager(request: Request) -> LiveJobManager:
    manager = getattr(request.app.state, "live_audio_manager", None)
    if manager is None:
        manager = LiveJobManager(get_settings().STORAGE_ROOT)
        request.app.state.live_audio_manager = manager
    return manager


@router.post("", status_code=202)
async def start_live_audio_translation(
    file: UploadFile = File(...), source_language: str = Form("auto"),
    target_language: str = Form("vi"), manager: LiveJobManager = Depends(get_live_manager),
):
    settings = get_settings()
    if not settings.LIVE_AUDIO_TRANSLATION_ENABLED:
        raise HTTPException(503, "feature_disabled")
    if not settings.GEMINI_LIVE_TRANSLATE_API_KEY:
        raise HTTPException(503, "missing_api_key")
    if not settings.GEMINI_LIVE_TRANSLATE_MODEL:
        raise HTTPException(503, "model_unavailable")
    if source_language != "auto" or target_language != "vi":
        raise HTTPException(422, "unsupported_language_selection")
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise HTTPException(415, "unsupported_audio_format")
    job_id = uuid4().hex
    directory = manager.directory / job_id
    directory.mkdir(parents=True, exist_ok=False)
    source = directory / f"source{suffix}"
    try:
        count = 0
        with source.open("wb") as saved:
            while chunk := await file.read(1024 * 1024):
                count += len(chunk)
                if count > MAX_UPLOAD_BYTES:
                    raise HTTPException(413, "audio_too_large")
                saved.write(chunk)
        if count == 0:
            raise HTTPException(415, "unsupported_audio_format")
        job = manager.start(job_id, source, directory,
                            key=settings.GEMINI_LIVE_TRANSLATE_API_KEY,
                            model=settings.GEMINI_LIVE_TRANSLATE_MODEL)
    except SessionCapacityError:
        shutil.rmtree(directory, ignore_errors=True)
        raise HTTPException(429, "session_limit") from None
    except Exception:
        shutil.rmtree(directory, ignore_errors=True)
        raise
    finally:
        await file.close()
    return {"success": True, "data": job.public()}


@router.get("/{job_id}")
async def get_live_audio_translation(job_id: str, manager: LiveJobManager = Depends(get_live_manager)):
    job = manager.jobs.get(job_id)
    if job is None:
        raise HTTPException(404, "session_not_found")
    return {"success": True, "data": job.public()}


@router.post("/{job_id}/cancel")
async def cancel_live_audio_translation(job_id: str, manager: LiveJobManager = Depends(get_live_manager)):
    if job_id not in manager.jobs:
        raise HTTPException(404, "session_not_found")
    if not await manager.cancel(job_id):
        raise HTTPException(409, "session_not_active")
    return {"success": True, "data": manager.jobs[job_id].public()}


@router.get("/{job_id}/audio")
async def download_live_audio_translation(job_id: str, manager: LiveJobManager = Depends(get_live_manager)):
    job = manager.jobs.get(job_id)
    if job is None:
        raise HTTPException(404, "session_not_found")
    result = job.directory / "translated.wav"
    if job.status != "completed" or not result.is_file():
        raise HTTPException(409, "audio_not_ready")
    return FileResponse(result, media_type="audio/wav", filename=f"live-translation-{job_id}.wav")
