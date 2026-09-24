"""Disposable migration rehearsal for exact image model identifiers."""

import importlib.util
import io
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text
import pytest

from tests.test_voice_version_width import mysql_db


def revision():
    path = Path(__file__).parents[1] / "alembic/versions/20260923_thumbnail_model_length.py"
    spec = importlib.util.spec_from_file_location("thumbnail_model_length", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def historical_schema(db):
    fixture = Path(__file__).parent / "fixtures/thumbnail_prerequisites_schema.sql"
    for statement in fixture.read_text().split(";"):
        if statement.strip():
            db.exec_driver_sql(statement)


def insert_thumbnail(db, model, identity="old"):
    db.execute(text("""INSERT INTO video_thumbnails
        (id, source_title, selected_style, provider, model, width, height,
         aspect_ratio, status, is_active, created_at, updated_at)
        VALUES (:id, 'Private title', 'auto', 'pollinations', :model, 1280, 720,
                '16:9', 'pending', 1, '2001-01-01', '2001-01-01')"""),
        {"id": identity, "model": model})


def test_upgrade_widens_model_without_changing_existing_thumbnail():
    engine = create_engine("sqlite://")
    with engine.begin() as db:
        db.exec_driver_sql("PRAGMA foreign_keys=ON")
        historical_schema(db)
        insert_thumbnail(db, "pollinations-default")
        with Operations.context(MigrationContext.configure(db)):
            revision().upgrade()
        columns = {item["name"]: item for item in inspect(db).get_columns("video_thumbnails")}
        assert columns["model"]["type"].length == 255
        assert db.execute(text("SELECT model FROM video_thumbnails WHERE id='old'")).scalar_one() == "pollinations-default"
        assert len(inspect(db).get_foreign_keys("video_thumbnails")) == 3
        assert len(inspect(db).get_indexes("video_thumbnails")) == 3
    engine.dispose()


def test_upgrade_emits_only_model_widening_for_mysql():
    output = io.StringIO()
    context = MigrationContext.configure(dialect_name="mysql", opts={"as_sql": True, "output_buffer": output})
    with Operations.context(context):
        revision().upgrade()
    sql = output.getvalue().upper()
    assert "VIDEO_THUMBNAILS" in sql and "VARCHAR(255)" in sql
    assert "DELETE " not in sql and "DROP TABLE" not in sql


def test_downgrade_refuses_to_truncate_new_long_model_identity():
    engine = create_engine("sqlite://")
    long_id = "image-model-" + "x" * 120
    with engine.begin() as db:
        historical_schema(db)
        with Operations.context(MigrationContext.configure(db)):
            revision().upgrade()
            insert_thumbnail(db, long_id, "new")
            with pytest.raises(RuntimeError, match="Cannot narrow thumbnail model IDs"):
                revision().downgrade()
        assert db.execute(text("SELECT model FROM video_thumbnails WHERE id='new'")).scalar_one() == long_id
    engine.dispose()


def test_upgrade_rejects_partial_table_without_writing():
    engine = create_engine("sqlite://")
    with engine.begin() as db:
        db.exec_driver_sql("CREATE TABLE video_thumbnails (id VARCHAR(36) PRIMARY KEY, model VARCHAR(100) NOT NULL)")
        with Operations.context(MigrationContext.configure(db)):
            with pytest.raises(RuntimeError, match="Historical schema mismatch"):
                revision().upgrade()
        assert {item["name"] for item in inspect(db).get_columns("video_thumbnails")} == {"id", "model"}
    engine.dispose()


def test_upgrade_replays_wide_schema_without_writing():
    engine = create_engine("sqlite://")
    with engine.begin() as db:
        historical_schema(db)
        with Operations.context(MigrationContext.configure(db)):
            revision().upgrade()
            from tests.test_progress_alembic_links import assert_no_writes, record_sql
            statements = record_sql(db)
            revision().upgrade()
            assert_no_writes(statements)
    engine.dispose()


@pytest.mark.parametrize("dependent", ["trigger", "incoming_fk", "view"])
def test_upgrade_refuses_dependent_objects_before_rebuild(dependent):
    engine = create_engine("sqlite://")
    with engine.begin() as db:
        historical_schema(db)
        insert_thumbnail(db, "private-model-id")
        if dependent == "trigger":
            db.exec_driver_sql("CREATE TRIGGER thumbnail_audit AFTER UPDATE ON video_thumbnails "
                               "BEGIN SELECT 1; END")
        elif dependent == "incoming_fk":
            db.exec_driver_sql("CREATE TABLE dependent_thumbnail (id VARCHAR(36) PRIMARY KEY, "
                               "thumbnail_id VARCHAR(36) REFERENCES video_thumbnails(id))")
        else:
            db.exec_driver_sql("CREATE VIEW thumbnail_model_view AS "
                               "SELECT model FROM video_thumbnails")
        with Operations.context(MigrationContext.configure(db)):
            with pytest.raises(RuntimeError, match="Historical schema mismatch"):
                revision().upgrade()
        assert inspect(db).get_columns("video_thumbnails")[11]["type"].length == 100
        assert db.exec_driver_sql("SELECT model FROM video_thumbnails").scalar_one() == "private-model-id"
    engine.dispose()


def test_mysql_populated_historical_thumbnail_widens_without_losing_data(mysql_db):
    db = mysql_db
    fixture = Path(__file__).parent / "fixtures/thumbnail_prerequisites_schema.sql"
    for statement in fixture.read_text().split(";")[2:]:
        if statement.strip():
            db.exec_driver_sql(statement)
    insert_thumbnail(db, "private-model-id")
    with Operations.context(MigrationContext.configure(db)):
        revision().upgrade()
        revision().upgrade()
    assert inspect(db).get_columns("video_thumbnails")[11]["type"].length == 255
    assert len(inspect(db).get_foreign_keys("video_thumbnails")) == 3
    assert len(inspect(db).get_indexes("video_thumbnails")) == 3
    assert db.exec_driver_sql("SELECT source_title, model FROM video_thumbnails").one() == (
        "Private title", "private-model-id")
