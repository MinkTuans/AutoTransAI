"""Additive key metadata rehearsal against disposable SQLite and offline MySQL."""
import importlib.util
import io
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError
import pytest


def revision():
    path = Path(__file__).parents[1] / "alembic/versions/20260923_key_rotation_domain.py"
    spec = importlib.util.spec_from_file_location("key_rotation_domain", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_upgrade_preserves_existing_key_and_safe_defaults():
    engine = create_engine("sqlite://")
    with engine.begin() as db:
        db.execute(text("PRAGMA foreign_keys=ON"))
        db.execute(text("CREATE TABLE api_keys (id VARCHAR(36) PRIMARY KEY, provider_id VARCHAR(50) NOT NULL, ciphertext TEXT NOT NULL, enabled BOOLEAN NOT NULL)"))
        db.execute(text("CREATE TABLE ai_key_model_access (key_id VARCHAR(36) NOT NULL REFERENCES api_keys(id), model_id VARCHAR(36) NOT NULL)"))
        db.execute(text("INSERT INTO api_keys VALUES ('old', 'openai', 'synthetic-cipher', 0)"))
        db.execute(text("INSERT INTO ai_key_model_access VALUES ('old', 'model')"))
        with Operations.context(MigrationContext.configure(db)):
            revision().upgrade()
        row = db.execute(text("SELECT id, provider_id, ciphertext, enabled, priority, runtime_status, cooldown_until, last_error_code, request_count, success_count, failure_count FROM api_keys")).one()
        assert tuple(row) == ("old", "openai", "synthetic-cipher", 0, 100, "ready", None, None, 0, 0, 0)
        assert "priority" in {c["name"] for c in inspect(db).get_columns("api_keys")}
        assert db.execute(text("SELECT key_id FROM ai_key_model_access")).scalar_one() == "old"
        with pytest.raises(IntegrityError):
            with db.begin_nested():
                db.execute(text("UPDATE api_keys SET priority=0 WHERE id='old'"))
        with Operations.context(MigrationContext.configure(db)):
            revision().downgrade()
        assert "priority" not in {c["name"] for c in inspect(db).get_columns("api_keys")}
        assert db.execute(text("SELECT ciphertext FROM api_keys WHERE id='old'")).scalar_one() == "synthetic-cipher"
        assert db.execute(text("SELECT key_id FROM ai_key_model_access")).scalar_one() == "old"
    engine.dispose()


def test_mysql_offline_ddl_is_additive():
    output = io.StringIO()
    context = MigrationContext.configure(dialect_name="mysql", opts={"as_sql": True, "output_buffer": output})
    with Operations.context(context):
        revision().upgrade()
    sql = output.getvalue().upper()
    assert "ALTER TABLE API_KEYS" in sql and "PRIORITY" in sql and "RUNTIME_STATUS" in sql
    assert "CHECK" in sql
    assert "DROP TABLE" not in sql and "DELETE " not in sql
