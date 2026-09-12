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
    
    # 1. Direct absolute path check
    p_abs = Path(raw_path)
    if p_abs.is_absolute() and p_abs.exists() and p_abs.is_file():
        return FileResponse(p_abs)

    # Clean relative path prefixes
    clean_path = raw_path.lstrip("/\\")
    for prefix in ("api/storage/files/", "storage/files/", "media/", "storage/"):
        if clean_path.startswith(prefix):
            clean_path = clean_path[len(prefix):]

    # 2. Check local storage dir
    local_target = SupabaseStorageService.get_local_storage_dir() / clean_path
    if local_target.exists() and local_target.is_file():
        return FileResponse(local_target)

    # 3. Check data directory
    data_target = settings.DATA_DIR / clean_path
    if data_target.exists() and data_target.is_file():
        return FileResponse(data_target)

    # 4. Check relative path from current directory
    root_target = Path(clean_path)
    if root_target.exists() and root_target.is_file():
        return FileResponse(root_target)

    raise HTTPException(status_code=404, detail=f"❌ File not found: {file_path}")

@router.get("/download")
async def download_file(path: str, filename: str = "download.mp4"):
    """Force download of a file with Content-Disposition attachment."""
    if not path:
        raise HTTPException(status_code=400, detail="❌ Khuyết đường dẫn file download.")

    raw_path = path.replace("\\", "/")
    target_file: Optional[Path] = None

    # 1. Direct absolute path check
    p_abs = Path(raw_path)
    if p_abs.is_absolute() and p_abs.exists() and p_abs.is_file():
        target_file = p_abs
    else:
        # Clean relative path prefixes
        clean_path = raw_path.lstrip("/\\")
        for prefix in ("api/storage/files/", "storage/files/", "media/", "storage/"):
            if clean_path.startswith(prefix):
                clean_path = clean_path[len(prefix):]

        # 2. Check local storage dir
        local_target = SupabaseStorageService.get_local_storage_dir() / clean_path
        if local_target.exists() and local_target.is_file():
            target_file = local_target
        else:
            # 3. Check data directory
            data_target = settings.DATA_DIR / clean_path
            if data_target.exists() and data_target.is_file():
                target_file = data_target
            else:
                # 4. Check relative path
                root_target = Path(clean_path)
                if root_target.exists() and root_target.is_file():
                    target_file = root_target

    if target_file and target_file.exists() and target_file.is_file():
        return FileResponse(
            path=target_file,
            filename=filename,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )

    raise HTTPException(status_code=404, detail=f"❌ File không tồn tại để tải về: {path}")
