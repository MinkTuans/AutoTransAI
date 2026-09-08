"""
AIRouter — Unified Router for AI Functions & Provider Resolution.

Delegates all model resolution to AIModelResolver.
No hardcoded model defaults — Settings Database is the single source of truth.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_logger
from app.services.model_resolver import AIModelResolver

logger = get_logger(__name__)


class AIRouter:
    """Central AI Router — thin wrapper over AIModelResolver for backward compatibility."""

    @staticmethod
    async def get_stt_config(db: AsyncSession) -> Dict[str, Any]:
        """Fetch active STT provider configuration from Settings Database."""
        resolution = await AIModelResolver.resolve_model(db, capability="STT", stage="STT")
        return {
            "primary_provider_id": resolution.provider_id,
            "model_id": resolution.model_id,
            "fallback_enabled": resolution.fallback_enabled,
            "fallback_provider_id": resolution.fallback_provider_id,
            "source": resolution.source,
        }

    @staticmethod
    async def resolve_stt_model(
        db: Optional[AsyncSession] = None,
        requested_model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Resolve STT Provider & Model via AIModelResolver.
        Delegates single source of truth to AIModelResolver.
        """
        return await AIModelResolver.resolve_stt_model(db, requested_model=requested_model)

    @staticmethod
    async def get_translation_config(db: AsyncSession) -> Dict[str, Any]:
        """Fetch active Translation provider configuration from Settings Database."""
        resolution = await AIModelResolver.resolve_model(db, capability="TRANSLATION", stage="TRANSLATE")
        return {
            "primary_provider_id": resolution.provider_id,
            "model_id": resolution.model_id,
            "fallback_enabled": resolution.fallback_enabled,
            "fallback_provider_id": resolution.fallback_provider_id,
            "source": resolution.source,
        }

    @staticmethod
    async def get_tts_config(db: AsyncSession) -> Dict[str, Any]:
        """Fetch active TTS provider configuration from Settings Database."""
        resolution = await AIModelResolver.resolve_model(db, capability="TTS", stage="DUB")
        return {
            "primary_provider_id": resolution.provider_id,
            "model_id": resolution.model_id,
            "fallback_enabled": resolution.fallback_enabled,
            "fallback_provider_id": resolution.fallback_provider_id,
            "source": resolution.source,
        }
