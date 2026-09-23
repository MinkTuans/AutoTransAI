"""Small request-local JSON LLM boundary shared by editor QC and SEO."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import get_settings
from app.models import APIKey, CatalogModel, CatalogRefreshRun
from app.models.settings import AIFunctionConfig
from app.providers.registry import get_registry
from app.services.ai_routing import (
    RouteConfigurationError, RouteTarget, UnsupportedModalityError, build_route, invoke_route,
)


class InvalidEditorOutput(ValueError):
    code = "invalid_output"


async def generate_catalog_json(
    *, sessions: async_sessionmaker[AsyncSession] | None, data_dir: Path | None,
    prompt_prefix: str, transcript: str, prompt_suffix: str,
    validate: Callable[[dict], dict],
) -> dict | None:
    """Return None only for an uninitialized catalog; canonical errors are visible."""
    if sessions is None:
        return None
    async with sessions() as db:
        catalog_model = await db.scalar(select(CatalogModel.id).where(
            CatalogModel.source != "system", CatalogModel.provider_id.in_(("gemini", "openai", "anthropic")),
        ).limit(1))
        catalog_key = await db.scalar(select(APIKey.id).where(
            APIKey.provider_id.in_(("gemini", "openai", "anthropic")),
        ).limit(1))
        await db.scalar(select(CatalogRefreshRun.id).limit(1))
        config = await db.get(AIFunctionConfig, "translation")
        selected = await db.get(CatalogModel, config.model_id) if config and config.model_id else None
        if catalog_model is None and catalog_key is None and selected is None:
            return None
        if config is None or not config.model_id:
            raise RouteConfigurationError("LLM default is not configured.")
        route = await build_route(db, "LLM")
        limits: dict[str, int] = {}
        for target in route.targets:
            if target.model_id in limits:
                continue
            model = await db.get(CatalogModel, target.model_id)
            metadata = model.discovery_metadata if isinstance(model.discovery_metadata, dict) else {}
            limits[target.model_id] = 6000
            for field in ("inputTokenLimit", "max_input_tokens"):
                value = metadata.get(field)
                if type(value) is int and value > 0:
                    limits[target.model_id] = min(6000, max(0, value - 512))
                    break

    fixed = prompt_prefix + prompt_suffix
    fixed_bytes = len(fixed.encode("utf-8"))

    async def transport(target: RouteTarget, secret: str | None) -> dict:
        room = limits[target.model_id] - fixed_bytes
        if room < 8:
            raise UnsupportedModalityError("Editor prompt exceeds model context budget.")
        prompt = prompt_prefix + transcript.encode("utf-8")[:room].decode("utf-8", errors="ignore") + prompt_suffix
        adapter = get_registry().get_llm(target.provider_id)
        if adapter is None:
            raise UnsupportedModalityError("No editor LLM adapter for this provider.")
        response = await adapter.generate_text(prompt, route_target=target, api_key=secret)
        if not isinstance(response, str):
            raise InvalidEditorOutput() from None
        value = response.strip()
        fence = re.fullmatch(r"```(?:json)?\s*([\s\S]*?)\s*```", value)
        if fence:
            value = fence.group(1).strip()
        try:
            parsed = json.loads(value)
            if not isinstance(parsed, dict):
                raise InvalidEditorOutput() from None
            return validate(parsed)
        except (ValueError, TypeError, KeyError):
            raise InvalidEditorOutput() from None

    return await invoke_route(route, transport, sessions, data_dir or get_settings().DATA_DIR,
                              max_attempts=2, timeout=60.0)
