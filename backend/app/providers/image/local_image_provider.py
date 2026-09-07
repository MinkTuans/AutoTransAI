"""
Local Fallback Image Provider implementation.

Generates visual scenery image using Picsum sceneries or FFmpeg dark gradient canvas.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from app.core import get_logger
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
        output_path = options.get("output_path")

        if output_path:
            out_file = Path(output_path)
        else:
            out_file = Path("data") / "tmp_thumbnail.jpg"

        out_file.parent.mkdir(parents=True, exist_ok=True)
        image_bytes = None

        # 1. Try fetching high-res scenery image from Picsum
        try:
            picsum_url = f"https://picsum.photos/seed/{seed}/{width}/{height}"
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                res = await client.get(picsum_url)
                if res.status_code == 200 and len(res.content) > 5000:
                    out_file.write_bytes(res.content)
                    image_bytes = res.content
        except Exception as ex:
            logger.debug("Picsum scenery fetch bypassed", error=str(ex))

        # 2. Fallback to FFmpeg cinematic dark gradient canvas if completely offline
        if not image_bytes:
            try:
                ffmpeg_bin = get_ffmpeg_executable()
                cmd = [
                    ffmpeg_bin, "-y",
                    "-f", "lavfi",
                    "-i", f"color=c=0x0f172a:s={width}x{height}:d=1",
                    "-vframes", "1",
                    str(out_file.resolve())
                ]
                await run_ffmpeg_with_progress_async(cmd, duration_sec=1.0)
                if out_file.exists():
                    image_bytes = out_file.read_bytes()
            except Exception as ffmpeg_err:
                logger.error("FFmpeg fallback thumbnail canvas failed", error=str(ffmpeg_err))

        if image_bytes:
            return GenerationResult(
                success=True,
                file_path=out_file,
                provider_id=self.provider_id,
                metadata={
                    "image_bytes": image_bytes,
                    "width": width,
                    "height": height,
                    "aspect_ratio": aspect_ratio,
                    "provider": self.provider_id,
                    "model": model,
                },
            )

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
