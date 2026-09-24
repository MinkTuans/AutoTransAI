"""Explicit, caller-transactional orchestration of legacy catalog data import.

This module never opens an application database or reads process credentials.
Imported source files and archival rows remain untouched.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.credential_service import CredentialError
from app.services.legacy_catalog_import import import_legacy_catalog
from app.services.legacy_default_remap import remap_legacy_function_defaults
from app.services.legacy_env_key_import import _parse_env
from app.services.legacy_json_key_import import (
    _import_parsed_keys, _parse as _parse_json, _valid_explicit_master_key,
)
from app.services.legacy_migration_inventory import _read_file, inventory_legacy_migration


_SOURCE_ERRORS = frozenset({
    "invalid_json", "invalid_env", "key_provider_mismatch",
    "json_symlink_refused", "json_not_regular", "json_file_too_large", "json_read_error",
    "env_symlink_refused", "env_not_regular", "env_file_too_large", "env_read_error",
})


class _Blocked(Exception):
    def __init__(self, reason: str):
        self.reason = reason


async def _ensure_sqlite_outer_transaction(db: AsyncSession) -> None:
    """SQLite's legacy driver may not BEGIN for SELECT before our savepoint."""
    connection = await db.connection()
    if connection.dialect.name == "sqlite":
        active = await connection.run_sync(
            lambda sync: sync.connection.driver_connection.in_transaction
        )
        if not active:
            await connection.exec_driver_sql("BEGIN")


async def run_legacy_data_cutover(
    db: AsyncSession, *, json_path: Path, env_path: Path | None = None,
    master_key: bytes | str | None = None, dry_run: bool = True,
) -> dict[str, object]:
    """Preview or stage a lossless import; the caller alone commits or rolls back.

    Apply runs under a savepoint so rejected source/catalog/key states do not
    leave a partly imported batch in the caller's transaction. An unresolved
    default keeps its archival model ID and receives a visible config error.
    """
    if db.new or db.dirty or db.deleted:
        raise RuntimeError("Legacy data cutover requires a clean session.")
    json_path = Path(json_path)
    env_path = Path(env_path) if env_path is not None else None
    if not dry_run and master_key is not None and not _valid_explicit_master_key(master_key):
        return {"status": "blocked", "reason": "invalid_master_key"}
    snapshot = (_read_file(json_path, "json"), _read_file(env_path, "env"))
    inventory = await inventory_legacy_migration(
        db, json_path=json_path, env_path=env_path, _source_snapshot=snapshot,
    )
    preview = await remap_legacy_function_defaults(db, dry_run=True)
    if dry_run:
        return {"status": "preview", "inventory": inventory, "defaults": preview}

    if _SOURCE_ERRORS.intersection(inventory["issues"]):
        return {"status": "blocked", "reason": "invalid_source"}
    if inventory["key_source"] != "none" and master_key is None:
        return {"status": "blocked", "reason": "invalid_master_key"}
    try:
        if inventory["key_source"] == "json":
            entries = _parse_json(snapshot[0][0])
            source_path = json_path
        elif inventory["key_source"] == "env":
            entries = _parse_env(snapshot[1][0])
            source_path = env_path
        else:
            entries, source_path = [], json_path
    except ValueError:
        return {"status": "blocked", "reason": "invalid_source"}

    try:
        await _ensure_sqlite_outer_transaction(db)
        async with db.begin_nested():
            if (_read_file(json_path, "json"), _read_file(env_path, "env")) != snapshot:
                raise _Blocked("source_changed")
            if inventory["key_source"] == "none":
                keys = {"status": "missing_source", "counts": {"imported": 0}}
            else:
                keys = await _import_parsed_keys(
                    db, entries, source_path=source_path, master_key=master_key,
                )
            if keys["status"] not in ("imported", "missing_source"):
                raise _Blocked("invalid_master_key" if keys["status"] == "invalid_master_key"
                               else "invalid_source")
            if (keys["counts"].get("skipped_missing_provider", 0)
                    or keys["counts"].get("skipped_keyless_provider", 0)):
                raise _Blocked("key_provider_conflict")

            catalog = await import_legacy_catalog(db)
            if catalog["status"] != "imported":
                raise _Blocked("catalog_conflict")
            defaults = await remap_legacy_function_defaults(db)
            if (_read_file(json_path, "json"), _read_file(env_path, "env")) != snapshot:
                raise _Blocked("source_changed")
    except _Blocked as error:
        return {"status": "blocked", "reason": error.reason}
    except CredentialError:
        return {"status": "blocked", "reason": "credential_error"}
    except Exception:
        raise RuntimeError("Legacy data cutover failed; transaction rolled back.") from None
    return {"status": "applied", "inventory": inventory, "catalog": catalog,
            "keys": keys, "defaults": defaults}
