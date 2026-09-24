"""Real Alembic traversal on a disposable database, without app env.py."""
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.util import load_python_file
from alembic.migration import MigrationContext
from alembic.operations import Operations
import sqlalchemy as sa

from tests.test_first_alembic_link import revision
from tests.test_progress_alembic_links import assert_no_writes, record_sql
from tests.test_voice_version_width import mysql_db


def config_for(url, tmp_path):
    script_dir = tmp_path / 'alembic'
    script_dir.mkdir()
    (script_dir / 'versions').symlink_to(Path(__file__).parents[1] / 'alembic/versions',
                                        target_is_directory=True)
    (script_dir / 'env.py').write_text(
        'from alembic import context\n'
        'from sqlalchemy import create_engine\n'
        'with create_engine(context.config.get_main_option("sqlalchemy.url")).connect() as db:\n'
        '    context.configure(connection=db)\n'
        '    with context.begin_transaction():\n'
        '        context.run_migrations()\n')
    config = Config()
    config.set_main_option('script_location', str(script_dir))
    config.set_main_option('sqlalchemy.url', url)
    return config


def test_blank_sqlite_traverses_catalog_refresh_with_legacy_prerequisites(tmp_path):
    url = f'sqlite:///{tmp_path / "catalog.sqlite"}'
    config = config_for(url, tmp_path)
    command.upgrade(config, '20260923_catalog_refresh')
    engine = sa.create_engine(url)
    try:
        with engine.connect() as db:
            names = set(sa.inspect(db).get_table_names())
            assert {'providers', 'ai_function_configs', 'ai_models',
                    'api_keys', 'ai_catalog_models', 'ai_key_model_access',
                    'ai_catalog_refresh_runs'} <= names
            assert db.exec_driver_sql('SELECT version_num FROM alembic_version').scalar_one() == (
                '20260923_catalog_refresh')
    finally:
        engine.dispose()


def test_blank_mysql_traverses_catalog_refresh_with_legacy_prerequisites(mysql_db, tmp_path):
    db = mysql_db
    db.exec_driver_sql('DROP TABLE video_translation_jobs')
    db.exec_driver_sql('DROP TABLE projects')
    config = config_for(db.engine.url.render_as_string(hide_password=False), tmp_path)
    command.upgrade(config, '20260923_catalog_refresh')
    names = set(sa.inspect(db).get_table_names())
    assert {'providers', 'ai_function_configs', 'ai_models',
            'api_keys', 'ai_catalog_models', 'ai_key_model_access',
            'ai_catalog_refresh_runs'} <= names
    assert db.exec_driver_sql('SELECT version_num FROM alembic_version').scalar_one() == (
        '20260923_catalog_refresh')


def test_partial_legacy_catalog_group_refuses_before_canonical_tables(tmp_path):
    engine = sa.create_engine(f'sqlite:///{tmp_path / "partial.sqlite"}')
    try:
        with engine.begin() as db:
            db.exec_driver_sql('CREATE TABLE providers (id VARCHAR(50) PRIMARY KEY)')
            with Operations.context(MigrationContext.configure(db)):
                with pytest.raises(RuntimeError, match='Historical schema mismatch'):
                    revision('20260923_ai_catalog').upgrade()
            assert 'api_keys' not in sa.inspect(db).get_table_names()
    finally:
        engine.dispose()


def test_canonical_name_collision_refuses_before_legacy_table_creation(tmp_path):
    engine = sa.create_engine(f'sqlite:///{tmp_path / "collision.sqlite"}')
    try:
        with engine.begin() as db:
            db.exec_driver_sql('CREATE TABLE api_keys (id VARCHAR(36) PRIMARY KEY)')
            with Operations.context(MigrationContext.configure(db)):
                with pytest.raises(RuntimeError, match='Historical schema mismatch'):
                    revision('20260923_ai_catalog').upgrade()
            assert 'providers' not in sa.inspect(db).get_table_names()
    finally:
        engine.dispose()


def test_populated_frozen_legacy_catalog_group_is_preserved_on_repeat(tmp_path):
    engine = sa.create_engine(f'sqlite:///{tmp_path / "populated.sqlite"}')
    try:
        with engine.begin() as db:
            fixture = (Path(__file__).parent / 'fixtures/catalog_prerequisites_schema.sql').read_text()
            for statement in fixture.split(';'):
                if statement.strip():
                    db.exec_driver_sql(statement)
            db.exec_driver_sql("INSERT INTO providers VALUES "
                               "('p1', 'Private provider', 'llm', 'unknown', NULL, 7, 1, 1, "
                               "'2001-02-03', 'private-capabilities', 1, 0, 1, NULL, NULL, NULL)")
            db.exec_driver_sql("INSERT INTO ai_function_configs VALUES "
                               "('translation', 'Private function', 'LLM', 'p1', 'private-model', "
                               "0, NULL, '2002-03-04')")
            db.exec_driver_sql("INSERT INTO ai_models VALUES "
                               "('m1', 'p1', 'Private model', '[\"LLM\"]', 1, 0, 1, "
                               "'private-description', '2003-04-05')")
            names = ('providers', 'ai_function_configs', 'ai_models')
            before = {name: db.exec_driver_sql(f'SELECT * FROM {name}').all()
                      for name in names}
            helper = load_python_file(str(Path(__file__).parents[1] / 'alembic'),
                                      'catalog_prerequisites.py')
            statements = record_sql(db)
            helper.ensure(db)
            helper.ensure(db)
            assert_no_writes(statements)
            assert {name: db.exec_driver_sql(f'SELECT * FROM {name}').all()
                    for name in names} == before
    finally:
        engine.dispose()
