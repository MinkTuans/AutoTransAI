"""
Local File Storage Service.

Provides high-performance, structured local object storage for videos, audio, TTS files,
subtitles, thumbnails, and final output media under `storage/projects/{project_id}/...`.
"""

from __future__ import annotations

import os
import shutil
import asyncio
from pathlib import Path
from typing import Optional, Tuple, List

from app.config import get_settings
from app.core import get_logger

logger = get_logger(__name__)
settings = get_settings()


class LocalStorageService:
    """Pure Local File Storage service operating directly on local disk storage."""

    @staticmethod
    def get_local_storage_dir() -> Path:
        """Get root local storage directory (storage/ or data/storage)."""
        p = getattr(settings, "STORAGE_ROOT", None) or (settings.DATA_DIR / "storage")
        p.mkdir(parents=True, exist_ok=True)
        return p

    @classmethod
    def create_project_directories(cls, project_id: str) -> Path:
        """Create structured subdirectory tree for a project under storage/projects/{project_id}."""
        if not project_id:
            raise ValueError("project_id is required")

        proj_dir = cls.get_local_storage_dir() / "projects" / project_id
        subdirs = [
            proj_dir / "videos" / "source",
            proj_dir / "videos" / "processed",
            proj_dir / "audio" / "original",
            proj_dir / "audio" / "extracted",
            proj_dir / "audio" / "dubbed",
            proj_dir / "subtitles",
            proj_dir / "thumbnails",
            proj_dir / "outputs",
            proj_dir / "temporary",
        ]
        for sd in subdirs:
            sd.mkdir(parents=True, exist_ok=True)
        return proj_dir

    @classmethod
    async def upload_file(
        cls,
        local_path: Path,
        object_key: str,
        content_type: Optional[str] = None,
        is_public: bool = False,
    ) -> Tuple[str, str]:
        """
        Store local file into structured persistent local storage.

        Returns:
            Tuple of (object_key, access_url)
        """
        local_path = Path(local_path)
        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found for storage: {local_path}")

        object_key = object_key.lstrip("/\\").replace("\\", "/")
        dest = cls.get_local_storage_dir() / object_key
        dest.parent.mkdir(parents=True, exist_ok=True)

        if local_path.resolve() != dest.resolve():
            await asyncio.to_thread(shutil.copy2, local_path, dest)

        url = f"/api/storage/files/{object_key}"
        logger.info("Stored object in persistent local storage", key=object_key, path=str(dest))
        return object_key, url

    @classmethod
    async def download_file(cls, object_key: str, target_path: Path, is_public: bool = False) -> bool:
        """Download/Copy object from local storage to target local path."""
        object_key = object_key.lstrip("/\\").replace("\\", "/")
        target_path = Path(target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        local_src = cls.get_local_storage_dir() / object_key
        if local_src.exists():
            if local_src.resolve() != target_path.resolve():
                await asyncio.to_thread(shutil.copy2, local_src, target_path)
            return True

        return False

    @classmethod
    async def delete_file(cls, object_key: str, is_public: bool = False) -> bool:
        """Delete file from local storage."""
        if not object_key:
            return False

        object_key = object_key.lstrip("/\\").replace("\\", "/")
        local_src = cls.get_local_storage_dir() / object_key
        if local_src.exists():
            try:
                local_src.unlink()
                logger.info("Deleted object from local storage", key=object_key)
                return True
            except Exception as e:
                logger.warning("Failed to delete file from local storage", error=str(e), key=object_key)

        return False

    @classmethod
    def get_url(cls, object_key: str, is_public: bool = False) -> str:
        """Get accessible URL path for an object key."""
        if not object_key:
            return ""
        object_key = object_key.lstrip("/\\").replace("\\", "/")
        return f"/api/storage/files/{object_key}"

    @classmethod
    def get_signed_url(cls, object_key: str, expires_in: int = 3600, is_public: bool = False) -> str:
        """Generate accessible local URL for object download."""
        return cls.get_url(object_key, is_public=is_public)

    @classmethod
    async def delete_project_files(cls, project_id: str) -> int:
        """Delete all local files under projects/{project_id}/ or translator/jobs/{project_id}/."""
        if not project_id:
            return 0

        count = 0
        prefixes = [f"projects/{project_id}", f"translator/jobs/{project_id}"]

        for prefix in prefixes:
            local_p = cls.get_local_storage_dir() / prefix
            if local_p.exists():
                try:
                    if local_p.is_dir():
                        shutil.rmtree(local_p)
                    else:
                        local_p.unlink()
                    count += 1
                    logger.info("Cleaned up local project storage directory", path=str(local_p))
                except Exception as e:
                    logger.warning("Error deleting local project files", error=str(e), project_id=project_id)

        return count


# Aliases for 100% backward compatibility
SupabaseStorageService = LocalStorageService
storage_service = LocalStorageService()


async def upload_file_to_r2(local_path: str | Path, object_key: str) -> str:
    """Helper alias for uploading file to persistent local storage (formerly R2)."""
    key, _url = await LocalStorageService.upload_file(Path(local_path), object_key)
    return key
