"""
Pollinations AI Image Provider implementation.

Free, fast AI image generation provider supporting customizable resolution,
seed control, and prompt options.
"""

from __future__ import annotations

import random
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from app.core import get_logger
from app.providers.base import (
    GenerationResult,
    ImageProvider,
    QuotaInfo,
    UsageEstimate,
)

logger = get_logger(__name__)


class PollinationsImageProvider(ImageProvider):
    """Pollinations AI Image Provider."""

    @property
    def provider_id(self) -> str:
        return "pollinations"

    @property
    def provider_name(self) -> str:
        return "Pollinations AI (Free)"

    @property
    def is_free(self) -> bool:
        return True

    @property
    def requires_api_key(self) -> bool:
        return False

    async def validate_configuration(self) -> bool:
        """Pollinations AI requires no API key and is publicly accessible."""
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

        cleaned_prompt = prompt.strip()
        encoded_prompt = urllib.parse.quote(cleaned_prompt)

        # Construct Pollinations AI Image Generation Endpoint
        url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?width={width}&height={height}&nologo=true&seed={seed}"
        )
        if model and model != "default":
            url += f"&model={urllib.parse.quote(model)}"

        logger.info(
            "Generating image via Pollinations AI",
            width=width,
            height=height,
            seed=seed,
            prompt_preview=cleaned_prompt[:80],
        )

        try:
            async with httpx.AsyncClient(timeout=25.0, follow_redirects=True) as client:
                res = await client.get(url)
                if res.status_code == 200 and len(res.content) > 5000:
                    output_path = options.get("output_path")
                    if output_path:
                        output_path = Path(output_path)
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        output_path.write_bytes(res.content)

                    return GenerationResult(
                        success=True,
                        file_path=output_path if output_path else None,
                        provider_id=self.provider_id,
                        metadata={
                            "image_bytes": res.content,
                            "width": width,
                            "height": height,
                            "aspect_ratio": aspect_ratio,
                            "seed": seed,
                            "provider": self.provider_id,
                            "model": model,
                            "content_type": res.headers.get("content-type", "image/jpeg"),
                        },
                    )
                else:
                    err_msg = f"Pollinations AI returned HTTP {res.status_code}"
                    logger.warning(err_msg, status=res.status_code)
                    return GenerationResult(
                        success=False,
                        error_message=err_msg,
                        error_code=f"HTTP_{res.status_code}",
                        provider_id=self.provider_id,
                    )
        except Exception as ex:
            logger.error("Pollinations AI image generation error", error=str(ex))
            return GenerationResult(
                success=False,
                error_message=f"Pollinations AI request failed: {str(ex)}",
                error_code="NETWORK_ERROR",
                provider_id=self.provider_id,
            )

    async def estimate_usage(self, prompt: str) -> List[UsageEstimate]:
        return [UsageEstimate(resource_type="images", estimated_amount=1.0, unit="image")]

    async def get_quota(self) -> List[QuotaInfo]:
        return [QuotaInfo(resource_type="images", used=0, limit=None, remaining=None, unit="unlimited")]
