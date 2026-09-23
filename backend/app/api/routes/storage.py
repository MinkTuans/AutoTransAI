"""
Storage API Routes.

Serves persistent object files for media assets and downloads.
"""

from __future__ import annotations

from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.services.storage_service import SupabaseStorageService
from app.config import get_settings

router = APIRouter(prefix="/api/storage", tags=["storage"])
settings = get_settings()

MEDIA_SUFFIXES = {
    ".aac", ".ass", ".avi", ".bmp", ".flac", ".gif", ".jpeg", ".jpg",
    ".m4a", ".m4v", ".mkv", ".mov", ".mp3", ".mp4", ".ogg",
    ".opus", ".png", ".srt", ".ssa", ".tif", ".tiff", ".vtt",
    ".wav", ".webm", ".webp",
}


def resolve_media_file(file_path: str, storage_root: Path, data_dir: Path) -> Path | None:
    """Resolve public media in storage or the legacy data/translator tree."""
    clean_path = file_path.replace("\\", "/").lstrip("/")
    for prefix in ("api/storage/files/", "storage/files/", "media/", "storage/"):
        if clean_path.startswith(prefix):
            clean_path = clean_path[len(prefix):]

    parts = Path(clean_path).parts
    if not parts or ".." in parts or any(part.startswith(".") for part in parts):
        return None
    if Path(clean_path).suffix.lower() not in MEDIA_SUFFIXES:
        return None

    storage_root = storage_root.resolve()
    data_root = data_dir.resolve()
    legacy_root = data_root / "translator"
    for root in (storage_root, legacy_root):
        try:
            target = (root / clean_path if root == storage_root else data_root / clean_path).resolve()
            is_file = target.is_file()
        except (OSError, RuntimeError):
            continue
        if not target.is_relative_to(root) or not is_file:
            continue
        if target.is_relative_to(data_root) and not target.is_relative_to(legacy_root):
            continue
        if target.suffix.lower() in MEDIA_SUFFIXES and not any(part.startswith(".") for part in target.relative_to(root).parts):
            return target
    return None


class MediaFiles(StaticFiles):
    """Serve the same validated media files as the storage API at /media."""

    def __init__(self, *, data_dir: Path, storage_root: Path):
        self.storage_root = storage_root
        super().__init__(directory=data_dir)

    def lookup_path(self, path: str):
        target = resolve_media_file(path, self.storage_root, Path(self.directory))
        if target is None:
            return "", None
        return str(target), target.stat()


@router.get("/files/{file_path:path}")
async def get_storage_file(file_path: str):
    """Stream media file stored in persistent local storage."""
    target = resolve_media_file(file_path, SupabaseStorageService.get_local_storage_dir(), settings.DATA_DIR)
    if target:
        return FileResponse(target)
    raise HTTPException(status_code=404, detail=f"❌ File not found: {file_path}")

@router.get("/download")
async def download_file(path: str, filename: str = "download.mp4"):
    """Force download of a file with Content-Disposition attachment."""
    if not path:
        raise HTTPException(status_code=400, detail="❌ Khuyết đường dẫn file download.")

    target_file = resolve_media_file(path, SupabaseStorageService.get_local_storage_dir(), settings.DATA_DIR)
    if target_file:
        return FileResponse(
            path=target_file,
            filename=filename,
            media_type="application/octet-stream",
        )

    raise HTTPException(status_code=404, detail=f"❌ File không tồn tại để tải về: {path}")
