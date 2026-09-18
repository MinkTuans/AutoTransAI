"""
Storage API Routes.

Serves persistent object files for media assets and downloads.
"""

from __future__ import annotations

import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.services.storage_service import SupabaseStorageService
from app.config import get_settings

router = APIRouter(prefix="/api/storage", tags=["storage"])
settings = get_settings()

@router.get("/files/{file_path:path}")
async def get_storage_file(file_path: str):
    """Stream media file stored in persistent local storage."""
    raw_path = file_path.replace("\\", "/")
    clean_path = raw_path.lstrip("/\\")
    for prefix in ("api/storage/files/", "storage/files/", "media/", "storage/"):
        if clean_path.startswith(prefix):
            clean_path = clean_path[len(prefix):]

    # Valid roots
    local_dir = SupabaseStorageService.get_local_storage_dir()
    data_dir = settings.DATA_DIR

    # Try local storage dir
    try:
        local_target = (local_dir / clean_path).resolve()
        if local_target.is_relative_to(local_dir.resolve()) and local_target.exists() and local_target.is_file():
            return FileResponse(local_target)
    except Exception:
        pass

    # Try data directory
    try:
        data_target = (data_dir / clean_path).resolve()
        if data_target.is_relative_to(data_dir.resolve()) and data_target.exists() and data_target.is_file():
            return FileResponse(data_target)
    except Exception:
        pass

    raise HTTPException(status_code=404, detail=f"❌ File not found: {file_path}")

@router.get("/download")
async def download_file(path: str, filename: str = "download.mp4"):
    """Force download of a file with Content-Disposition attachment."""
    if not path:
        raise HTTPException(status_code=400, detail="❌ Khuyết đường dẫn file download.")

    raw_path = path.replace("\\", "/")
    clean_path = raw_path.lstrip("/\\")
    for prefix in ("api/storage/files/", "storage/files/", "media/", "storage/"):
        if clean_path.startswith(prefix):
            clean_path = clean_path[len(prefix):]

    local_dir = SupabaseStorageService.get_local_storage_dir()
    data_dir = settings.DATA_DIR
    target_file = None

    try:
        local_target = (local_dir / clean_path).resolve()
        if local_target.is_relative_to(local_dir.resolve()) and local_target.exists() and local_target.is_file():
            target_file = local_target
    except Exception:
        pass

    if not target_file:
        try:
            data_target = (data_dir / clean_path).resolve()
            if data_target.is_relative_to(data_dir.resolve()) and data_target.exists() and data_target.is_file():
                target_file = data_target
        except Exception:
            pass

    if target_file:
        return FileResponse(
            path=target_file,
            filename=filename,
            media_type="application/octet-stream",
        )

    raise HTTPException(status_code=404, detail=f"❌ File không tồn tại để tải về: {path}")
