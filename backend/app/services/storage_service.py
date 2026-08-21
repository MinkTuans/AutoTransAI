"""
Cloudflare R2 Storage Service.

Provides S3-compatible persistent object storage for videos, audio, TTS files, and media.
Uses Cloudflare R2 bucket via boto3 when credentials are provided in .env.
Falls back seamlessly to local persistent object storage (data/r2_storage/) when credentials are omitted.
"""

from __future__ import annotations

import os
import shutil
import asyncio
from pathlib import Path
from typing import Optional, Tuple

from app.config import get_settings
from app.core import get_logger

logger = get_logger(__name__)
settings = get_settings()

_r2_client = None

def _get_boto_client():
    global _r2_client
    if _r2_client is not None:
        return _r2_client

    acc_id = settings.R2_ACCOUNT_ID
    key_id = settings.R2_ACCESS_KEY_ID
    secret_key = settings.R2_SECRET_ACCESS_KEY

    if acc_id and key_id and secret_key:
        try:
            import boto3
            from botocore.config import Config

            endpoint_url = settings.R2_ENDPOINT_URL or f"https://{acc_id}.r2.cloudflarestorage.com"
            _r2_client = boto3.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=key_id,
                aws_secret_access_key=secret_key,
                config=Config(signature_version="s3v4"),
                region_name="auto",
            )
            logger.info("Initialized Cloudflare R2 boto3 client", bucket=settings.R2_BUCKET_NAME)
            return _r2_client
        except Exception as e:
            logger.warning("Failed to initialize boto3 R2 client", error=str(e))
    
    return None


class R2StorageService:
    """Service for interacting with Cloudflare R2 object storage."""

    @staticmethod
    def get_local_storage_dir() -> Path:
        p = settings.DATA_DIR / "r2_storage"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @classmethod
    async def upload_file(
        cls,
        local_path: Path,
        object_key: str,
        content_type: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Upload file to R2 storage (or local R2 emulator).

        Returns:
            Tuple of (object_key, access_url)
        """
        local_path = Path(local_path)
        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found for R2 upload: {local_path}")

        object_key = object_key.lstrip("/\\").replace("\\", "/")
        client = _get_boto_client()

        if client:
            try:
                extra_args = {}
                if content_type:
                    extra_args["ContentType"] = content_type

                await asyncio.to_thread(
                    client.upload_file,
                    str(local_path),
                    settings.R2_BUCKET_NAME,
                    object_key,
                    ExtraArgs=extra_args if extra_args else None
                )
                logger.info("Uploaded object to Cloudflare R2", key=object_key)

                if settings.R2_PUBLIC_DOMAIN:
                    domain = settings.R2_PUBLIC_DOMAIN.rstrip("/")
                    url = f"{domain}/{object_key}"
                else:
                    url = f"/api/storage/files/{object_key}"

                return object_key, url
            except Exception as e:
                logger.error("Cloudflare R2 upload error, falling back to local persistent store", error=str(e), key=object_key)

        # Fallback local store
        dest = cls.get_local_storage_dir() / object_key
        dest.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(shutil.copy2, local_path, dest)

        url = f"/api/storage/files/{object_key}"
        logger.info("Stored object in persistent local R2 storage", key=object_key, path=str(dest))
        return object_key, url

    @classmethod
    async def download_file(cls, object_key: str, target_path: Path) -> bool:
        """Download object from R2 to local path."""
        object_key = object_key.lstrip("/\\").replace("\\", "/")
        target_path = Path(target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        client = _get_boto_client()
        if client:
            try:
                await asyncio.to_thread(
                    client.download_file,
                    settings.R2_BUCKET_NAME,
                    object_key,
                    str(target_path)
                )
                return target_path.exists()
            except Exception as e:
                logger.warning("R2 download error", error=str(e), key=object_key)

        # Fallback local
        local_src = cls.get_local_storage_dir() / object_key
        if local_src.exists():
            await asyncio.to_thread(shutil.copy2, local_src, target_path)
            return True

        return False

    @classmethod
    async def delete_file(cls, object_key: str) -> bool:
        """Delete object from R2 storage."""
        if not object_key:
            return False

        object_key = object_key.lstrip("/\\").replace("\\", "/")
        deleted = False

        client = _get_boto_client()
        if client:
            try:
                await asyncio.to_thread(
                    client.delete_object,
                    Bucket=settings.R2_BUCKET_NAME,
                    Key=object_key
                )
                logger.info("Deleted object from Cloudflare R2", key=object_key)
                deleted = True
            except Exception as e:
                logger.warning("Failed to delete object from Cloudflare R2", error=str(e), key=object_key)

        local_src = cls.get_local_storage_dir() / object_key
        if local_src.exists():
            try:
                local_src.unlink()
                deleted = True
            except Exception:
                pass

        return deleted

    @classmethod
    def get_url(cls, object_key: str) -> str:
        """Get accessible URL for an object key."""
        if not object_key:
            return ""
        object_key = object_key.lstrip("/\\").replace("\\", "/")
        if settings.R2_PUBLIC_DOMAIN:
            return f"{settings.R2_PUBLIC_DOMAIN.rstrip('/')}/{object_key}"
        return f"/api/storage/files/{object_key}"


storage_service = R2StorageService()
