"""
Google Gemini Vision Multimodal Provider.
Sends image + prompt to Google Gemini generateContent API endpoint.
"""

from __future__ import annotations

import base64
import logging
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote

import httpx

from app.config import get_settings
from app.providers.base import VisionProvider
from app.services.ai_routing import RouteTarget

logger = logging.getLogger(__name__)
settings = get_settings()
MAX_VISION_IMAGE_BYTES = 8 * 1024 * 1024


class VisionHTTPError(RuntimeError):
    def __init__(self, status_code: int):
        self.status_code = status_code
        super().__init__(f"Vision provider returned HTTP {status_code}.")


class GeminiVisionProvider(VisionProvider):
    """Google Gemini Vision API Provider."""

    @property
    def provider_id(self) -> str:
        return "gemini"

    @property
    def provider_name(self) -> str:
        return "Google Gemini Vision"

    @property
    def is_free(self) -> bool:
        return True

    @property
    def requires_api_key(self) -> bool:
        return True

    async def validate_configuration(self) -> bool:
        return bool(settings.GEMINI_API_KEY)

    async def analyze_image(
        self,
        image_path: Path | str,
        prompt: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Send image and prompt to Gemini Vision API."""
        route_target: RouteTarget | None = kwargs.get("route_target")
        if route_target is not None and route_target.provider_id != self.provider_id:
            raise ValueError("Vision route provider mismatch.")
        key = api_key if route_target is not None else (api_key or settings.GEMINI_API_KEY)
        if not key:
            raise ValueError("[Gemini Vision] Missing GEMINI_API_KEY")

        target_model = route_target.remote_model_id if route_target is not None else (model or "gemini-2.0-flash")
        if target_model.startswith("models/"):
            target_model = target_model[len("models/"):]

        img_path = Path(image_path)
        if not img_path.is_file():
            raise FileNotFoundError(f"[Gemini Vision] Image file not found: {img_path}")

        if img_path.stat().st_size > MAX_VISION_IMAGE_BYTES:
            raise ValueError("Vision image exceeds size limit.")
        image_bytes = img_path.read_bytes()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        suffix = img_path.suffix.lower()
        mime_type = "image/png" if suffix == ".png" else "image/jpeg"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{quote(target_model, safe='-._~')}:generateContent"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": base64_image,
                            }
                        },
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 20,
            },
        }

        timeout = float(kwargs.get("timeout", 45.0))
        async with httpx.AsyncClient(timeout=timeout) as client:
            res = await client.post(url, json=payload, headers={"x-goog-api-key": key})
            if res.status_code == 200:
                data = res.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
                return ""
            else:
                raise VisionHTTPError(res.status_code)
