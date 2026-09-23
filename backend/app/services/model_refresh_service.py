"""Additive discovery and explicit, fail-closed catalog reconciliation.

Owns sessions/commits: callers commit newly created credentials before invoking.
Network calls happen after the snapshot session closes. Provider revision locks
serialize reconciliation with CredentialService mutations on SQLite and MySQL.
All credential writes must use CredentialService; direct SQL writers must acquire
the same provider lock. Model rows are retired, never physically deleted.
"""
import asyncio
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models import APIKey, CatalogModel, CatalogRefreshRun, KeyModelAccess, Provider
from app.models.api_key import utcnow
from app.models.settings import AIFunctionConfig
from app.providers.discovery.adapters import ADAPTERS
from app.providers.discovery.types import DiscoveredModel, DiscoveryResult
from app.services.credential_service import CredentialError, CredentialService, lock_catalog_provider
from app.services.model_discovery_service import discover_models

EDGE_PROVIDERS = {"edge_tts", "edge-tts"}


@dataclass(frozen=True)
class RefreshOutcome:
    id: str
    status: str
    summary: dict


def _signature(keys):
    return tuple(sorted((k.id, k.provider_id, k.revision, k.enabled, k.ciphertext) for k in keys))


def _validated(result, provider, secret):
    """Do not let an unexpected injected/adapter result authorize retirement."""
    if (not isinstance(result, DiscoveryResult)
            or result.status not in {"complete", "partial", "failed", "unsupported"}
            or result.access_scope not in {"credential", "catalog", "unknown"}
            or not isinstance(result.models, tuple)
            or any(not isinstance(m, DiscoveredModel) or not isinstance(m.remote_model_id, str)
                   or not m.remote_model_id or len(m.remote_model_id) > 255
                   or m.display_name is not None and (not isinstance(m.display_name, str) or len(m.display_name) > 255)
                   for m in result.models)):
        return DiscoveryResult("failed", error_code="malformed")
    adapter = ADAPTERS.get(provider)
    models = tuple(DiscoveredModel(m.remote_model_id, m.display_name,
        adapter.metadata(m.metadata, secret) if adapter is not None else {}) for m in result.models)
    return DiscoveryResult(result.status, models, result.error_code, result.pages_fetched, result.access_scope)


def _complete(result):
    return (result.status == "complete" and bool(result.models) and result.error_code is None
            and result.access_scope in {"credential", "catalog"})


def _safe_error(result):
    allowed = {"auth_invalid", "permission_denied", "rate_limited", "malformed", "unsupported",
               "timeout", "transient", "redirect_rejected", "request_rejected", "empty_result",
               "incomplete", "page_limit", "model_limit", "byte_limit", "credential_unavailable"}
    if result.error_code is None:
        return None if _complete(result) else "incomplete"
    return result.error_code if result.error_code in allowed else "discovery_failed"


class ModelRefreshService:
    def __init__(self, sessions: async_sessionmaker, data_dir: Path, *, discovery=discover_models,
                 master_key: bytes | str | None = None):
        self.sessions = sessions
        self.data_dir = data_dir
        self.discovery = discovery
        self.master_key = master_key

    async def discover_key(self, key_id: str) -> RefreshOutcome:
        """Discover one committed key. Always additive, including its access rows."""
        return await self._run(key_id)

    async def refresh(self) -> RefreshOutcome:
        """Explicit global refresh: union all active credentials per provider."""
        return await self._run(None)

    async def _run(self, key_id):
        async with self.sessions.begin() as db:
            run = CatalogRefreshRun(mode="additive" if key_id else "refresh")
            db.add(run)
            await db.flush()
            run_id = run.id
            providers = (await db.scalars(select(Provider).order_by(Provider.id))).all()
            revisions = {p.id: (p.catalog_revision, p.enabled) for p in providers}
            keys = (await db.scalars(select(APIKey).order_by(APIKey.id))).all()
            signature = _signature(keys)
            active_providers = {p.id for p in providers if p.enabled and p.id not in EDGE_PROVIDERS}
            selected = [k for k in keys if k.enabled and k.provider_id in active_providers
                        and (key_id is None or k.id == key_id)]
            credentials = None
            staged = []
            for key in selected:
                try:
                    if credentials is None:
                        credentials = await CredentialService.open(db, self.data_dir, master_key=self.master_key)
                    secret = await credentials.reveal(key.id)
                except CredentialError:
                    secret = None
                staged.append((key.id, key.provider_id, secret))
        # No DB session/transaction survives into this loop.
        results = defaultdict(list)
        try:
            for kid, provider, secret in staged:
                if secret is None:
                    result = DiscoveryResult("failed", error_code="credential_unavailable")
                else:
                    try:
                        result = _validated(await self.discovery(provider, secret), provider, secret)
                    except Exception:
                        # No adapter exception text is persisted or exposed (may contain auth).
                        result = DiscoveryResult("failed", error_code="discovery_failed")
                results[provider].append((kid, result))
            return await self._reconcile(run_id, key_id, revisions, signature, results)
        except asyncio.CancelledError:
            await self._finish_failed(run_id, "cancelled")
            raise
        except Exception:
            # The reconciliation transaction rolls back as a unit before recording failure.
            return await self._finish_failed(run_id, "failed")

    async def _finish_failed(self, run_id, status):
        summary = {"error_code": "refresh_" + status}
        async with self.sessions.begin() as db:
            run = await db.get(CatalogRefreshRun, run_id)
            run.status, run.summary, run.completed_at = status, summary, utcnow()
        return RefreshOutcome(run_id, status, summary)

    async def _reconcile(self, run_id, key_id, revisions, signature, results):
        async with self.sessions.begin() as db:
            # UPDATE is intentional: SELECT FOR UPDATE is ignored by SQLite.
            # Deterministic order prevents MySQL provider-lock inversion.
            for provider in sorted(revisions):
                await lock_catalog_provider(db, provider)
            current = (await db.scalars(select(Provider).with_for_update())).all()
            keys = (await db.scalars(select(APIKey).with_for_update())).all()
            stale = ({p.id: (p.catalog_revision, p.enabled) for p in current}
                     != {p: (r + 1, enabled) for p, (r, enabled) in revisions.items()}
                     or _signature(keys) != signature)
            summary = {"providers": {}}
            status = "stale" if stale else "complete"
            if not stale:
                targets = sorted(results) if key_id else sorted(revisions)
                for provider in targets:
                    entries = results.get(provider, [])
                    report = {"keys_scanned": len(entries), "retired": 0,
                              "status": "preserved", "results": [
                                  {"key_id": kid, "status": result.status,
                                   "access_scope": result.access_scope,
                                   "error_code": _safe_error(result),
                                   "complete": _complete(result)} for kid, result in entries]}
                    summary["providers"][provider] = report
                    if not entries:
                        report["reason"] = "system_keyless" if provider in EDGE_PROVIDERS else "no_active_keys"
                        if provider in ADAPTERS and next(p for p in current if p.id == provider).enabled:
                            await self._apply_provider(db, provider, [], True, report)
                        continue
                    complete = all(_complete(result) for _, result in entries)
                    if not complete:
                        status = "partial"
                    await self._apply_provider(db, provider, entries, bool(not key_id and complete), report)
                if key_id and not results:
                    status = "partial"
                    summary["error_code"] = "key_unavailable"
                await self._reconcile_defaults(db)
            run = await db.get(CatalogRefreshRun, run_id)
            run.status, run.summary, run.completed_at = status, summary, utcnow()
        return RefreshOutcome(run_id, status, summary)

    async def _apply_provider(self, db, provider, entries, cleanup, report):
        rows = {m.remote_model_id: m for m in (await db.scalars(
            select(CatalogModel).where(CatalogModel.provider_id == provider))).all()}
        visible = set()
        for kid, result in entries:
            # Partial pages can add evidence; failed/unsupported results cannot.
            if result.status not in {"complete", "partial"}:
                continue
            for discovered in result.models:
                visible.add(discovered.remote_model_id)
                model = rows.get(discovered.remote_model_id)
                if model is None:
                    model = CatalogModel(provider_id=provider, remote_model_id=discovered.remote_model_id,
                                         display_name=discovered.display_name)
                    db.add(model)
                    await db.flush()
                    rows[model.remote_model_id] = model
                # Non-discovered rows are curated: positive matches can establish
                # listing edges, but cannot rewrite or reactivate the model row.
                if model.source == "discovered":
                    model.retired_at = None
                    model.discovery_metadata = discovered.metadata
                    if discovered.display_name is not None:
                        model.display_name = discovered.display_name
                if result.access_scope == "credential":
                    access = await db.get(KeyModelAccess, (kid, model.id))
                    if access is None:
                        db.add(KeyModelAccess(key_id=kid, model_id=model.id, provider_id=provider))
            # No access cleanup when *any* key in this provider failed/was partial.
            if cleanup:
                found = [rows[m.remote_model_id].id for m in result.models] if result.access_scope == "credential" else []
                await db.execute(delete(KeyModelAccess).where(KeyModelAccess.key_id == kid,
                                                             KeyModelAccess.model_id.not_in(found)))
        if cleanup and provider not in EDGE_PROVIDERS:
            for remote_id, model in rows.items():
                if remote_id not in visible and model.source == "discovered" and model.retired_at is None:
                    model.retired_at = utcnow()
                    report["retired"] += 1
            report["status"] = "reconciled"
        else:
            report["status"] = "additive"
        await db.flush()

    async def _reconcile_defaults(self, db):
        # Capability classification is a later layer. Preserve user choices and
        # expose invalid defaults instead of selecting an unclassified replacement.
        rows = (await db.scalars(select(CatalogModel))).all()
        by_remote = {(m.provider_id, m.remote_model_id): m for m in rows}
        by_id = {(m.provider_id, m.id): m for m in rows}
        for config in (await db.scalars(select(AIFunctionConfig))).all():
            model = by_id.get((config.primary_provider_id, config.model_id)) or by_remote.get(
                (config.primary_provider_id, config.model_id))
            if model is not None and model.retired_at is not None:
                config.configuration_error = "catalog_model_retired"
            elif model is not None and config.configuration_error == "catalog_model_retired":
                config.configuration_error = None
