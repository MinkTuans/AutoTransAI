"""Explicit, caller-transactional remap of archival function defaults.

Only previously discovered catalog identities and keyless system models can
receive a legacy default. This service never imports legacy catalog rows.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import APIKey, CatalogModel, KeyModelAccess, Provider
from app.models.settings import AIModel, AIFunctionConfig
from app.services.ai_routing import _PUBLIC_CATALOG_PROVIDERS, _key_eligible, _keyless_allowed
from app.services.capability_registry import CAPABILITIES, compatible, model_evidence
from app.services.model_resolver import _is_capability_compatible


_MIGRATION_ERROR = "legacy_default_unresolved"
_CONFLICT_ISSUES = frozenset({"legacy_provider_conflict", "canonical_provider_conflict"})


def _is_canonical_uuid(value: str) -> bool:
    try:
        return str(UUID(value)) == value.lower()
    except (ValueError, TypeError, AttributeError):
        return False


def _legacy_capability_issue(row: AIModel, capability: str) -> str | None:
    try:
        tags = json.loads(row.capabilities)
    except (ValueError, TypeError, RecursionError):
        return "invalid_legacy_capability"
    if not isinstance(tags, list) or any(type(tag) is not str or tag not in CAPABILITIES for tag in tags):
        return "invalid_legacy_capability"
    if not _is_capability_compatible(capability, tags, row.provider_id):
        return "capability_mismatch"
    return None


def _maybe_lock(statement, dry_run: bool):
    return statement if dry_run else statement.with_for_update()


async def _has_access(
    db: AsyncSession, model: CatalogModel, capability: str, *, dry_run: bool,
) -> bool:
    if model.source == "system" and _keyless_allowed(model, capability):
        return True
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    keys = (await db.scalars(_maybe_lock(
        select(APIKey).where(APIKey.provider_id == model.provider_id), dry_run
    ).execution_options(populate_existing=True))).all()
    eligible = {key.id for key in keys if key.provider_id == model.provider_id and _key_eligible(key, now)}
    if not eligible:
        return False
    if model.provider_id in _PUBLIC_CATALOG_PROVIDERS:
        return True
    edges = (await db.scalars(_maybe_lock(select(KeyModelAccess).where(
        KeyModelAccess.model_id == model.id, KeyModelAccess.provider_id == model.provider_id,
    ), dry_run).execution_options(populate_existing=True))).all()
    return any(edge.key_id in eligible and edge.model_id == model.id
               and edge.provider_id == model.provider_id for edge in edges)


async def remap_legacy_function_defaults(
    db: AsyncSession, *, dry_run: bool = False,
) -> dict[str, object]:
    """Map only safe legacy defaults; caller owns commit or rollback.

    Locking reads are current reads under MySQL REPEATABLE READ. Provider locks
    interlock with catalog refresh and credential mutation without incrementing
    their catalog revision for this configuration-only operation. A dry-run is
    advisory: nonlocking MySQL reads can use an older transaction snapshot, so
    later locked execution may differ after concurrent commits.
    """
    if dry_run:
        if db.new or db.dirty or db.deleted:
            raise RuntimeError("Legacy default shadow comparison requires a clean session.")
        # A separate identity map keeps populate_existing reads from
        # overwriting the caller's unflushed objects during a read-only preview.
        async with AsyncSession(bind=await db.connection(), autoflush=False) as shadow:
            return await _evaluate_legacy_function_defaults(shadow, dry_run=True)
    return await _evaluate_legacy_function_defaults(db, dry_run=False)


async def _evaluate_legacy_function_defaults(db: AsyncSession, *, dry_run: bool) -> dict[str, object]:
    counts = {"resolved": 0, "unresolved": 0, "already_canonical": 0, "conflicts": 0}
    issues: set[str] = set()
    # Canonical Function PUT locks its provider before the config. Lock the
    # small provider table in stable order first so this batch service cannot
    # invert that order if a config's provider changes concurrently.
    providers = {provider.id: provider for provider in (await db.scalars(
        _maybe_lock(select(Provider).order_by(Provider.id), dry_run)
        .execution_options(populate_existing=True)
    )).all()}
    configs = (await db.scalars(_maybe_lock(
        select(AIFunctionConfig).order_by(AIFunctionConfig.function_id), dry_run
    ).execution_options(populate_existing=True))).all()
    for config in configs:
        reason = None
        provider_id = config.primary_provider_id
        provider = providers.get(provider_id)
        if provider is None or provider.id != provider_id:
            reason = "missing_provider"

        # A catalog UUID belonging to this provider is already canonical even
        # when its current route is unavailable or has an unrelated error.
        existing = await db.scalar(_maybe_lock(
            select(CatalogModel).where(CatalogModel.id == config.model_id), dry_run
        ).execution_options(populate_existing=True))
        if existing is not None and existing.id != config.model_id:
            existing = None
        if _is_canonical_uuid(config.model_id) and existing is not None and existing.provider_id == provider_id:
            counts["already_canonical"] += 1
            continue

        collision = existing is not None and existing.provider_id != provider_id
        if reason is None and config.capability not in CAPABILITIES:
            reason = "invalid_function_capability"
        if reason is None and config.model_id == "default":
            reason = "default_sentinel"
        legacy = None
        if reason is None:
            legacy = await db.scalar(_maybe_lock(
                select(AIModel).where(AIModel.id == config.model_id), dry_run
            ).execution_options(populate_existing=True))
            if legacy is None or legacy.id != config.model_id:
                reason = "canonical_provider_conflict" if collision else "missing_legacy_model"
            elif legacy.provider_id != provider_id:
                reason = "legacy_provider_conflict"
            else:
                reason = _legacy_capability_issue(legacy, config.capability)

        model = None
        if reason is None:
            matches = [candidate for candidate in (await db.scalars(_maybe_lock(
                select(CatalogModel).where(
                CatalogModel.provider_id == provider_id,
                CatalogModel.remote_model_id == legacy.id,
            ), dry_run).execution_options(populate_existing=True))).all()
                       if candidate.provider_id == provider_id and candidate.remote_model_id == legacy.id]
            if not matches:
                reason = "canonical_provider_conflict" if collision else "missing_catalog_model"
            elif len(matches) != 1:
                reason = "ambiguous_catalog_model"
            else:
                model = matches[0]
                # The router permits unknown evidence, but rejects explicit
                # incompatibility; apply the same capability decision here.
                if (not provider.enabled or not model.enabled or model.retired_at is not None
                        or model.source not in ("discovered", "system")
                        or (model.source == "system" and not _keyless_allowed(model, config.capability))):
                    reason = "catalog_unavailable"
                elif not compatible(config.capability, model_evidence(model)):
                    reason = "capability_mismatch"
                elif not await _has_access(db, model, config.capability, dry_run=dry_run):
                    reason = "no_credential_access"

        if reason is None:
            if not dry_run:
                config.model_id = model.id
                if config.configuration_error == _MIGRATION_ERROR:
                    config.configuration_error = None
            counts["resolved"] += 1
        else:
            if not dry_run and config.configuration_error != _MIGRATION_ERROR:
                config.configuration_error = _MIGRATION_ERROR
            counts["unresolved"] += 1
            counts["conflicts"] += reason in _CONFLICT_ISSUES
            issues.add(reason)
    if not dry_run:
        await db.flush()
    return {"counts": counts, "issues": sorted(issues)}
