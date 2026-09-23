"""Read-only, explicit-path inventory for a future legacy data migration.

This module intentionally does not import KeyManager or application settings.
Only aggregate counts and fixed issue codes leave this module.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import stat

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import APIKey, CatalogModel, Provider
from app.models.settings import AIModel, AIFunctionConfig
from app.services.capability_registry import CAPABILITIES


MAX_FILE_BYTES = 1024 * 1024
MAX_ENTRIES = 5000
ENV_PROVIDERS = ("gemini", "openai", "google_cloud_tts", "elevenlabs", "kling", "fal")
COUNT_NAMES = (
    "providers", "legacy_models", "function_configs", "fallback_enabled",
    "fallback_references", "catalog_models", "api_keys", "json_providers",
    "json_keys", "env_providers", "env_keys", "effective_keys",
    "duplicate_json_keys", "duplicate_env_keys", "key_provider_mismatches",
    "source_disagreements", "model_provider_conflicts", "missing_model_providers",
    "invalid_model_capabilities", "unresolved_defaults", "missing_fallback_providers",
    "existing_canonical_identities",
)


def _read_file(path: Path | None, kind: str) -> tuple[bytes | None, str | None]:
    if path is None:
        return None, None
    try:
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            return None, f"{kind}_symlink_refused"
        if not stat.S_ISREG(mode):
            return None, f"{kind}_not_regular"
        # NONBLOCK prevents a pathname swap to a FIFO from hanging in open().
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))
        try:
            opened = os.fstat(fd)
            if not stat.S_ISREG(opened.st_mode):
                return None, f"{kind}_not_regular"
            if opened.st_size > MAX_FILE_BYTES:
                return None, f"{kind}_file_too_large"
            data = os.read(fd, MAX_FILE_BYTES + 1)
        finally:
            os.close(fd)
        if len(data) > MAX_FILE_BYTES:
            return None, f"{kind}_file_too_large"
        return data, None
    except FileNotFoundError:
        return None, None
    except OSError:
        return None, f"{kind}_read_error"


def _json_keys(data: bytes | None, counts: dict[str, int], issues: set[str]) -> dict[str, list[str]]:
    if data is None:
        return {}
    try:
        parsed = json.loads(data)
        if not isinstance(parsed, dict) or len(parsed) > MAX_ENTRIES:
            raise ValueError
        if any(not isinstance(provider, str) or not isinstance(entries, list)
               for provider, entries in parsed.items()):
            raise ValueError
        if sum(len(entries) for entries in parsed.values()) > MAX_ENTRIES:
            raise ValueError
        keys: dict[str, list[str]] = {}
        duplicates = 0
        mismatches = 0
        for provider, entries in parsed.items():
            seen_ids: set[str] = set()
            seen_values: set[str] = set()
            values: list[str] = []
            for entry in entries:
                if not isinstance(entry, dict) or not isinstance(entry.get("api_key"), str) or not isinstance(entry.get("key_id"), str) or not isinstance(entry.get("provider_id"), str):
                    raise ValueError
                key = entry["api_key"]
                key_id = entry["key_id"]
                if key in seen_values or key_id in seen_ids:
                    duplicates += 1
                seen_values.add(key)
                seen_ids.add(key_id)
                if entry["provider_id"] != provider:
                    mismatches += 1
                values.append(key)
            keys[provider] = values
        counts["json_providers"] = len(parsed)
        counts["json_keys"] = sum(map(len, keys.values()))
        counts["duplicate_json_keys"] = duplicates
        counts["key_provider_mismatches"] = mismatches
        return keys
    except (UnicodeError, ValueError, TypeError, RecursionError):
        issues.add("invalid_json")
        return {}


def _env_keys(data: bytes | None, counts: dict[str, int], issues: set[str]) -> dict[str, list[str]]:
    if data is None:
        return {}
    try:
        lines = data.decode("utf-8").splitlines()
    except UnicodeError:
        issues.add("invalid_env")
        return {}
    variables: dict[str, str] = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        name, sep, value = line.partition("=")
        if not sep:
            continue
        variables[name.strip()] = value.strip().strip('"').strip("'")
    keys: dict[str, list[str]] = {}
    for provider in ENV_PROVIDERS:
        base = f"{provider.upper()}_API_KEY"
        values = [value.strip() for value in variables.get(base, "").splitlines() if value.strip()]
        values.extend(variables.get(f"{base}_{i}", "").strip() for i in range(1, 10))
        values = [value for value in values if value]
        if values:
            keys[provider] = values
            counts["duplicate_env_keys"] += len(values) - len(set(values))
    counts["env_providers"] = len(keys)
    counts["env_keys"] = sum(map(len, keys.values()))
    return keys


async def inventory_legacy_migration(
    db: AsyncSession, *, json_path: Path, env_path: Path | None = None,
) -> dict[str, object]:
    """Inspect existing rows and explicitly supplied legacy files without writes."""
    counts = dict.fromkeys(COUNT_NAMES, 0)
    issues: set[str] = set()
    # Prevent a caller's pending ORM changes from being flushed by our SELECTs.
    with db.no_autoflush:
        providers = set((await db.scalars(select(Provider.id))).all())
        legacy = (await db.execute(select(AIModel.id, AIModel.provider_id, AIModel.capabilities))).all()
        configs = (await db.execute(select(
            AIFunctionConfig.primary_provider_id, AIFunctionConfig.model_id,
            AIFunctionConfig.fallback_enabled, AIFunctionConfig.fallback_provider_id,
        ))).all()
        catalog = (await db.execute(select(CatalogModel.id, CatalogModel.provider_id, CatalogModel.remote_model_id))).all()
        key_ids = (await db.scalars(select(APIKey.id))).all()

    counts["providers"] = len(providers)
    counts["legacy_models"] = len(legacy)
    counts["function_configs"] = len(configs)
    counts["catalog_models"] = len(catalog)
    counts["api_keys"] = len(key_ids)
    legacy_by_id = {row.id: row.provider_id for row in legacy}
    catalog_ids = {(row.id, row.provider_id) for row in catalog}
    catalog_identity = {(row.provider_id, row.remote_model_id) for row in catalog}
    for row in legacy:
        if row.provider_id not in providers:
            counts["missing_model_providers"] += 1
        try:
            caps = json.loads(row.capabilities)
            valid = isinstance(caps, list) and all(isinstance(cap, str) and cap in CAPABILITIES for cap in caps)
        except (ValueError, TypeError):
            valid = False
        if not valid:
            counts["invalid_model_capabilities"] += 1
        if (row.provider_id, row.id) in catalog_identity:
            counts["existing_canonical_identities"] += 1
    for provider, model, fallback_enabled, fallback_provider in configs:
        counts["fallback_enabled"] += bool(fallback_enabled)
        counts["fallback_references"] += bool(fallback_provider)
        if fallback_provider and fallback_provider not in providers:
            counts["missing_fallback_providers"] += 1
        if model in legacy_by_id and legacy_by_id[model] != provider:
            counts["model_provider_conflicts"] += 1
        if not ((model in legacy_by_id and legacy_by_id[model] == provider)
                or (model, provider) in catalog_ids
                or (provider, model) in catalog_identity):
            counts["unresolved_defaults"] += 1

    json_data, json_error = _read_file(Path(json_path), "json")
    env_data, env_error = _read_file(Path(env_path) if env_path is not None else None, "env")
    issues.update(error for error in (json_error, env_error) if error)
    json_keys = _json_keys(json_data, counts, issues)
    env_keys = _env_keys(env_data, counts, issues)
    if json_data is not None and "invalid_json" not in issues and json_error is None:
        source = "json"
        counts["effective_keys"] = counts["json_keys"]
        if env_data is not None:
            counts["source_disagreements"] = sum(
                set(json_keys.get(provider, ())) != set(env_keys.get(provider, ()))
                for provider in set(json_keys) | set(env_keys)
            )
    elif json_error or "invalid_json" in issues:
        source = "invalid_json"
    elif env_data is not None and env_error is None and "invalid_env" not in issues:
        source = "env"
        # KeyManager's env bootstrap retains only the first occurrence of each
        # value within a provider; keep env_keys as the raw source count.
        counts["effective_keys"] = sum(len(set(values)) for values in env_keys.values())
    else:
        source = "none"

    issue_for_count = {
        "duplicate_json_keys": "duplicate_json_keys", "duplicate_env_keys": "duplicate_env_keys",
        "key_provider_mismatches": "key_provider_mismatch", "source_disagreements": "source_disagreement",
        "model_provider_conflicts": "model_provider_conflict", "missing_model_providers": "missing_model_provider",
        "invalid_model_capabilities": "invalid_model_capability", "unresolved_defaults": "unresolved_default",
        "missing_fallback_providers": "missing_fallback_provider",
        "existing_canonical_identities": "existing_canonical_identity",
    }
    issues.update(code for name, code in issue_for_count.items() if counts[name])
    return {"counts": counts, "issues": sorted(issues), "key_source": source}
