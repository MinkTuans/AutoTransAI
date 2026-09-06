"""
Supabase Storage Service.

Provides object storage for videos, audio, TTS files, and media using Supabase Storage API.
Falls back to local persistent storage (data/supabase_storage/) for offline development when credentials are omitted.
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

_supabase_client = None


def _get_supabase_client():
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    url = settings.SUPABASE_URL
    key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY

    if url and key:
        try:
            from supabase import create_client
            _supabase_client = create_client(url, key)
            logger.info("Initialized Supabase Storage client", url=url)
            return _supabase_client
        except Exception as e:
            logger.warning("Failed to initialize Supabase client", error=str(e))

    return None


class SupabaseStorageService:
    """Storage service supporting Supabase Storage (private/public buckets) and local fallback."""

    @staticmethod
    def get_local_storage_dir() -> Path:
        p = settings.DATA_DIR / "supabase_storage"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @classmethod
    def _get_bucket_name(cls, is_public: bool = False) -> str:
        if is_public:
            return settings.SUPABASE_STORAGE_BUCKET_PUBLIC or "autotransai-public"
        return settings.SUPABASE_STORAGE_BUCKET_PRIVATE or "autotransai-private"

    @classmethod
    async def upload_file(
        cls,
        local_path: Path,
        object_key: str,
        content_type: Optional[str] = None,
        is_public: bool = False,
    ) -> Tuple[str, str]:
        """
        Upload file to Supabase storage (or local fallback).

        Returns:
            Tuple of (object_key, access_url)
        """
        local_path = Path(local_path)
        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found for upload: {local_path}")

        object_key = object_key.lstrip("/\\").replace("\\", "/")
        supabase = _get_supabase_client()

        if supabase:
            bucket = cls._get_bucket_name(is_public=is_public)
            try:
                def _do_supabase_upload():
                    with open(local_path, "rb") as f:
                        file_data = f.read()
                    opts = {"upsert": "true"}
                    if content_type:
                        opts["content-type"] = content_type
                    return supabase.storage.from_(bucket).upload(
                        path=object_key,
                        file=file_data,
                        file_options=opts
                    )

                await asyncio.to_thread(_do_supabase_upload)
                logger.info("Uploaded object to Supabase Storage", bucket=bucket, key=object_key)

                if is_public:
                    url_res = supabase.storage.from_(bucket).get_public_url(object_key)
                    url = url_res if isinstance(url_res, str) else str(url_res)
                else:
                    url = f"/api/storage/files/{object_key}"

                return object_key, url
            except Exception as e:
                logger.error("Supabase Storage upload error, falling back to local persistent store", error=str(e), key=object_key)

        # Fallback local store
        dest = cls.get_local_storage_dir() / object_key
        dest.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(shutil.copy2, local_path, dest)

        url = f"/api/storage/files/{object_key}"
        logger.info("Stored object in persistent local storage", key=object_key, path=str(dest))
        return object_key, url

    @classmethod
    async def download_file(cls, object_key: str, target_path: Path, is_public: bool = False) -> bool:
        """Download object from Supabase or Local storage to target local path."""
        object_key = object_key.lstrip("/\\").replace("\\", "/")
        target_path = Path(target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        supabase = _get_supabase_client()
        if supabase:
            bucket = cls._get_bucket_name(is_public=is_public)
            try:
                def _do_supabase_download():
                    res = supabase.storage.from_(bucket).download(object_key)
                    target_path.write_bytes(res)
                    return True

                await asyncio.to_thread(_do_supabase_download)
                return target_path.exists()
            except Exception as e:
                logger.warning("Supabase Storage download error", error=str(e), key=object_key)

        # Fallback local
        local_src = cls.get_local_storage_dir() / object_key
        if local_src.exists():
            await asyncio.to_thread(shutil.copy2, local_src, target_path)
            return True

        return False

    @classmethod
    async def delete_file(cls, object_key: str, is_public: bool = False) -> bool:
        """Delete object from Supabase or Local storage."""
        if not object_key:
            return False

        object_key = object_key.lstrip("/\\").replace("\\", "/")
        deleted = False

        supabase = _get_supabase_client()
        if supabase:
            bucket = cls._get_bucket_name(is_public=is_public)
            try:
                def _do_supabase_delete():
                    supabase.storage.from_(bucket).remove([object_key])
                    return True

                await asyncio.to_thread(_do_supabase_delete)
                logger.info("Deleted object from Supabase Storage", bucket=bucket, key=object_key)
                deleted = True
            except Exception as e:
                logger.warning("Failed to delete object from Supabase Storage", error=str(e), key=object_key)

        local_src = cls.get_local_storage_dir() / object_key
        if local_src.exists():
            try:
                local_src.unlink()
                deleted = True
            except Exception:
                pass

        return deleted

    @classmethod
    def get_url(cls, object_key: str, is_public: bool = False) -> str:
        """Get accessible URL for an object key."""
        if not object_key:
            return ""
        object_key = object_key.lstrip("/\\").replace("\\", "/")

        supabase = _get_supabase_client()
        if supabase and is_public:
            bucket = cls._get_bucket_name(is_public=True)
            res = supabase.storage.from_(bucket).get_public_url(object_key)
            return res if isinstance(res, str) else str(res)

        return f"/api/storage/files/{object_key}"

    @classmethod
    def get_signed_url(cls, object_key: str, expires_in: int = 3600, is_public: bool = False) -> str:
        """Generate temporary signed URL for object download."""
        if not object_key:
            return ""
        object_key = object_key.lstrip("/\\").replace("\\", "/")

        supabase = _get_supabase_client()
        if supabase:
            bucket = cls._get_bucket_name(is_public=is_public)
            try:
                res = supabase.storage.from_(bucket).create_signed_url(object_key, expires_in)
                if isinstance(res, dict):
                    return res.get("signedURL", res.get("signed_url", ""))
                elif hasattr(res, "signed_url"):
                    return getattr(res, "signed_url")
                return str(res)
            except Exception as e:
                logger.warning("Failed to create Supabase signed URL", error=str(e))

        return cls.get_url(object_key, is_public=is_public)

    @classmethod
    async def delete_project_files(cls, project_id: str) -> int:
        """Delete all files under prefix projects/{project_id}/ or translator/jobs/{project_id}/."""
        if not project_id:
            return 0

        count = 0
        prefixes = [f"projects/{project_id}/", f"translator/jobs/{project_id}/"]

        supabase = _get_supabase_client()
        if supabase:
            for bucket in [cls._get_bucket_name(False), cls._get_bucket_name(True)]:
                try:
                    for prefix in prefixes:
                        files_res = supabase.storage.from_(bucket).list(prefix)
                        if files_res and isinstance(files_res, list):
                            keys_to_del = [f"{prefix}{item['name']}" for item in files_res if 'name' in item]
                            if keys_to_del:
                                supabase.storage.from_(bucket).remove(keys_to_del)
                                count += len(keys_to_del)
                except Exception as e:
                    logger.warning("Error deleting project files from Supabase Storage", error=str(e), project_id=project_id)

        # Local cleanup
        for prefix in prefixes:
            local_p = cls.get_local_storage_dir() / prefix
            if local_p.exists() and local_p.is_dir():
                try:
                    shutil.rmtree(local_p)
                except Exception:
                    pass

        return count


# Storage service singleton instance
storage_service = SupabaseStorageService()
