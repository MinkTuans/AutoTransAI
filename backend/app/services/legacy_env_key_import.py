"""Explicit legacy dotenv fallback; never consults process settings or environment."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

from dotenv.parser import parse_stream
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.legacy_json_key_import import _import_parsed_keys, _parse as _parse_json, _result
from app.services.legacy_migration_inventory import ENV_PROVIDERS, MAX_ENTRIES, _read_file


def _parse_env(data: bytes) -> list[tuple[str, str, dict[str, object]]]:
    """Parse bounded dotenv bytes without interpolation or process-env lookup."""
    try:
        text = data.decode("utf-8")
        variables: dict[str, str] = {}
        managed = {f"{provider.upper()}_API_KEY" for provider in ENV_PROVIDERS}
        managed.update(f"{provider.upper()}_API_KEY_{index}"
                       for provider in ENV_PROVIDERS for index in range(1, 10))
        count = 0
        for binding in parse_stream(StringIO(text)):
            if binding.error or (binding.key is None and binding.original.string.strip()
                                 and not binding.original.string.lstrip().startswith("#")):
                raise ValueError
            if binding.key is None:
                continue
            count += 1
            if count > MAX_ENTRIES or binding.value is None:
                raise ValueError
            if binding.key in managed:
                if binding.key in variables or "\x00" in binding.value:
                    raise ValueError
                variables[binding.key] = binding.value

        entries: list[tuple[str, str, dict[str, object]]] = []
        for provider in ENV_PROVIDERS:
            base = f"{provider.upper()}_API_KEY"
            primary = variables.get(base, "")
            candidates = primary.splitlines()
            candidates.extend(variables.get(f"{base}_{index}", "") for index in range(1, 10))
            seen: set[str] = set()
            for candidate in candidates:
                secret = candidate.strip()
                if not secret:
                    continue
                priority = len(seen) + 1 if secret not in seen else len(seen)
                seen.add(secret)
                entries.append((provider, secret, {"priority": priority}))
                if len(entries) > MAX_ENTRIES:
                    raise ValueError
        return entries
    except (UnicodeError, ValueError, TypeError):
        raise ValueError("invalid_source") from None

async def import_legacy_env_fallback_keys(
    db: AsyncSession, *, json_path: Path, env_path: Path, master_key: bytes | str,
) -> dict[str, object]:
    """Use JSON whenever present; only a missing JSON file permits dotenv fallback."""
    json_path = Path(json_path)
    env_path = Path(env_path)
    json_data, json_error = _read_file(json_path, "json")
    if json_error:
        return _result("invalid_source")
    if json_data is not None:
        try:
            entries = _parse_json(json_data)
        except ValueError:
            return _result("invalid_source")
        return await _import_parsed_keys(db, entries, source_path=json_path, master_key=master_key)

    env_data, env_error = _read_file(env_path, "env")
    if env_error:
        return _result("invalid_source")
    if env_data is None:
        return _result("missing_source")
    try:
        entries = _parse_env(env_data)
    except ValueError:
        return _result("invalid_source")
    return await _import_parsed_keys(db, entries, source_path=env_path, master_key=master_key)
