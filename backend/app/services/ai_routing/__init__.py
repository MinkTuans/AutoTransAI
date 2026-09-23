"""Immutable catalog route plans; generation adapters join this contract in Task 6."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Awaitable, Callable, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models import APIKey, CatalogModel, KeyModelAccess, Provider
from app.models.settings import AIFunctionConfig
from app.services.capability_registry import CAPABILITIES, compatible, model_evidence
from app.services.credential_service import CredentialError, CredentialService

_FUNCTION = {"STT": "stt", "TRANSLATION": "translation", "LLM": "translation", "TTS": "tts",
             "VIDEO_GENERATION": "video_generation", "IMAGE_GENERATION": "image_generation",
             "VISUAL_GENDER": "visual_gender"}
# Discovery adapters for these services return a public catalog listing.
# They cannot establish a model/key edge; an enabled provider key is only a
# candidate to try at generation time, not verified model entitlement.
_PUBLIC_CATALOG_PROVIDERS = frozenset({"fal", "elevenlabs"})
_KEYLESS_SYSTEM_IMAGE_PROVIDERS = frozenset({"pollinations", "local_image"})
_log = logging.getLogger(__name__)


def _keyless_provider(provider_id: str) -> bool:
    """Service credential policy, independent of catalog model lifecycle."""
    return provider_id == "edge_tts" or provider_id in _KEYLESS_SYSTEM_IMAGE_PROVIDERS


def _keyless_allowed(model: CatalogModel, capability: str) -> bool:
    return (model.provider_id == "edge_tts" and capability == "TTS"
            or (capability == "IMAGE_GENERATION" and model.source == "system"
                and model.provider_id in _KEYLESS_SYSTEM_IMAGE_PROVIDERS))


def _key_eligible(key: APIKey, now: datetime) -> bool:
    if not key.enabled or key.runtime_status in ("invalid", "exhausted"):
        return False
    if key.cooldown_until is not None and key.cooldown_until > now:
        return False
    return key.runtime_status in ("ready", "rate_limited")


class RouteConfigurationError(Exception):
    """Visible configuration problem; no credential or provider exception text."""


class RouteExhausted(Exception):
    """Every eligible target failed; message contains only classified codes."""


class RoutePending(Exception):
    """An accepted asynchronous provider job may still finish; never retry it."""

    code = "pending"


class UnsupportedModalityError(Exception):
    """The runtime adapter cannot invoke this model for the requested function."""


@dataclass(frozen=True)
class RouteTarget:
    model_id: str
    provider_id: str
    remote_model_id: str
    key_id: str | None
    capability: str
    access_scope: str = "listing_unverified"


@dataclass(frozen=True)
class RoutePlan:
    capability: str
    targets: tuple[RouteTarget, ...]
    configured_model_id: str | None


async def build_route(db: AsyncSession, capability: str, *, preferred_key_ids: tuple[str, ...] = ()) -> RoutePlan:
    """Order default, same-provider alternatives, then other enabled providers.

    A listing edge is visibility evidence, never successful generation proof.
    Invalid explicit defaults fail visibly and preserve their stored choice.
    """
    if capability not in CAPABILITIES:
        raise RouteConfigurationError("Unsupported AI capability.")
    config = await db.get(AIFunctionConfig, _FUNCTION[capability])
    providers = {p.id: p for p in (await db.scalars(select(Provider))).all() if p.enabled}
    models = (await db.scalars(select(CatalogModel))).all()
    usable = {m.id: m for m in models if m.provider_id in providers and m.enabled
              and m.retired_at is None and compatible(capability, model_evidence(m))}
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    keys = {k.id: k for k in (await db.scalars(select(APIKey))).all() if _key_eligible(k, now)}
    access: dict[str, list[str]] = {}
    for edge in (await db.scalars(select(KeyModelAccess))).all():
        if edge.key_id in keys and edge.model_id in usable and keys[edge.key_id].provider_id == edge.provider_id == usable[edge.model_id].provider_id:
            access.setdefault(edge.model_id, []).append(edge.key_id)
    for model in usable.values():
        if model.provider_id in _PUBLIC_CATALOG_PROVIDERS:
            access[model.id] = [key.id for key in keys.values() if key.provider_id == model.provider_id]
    priority = {key_id: index for index, key_id in enumerate(preferred_key_ids)}
    for ids in access.values():
        ids.sort(key=lambda key_id: (0 if key_id in priority else 1,
                                     priority.get(key_id, 0), keys[key_id].priority,
                                     keys[key_id].request_count, key_id))

    def available(model: CatalogModel) -> bool:
        return _keyless_allowed(model, capability) or bool(access.get(model.id))

    configured = config.model_id if config and config.model_id and config.model_id != "default" else None
    selected = None
    if config and config.configuration_error:
        raise RouteConfigurationError("Configured AI model needs review.")
    if configured:
        selected = usable.get(configured)
        if selected is None:
            matches = [m for m in usable.values() if m.remote_model_id == configured and m.provider_id == config.primary_provider_id]
            selected = matches[0] if len(matches) == 1 else None
        if selected is None or selected.provider_id != config.primary_provider_id or not available(selected):
            raise RouteConfigurationError("Configured AI model is unavailable, incompatible, or has no credential access.")
    ordered = sorted((m for m in usable.values() if available(m)), key=lambda m: (m.provider_id, m.remote_model_id, m.id))
    if config and config.model_id == "default":
        preferred = [m for m in ordered if m.provider_id == config.primary_provider_id]
        if not preferred:
            raise RouteConfigurationError("No compatible accessible model exists for the configured provider.")
        selected = preferred[0]
    if selected:
        ordered.remove(selected)
        ordered = [selected] + sorted((m for m in ordered if m.provider_id == selected.provider_id),
                                      key=lambda m: (m.remote_model_id, m.id)) + [m for m in ordered if m.provider_id != selected.provider_id]
    targets = tuple(RouteTarget(m.id, m.provider_id, m.remote_model_id, key_id, capability,
                                "keyless" if key_id is None else
                                "catalog_unverified" if m.provider_id in _PUBLIC_CATALOG_PROVIDERS else "listing_unverified")
                    for m in ordered for key_id in (
                        [None] if _keyless_allowed(m, capability) else access[m.id]))
    if not targets:
        raise RouteConfigurationError("No compatible AI model with credential access is available.")
    return RoutePlan(capability, targets, selected.id if selected and configured else None)


def classify_failure(error: BaseException) -> str:
    """Return an allowlisted code; never include arbitrary exception text."""
    if isinstance(error, UnsupportedModalityError):
        return "capability_mismatch"
    if isinstance(error, asyncio.TimeoutError):
        return "timeout"
    code = getattr(error, "code", None)
    if code == "invalid_output":
        return "invalid_output"
    if code == "insufficient_quota":
        return "quota"
    status = getattr(error, "status_code", None)
    if status is None:
        status = getattr(error, "http_status", None)
    if status is None:
        status = getattr(getattr(error, "response", None), "status_code", None)
    if status == 401:
        return "auth"
    if status == 403:
        return "model_unavailable"
    if status == 429:
        return "rate_limit"
    if status == 404:
        return "model_unavailable"
    if status in (400, 422):
        return "capability_mismatch"
    if isinstance(status, int) and status >= 500:
        return "provider_unavailable"
    name = type(error).__name__.lower()
    message = str(error).lower()
    for token, code in (("auth", "auth"), ("quota", "quota"), ("rate", "rate_limit"),
                        ("model unavailable", "model_unavailable"), ("provider unavailable", "provider_unavailable"),
                        ("unsupported", "capability_mismatch")):
        if token in name or token in message:
            return code
    return "provider_unavailable"


_T = TypeVar("_T")


async def invoke_route(route: RoutePlan, transport: Callable[[RouteTarget, str | None], Awaitable[_T]],
                       sessions: async_sessionmaker[AsyncSession], data_dir: Path, *, max_attempts: int = 2,
                       timeout: float = 30.0, sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
                       wait_for: Callable[[Awaitable[_T], float], Awaitable[_T]] = asyncio.wait_for) -> _T:
    if max_attempts < 1 or max_attempts > 5 or timeout <= 0:
        raise ValueError("Route retry or timeout limit is invalid.")
    failures: list[str] = []
    for target in route.targets:
        try:
            for attempt in range(max_attempts):
                # Recheck before every transport, including a retry after sleep.
                async with sessions() as db:
                    provider = await db.get(Provider, target.provider_id)
                    model = await db.get(CatalogModel, target.model_id)
                    if (provider is None or not provider.enabled or model is None or not model.enabled or model.retired_at is not None
                            or model.provider_id != target.provider_id
                            or model.remote_model_id != target.remote_model_id
                            or not compatible(target.capability, model_evidence(model))):
                        raise RouteConfigurationError("Catalog route target changed.")
                    if target.key_id:
                        row = await db.get(APIKey, target.key_id)
                        if (row is None or not _key_eligible(row, datetime.now(timezone.utc).replace(tzinfo=None))
                                or row.provider_id != target.provider_id):
                            raise RouteConfigurationError("Credential access changed.")
                        if target.access_scope == "listing_unverified" and await db.get(
                                KeyModelAccess, (target.key_id, target.model_id)) is None:
                            raise RouteConfigurationError("Credential listing access changed.")
                        revision = row.revision
                        secret = await (await CredentialService.open(db, data_dir)).reveal(target.key_id)
                    else:
                        if not _keyless_allowed(model, target.capability) or target.access_scope != "keyless":
                            raise RouteConfigurationError("Keyless target is not allowed.")
                        revision, secret = None, None

                async def account(*, success: bool, code: str | None = None,
                                  error: BaseException | None = None) -> None:
                    if target.key_id is None or revision is None:
                        return
                    status = getattr(error, "status_code", None)
                    if status is None:
                        status = getattr(error, "http_status", None)
                    if status is None:
                        status = getattr(getattr(error, "response", None), "status_code", None)
                    try:
                        async with sessions.begin() as accounting_db:
                            credentials = await CredentialService.open(accounting_db, data_dir)
                            await credentials.record_result(
                                target.key_id, revision, success=success, code=code,
                                http_status=status if isinstance(status, int) else None,
                                quota_exhausted=getattr(error, "code", None) == "insufficient_quota",
                            )
                    except Exception:
                        # The provider may already have completed a side effect.
                        # Never expose accounting/SQL exception details or resubmit it.
                        _log.warning("AI route credential result accounting failed")

                try:
                    result = await wait_for(transport(target, secret), timeout)
                except RoutePending:
                    raise
                except Exception as error:
                    code = classify_failure(error)
                    await account(success=False, code=code, error=error)
                    if code not in ("timeout", "provider_unavailable") or attempt + 1 == max_attempts:
                        failures.append(code)
                        break
                    await sleep(min(0.25 * (2 ** attempt), 2.0))
                else:
                    await account(success=True)
                    return result
        except RoutePending:
            raise
        except Exception as error:
            failures.append("configuration" if isinstance(error, (RouteConfigurationError, CredentialError))
                            else classify_failure(error))
    raise RouteExhausted("AI route failed: " + ", ".join(failures))
