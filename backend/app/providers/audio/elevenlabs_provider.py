"""
ElevenLabs Audio Provider implementation.

Calls the official ElevenLabs Text-to-Speech API.
"""

from __future__ import annotations

from pathlib import Path
import httpx

from app.config import get_settings
from app.core import get_logger
from app.providers.base import (
    AudioProvider,
    GenerationResult,
    QuotaInfo,
    UsageEstimate,
    VoiceInfo,
)
from app.providers.request_target import resolve_request_target
from app.services.ai_routing import RouteTarget

logger = get_logger(__name__)
settings = get_settings()


class ElevenLabsAudioProvider(AudioProvider):
    """ElevenLabs TTS Provider."""

    @property
    def provider_id(self) -> str:
        return "elevenlabs"

    @property
    def provider_name(self) -> str:
        return "ElevenLabs"

    @property
    def is_free(self) -> bool:
        return False

    @property
    def requires_api_key(self) -> bool:
        return True

    async def validate_configuration(self) -> bool:
        if not settings.ELEVENLABS_API_KEY:
            return False
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(
                    "https://api.elevenlabs.io/v1/user/subscription",
                    headers={"xi-api-key": settings.ELEVENLABS_API_KEY},
                )
                return res.status_code == 200
        except Exception:
            logger.warning("ElevenLabs validation failed")
            return False

    async def get_voices(self, language: str | None = None) -> list[VoiceInfo]:
        if settings.ELEVENLABS_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    res = await client.get(
                        "https://api.elevenlabs.io/v1/voices",
                        headers={"xi-api-key": settings.ELEVENLABS_API_KEY},
                    )
                    if res.status_code == 200:
                        data = res.json()
                        voices = []
                        for v in data.get("voices", []):
                            voices.append(
                                VoiceInfo(
                                    id=v.get("voice_id", ""),
                                    name=v.get("name", ""),
                                    language=v.get("category", "en-US"),
                                    gender=v.get("labels", {}).get("gender"),
                                )
                            )
                        if voices:
                            return voices
            except Exception:
                logger.warning("Failed to fetch live ElevenLabs voices")

        # Fallback default voices
        fallbacks = [
            VoiceInfo(id="21m00Tcm4TlvDq8ikWAM", name="Rachel", language="en-US", gender="Female"),
            VoiceInfo(id="AZnzlk1XvdvUeBnXmlld", name="Domi", language="en-US", gender="Female"),
            VoiceInfo(id="EXAVITQu4vr4xnSDxMaL", name="Bella", language="en-US", gender="Female"),
            VoiceInfo(id="ErXwobaYiN019PkySvjV", name="Antoni", language="en-US", gender="Male"),
            VoiceInfo(id="TxGEqnHWrfWFTfGW9XjX", name="Josh", language="en-US", gender="Male"),
        ]
        if language:
            norm_lang = language.lower().split("-")[0]
            fallbacks = [
                v for v in fallbacks
                if v.language.lower().startswith(norm_lang) or v.language.lower() == language.lower()
            ]
        return fallbacks

    async def generate_audio(
        self,
        text: str,
        voice_id: str,
        output_path: Path,
        *,
        route_target: RouteTarget | None = None,
        api_key: str | None = None,
    ) -> GenerationResult:
        model_id, request_key = resolve_request_target(
            route_target, api_key, provider_id=self.provider_id, capabilities=("TTS",),
            legacy_model="eleven_multilingual_v2", legacy_key=settings.ELEVENLABS_API_KEY,
        )
        if not request_key:
            return GenerationResult(
                success=False,
                error_message="ELEVENLABS_API_KEY not set in .env",
                error_code="API_KEY_MISSING",
                provider_id=self.provider_id,
            )

        v_id = voice_id or "21m00Tcm4TlvDq8ikWAM"
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{v_id}"
        headers = {
            "xi-api-key": request_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            },
        }

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload, headers=headers)

                if response.status_code != 200:
                    err_msg = f"ElevenLabs API error HTTP {response.status_code}"
                    logger.error(err_msg)
                    return GenerationResult(
                        success=False,
                        error_message=err_msg,
                        error_code=f"HTTP_{response.status_code}",
                        provider_id=self.provider_id,
                    )

                audio_data = response.content
                if not audio_data or len(audio_data) == 0:
                    return GenerationResult(
                        success=False,
                        error_message="ElevenLabs API returned empty audio content",
                        error_code="EMPTY_RESPONSE",
                        provider_id=self.provider_id,
                    )

                output_path.write_bytes(audio_data)

                if not output_path.exists() or output_path.stat().st_size == 0:
                    return GenerationResult(
                        success=False,
                        error_message="Failed to save audio file or file is 0 bytes",
                        error_code="FILE_WRITE_ERROR",
                        provider_id=self.provider_id,
                    )

                logger.info(
                    "ElevenLabs audio generated",
                    voice_id=v_id,
                    size=len(audio_data),
                    output_path=str(output_path),
                )
                return GenerationResult(
                    success=True,
                    file_path=output_path,
                    provider_id=self.provider_id,
                    metadata={"voice_id": v_id, "char_count": len(text)},
                )

        except httpx.TimeoutException:
            logger.error("ElevenLabs generation timed out")
            return GenerationResult(success=False, error_message="ElevenLabs generation timed out",
                                    error_code="TTS_TIMEOUT", provider_id=self.provider_id)
        except Exception:
            logger.error("ElevenLabs generation failed")
            return GenerationResult(
                success=False,
                error_message="ElevenLabs generation failed",
                error_code="GENERATION_EXCEPTION",
                provider_id=self.provider_id,
            )

    async def estimate_usage(self, text: str) -> list[UsageEstimate]:
        return [
            UsageEstimate(
                resource_type="characters",
                estimated_amount=float(len(text)),
                unit="characters",
            )
        ]

    async def get_quota(self) -> list[QuotaInfo]:
        if settings.ELEVENLABS_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    res = await client.get(
                        "https://api.elevenlabs.io/v1/user/subscription",
                        headers={"xi-api-key": settings.ELEVENLABS_API_KEY},
                    )
                    if res.status_code == 200:
                        sub = res.json()
                        used = float(sub.get("character_count", 0))
                        limit = float(sub.get("character_limit", 10000))
                        return [
                            QuotaInfo(
                                resource_type="characters",
                                used=used,
                                limit=limit,
                                remaining=max(0.0, limit - used),
                                unit="characters",
                            )
                        ]
            except Exception:
                logger.warning("Failed to fetch ElevenLabs quota")

        return [
            QuotaInfo(
                resource_type="characters",
                used=None,
                limit=10000.0,
                remaining=None,
                unit="characters",
            )
        ]
