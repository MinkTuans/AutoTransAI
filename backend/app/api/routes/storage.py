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
    """Stream media file stored in persistent Supabase/local storage."""
    file_path = file_path.lstrip("/\\").replace("\\", "/")
    
    # 1. Check local supabase_storage
    local_target = SupabaseStorageService.get_local_storage_dir() / file_path
    if local_target.exists() and local_target.is_file():
        return FileResponse(local_target)

    # 2. Check data directory
    data_target = settings.DATA_DIR / file_path
    if data_target.exists() and data_target.is_file():
        return FileResponse(data_target)

    # 3. Check relative path from root
    root_target = Path(file_path)
    if root_target.exists() and root_target.is_file():
        return FileResponse(root_target)

    raise HTTPException(status_code=404, detail=f"❌ File not found: {file_path}")
