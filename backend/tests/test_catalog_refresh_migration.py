"""Run the additive refresh migration only against disposable/offline databases."""
import importlib.util
import io
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text


def revision():
    path = Path(__file__).parents[1] / "alembic/versions/20260923_catalog_refresh.py"
    spec = importlib.util.spec_from_file_location("refresh_migration", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_refresh_migration_preserves_existing_rows_and_sets_revision_default():
    engine = create_engine("sqlite://")
    with engine.begin() as db:
        db.execute(text("CREATE TABLE providers (id VARCHAR(50) PRIMARY KEY)"))
        db.execute(text("INSERT INTO providers VALUES ('existing')"))
        db.execute(text("CREATE TABLE ai_function_configs (function_id VARCHAR(50) PRIMARY KEY)"))
        db.execute(text("INSERT INTO ai_function_configs VALUES ('translation')"))
        with Operations.context(MigrationContext.configure(db)):
            revision().upgrade()
            assert db.execute(text("SELECT catalog_revision FROM providers")).scalar_one() == 0
            assert db.execute(text("SELECT configuration_error FROM ai_function_configs")).scalar_one() is None
            assert {c["name"] for c in inspect(db).get_columns("ai_catalog_refresh_runs")} == {
                "id", "mode", "status", "summary", "started_at", "completed_at"}
            revision().downgrade()
        assert db.execute(text("SELECT id FROM providers")).scalar_one() == "existing"
        assert db.execute(text("SELECT function_id FROM ai_function_configs")).scalar_one() == "translation"
    engine.dispose()


def test_refresh_migration_compiles_offline_for_mysql_without_destructive_ddl():
    output = io.StringIO()
    context = MigrationContext.configure(dialect_name="mysql", opts={"as_sql": True, "output_buffer": output})
    with Operations.context(context):
        revision().upgrade()
    sql = output.getvalue()
    assert "CREATE TABLE ai_catalog_refresh_runs" in sql
    assert "ADD COLUMN catalog_revision INTEGER NOT NULL DEFAULT '0'" in sql
    assert "DROP " not in sql and "DELETE " not in sql
