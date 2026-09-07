"""
OpenAI DALL-E Image Provider implementation.

Uses OpenAI DALL-E 3 API with KeyManager failover.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from app.config import get_settings
from app.core import get_logger
from app.providers.base import (
    GenerationResult,
    ImageProvider,
    QuotaInfo,
    UsageEstimate,
)
from app.services.key_manager import get_key_manager

logger = get_logger(__name__)
settings = get_settings()


class OpenAIImageProvider(ImageProvider):
    """OpenAI DALL-E Image Provider."""

    @property
    def provider_id(self) -> str:
        return "openai"

    @property
    def provider_name(self) -> str:
        return "OpenAI DALL-E 3"

    @property
    def is_free(self) -> bool:
        return False

    @property
    def requires_api_key(self) -> bool:
        return True

    async def validate_configuration(self) -> bool:
        key_mgr = get_key_manager()
        key_entry = await key_mgr.get_active_key(self.provider_id)
        return key_entry is not None

    async def generate_image(
        self,
        prompt: str,
        width: int = 1792,
        height: int = 1024,
        aspect_ratio: str = "16:9",
        model: str = "dall-e-3",
        options: Optional[Dict[str, Any]] = None,
    ) -> GenerationResult:
        options = options or {}
        key_mgr = get_key_manager()
        key_entry = await key_mgr.get_active_key(self.provider_id)

        if not key_entry:
            return GenerationResult(
                success=False,
                error_message="No valid OpenAI API key configured.",
                error_code="NO_API_KEY",
                provider_id=self.provider_id,
            )

        url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {key_entry.api_key}",
            "Content-Type": "application/json",
        }

        # DALL-E 3 supports 1792x1024 (16:9 widescreen) or 1024x1024
        size_str = "1792x1024" if aspect_ratio == "16:9" else "1024x1024"

        payload = {
            "model": "dall-e-3",
            "prompt": prompt[:4000],
            "n": 1,
            "size": size_str,
            "response_format": "url",
            "quality": options.get("quality", "standard"),
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.status_code == 429:
                    await key_mgr.report_result(self.provider_id, key_entry.key_id, success=False, status_code=429)
                    return GenerationResult(
                        success=False,
                        error_message="OpenAI API rate limited (429)",
                        error_code="RATE_LIMIT",
                        provider_id=self.provider_id,
                    )

                if res.status_code != 200:
                    fail_msg = f"OpenAI DALL-E error HTTP {res.status_code}: {res.text[:200]}"
                    await key_mgr.report_result(self.provider_id, key_entry.key_id, success=False, status_code=res.status_code)
                    return GenerationResult(
                        success=False,
                        error_message=fail_msg,
                        error_code=f"HTTP_{res.status_code}",
                        provider_id=self.provider_id,
                    )

                data = res.json()
                data_list = data.get("data", [])
                if not data_list or not data_list[0].get("url"):
                    return GenerationResult(
                        success=False,
                        error_message="OpenAI DALL-E returned empty response.",
                        error_code="EMPTY_RESPONSE",
                        provider_id=self.provider_id,
                    )

                img_url = data_list[0]["url"]
                img_dl_res = await client.get(img_url)
                if img_dl_res.status_code == 200 and len(img_dl_res.content) > 1000:
                    output_path = options.get("output_path")
                    if output_path:
                        output_path = Path(output_path)
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        output_path.write_bytes(img_dl_res.content)

                    await key_mgr.report_result(self.provider_id, key_entry.key_id, success=True)
                    return GenerationResult(
                        success=True,
                        file_path=output_path if output_path else None,
                        provider_id=self.provider_id,
                        metadata={
                            "image_bytes": img_dl_res.content,
                            "image_url": img_url,
                            "width": width,
                            "height": height,
                            "aspect_ratio": aspect_ratio,
                            "provider": self.provider_id,
                            "model": "dall-e-3",
                        },
                    )

                return GenerationResult(
                    success=False,
                    error_message=f"Failed downloading DALL-E image from {img_url}",
                    error_code="DOWNLOAD_FAILED",
                    provider_id=self.provider_id,
                )

        except Exception as ex:
            logger.error("OpenAI DALL-E image generation exception", error=str(ex))
            return GenerationResult(
                success=False,
                error_message=f"OpenAI DALL-E error: {str(ex)}",
                error_code="EXCEPTION",
                provider_id=self.provider_id,
            )

    async def estimate_usage(self, prompt: str) -> List[UsageEstimate]:
        return [UsageEstimate(resource_type="images", estimated_amount=1.0, unit="image")]

    async def get_quota(self) -> List[QuotaInfo]:
        return [QuotaInfo(resource_type="images", used=None, limit=None, remaining=None, unit="images")]
