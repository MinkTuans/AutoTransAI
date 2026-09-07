"""
fal.ai Image Provider implementation.

Uses fal.ai REST API for FLUX and image generation models with KeyManager failover.
"""

from __future__ import annotations

import asyncio
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


class FalImageProvider(ImageProvider):
    """fal.ai FLUX & Image Generation Provider."""

    @property
    def provider_id(self) -> str:
        return "fal"

    @property
    def provider_name(self) -> str:
        return "fal.ai Image Generation"

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
        width: int = 1280,
        height: int = 720,
        aspect_ratio: str = "16:9",
        model: str = "fal-ai/flux/schnell",
        options: Optional[Dict[str, Any]] = None,
    ) -> GenerationResult:
        options = options or {}
        key_mgr = get_key_manager()
        key_entry = await key_mgr.get_active_key(self.provider_id)

        if not key_entry:
            return GenerationResult(
                success=False,
                error_message="No valid fal.ai API key configured.",
                error_code="NO_API_KEY",
                provider_id=self.provider_id,
            )

        model_endpoint = model if "/" in model else "fal-ai/flux/schnell"
        url = f"https://queue.fal.run/{model_endpoint}"

        headers = {
            "Authorization": f"Key {key_entry.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "prompt": prompt,
            "image_size": {
                "width": width,
                "height": height,
            },
            "num_images": 1,
            "enable_safety_checker": True,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.status_code == 429:
                    await key_mgr.report_result(self.provider_id, key_entry.key_id, success=False, status_code=429)
                    return GenerationResult(
                        success=False,
                        error_message="fal.ai API key rate limited (429)",
                        error_code="RATE_LIMIT",
                        provider_id=self.provider_id,
                    )

                if res.status_code not in (200, 202):
                    fail_msg = f"fal.ai API error HTTP {res.status_code}: {res.text[:200]}"
                    await key_mgr.report_result(self.provider_id, key_entry.key_id, success=False, status_code=res.status_code)
                    return GenerationResult(
                        success=False,
                        error_message=fail_msg,
                        error_code=f"HTTP_{res.status_code}",
                        provider_id=self.provider_id,
                    )

                data = res.json()
                image_url = None

                if "images" in data and len(data["images"]) > 0:
                    image_url = data["images"][0].get("url")
                elif "response_url" in data or "status_url" in data:
                    # Async polling task
                    status_url = data.get("status_url")
                    response_url = data.get("response_url")
                    max_polls = 40

                    for _ in range(max_polls):
                        await asyncio.sleep(2.0)
                        poll_res = await client.get(status_url, headers=headers)
                        if poll_res.status_code == 200:
                            p_data = poll_res.json()
                            if p_data.get("status") == "COMPLETED":
                                break
                            elif p_data.get("status") == "FAILED":
                                return GenerationResult(
                                    success=False,
                                    error_message="fal.ai task failed during processing.",
                                    error_code="TASK_FAILED",
                                    provider_id=self.provider_id,
                                )

                    final_res = await client.get(response_url, headers=headers)
                    if final_res.status_code == 200:
                        f_data = final_res.json()
                        imgs = f_data.get("images", [])
                        if imgs:
                            image_url = imgs[0].get("url")

                if not image_url:
                    return GenerationResult(
                        success=False,
                        error_message="fal.ai failed to return image URL.",
                        error_code="MISSING_IMAGE_URL",
                        provider_id=self.provider_id,
                    )

                # Download image bytes
                img_dl_res = await client.get(image_url)
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
                            "image_url": image_url,
                            "width": width,
                            "height": height,
                            "aspect_ratio": aspect_ratio,
                            "provider": self.provider_id,
                            "model": model,
                        },
                    )

                return GenerationResult(
                    success=False,
                    error_message=f"Failed to download image from fal.ai URL: {image_url}",
                    error_code="DOWNLOAD_FAILED",
                    provider_id=self.provider_id,
                )

        except Exception as ex:
            logger.error("fal.ai image generation exception", error=str(ex))
            return GenerationResult(
                success=False,
                error_message=f"fal.ai error: {str(ex)}",
                error_code="EXCEPTION",
                provider_id=self.provider_id,
            )

    async def estimate_usage(self, prompt: str) -> List[UsageEstimate]:
        return [UsageEstimate(resource_type="credits", estimated_amount=1.0, unit="credit")]

    async def get_quota(self) -> List[QuotaInfo]:
        return [QuotaInfo(resource_type="credits", used=None, limit=None, remaining=None, unit="credits")]
