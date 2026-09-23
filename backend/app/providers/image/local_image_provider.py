"""
Local Fallback Image Provider implementation.

Generates visual scenery image using Picsum sceneries or FFmpeg dark gradient canvas.
"""

from __future__ import annotations

import random
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from app.config import get_settings
from app.core import get_logger
from app.providers.image.catalog_media import (
    download_image, validate_image_bytes,
)
from app.media.ffmpeg_process import get_ffmpeg_executable, run_ffmpeg_with_progress_async
from app.providers.base import (
    GenerationResult,
    ImageProvider,
    QuotaInfo,
    UsageEstimate,
)

logger = get_logger(__name__)


class LocalImageProvider(ImageProvider):
    """Local / Scenery Fallback Image Provider."""

    @property
    def provider_id(self) -> str:
        return "local_image"

    @property
    def provider_name(self) -> str:
        return "Local Visual Scenery (Offline Fallback)"

    @property
    def is_free(self) -> bool:
        return True

    @property
    def requires_api_key(self) -> bool:
        return False

    async def validate_configuration(self) -> bool:
        return True

    async def generate_image(
        self,
        prompt: str,
        width: int = 1280,
        height: int = 720,
        aspect_ratio: str = "16:9",
        model: str = "default",
        options: Optional[Dict[str, Any]] = None,
    ) -> GenerationResult:
        options = options or {}
        seed = options.get("seed") or random.randint(1000, 999999)
        # No application caller needs a local-provider output path. Refusing it
        # avoids partial FFmpeg output overwriting an existing caller file.
        if options.get("output_path") is not None:
            return GenerationResult(False, provider_id=self.provider_id,
                                    error_code="INVALID_OUTPUT_PATH",
                                    error_message="Local image output path is not supported.")

        # 1. Try fetching high-res scenery image from Picsum
        try:
            picsum_url = f"https://picsum.photos/seed/{seed}/{width}/{height}"
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
                image_bytes = await download_image(client, picsum_url, max_redirects=3)
            return GenerationResult(
                success=True, provider_id=self.provider_id,
                metadata={"image_bytes": image_bytes, "width": width, "height": height,
                          "aspect_ratio": aspect_ratio, "provider": self.provider_id,
                          "model": model},
            )
        except Exception:
            logger.debug("Picsum scenery fetch bypassed", code="provider_unavailable")

        # 2. Fallback to FFmpeg cinematic dark gradient canvas if completely offline
        out_file = None
        try:
            root = get_settings().DATA_DIR.resolve()
            root.mkdir(parents=True, exist_ok=True)
            descriptor, path = tempfile.mkstemp(prefix="thumbnail_", suffix=".jpg", dir=root)
            os.close(descriptor)
            out_file = Path(path)
            ffmpeg_bin = get_ffmpeg_executable()
            cmd = [
                ffmpeg_bin, "-y", "-f", "lavfi",
                "-i", f"color=c=0x0f172a:s={width}x{height}:d=1",
                "-vframes", "1", str(out_file.resolve()),
            ]
            await run_ffmpeg_with_progress_async(cmd, duration_sec=1.0)
            image_bytes = validate_image_bytes(out_file.read_bytes())
            return GenerationResult(
                success=True, provider_id=self.provider_id,
                metadata={"image_bytes": image_bytes, "width": width, "height": height,
                          "aspect_ratio": aspect_ratio, "provider": self.provider_id,
                          "model": model},
            )
        except Exception:
            logger.error("FFmpeg fallback thumbnail canvas failed", code="provider_unavailable")
        finally:
            if out_file is not None:
                out_file.unlink(missing_ok=True)

        return GenerationResult(
            success=False,
            error_message="Local image provider generation failed.",
            error_code="LOCAL_GEN_FAILED",
            provider_id=self.provider_id,
        )

    async def estimate_usage(self, prompt: str) -> List[UsageEstimate]:
        return [UsageEstimate(resource_type="images", estimated_amount=1.0, unit="image")]

    async def get_quota(self) -> List[QuotaInfo]:
        return [QuotaInfo(resource_type="images", used=0, limit=None, remaining=None, unit="unlimited")]
