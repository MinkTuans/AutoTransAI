"""Disposable migration rehearsal for exact image model identifiers."""

import importlib.util
import io
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text
import pytest


def revision():
    path = Path(__file__).parents[1] / "alembic/versions/20260923_thumbnail_model_length.py"
    spec = importlib.util.spec_from_file_location("thumbnail_model_length", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_upgrade_widens_model_without_changing_existing_thumbnail():
    engine = create_engine("sqlite://")
    with engine.begin() as db:
        db.execute(text("CREATE TABLE video_thumbnails (id VARCHAR(36) PRIMARY KEY, model VARCHAR(100) NOT NULL)"))
        db.execute(text("INSERT INTO video_thumbnails VALUES ('old', 'pollinations-default')"))
        with Operations.context(MigrationContext.configure(db)):
            revision().upgrade()
        columns = {item["name"]: item for item in inspect(db).get_columns("video_thumbnails")}
        assert columns["model"]["type"].length == 255
        assert db.execute(text("SELECT model FROM video_thumbnails WHERE id='old'")).scalar_one() == "pollinations-default"
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
        db.execute(text("CREATE TABLE video_thumbnails (id VARCHAR(36) PRIMARY KEY, model VARCHAR(100) NOT NULL)"))
        with Operations.context(MigrationContext.configure(db)):
            revision().upgrade()
            db.execute(text("INSERT INTO video_thumbnails VALUES ('new', :model)"), {"model": long_id})
            with pytest.raises(RuntimeError, match="Cannot narrow thumbnail model IDs"):
                revision().downgrade()
        assert db.execute(text("SELECT model FROM video_thumbnails WHERE id='new'")).scalar_one() == long_id
    engine.dispose()
