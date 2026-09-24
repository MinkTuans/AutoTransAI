"""Opt-in MySQL rehearsal of the first 33-character Alembic revision."""
import os
import uuid
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.engine import make_url

from tests.test_first_alembic_link import revision


@pytest.fixture
def mysql_db():
    raw = os.environ.get('AUTOTRANSAI_DISPOSABLE_MYSQL_VERSION_URL')
    if not raw:
        pytest.skip('disposable MySQL version URL not supplied')
    url = make_url(raw)
    if (url.get_backend_name() != 'mysql' or url.database != 'version_lab'
            or not (url.host or '').startswith('172.17.')):
        pytest.fail('integration test requires the isolated version_lab Docker MySQL')
    admin = sa.create_engine(url)
    name = 'version_test_' + uuid.uuid4().hex[:12]
    with admin.connect() as db:
        db.exec_driver_sql(f'CREATE DATABASE `{name}`')
    engine = sa.create_engine(url.set(database=name))
    try:
        with engine.connect() as db:
            db.exec_driver_sql('CREATE TABLE projects (id VARCHAR(36) NOT NULL PRIMARY KEY)')
            db.exec_driver_sql('CREATE TABLE video_translation_jobs '
                               '(id VARCHAR(36) NOT NULL PRIMARY KEY)')
            yield db
    finally:
        engine.dispose()
        with admin.connect() as db:
            db.exec_driver_sql(f'DROP DATABASE `{name}`')
        admin.dispose()


def upgrade_voice(db):
    with Operations.context(MigrationContext.configure(db)):
        revision('20260916_character_voice_timeline').upgrade()


def test_mysql_voice_revision_widens_default_version_table_before_its_33_char_id(mysql_db):
    db = mysql_db
    db.exec_driver_sql('CREATE TABLE alembic_version '
                       '(version_num VARCHAR(32) NOT NULL PRIMARY KEY)')
    db.exec_driver_sql("INSERT INTO alembic_version VALUES ('20260915_tiktok_accounts')")
    upgrade_voice(db)
    assert sa.inspect(db).get_columns('alembic_version')[0]['type'].length >= 33
    assert db.exec_driver_sql('SELECT version_num FROM alembic_version').scalar_one() == (
        '20260915_tiktok_accounts')
    db.exec_driver_sql("UPDATE alembic_version SET version_num='20260916_character_voice_timeline'")
    assert db.exec_driver_sql('SELECT version_num FROM alembic_version').scalar_one() == (
        '20260916_character_voice_timeline')


def test_mysql_unknown_version_width_refuses_before_voice_schema_writes(mysql_db):
    db = mysql_db
    db.exec_driver_sql('CREATE TABLE alembic_version '
                       '(version_num VARCHAR(30) NOT NULL PRIMARY KEY)')
    db.exec_driver_sql("INSERT INTO alembic_version VALUES ('20260915_tiktok_accounts')")
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        upgrade_voice(db)
    assert 'speaker_voice_mappings' not in sa.inspect(db).get_table_names()
    assert sa.inspect(db).get_columns('alembic_version')[0]['type'].length == 30


def test_mysql_enum_version_column_refuses_before_voice_schema_writes(mysql_db):
    db = mysql_db
    db.exec_driver_sql('CREATE TABLE alembic_version (version_num '
                       "ENUM('20260915_tiktok_accounts', 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx') "
                       'NOT NULL PRIMARY KEY)')
    db.exec_driver_sql("INSERT INTO alembic_version VALUES ('20260915_tiktok_accounts')")
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        upgrade_voice(db)
    assert 'speaker_voice_mappings' not in sa.inspect(db).get_table_names()


@pytest.mark.parametrize('stored', [None, 'unexpected-revision'])
def test_mysql_wide_version_table_refuses_unknown_state(mysql_db, stored):
    db = mysql_db
    db.exec_driver_sql('CREATE TABLE alembic_version '
                       '(version_num VARCHAR(64) NOT NULL PRIMARY KEY)')
    if stored:
        db.execute(sa.text('INSERT INTO alembic_version VALUES (:version)'),
                   {'version': stored})
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        upgrade_voice(db)
    assert 'speaker_voice_mappings' not in sa.inspect(db).get_table_names()


def test_actual_alembic_mysql_upgrade_records_full_long_revision(mysql_db, tmp_path):
    db = mysql_db
    db.exec_driver_sql('DROP TABLE video_translation_jobs')
    db.exec_driver_sql('DROP TABLE projects')
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
    config.set_main_option('sqlalchemy.url', db.engine.url.render_as_string(hide_password=False))
    command.upgrade(config, '20260915_tiktok_accounts')
    assert sa.inspect(db).get_columns('alembic_version')[0]['type'].length == 32
    command.upgrade(config, '20260916_character_voice_timeline')
    assert sa.inspect(db).get_columns('alembic_version')[0]['type'].length == 64
    assert db.exec_driver_sql('SELECT version_num FROM alembic_version').scalar_one() == (
        '20260916_character_voice_timeline')
