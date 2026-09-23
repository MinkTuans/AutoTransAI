"""
fal.ai Image Provider implementation.

Uses fal.ai REST API for FLUX and image generation models with KeyManager failover.
"""

from __future__ import annotations

import asyncio
import re
from typing import Any, Dict, List, Optional

import httpx

from app.providers.image.catalog_media import (
    CatalogImageError, download_image, request_json, validate_public_https_url, validated_output_path,
)
from app.providers.request_target import resolve_request_target
from app.services.ai_routing import RouteTarget
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
        *,
        route_target: RouteTarget | None = None,
        api_key: str | None = None,
    ) -> GenerationResult:
        if route_target is not None:
            return await self._generate_catalog_image(prompt, width, height, route_target, api_key)
        if api_key is not None:
            raise ValueError("A request credential requires a route target.")
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
            output_path = validated_output_path(options.get("output_path"), settings.DATA_DIR)
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=False) as client:
                data = await request_json(client, "POST", url, headers=headers,
                                          payload=payload, accepted=(200, 202))
                image_url = None

                if isinstance(data.get("images"), list) and data["images"] and isinstance(data["images"][0], dict):
                    image_url = data["images"][0].get("url")
                elif "response_url" in data or "status_url" in data:
                    # Async polling task
                    status_url = await validate_public_https_url(data.get("status_url"), expected_host="queue.fal.run")
                    response_url = await validate_public_https_url(data.get("response_url"), expected_host="queue.fal.run")
                    max_polls = 40

                    for _ in range(max_polls):
                        await asyncio.sleep(2.0)
                        p_data = await request_json(client, "GET", status_url, headers=headers)
                        if p_data.get("status") == "COMPLETED":
                            break
                        if p_data.get("status") in ("FAILED", "CANCELED"):
                            raise CatalogImageError("provider_unavailable")
                    else:
                        raise CatalogImageError("timeout")

                    f_data = await request_json(client, "GET", response_url, headers=headers)
                    imgs = f_data.get("images", [])
                    if isinstance(imgs, list) and imgs and isinstance(imgs[0], dict):
                        image_url = imgs[0].get("url")

                if not image_url:
                    return GenerationResult(
                        success=False,
                        error_message="fal.ai failed to return image URL.",
                        error_code="MISSING_IMAGE_URL",
                        provider_id=self.provider_id,
                    )

                # Download image bytes
                image_bytes = await download_image(client, image_url)
                if output_path:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_bytes(image_bytes)

                await key_mgr.report_result(self.provider_id, key_entry.key_id, success=True)
                return GenerationResult(
                    success=True,
                    file_path=output_path,
                    provider_id=self.provider_id,
                    metadata={"image_bytes": image_bytes, "width": width, "height": height,
                              "aspect_ratio": aspect_ratio, "provider": self.provider_id,
                              "model": model},
                )

        except CatalogImageError as error:
            if error.status_code:
                await key_mgr.report_result(self.provider_id, key_entry.key_id,
                                            success=False, status_code=error.status_code)
            return GenerationResult(
                success=False, provider_id=self.provider_id,
                error_code="RATE_LIMIT" if error.status_code == 429 else
                f"HTTP_{error.status_code}" if error.status_code else error.code.upper(),
                error_message=str(error),
            )
        except Exception:
            logger.error("fal.ai image generation exception", code="provider_unavailable")
            return GenerationResult(
                success=False,
                error_message="fal.ai request failed.",
                error_code="EXCEPTION",
                provider_id=self.provider_id,
            )

    async def _generate_catalog_image(
        self, prompt: str, width: int, height: int,
        route_target: RouteTarget, api_key: str | None,
    ) -> GenerationResult:
        model_id, secret = resolve_request_target(
            route_target, api_key, provider_id=self.provider_id,
            capabilities=("IMAGE_GENERATION",), legacy_model=None, legacy_key=None,
        )
        if (len(model_id) > 255 or not re.fullmatch(r"[A-Za-z0-9_-]+(?:/[A-Za-z0-9_.-]+)+", model_id)
                or any(part in (".", "..") for part in model_id.split("/"))):
            return GenerationResult(False, provider_id=self.provider_id,
                                    error_code="CAPABILITY_MISMATCH",
                                    error_message="Image generation failed: capability_mismatch")
        headers = {"Authorization": f"Key {secret}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=False) as client:
                payload = await request_json(
                    client, "POST",
                    f"https://queue.fal.run/{model_id}", headers=headers,
                    payload={"prompt": prompt, "image_size": {"width": width, "height": height},
                             "num_images": 1, "enable_safety_checker": True},
                    accepted=(200, 202),
                )
                images = payload.get("images")
                if not images:
                    status_url = await validate_public_https_url(
                        payload.get("status_url"), expected_host="queue.fal.run")
                    response_url = await validate_public_https_url(
                        payload.get("response_url"), expected_host="queue.fal.run")
                    for _ in range(12):
                        state = (await request_json(client, "GET", status_url, headers=headers)).get("status")
                        if state == "COMPLETED":
                            break
                        if state in ("FAILED", "CANCELED"):
                            raise CatalogImageError("provider_unavailable")
                        await asyncio.sleep(1)
                    else:
                        raise CatalogImageError("timeout")
                    images = (await request_json(client, "GET", response_url, headers=headers)).get("images")
                if not isinstance(images, list) or not images or not isinstance(images[0], dict):
                    raise CatalogImageError("invalid_output")
                image_bytes = await download_image(client, images[0].get("url"))
            return GenerationResult(
                success=True, provider_id=self.provider_id,
                metadata={"image_bytes": image_bytes, "model": model_id,
                          "width": width, "height": height},
            )
        except CatalogImageError as error:
            return GenerationResult(
                success=False, provider_id=self.provider_id,
                error_code=f"HTTP_{error.status_code}" if error.status_code else error.code.upper(),
                error_message=str(error),
            )
        except (httpx.HTTPError, ValueError):
            return GenerationResult(
                success=False, provider_id=self.provider_id,
                error_code="PROVIDER_UNAVAILABLE", error_message="Image generation failed: provider_unavailable",
            )

    async def estimate_usage(self, prompt: str) -> List[UsageEstimate]:
        return [UsageEstimate(resource_type="credits", estimated_amount=1.0, unit="credit")]

    async def get_quota(self) -> List[QuotaInfo]:
        return [QuotaInfo(resource_type="credits", used=None, limit=None, remaining=None, unit="credits")]
