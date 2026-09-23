"""
OpenAI DALL-E Image Provider implementation.

Uses OpenAI DALL-E 3 API with KeyManager failover.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from app.providers.image.catalog_media import (
    CatalogImageError, decode_image_base64, download_image, request_json, validated_output_path,
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
        *,
        route_target: RouteTarget | None = None,
        api_key: str | None = None,
    ) -> GenerationResult:
        if route_target is not None:
            return await self._generate_catalog_image(prompt, width, height, aspect_ratio, route_target, api_key)
        if api_key is not None:
            raise ValueError("A request credential requires a route target.")
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
            output_path = validated_output_path(options.get("output_path"), settings.DATA_DIR)
            async with httpx.AsyncClient(timeout=45.0, follow_redirects=False) as client:
                data = await request_json(client, "POST", url, headers=headers, payload=payload)
                data_list = data.get("data", [])
                if (not isinstance(data_list, list) or not data_list
                        or not isinstance(data_list[0], dict) or not data_list[0].get("url")):
                    return GenerationResult(
                        success=False,
                        error_message="OpenAI DALL-E returned empty response.",
                        error_code="EMPTY_RESPONSE",
                        provider_id=self.provider_id,
                    )

                img_url = data_list[0]["url"]
                image_bytes = await download_image(client, img_url)
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
                              "model": "dall-e-3"},
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
            logger.error("OpenAI DALL-E image generation exception", code="provider_unavailable")
            return GenerationResult(
                success=False,
                error_message="OpenAI DALL-E request failed.",
                error_code="EXCEPTION",
                provider_id=self.provider_id,
            )

    async def _generate_catalog_image(
        self, prompt: str, width: int, height: int, aspect_ratio: str,
        route_target: RouteTarget, api_key: str | None,
    ) -> GenerationResult:
        model_id, secret = resolve_request_target(
            route_target, api_key, provider_id=self.provider_id,
            capabilities=("IMAGE_GENERATION",), legacy_model=None, legacy_key=None,
        )
        try:
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=False) as client:
                payload = await request_json(
                    client, "POST",
                    "https://api.openai.com/v1/images/generations",
                    headers={"Authorization": f"Bearer {secret}", "Content-Type": "application/json"},
                    payload={"model": model_id, "prompt": prompt[:4000], "n": 1},
                )
                try:
                    item = payload["data"][0]
                    if not isinstance(item, dict):
                        raise ValueError()
                except (ValueError, TypeError, KeyError, IndexError):
                    raise CatalogImageError("invalid_output") from None
                if isinstance(item.get("url"), str):
                    image_bytes = await download_image(client, item["url"])
                elif isinstance(item.get("b64_json"), str):
                    image_bytes = decode_image_base64(item["b64_json"])
                else:
                    raise CatalogImageError("invalid_output")
            return GenerationResult(
                success=True, provider_id=self.provider_id,
                metadata={"image_bytes": image_bytes, "model": model_id},
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
        return [UsageEstimate(resource_type="images", estimated_amount=1.0, unit="image")]

    async def get_quota(self) -> List[QuotaInfo]:
        return [QuotaInfo(resource_type="images", used=None, limit=None, remaining=None, unit="images")]
