"""Explicit, caller-transaction import of legacy JSON credentials as disabled rows."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import APIKey, Provider
from app.services.credential_service import CredentialService, DuplicateCredentialError
from app.services.legacy_migration_inventory import MAX_ENTRIES, _read_file


_COUNT_NAMES = (
    "imported", "duplicate_source", "duplicate_existing",
    "skipped_missing_provider", "skipped_keyless_provider", "normalized_metadata",
)
_STATUSES = {"active": "ready", "ready": "ready", "rate_limited": "rate_limited",
             "exhausted": "exhausted", "invalid": "invalid", "disabled": "ready"}
_MAX_COUNTER = 2**31 - 1


def _result(status: str, counts: dict[str, int] | None = None) -> dict[str, object]:
    return {"status": status, "counts": counts if counts is not None else dict.fromkeys(_COUNT_NAMES, 0)}


def _metadata(entry: dict[str, object]) -> tuple[dict[str, object], bool]:
    normalized = False
    priority = entry.get("priority", 100)
    if type(priority) is not int or not 0 < priority <= _MAX_COUNTER:
        priority, normalized = 100, True
    status = entry.get("status", "ready")
    if not isinstance(status, str) or status not in _STATUSES:
        status, normalized = "ready", True
    counters = {}
    for legacy, canonical in (("total_requests", "request_count"),
                              ("successful_requests", "success_count"),
                              ("failed_requests", "failure_count")):
        value = entry.get(legacy, 0)
        if type(value) is not int or not 0 <= value <= _MAX_COUNTER:
            value, normalized = 0, True
        counters[canonical] = value
    cooldown = entry.get("cooldown_until")
    if cooldown is not None:
        try:
            if type(cooldown) not in (int, float) or not 0 <= cooldown < 253402300800:
                raise ValueError
            cooldown = datetime.fromtimestamp(cooldown, timezone.utc).replace(tzinfo=None)
        except (ValueError, OverflowError, OSError):
            cooldown, normalized = None, True
    return {"priority": priority, "runtime_status": _STATUSES[status],
            "cooldown_until": cooldown, **counters}, normalized


def _parse(data: bytes) -> list[tuple[str, str, dict[str, object]]]:
    try:
        parsed = json.loads(data)
        if not isinstance(parsed, dict) or len(parsed) > MAX_ENTRIES:
            raise ValueError
        entries = []
        for provider, values in parsed.items():
            if not isinstance(provider, str) or not provider or len(provider) > 50 or not isinstance(values, list):
                raise ValueError
            for value in values:
                if not isinstance(value, dict) or any(
                    not isinstance(value.get(field), str) or not value[field]
                    for field in ("key_id", "provider_id", "api_key")
                ) or value["provider_id"] != provider or value["api_key"] != value["api_key"].strip():
                    raise ValueError
                entries.append((provider, value["api_key"], value))
                if len(entries) > MAX_ENTRIES:
                    raise ValueError
        return entries
    except (UnicodeError, ValueError, TypeError, RecursionError):
        raise ValueError("invalid_source") from None


async def import_legacy_json_keys(
    db: AsyncSession, *, json_path: Path, master_key: bytes | str,
) -> dict[str, object]:
    """Read only the named JSON file; flush encrypted, disabled rows without committing."""
    data, error = _read_file(Path(json_path), "json")
    if error:
        return _result("invalid_source")
    if data is None:
        return _result("missing_source")
    try:
        entries = _parse(data)
    except ValueError:
        return _result("invalid_source")

    return await _import_parsed_keys(db, entries, source_path=Path(json_path), master_key=master_key)


async def _import_parsed_keys(
    db: AsyncSession, entries: list[tuple[str, str, dict[str, object]]],
    *, source_path: Path, master_key: bytes | str,
) -> dict[str, object]:
    """Shared disabled-key mutation; callers validate every source entry first."""

    counts = dict.fromkeys(_COUNT_NAMES, 0)
    prepared = []
    seen: set[tuple[str, str]] = set()
    for provider, secret, value in entries:
        identity = (provider, secret)
        if identity in seen:
            counts["duplicate_source"] += 1
            continue
        seen.add(identity)
        metadata, normalized = _metadata(value)
        counts["normalized_metadata"] += normalized
        prepared.append((provider, secret, metadata))

    with db.no_autoflush:
        providers = {row.id: row for row in (await db.scalars(select(Provider))).all()}
    eligible = []
    for provider, secret, metadata in prepared:
        row = providers.get(provider)
        if row is None:
            counts["skipped_missing_provider"] += 1
        elif not row.requires_api_key:
            counts["skipped_keyless_provider"] += 1
        else:
            eligible.append((provider, secret, metadata))

    if not eligible:
        return _result("imported", counts)
    service = await CredentialService.open(db, source_path.parent, master_key=master_key)
    for provider, secret, metadata in eligible:
        fingerprint = service._fingerprint(provider, secret)
        with db.no_autoflush:
            existing = await db.scalar(select(APIKey.id).where(
                APIKey.provider_id == provider, APIKey.fingerprint == fingerprint,
            ))
        if existing is not None:
            counts["duplicate_existing"] += 1
            continue
        try:
            dto = await service.create(provider, secret, enabled=False)
        except DuplicateCredentialError:
            counts["duplicate_existing"] += 1
            continue
        row = await db.get(APIKey, dto.id)
        for name, value in metadata.items():
            setattr(row, name, value)
        counts["imported"] += 1
    await db.flush()
    return _result("imported", counts)
