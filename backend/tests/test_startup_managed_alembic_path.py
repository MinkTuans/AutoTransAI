"""Actual Alembic traversal of an isolated startup-created schema."""
import sqlalchemy as sa
from alembic import command
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.util import load_python_file
from pathlib import Path
import pytest

from app.database import Base
import app.models  # noqa: F401 - register the startup ORM tables in Base metadata
from tests.test_catalog_alembic_link import config_for


def test_startup_profile_rejects_duplicate_job_fk_without_project_fk():
    engine = sa.create_engine('sqlite:///:memory:')
    try:
        with engine.begin() as db:
            Base.metadata.create_all(db)
            inspector = sa.inspect(db)
            actual = inspector.get_foreign_keys('youtube_publications')
            job = next(fk for fk in actual if fk['constrained_columns'] == ['job_id'])
            reflected = [fk for fk in actual if fk['constrained_columns'] != ['project_id']]
            reflected.append({**job, 'name': 'duplicate_job_fk'})
            inspector.get_foreign_keys = lambda name: (
                reflected if name == 'youtube_publications' else sa.inspect(db).get_foreign_keys(name))
            helper = load_python_file(str(Path(__file__).parents[1] / 'alembic'),
                                      'progress_prerequisites.py')
            publication = helper._tables()[1][1]
            with pytest.raises(RuntimeError, match='schema'):
                helper._validate_table(inspector, publication,
                                       helper._additions()['youtube_publications'], db.dialect)
    finally:
        engine.dispose()


@pytest.mark.parametrize('definition', ['project_id) WHERE 0', 'project_id COLLATE NOCASE)'])
def test_startup_profile_rejects_unusable_project_index(definition):
    engine = sa.create_engine('sqlite:///:memory:')
    try:
        with engine.begin() as db:
            Base.metadata.create_all(db)
            db.exec_driver_sql('DROP INDEX ix_youtube_publications_project_id')
            db.exec_driver_sql('CREATE INDEX ix_youtube_publications_project_id '
                               f'ON youtube_publications({definition}')
            module = load_python_file(str(Path(__file__).parents[1] / 'alembic' / 'versions'),
                                      '20260908_add_youtube_progress.py')
            with Operations.context(MigrationContext.configure(db)):
                with pytest.raises(RuntimeError, match='schema'):
                    module.upgrade()
            assert db.exec_driver_sql('SELECT COUNT(*) FROM youtube_publications').scalar_one() == 0
    finally:
        engine.dispose()


def test_current_startup_schema_traverses_youtube_progress_without_rebuild(tmp_path):
    url = f'sqlite:///{tmp_path / "startup.sqlite"}'
    engine = sa.create_engine(url)
    with engine.begin() as db:
        Base.metadata.create_all(db)
        db.exec_driver_sql("INSERT INTO youtube_channels "
                           "(id, channel_name, credentials_json, is_active, created_at) "
                           "VALUES ('channel', 'Private', 'private-credential-fixture', 1, '2001-01-01')")
        db.exec_driver_sql("INSERT INTO youtube_publications "
                           "(id, channel_id, title, description, category_id, privacy_status, "
                           "status, progress, created_at, updated_at) "
                           "VALUES ('publication', 'channel', 'Private title', 'Private description', "
                           "'22', 'private', 'pending', 17, '2001-01-01', '2001-01-01')")
        before_row = db.exec_driver_sql(
            "SELECT * FROM youtube_publications WHERE id='publication'").one()
        before = set(sa.inspect(db).get_table_names())
    engine.dispose()
    command.upgrade(config_for(url, tmp_path), '20260908_youtube_progress')
    engine = sa.create_engine(url)
    try:
        with engine.connect() as db:
            assert before <= set(sa.inspect(db).get_table_names())
            assert db.exec_driver_sql(
                "SELECT * FROM youtube_publications WHERE id='publication'").one() == before_row
            assert db.exec_driver_sql('SELECT version_num FROM alembic_version').scalar_one() == (
                '20260908_youtube_progress')
    finally:
        engine.dispose()
