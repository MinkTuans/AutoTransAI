"""
AIRouter — Unified Router for AI Functions & Provider Resolution.

Decouples workflow stages from specific provider implementations, querying
active AIFunctionConfig from the database.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_logger
from app.services.settings_service import SettingsService

logger = get_logger(__name__)


class AIRouter:
    """Central AI Router resolving active providers & models for system functions."""

    @staticmethod
    async def get_stt_config(db: AsyncSession) -> Dict[str, Any]:
        """Fetch active STT provider configuration."""
        configs = await SettingsService.get_function_configs(db)
        stt_conf = next((c for c in configs if c["function_id"] == "stt"), None)

        if not stt_conf:
            return {
                "primary_provider_id": "gemini",
                "model_id": "gemini-2.5-flash",
                "fallback_enabled": False,
                "fallback_provider_id": None,
                "source": "HARDCODED SAFE DEFAULT",
            }
        stt_conf["source"] = "DATABASE"
        return stt_conf

    @staticmethod
    async def resolve_stt_model(db: Optional[AsyncSession] = None, requested_model: Optional[str] = None) -> Dict[str, Any]:
        """
        Resolve STT Provider & Model according to Configuration Priority Hierarchy:
        REQUESTED MODEL -> DATABASE AI FUNCTION CONFIG -> ENVIRONMENT DEFAULT -> HARDCODED SAFE DEFAULT
        """
        if requested_model:
            return {
                "provider_id": "gemini",
                "model_id": requested_model,
                "source": "REQUESTED MODEL",
            }

        if db:
            try:
                conf = await AIRouter.get_stt_config(db)
                if conf and conf.get("model_id"):
                    return {
                        "provider_id": conf.get("primary_provider_id", "gemini"),
                        "model_id": conf["model_id"],
                        "source": conf.get("source", "DATABASE"),
                    }
            except Exception as e:
                logger.warning(f"[STT ROUTING] Failed to query DB for STT config: {e}")

        # Fallback to Environment or Hardcoded
        from app.config import get_settings
        settings = get_settings()
        env_model = getattr(settings, "GEMINI_STT_MODEL", None) or getattr(settings, "GEMINI_MODEL", None)
        if env_model:
            return {
                "provider_id": getattr(settings, "DEFAULT_LLM_PROVIDER", "gemini"),
                "model_id": env_model,
                "source": "ENVIRONMENT",
            }

        return {
            "provider_id": "gemini",
            "model_id": "gemini-2.5-flash",
            "source": "HARDCODED SAFE DEFAULT",
        }

    @staticmethod
    async def get_translation_config(db: AsyncSession) -> Dict[str, Any]:
        """Fetch active Translation provider configuration."""
        configs = await SettingsService.get_function_configs(db)
        trans_conf = next((c for c in configs if c["function_id"] == "translation"), None)

        if not trans_conf:
            return {
                "primary_provider_id": "gemini",
                "model_id": "gemini-2.5-flash",
                "fallback_enabled": False,
                "fallback_provider_id": None,
            }
        return trans_conf

    @staticmethod
    async def get_tts_config(db: AsyncSession) -> Dict[str, Any]:
        """Fetch active TTS provider configuration."""
        configs = await SettingsService.get_function_configs(db)
        tts_conf = next((c for c in configs if c["function_id"] == "tts"), None)

        if not tts_conf:
            return {
                "primary_provider_id": "edge_tts",
                "model_id": "edge-tts",
                "fallback_enabled": False,
                "fallback_provider_id": None,
            }
        return tts_conf
