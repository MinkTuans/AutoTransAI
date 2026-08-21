"""
Edge TTS provider — free, no API key, high quality Microsoft neural voices.

Uses the edge-tts library which emulates the Edge browser's Read Aloud feature.
No API key required. Sends text to Microsoft's servers for processing.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import edge_tts

from app.core import get_logger
from app.providers.base import (
    AudioProvider,
    GenerationResult,
    QuotaInfo,
    UsageEstimate,
    VoiceInfo,
)

logger = get_logger(__name__)

# Cache voices to avoid repeated network calls
_voices_cache: list[dict] | None = None
_voices_cache_lock = asyncio.Lock()


class EdgeTTSProvider(AudioProvider):
    """
    Microsoft Edge TTS provider.

    Free, no API key, 200+ neural voices, 40+ languages.
    Unofficial interface — could break if Microsoft changes their backend.
    """

    @property
    def provider_id(self) -> str:
        return "edge_tts"

    @property
    def provider_name(self) -> str:
        return "Edge TTS (Microsoft)"

    @property
    def is_free(self) -> bool:
        return True

    @property
    def requires_api_key(self) -> bool:
        return False

    async def validate_configuration(self) -> bool:
        """Validate by attempting to list voices (requires internet)."""
        try:
            voices = await edge_tts.list_voices()
            return len(voices) > 0
        except Exception as e:
            logger.warning(
                "Edge TTS validation failed",
                error=str(e),
                provider_id=self.provider_id,
            )
            return False

    async def get_voices(self, language: str | None = None) -> list[VoiceInfo]:
        """List available voices, optionally filtered by language code."""
        global _voices_cache

        async with _voices_cache_lock:
            if _voices_cache is None:
                try:
                    _voices_cache = await edge_tts.list_voices()
                except Exception as e:
                    logger.error("Failed to list Edge TTS voices", error=str(e))
                    return []

        voices = _voices_cache or []

        result = []
        for v in voices:
            locale = v.get("Locale", "")
            if language and not locale.lower().startswith(language.lower()):
                continue

            result.append(VoiceInfo(
                id=v.get("ShortName", ""),
                name=v.get("FriendlyName", v.get("ShortName", "")),
                language=locale,
                gender=v.get("Gender", None),
            ))

        return result

    async def generate_audio(
        self,
        text: str,
        voice_id: str,
        output_path: Path,
    ) -> GenerationResult:
        """
        Generate audio using Edge TTS.

        Args:
            text: Text to speak.
            voice_id: Voice ShortName (e.g., "en-US-AriaNeural").
            output_path: Where to save the output file.

        Returns:
            GenerationResult with the saved audio file path.
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            communicate = edge_tts.Communicate(text, voice_id)
            await communicate.save(str(output_path))

            if not output_path.exists():
                return GenerationResult(
                    success=False,
                    error_message="Audio file was not created",
                    error_code="FILE_NOT_CREATED",
                    provider_id=self.provider_id,
                )

            file_size = output_path.stat().st_size
            if file_size == 0:
                output_path.unlink(missing_ok=True)
                return GenerationResult(
                    success=False,
                    error_message="Audio file is empty",
                    error_code="EMPTY_FILE",
                    provider_id=self.provider_id,
                )

            logger.info(
                "Audio generated",
                provider_id=self.provider_id,
                voice=voice_id,
                chars=len(text),
                file_size=file_size,
                output=str(output_path),
            )

            return GenerationResult(
                success=True,
                file_path=output_path,
                provider_id=self.provider_id,
                metadata={"voice_id": voice_id, "char_count": len(text)},
            )

        except Exception as e:
            logger.error(
                "Edge TTS generation failed",
                error=str(e),
                voice=voice_id,
                text_length=len(text),
            )
            return GenerationResult(
                success=False,
                error_message=str(e),
                error_code="GENERATION_ERROR",
                provider_id=self.provider_id,
            )

    async def estimate_usage(self, text: str) -> list[UsageEstimate]:
        """Edge TTS is free — no usage to estimate."""
        return [
            UsageEstimate(
                resource_type="characters",
                estimated_amount=float(len(text)),
                unit="characters",
            )
        ]

    async def get_quota(self) -> list[QuotaInfo]:
        """Edge TTS has no quota — it's free and unlimited (unofficial)."""
        return [
            QuotaInfo(
                resource_type="characters",
                used=None,
                limit=None,
                remaining=None,  # Unknown / unlimited
                unit="characters",
                reset_period=None,
            )
        ]
