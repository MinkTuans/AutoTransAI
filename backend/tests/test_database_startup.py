"""Startup schema safety checks using only disposable databases."""

import logging

import pytest
from sqlalchemy import event, inspect, text
from sqlalchemy.ext.asyncio import create_async_engine

import app.models  # noqa: F401 - register canonical metadata
from app import database


class FailingEngine:
    def __init__(self, phase):
        self.phase = phase
        self.schema_steps = 0

    async def dispose(self):
        return None

    def begin(self):
        if self.phase == "connect":
            raise RuntimeError("mysql://user:secret@example.invalid/private connection failed")
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def run_sync(self, *args):
        self.schema_steps += 1
        if self.schema_steps == 3:
            raise RuntimeError("mysql://user:secret@example.invalid/private schema failed")


@pytest.mark.asyncio
@pytest.mark.parametrize("phase", ["connect", "schema"])
async def test_mysql_failure_stops_startup_without_sqlite_fallback(monkeypatch, caplog, phase):
    monkeypatch.setattr(database, "engine", FailingEngine(phase))
    monkeypatch.setattr(database, "is_mysql", True)
    monkeypatch.setattr(database, "is_sqlite", False)

    def forbid_fallback(*args, **kwargs):
        pytest.fail("startup attempted to create a fallback database")

    monkeypatch.setattr(database, "create_async_engine", forbid_fallback)
    with caplog.at_level(logging.WARNING), pytest.raises(RuntimeError) as error:
        await database.init_db()

    assert "secret" not in str(error.value) + caplog.text
    assert "private" not in str(error.value) + caplog.text
    assert "database startup failed" in str(error.value).lower()
    assert database.is_mysql and not database.is_sqlite


@pytest.mark.asyncio
async def test_failed_required_column_add_stops_startup(monkeypatch, tmp_path, caplog):
    path = tmp_path / "legacy.db"
    disposable = create_async_engine(f"sqlite+aiosqlite:///{path}")
    async with disposable.begin() as conn:
        await conn.exec_driver_sql("CREATE TABLE providers (id VARCHAR(50) PRIMARY KEY)")
        await conn.exec_driver_sql("INSERT INTO providers VALUES ('old-provider')")

    @event.listens_for(disposable.sync_engine, "before_cursor_execute")
    def fail_alter(conn, cursor, statement, parameters, context, executemany):
        if statement.startswith('ALTER TABLE "providers" ADD COLUMN'):
            raise RuntimeError("sqlite:///secret-path alter failed")

    monkeypatch.setattr(database, "engine", disposable)
    monkeypatch.setattr(database, "is_sqlite", True)
    monkeypatch.setattr(database, "is_mysql", False)
    try:
        with caplog.at_level(logging.ERROR), pytest.raises(RuntimeError) as error:
            await database.init_db()
        assert "database startup failed" in str(error.value).lower()
        assert "secret-path" not in str(error.value) + caplog.text
        async with disposable.connect() as conn:
            assert await conn.scalar(text("SELECT id FROM providers")) == "old-provider"
            assert "name" not in {c["name"] for c in await conn.run_sync(lambda db: inspect(db).get_columns("providers"))}
    finally:
        await disposable.dispose()


@pytest.mark.asyncio
async def test_existing_sqlite_schema_is_extended_idempotently_without_row_loss(monkeypatch, tmp_path):
    disposable = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'legacy.db'}")
    async with disposable.begin() as conn:
        await conn.exec_driver_sql("CREATE TABLE providers (id VARCHAR(50) PRIMARY KEY)")
        await conn.exec_driver_sql("INSERT INTO providers VALUES ('old-provider')")
    monkeypatch.setattr(database, "engine", disposable)
    monkeypatch.setattr(database, "is_sqlite", True)
    monkeypatch.setattr(database, "is_mysql", False)
    try:
        await database.init_db()
        await database.init_db()
        async with disposable.connect() as conn:
            assert await conn.scalar(text("SELECT id FROM providers")) == "old-provider"
            columns = {c["name"] for c in await conn.run_sync(lambda db: inspect(db).get_columns("providers"))}
            assert {"name", "catalog_revision", "enabled"} <= columns
    finally:
        await disposable.dispose()


@pytest.mark.asyncio
async def test_failed_column_inspection_stops_startup(monkeypatch, tmp_path):
    disposable = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'inspection.db'}")
    async with disposable.begin() as conn:
        await conn.exec_driver_sql("CREATE TABLE providers (id VARCHAR(50) PRIMARY KEY)")

    @event.listens_for(disposable.sync_engine, "before_cursor_execute")
    def fail_inspection(conn, cursor, statement, parameters, context, executemany):
        if "table_xinfo" in statement and "providers" in statement:
            raise RuntimeError("sqlite:///secret-path inspection failed")

    monkeypatch.setattr(database, "engine", disposable)
    monkeypatch.setattr(database, "is_sqlite", True)
    monkeypatch.setattr(database, "is_mysql", False)
    try:
        with pytest.raises(RuntimeError, match="Database startup failed") as error:
            await database.init_db()
        assert "secret-path" not in str(error.value)
    finally:
        await disposable.dispose()
