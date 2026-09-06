"""
SettingsService — Handles persistence and business logic for System Settings,
AI Function Configurations, AI Models Catalog, and Social Accounts.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_logger
from app.models.settings import AIFunctionConfig, AIModel, SocialAccount, SystemSetting
from app.models.provider import Provider
from app.providers.registry import get_registry
from app.services.key_manager import get_key_manager

logger = get_logger(__name__)


# ── Default System Configurations Seed Data ─────────────────────────────
DEFAULT_SYSTEM_SETTINGS = {
    # Storage
    "storage_provider": "supabase",
    "supabase_bucket_private": "autotransai-private",
    "supabase_bucket_public": "autotransai-public",
    # Processing
    "max_concurrency": "2",
    "max_retries": "3",
    "retry_backoff": "2.0",
    "video_target_duration": "8",
    "video_output_resolution": "1080p",
    "audio_format": "wav",
    "audio_sample_rate": "24000",
    "sync_strategy": "trim_video",
    "sync_tolerance_seconds": "0.5",
    # Workflow Defaults
    "default_source_language": "auto",
    "default_target_language": "vi",
    "default_tts_voice": "vi-VN-HoaiMyNeural",
    "default_video_provider": "kling",
    # Social Strategy
    "social_account_strategy": "priority",
}

DEFAULT_AI_FUNCTIONS = [
    {
        "function_id": "stt",
        "function_name": "Speech To Text",
        "capability": "STT",
        "primary_provider_id": "gemini",
        "model_id": "gemini-2.5-flash",
        "fallback_enabled": False,
        "fallback_provider_id": None,
    },
    {
        "function_id": "translation",
        "function_name": "Text Translation & Glossaries",
        "capability": "TRANSLATION",
        "primary_provider_id": "gemini",
        "model_id": "gemini-2.5-flash",
        "fallback_enabled": False,
        "fallback_provider_id": None,
    },
    {
        "function_id": "tts",
        "function_name": "Text To Speech (Dubbing)",
        "capability": "TTS",
        "primary_provider_id": "edge_tts",
        "model_id": "edge-tts",
        "fallback_enabled": False,
        "fallback_provider_id": None,
    },
    {
        "function_id": "video_generation",
        "function_name": "Video Generation & B-Roll Clips",
        "capability": "VIDEO_GENERATION",
        "primary_provider_id": "kling",
        "model_id": "kling-v1",
        "fallback_enabled": False,
        "fallback_provider_id": None,
    },
    {
        "function_id": "image_generation",
        "function_name": "Image & Asset Generation",
        "capability": "IMAGE_GENERATION",
        "primary_provider_id": "fal",
        "model_id": "fal-ai/flux",
        "fallback_enabled": False,
        "fallback_provider_id": None,
    },
]

DEFAULT_AI_MODELS = [
    # Gemini
    {"id": "gemini-2.5-flash", "provider_id": "gemini", "model_name": "Gemini 2.5 Flash", "capabilities": json.dumps(["STT", "LLM", "TRANSLATION"]), "is_default": True},
    {"id": "gemini-1.5-pro", "provider_id": "gemini", "model_name": "Gemini 1.5 Pro", "capabilities": json.dumps(["LLM", "TRANSLATION"]), "is_default": False},
    {"id": "gemini-2.0-flash", "provider_id": "gemini", "model_name": "Gemini 2.0 Flash", "capabilities": json.dumps(["STT", "LLM", "TRANSLATION"]), "is_default": False},
    # OpenAI
    {"id": "gpt-4o", "provider_id": "openai", "model_name": "GPT-4o", "capabilities": json.dumps(["LLM", "TRANSLATION"]), "is_default": True},
    {"id": "gpt-4o-mini", "provider_id": "openai", "model_name": "GPT-4o Mini", "capabilities": json.dumps(["LLM", "TRANSLATION"]), "is_default": False},
    {"id": "whisper-1", "provider_id": "openai", "model_name": "Whisper STT v1", "capabilities": json.dumps(["STT"]), "is_default": True},
    # Audio TTS
    {"id": "edge-tts", "provider_id": "edge_tts", "model_name": "Microsoft Edge Neural TTS", "capabilities": json.dumps(["TTS"]), "is_default": True},
    {"id": "google-cloud-tts", "provider_id": "google_cloud_tts", "model_name": "Google Cloud Neural TTS", "capabilities": json.dumps(["TTS"]), "is_default": True},
    {"id": "eleven_multilingual_v2", "provider_id": "elevenlabs", "model_name": "Eleven Multilingual v2", "capabilities": json.dumps(["TTS"]), "is_default": True},
    # Video & Image
    {"id": "kling-v1", "provider_id": "kling", "model_name": "Kling AI Text2Video v1.0", "capabilities": json.dumps(["VIDEO_GENERATION"]), "is_default": True},
    {"id": "fal-ai/hunyuan-video", "provider_id": "fal", "model_name": "Hunyuan Video (fal.ai)", "capabilities": json.dumps(["VIDEO_GENERATION"]), "is_default": True},
    {"id": "fal-ai/flux", "provider_id": "fal", "model_name": "Flux Image Gen (fal.ai)", "capabilities": json.dumps(["IMAGE_GENERATION"]), "is_default": True},
]


class SettingsService:
    """Service servicing all Settings, Provider configurations, and AI Function routing."""

    @staticmethod
    async def ensure_defaults_seeded(db: AsyncSession) -> None:
        """Seed default system settings, AI functions, and AI models if DB is empty."""
        try:
            # Seed system settings
            for key, val in DEFAULT_SYSTEM_SETTINGS.items():
                stmt = select(SystemSetting).where(SystemSetting.key == key)
                res = await db.execute(stmt)
                if not res.scalar_one_or_none():
                    cat = "storage" if key.startswith("supabase") or key.startswith("storage") else "processing"
                    db.add(SystemSetting(key=key, value=val, category=cat))

            # Seed AI function configs
            for fn in DEFAULT_AI_FUNCTIONS:
                stmt = select(AIFunctionConfig).where(AIFunctionConfig.function_id == fn["function_id"])
                res = await db.execute(stmt)
                if not res.scalar_one_or_none():
                    db.add(AIFunctionConfig(**fn))

            # Seed AI models
            for m in DEFAULT_AI_MODELS:
                stmt = select(AIModel).where(AIModel.id == m["id"])
                res = await db.execute(stmt)
                if not res.scalar_one_or_none():
                    db.add(AIModel(**m))

            await db.commit()
            logger.info("Settings defaults successfully seeded")
        except Exception as e:
            await db.rollback()
            logger.error("Failed seeding settings defaults", error=str(e))

    # ── System Settings CRUD ───────────────────────────────────────────
    @staticmethod
    async def get_all_settings(db: AsyncSession) -> Dict[str, str]:
        """Fetch all system settings as key-value dictionary."""
        stmt = select(SystemSetting)
        res = await db.execute(stmt)
        settings_map = {s.key: s.value for s in res.scalars().all()}
        # Fill in any missing default key
        for k, v in DEFAULT_SYSTEM_SETTINGS.items():
            if k not in settings_map:
                settings_map[k] = v
        return settings_map

    @staticmethod
    async def update_settings(db: AsyncSession, new_settings: Dict[str, str]) -> Dict[str, str]:
        """Update multiple system settings."""
        for key, val in new_settings.items():
            stmt = select(SystemSetting).where(SystemSetting.key == key)
            res = await db.execute(stmt)
            obj = res.scalar_one_or_none()
            if obj:
                obj.value = str(val)
            else:
                db.add(SystemSetting(key=key, value=str(val)))
        await db.commit()
        return await SettingsService.get_all_settings(db)

    # ── AI Function Configs CRUD ───────────────────────────────────────
    @staticmethod
    async def get_function_configs(db: AsyncSession) -> List[Dict[str, Any]]:
        """List all AI function configurations."""
        stmt = select(AIFunctionConfig)
        res = await db.execute(stmt)
        configs = res.scalars().all()

        out = []
        for c in configs:
            out.append({
                "function_id": c.function_id,
                "function_name": c.function_name,
                "capability": c.capability,
                "primary_provider_id": c.primary_provider_id,
                "model_id": c.model_id,
                "fallback_enabled": c.fallback_enabled,
                "fallback_provider_id": c.fallback_provider_id,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            })
        return out

    @staticmethod
    async def update_function_config(
        db: AsyncSession, function_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a specific AI function configuration."""
        stmt = select(AIFunctionConfig).where(AIFunctionConfig.function_id == function_id)
        res = await db.execute(stmt)
        config = res.scalar_one_or_none()
        if not config:
            raise ValueError(f"AI Function '{function_id}' not found")

        if "primary_provider_id" in payload:
            config.primary_provider_id = payload["primary_provider_id"]
        if "model_id" in payload:
            config.model_id = payload["model_id"]
        if "fallback_enabled" in payload:
            config.fallback_enabled = bool(payload["fallback_enabled"])
        if "fallback_provider_id" in payload:
            config.fallback_provider_id = payload["fallback_provider_id"]

        await db.commit()
        return {
            "function_id": config.function_id,
            "function_name": config.function_name,
            "capability": config.capability,
            "primary_provider_id": config.primary_provider_id,
            "model_id": config.model_id,
            "fallback_enabled": config.fallback_enabled,
            "fallback_provider_id": config.fallback_provider_id,
        }

    # ── Eligible Providers Filtering ────────────────────────────────────
    @staticmethod
    async def get_eligible_providers_for_function(db: AsyncSession, function_id: str) -> List[Dict[str, Any]]:
        """
        Filter candidate providers for a given AI function based on:
        - Supported in backend (supported == True)
        - Enabled (enabled == True)
        - Key set or Free tier (api_key_set / free_tier == True)
        - Capability match (capability in provider.capabilities)
        """
        # Map function_id to capability
        cap_map = {
            "stt": "STT",
            "translation": "TRANSLATION",
            "tts": "TTS",
            "video_generation": "VIDEO_GENERATION",
            "image_generation": "IMAGE_GENERATION",
        }
        target_cap = cap_map.get(function_id, "LLM")

        registry = get_registry()
        key_mgr = get_key_manager()

        # Build list of all system known providers
        known_providers = [
            {"id": "gemini", "name": "Google Gemini", "type": "llm", "caps": ["STT", "LLM", "TRANSLATION"], "free": False},
            {"id": "openai", "name": "OpenAI", "type": "llm", "caps": ["STT", "LLM", "TRANSLATION"], "free": False},
            {"id": "edge_tts", "name": "Edge TTS", "type": "audio", "caps": ["TTS"], "free": True},
            {"id": "google_cloud_tts", "name": "Google Cloud TTS", "type": "audio", "caps": ["TTS"], "free": False},
            {"id": "elevenlabs", "name": "ElevenLabs", "type": "audio", "caps": ["TTS"], "free": False},
            {"id": "kling", "name": "Kling AI", "type": "video", "caps": ["VIDEO_GENERATION"], "free": False},
            {"id": "fal", "name": "fal.ai", "type": "video", "caps": ["VIDEO_GENERATION", "IMAGE_GENERATION"], "free": False},
        ]

        eligible = []
        for p in known_providers:
            if target_cap not in p["caps"]:
                continue

            # Check if key is available or free tier
            has_key = p["free"]
            if not p["free"]:
                keys = await key_mgr.get_keys_for_provider(p["id"])
                has_key = len(keys) > 0 and any(k.get("status") not in ("disabled", "invalid") for k in keys)

            eligible.append({
                "id": p["id"],
                "name": p["name"],
                "provider_type": p["type"],
                "configured": has_key,
                "supported": True,
                "capability_compatible": True,
            })
        return eligible

    # ── AI Models Catalog CRUD ────────────────────────────────────────
    @staticmethod
    async def get_models(db: AsyncSession, provider_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List AI models catalog."""
        stmt = select(AIModel)
        if provider_id:
            stmt = stmt.where(AIModel.provider_id == provider_id)
        res = await db.execute(stmt)
        models = res.scalars().all()

        out = []
        for m in models:
            caps = []
            try:
                caps = json.loads(m.capabilities)
            except Exception:
                caps = [m.capabilities]
            out.append({
                "id": m.id,
                "provider_id": m.provider_id,
                "model_name": m.model_name,
                "capabilities": caps,
                "is_default": m.is_default,
                "is_custom": m.is_custom,
                "enabled": m.enabled,
                "description": m.description,
            })
        return out

    @staticmethod
    async def add_custom_model(db: AsyncSession, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a custom model definition."""
        m_id = model_data.get("id") or model_data.get("model_name").lower().replace(" ", "-")
        stmt = select(AIModel).where(AIModel.id == m_id)
        res = await db.execute(stmt)
        if res.scalar_one_or_none():
            raise ValueError(f"Model ID '{m_id}' already exists")

        caps = model_data.get("capabilities", ["LLM"])
        caps_str = json.dumps(caps) if isinstance(caps, list) else caps

        new_m = AIModel(
            id=m_id,
            provider_id=model_data["provider_id"],
            model_name=model_data["model_name"],
            capabilities=caps_str,
            is_default=bool(model_data.get("is_default", False)),
            is_custom=True,
            enabled=True,
            description=model_data.get("description", "Custom user model"),
        )
        db.add(new_m)
        await db.commit()
        return {
            "id": new_m.id,
            "provider_id": new_m.provider_id,
            "model_name": new_m.model_name,
            "capabilities": caps,
            "is_default": new_m.is_default,
            "is_custom": True,
        }

    # ── Social Accounts Manager ───────────────────────────────────────
    @staticmethod
    async def get_social_accounts(db: AsyncSession) -> List[Dict[str, Any]]:
        """List connected social media accounts."""
        stmt = select(SocialAccount)
        res = await db.execute(stmt)
        accs = res.scalars().all()
        return [
            {
                "id": a.id,
                "platform": a.platform,
                "account_name": a.account_name,
                "channel_id": a.channel_id,
                "channel_name": a.channel_name,
                "status": a.status,
                "connected_at": a.connected_at.isoformat() if a.connected_at else None,
                "priority": a.priority,
            }
            for a in accs
        ]

    @staticmethod
    async def add_social_account(db: AsyncSession, acc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add or update a social media account."""
        import uuid
        acc_id = str(uuid.uuid4())
        acc = SocialAccount(
            id=acc_id,
            platform=acc_data["platform"],
            account_name=acc_data["account_name"],
            channel_id=acc_data.get("channel_id"),
            channel_name=acc_data.get("channel_name", acc_data["account_name"]),
            status="connected",
            priority=int(acc_data.get("priority", 1)),
        )
        db.add(acc)
        await db.commit()
        return {
            "id": acc.id,
            "platform": acc.platform,
            "account_name": acc.account_name,
            "channel_name": acc.channel_name,
            "status": acc.status,
        }

    @staticmethod
    async def delete_social_account(db: AsyncSession, account_id: str) -> bool:
        """Delete a social account."""
        stmt = select(SocialAccount).where(SocialAccount.id == account_id)
        res = await db.execute(stmt)
        acc = res.scalar_one_or_none()
        if acc:
            await db.delete(acc)
            await db.commit()
            return True
        return False
