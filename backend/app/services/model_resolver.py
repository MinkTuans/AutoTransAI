"""
AIModelResolver — Central single-source-of-truth for AI Model selection.

All pipeline stages MUST use this resolver to obtain the correct model.
No hardcoded model names are permitted in pipeline code.

Resolution Priority:
    1. DEFAULT model in Settings (ai_function_configs.model_id)
    2. Enabled SYSTEM model matching capability
    3. Enabled CUSTOM model matching capability
    4. → Raise PipelineError (NEVER fall back to hardcoded model)
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_logger
from app.core.pipeline_errors import (
    PipelineError,
    AI_MODEL_NOT_FOUND,
    AI_MODEL_CAPABILITY_MISMATCH,
    AI_CONFIGURATION_ERROR,
    AI_PROVIDER_AUTH_ERROR,
    CAPABILITY_DISPLAY,
)

logger = get_logger(__name__)


class ModelResolution:
    """Immutable result of model resolution."""

    __slots__ = ("provider_id", "model_id", "model_name", "source", "capabilities", "fallback_enabled", "fallback_provider_id")

    def __init__(
        self,
        provider_id: str,
        model_id: str,
        model_name: str = "",
        source: str = "Settings Database",
        capabilities: Optional[List[str]] = None,
        fallback_enabled: bool = False,
        fallback_provider_id: Optional[str] = None,
    ):
        self.provider_id = provider_id
        self.model_id = model_id
        self.model_name = model_name or model_id
        self.source = source
        self.capabilities = capabilities or []
        self.fallback_enabled = fallback_enabled
        self.fallback_provider_id = fallback_provider_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "model_name": self.model_name,
            "source": self.source,
            "capabilities": self.capabilities,
            "fallback_enabled": self.fallback_enabled,
            "fallback_provider_id": self.fallback_provider_id,
        }


# ── Capability → function_id mapping ─────────────────────────────────────
_CAPABILITY_TO_FUNCTION = {
    "STT": "stt",
    "TRANSLATION": "translation",
    "LLM": "translation",  # LLM maps to translation function config
    "TTS": "tts",
    "VIDEO_GENERATION": "video_generation",
    "IMAGE_GENERATION": "image_generation",
}


def _is_capability_compatible(target_capability: str, model_capabilities: List[str], provider_id: str) -> bool:
    """Check if a model is compatible with a target capability."""
    if target_capability in model_capabilities:
        return True
    if "LLM" in model_capabilities and target_capability in ("STT", "TRANSLATION"):
        return True
    if provider_id in ("gemini", "openai") and target_capability in ("STT", "TRANSLATION"):
        return True
    return False


class AIModelResolver:
    """
    Central model resolver. The ONLY place that decides which AI model to use.

    Usage:
        resolution = await AIModelResolver.resolve_model(db, capability="STT")
        model_id = resolution.model_id
        provider_id = resolution.provider_id
    """

    @staticmethod
    async def resolve_model(
        db: Optional[AsyncSession],
        capability: str,
        stage: str = "",
    ) -> ModelResolution:
        """
        Resolve the active AI model for a given capability strictly from Database.

        Resolution Priority:
            1. ai_function_configs table (user-configured model for this function)
            2. ai_models table — DEFAULT model with matching capability
            3. ai_models table — any ENABLED model with matching capability
            4. Raise PipelineError — NEVER fall back to hardcoded model strings
        """
        cap_display = CAPABILITY_DISPLAY.get(capability, capability)

        if db is None:
            try:
                from app.database import async_session_factory
                async with async_session_factory() as session:
                    return await AIModelResolver.resolve_model(session, capability=capability, stage=stage)
            except PipelineError:
                raise
            except Exception as e:
                logger.error(f"[MODEL RESOLVER] Failed to open DB session for model resolution: {e}")
                raise PipelineError(
                    code=AI_MODEL_NOT_FOUND,
                    stage=stage,
                    message=f"Không thể kết nối Database để tra cứu Cài đặt AI Model cho chức năng {cap_display}.",
                )

        from app.models.settings import AIFunctionConfig, AIModel

        function_id = _CAPABILITY_TO_FUNCTION.get(capability)

        # ── Step 1: Check ai_function_configs for user-configured model ───
        if function_id:
            try:
                stmt = select(AIFunctionConfig).where(AIFunctionConfig.function_id == function_id)
                res = await db.execute(stmt)
                func_config = res.scalar_one_or_none()

                if func_config and func_config.model_id:
                    # Validate the configured model actually exists and is enabled
                    model_stmt = select(AIModel).where(AIModel.id == func_config.model_id)
                    model_res = await db.execute(model_stmt)
                    model_obj = model_res.scalar_one_or_none()

                    if model_obj and model_obj.enabled:
                        model_caps = _parse_capabilities(model_obj.capabilities)
                        if _is_capability_compatible(capability, model_caps, model_obj.provider_id):
                            resolution = ModelResolution(
                                provider_id=func_config.primary_provider_id or model_obj.provider_id,
                                model_id=func_config.model_id,
                                model_name=model_obj.model_name,
                                source="Settings Database (AI Function Config)",
                                capabilities=model_caps,
                                fallback_enabled=func_config.fallback_enabled,
                                fallback_provider_id=func_config.fallback_provider_id,
                            )
                            _log_resolution(capability, resolution, stage)
                            return resolution
                        else:
                            logger.warning(
                                f"[MODEL RESOLVER] Configured model '{func_config.model_id}' for {function_id} "
                                f"does not match capability '{capability}'. Capabilities: {model_caps}. "
                                f"Falling through to model catalog search."
                            )
                    elif model_obj and not model_obj.enabled:
                        logger.warning(
                            f"[MODEL RESOLVER] Configured model '{func_config.model_id}' for {function_id} is DISABLED. "
                            f"Falling through to model catalog search."
                        )
            except Exception as e:
                logger.warning(f"[MODEL RESOLVER] Failed to query AI Function Config for '{function_id}': {e}")

        # ── Step 2: Search ai_models for DEFAULT model with matching capability ──
        try:
            stmt = select(AIModel).where(AIModel.enabled == True, AIModel.is_default == True)
            res = await db.execute(stmt)
            default_models = res.scalars().all()

            for m in default_models:
                model_caps = _parse_capabilities(m.capabilities)
                if _is_capability_compatible(capability, model_caps, m.provider_id):
                    resolution = ModelResolution(
                        provider_id=m.provider_id,
                        model_id=m.id,
                        model_name=m.model_name,
                        source="Settings Database (Default Model)",
                        capabilities=model_caps,
                    )
                    _log_resolution(capability, resolution, stage)
                    return resolution
        except Exception as e:
            logger.warning(f"[MODEL RESOLVER] Failed to query default models: {e}")

        # ── Step 3: Search ai_models for ANY enabled model with capability ──
        try:
            stmt = select(AIModel).where(AIModel.enabled == True)
            res = await db.execute(stmt)
            all_models = res.scalars().all()

            for m in all_models:
                model_caps = _parse_capabilities(m.capabilities)
                if _is_capability_compatible(capability, model_caps, m.provider_id):
                    resolution = ModelResolution(
                        provider_id=m.provider_id,
                        model_id=m.id,
                        model_name=m.model_name,
                        source="Settings Database (Enabled Model Fallback)",
                        capabilities=model_caps,
                    )
                    logger.warning(
                        f"[MODEL RESOLVER] No DEFAULT model found for '{capability}'. "
                        f"Using enabled model: {m.id}"
                    )
                    _log_resolution(capability, resolution, stage)
                    return resolution
        except Exception as e:
            logger.warning(f"[MODEL RESOLVER] Failed to query enabled models: {e}")

        raise PipelineError(
            code=AI_MODEL_NOT_FOUND,
            stage=stage,
            message=(
                f"Không tìm thấy AI Model khả dụng trong Database cho chức năng {cap_display}. "
                f"Vui lòng kiểm tra Cài đặt AI Model trong hệ thống."
            ),
        )

    @classmethod
    async def resolve_stt_model(
        cls,
        db: Optional[AsyncSession] = None,
        requested_model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Convenience method to resolve STT model strictly from Database (or explicit override)."""
        if requested_model:
            return {
                "provider_id": "gemini" if "gemini" in requested_model.lower() else "openai",
                "model_id": requested_model,
                "source": "REQUESTED MODEL",
            }
        res = await cls.resolve_model(db, capability="STT", stage="STT")
        return res.to_dict()

    @classmethod
    async def resolve_llm_model(
        cls,
        db: Optional[AsyncSession] = None,
        requested_model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Convenience method to resolve LLM/Translation model strictly from Database (or explicit override)."""
        if requested_model:
            return {
                "provider_id": "gemini" if "gemini" in requested_model.lower() else "openai",
                "model_id": requested_model,
                "source": "REQUESTED MODEL",
            }
        res = await cls.resolve_model(db, capability="TRANSLATION", stage="LLM")
        return res.to_dict()

    @staticmethod
    async def validate_pipeline_models(
        db: AsyncSession,
        capabilities_needed: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Pre-validate all models needed for a pipeline before starting.

        Returns list of validation issues. Empty list = all OK.
        """
        from app.services.key_manager import get_key_manager

        issues: List[Dict[str, Any]] = []
        key_mgr = get_key_manager()

        for cap in capabilities_needed:
            cap_display = CAPABILITY_DISPLAY.get(cap, cap)
            try:
                resolution = await AIModelResolver.resolve_model(db, capability=cap)

                # Check provider API key
                provider_id = resolution.provider_id
                # Free providers don't need keys
                free_providers = {"edge_tts", "pollinations"}
                if provider_id not in free_providers:
                    keys = await key_mgr.get_keys_for_provider(provider_id)
                    valid_keys = [k for k in keys if k.get("status") not in ("disabled", "invalid")]
                    if not valid_keys:
                        # Also check .env API key as backup
                        from app.config import get_settings
                        settings = get_settings()
                        env_key_map = {
                            "gemini": settings.GEMINI_API_KEY,
                            "openai": settings.OPENAI_API_KEY,
                            "elevenlabs": settings.ELEVENLABS_API_KEY,
                            "google_cloud_tts": settings.GOOGLE_CLOUD_TTS_API_KEY,
                            "kling": settings.KLING_API_KEY,
                            "fal": settings.FAL_API_KEY,
                        }
                        env_key = env_key_map.get(provider_id, "")
                        if not env_key:
                            issues.append({
                                "capability": cap,
                                "capability_display": cap_display,
                                "code": AI_PROVIDER_AUTH_ERROR,
                                "message": f"Chưa cấu hình API Key cho provider '{provider_id}' (chức năng {cap_display}).",
                                "provider": provider_id,
                                "model": resolution.model_id,
                            })

            except PipelineError as pe:
                issues.append({
                    "capability": cap,
                    "capability_display": cap_display,
                    "code": pe.code,
                    "message": pe.message,
                    "provider": pe.provider,
                    "model": pe.model,
                })

        return issues

    @staticmethod
    async def resolve_model_safe(
        db: Optional[AsyncSession],
        capability: str,
        stage: str = "",
    ) -> Optional[ModelResolution]:
        """
        Safe version of resolve_model that returns None on failure instead of raising.
        Use only for non-critical operations where a missing model is acceptable.
        """
        try:
            return await AIModelResolver.resolve_model(db, capability=capability, stage=stage)
        except PipelineError:
            return None
        except Exception as e:
            logger.warning(f"[MODEL RESOLVER] Safe resolution failed for '{capability}': {e}")
            return None


def _parse_capabilities(caps_str: str) -> List[str]:
    """Parse capabilities JSON string into list."""
    try:
        caps = json.loads(caps_str)
        if isinstance(caps, list):
            return caps
    except Exception:
        pass
    return [caps_str] if caps_str else []


def _log_resolution(capability: str, resolution: ModelResolution, stage: str = "") -> None:
    """Log model resolution decision with full diagnostic trace."""
    stage_prefix = f"[{stage}] " if stage else ""
    logger.info(
        f"{stage_prefix}[MODEL RESOLVER] "
        f"Capability: {capability} | "
        f"Selected Provider: {resolution.provider_id} | "
        f"Selected Model: {resolution.model_id} | "
        f"Model Name: {resolution.model_name} | "
        f"Source: {resolution.source} | "
        f"Fallback Enabled: {resolution.fallback_enabled}"
    )
