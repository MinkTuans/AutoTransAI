"""Direct foreign-key revision checks on isolated historical SQLite fixtures."""
import os
import uuid

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.engine import make_url

from tests.test_first_alembic_link import fixture_schema, revision
from tests.test_progress_alembic_links import assert_no_writes, record_sql


@pytest.fixture
def db():
    engine = sa.create_engine('sqlite:///:memory:')
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql('PRAGMA foreign_keys=ON')
            fixture_schema(connection)
            connection.commit()
            yield connection
    finally:
        engine.dispose()


@pytest.fixture
def mysql_db():
    raw = os.environ.get('AUTOTRANSAI_DISPOSABLE_MYSQL_FK_URL')
    if not raw:
        pytest.skip('disposable MySQL FK URL not supplied')
    url = make_url(raw)
    if (url.get_backend_name() != 'mysql' or url.database != 'fk_lab'
            or not (url.host or '').startswith('172.17.')):
        pytest.fail('integration test requires the isolated fk_lab Docker MySQL')
    admin = sa.create_engine(url)
    name = 'fk_test_' + uuid.uuid4().hex[:12]
    with admin.connect() as connection:
        connection.exec_driver_sql(f'CREATE DATABASE `{name}`')
    engine = sa.create_engine(url.set(database=name))
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql('CREATE TABLE projects (id VARCHAR(36) PRIMARY KEY)')
            connection.exec_driver_sql("INSERT INTO projects VALUES ('p1')")
            connection.exec_driver_sql('CREATE TABLE segments ('
                                       'id INTEGER PRIMARY KEY, project_id VARCHAR(36) NOT NULL, '
                                       'CONSTRAINT existing_segment_fk FOREIGN KEY (project_id) '
                                       'REFERENCES projects(id) ON DELETE CASCADE)')
            yield connection
    finally:
        engine.dispose()
        with admin.connect() as connection:
            connection.exec_driver_sql(f'DROP DATABASE `{name}`')
        admin.dispose()


def upgrade(db):
    with Operations.context(MigrationContext.configure(db)):
        revision('20260918_add_foreign_keys').upgrade()


def test_historical_chain_tables_need_no_rebuild_and_replay_is_read_only(db):
    before = db.exec_driver_sql('SELECT * FROM segments').all()
    statements = record_sql(db)
    upgrade(db)
    upgrade(db)
    assert_no_writes(statements)
    assert db.exec_driver_sql('SELECT * FROM segments').all() == before
    assert db.exec_driver_sql('PRAGMA foreign_key_check').all() == []


def test_startup_created_optional_tables_with_equivalent_fks_are_preserved(db):
    db.exec_driver_sql('CREATE TABLE jobs (id VARCHAR(36) PRIMARY KEY, '
                       'project_id VARCHAR(36) NOT NULL, private_text TEXT, '
                       'FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE)')
    db.exec_driver_sql('CREATE TABLE assets (id VARCHAR(36) PRIMARY KEY, '
                       'project_id VARCHAR(36) NOT NULL, private_text TEXT, '
                       'FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE)')
    db.exec_driver_sql('CREATE TABLE video_edit_configs (id VARCHAR(36) PRIMARY KEY, '
                       'project_id VARCHAR(36), job_id VARCHAR(36), private_text TEXT, '
                       'FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE, '
                       'FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE)')
    db.exec_driver_sql("INSERT INTO jobs VALUES ('j1', 'projects', 'private-job')")
    db.exec_driver_sql("INSERT INTO assets VALUES ('a1', 'projects', 'private-asset')")
    db.exec_driver_sql("INSERT INTO video_edit_configs VALUES "
                       "('c1', 'projects', 'j1', 'private-config')")
    before = {name: db.exec_driver_sql(f'SELECT * FROM {name}').all()
              for name in ('jobs', 'assets', 'video_edit_configs')}
    statements = record_sql(db)
    upgrade(db)
    assert_no_writes(statements)
    assert {name: db.exec_driver_sql(f'SELECT * FROM {name}').all()
            for name in before} == before


def test_missing_fk_on_populated_optional_table_refuses_before_writes(db):
    db.exec_driver_sql('CREATE TABLE jobs (id VARCHAR(36) PRIMARY KEY, '
                       'project_id VARCHAR(36) NOT NULL, private_text TEXT)')
    db.exec_driver_sql("INSERT INTO jobs VALUES ('j1', 'projects', 'private-job')")
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch') as exc:
        upgrade(db)
    assert 'private' not in str(exc.value).lower()
    assert_no_writes(statements)
    assert db.exec_driver_sql('SELECT private_text FROM jobs').scalar_one() == 'private-job'


def test_orphan_hidden_by_disabled_sqlite_fk_enforcement_refuses(db):
    db.exec_driver_sql('PRAGMA foreign_keys=OFF')
    db.exec_driver_sql("INSERT INTO segments "
                       "(project_id, segment_number, text_content, char_count, audio_status, video_status) "
                       "VALUES ('private-orphan', 2, 'private-text', 12, 'pending', 'pending')")
    db.commit()
    db.exec_driver_sql('PRAGMA foreign_keys=ON')
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch') as exc:
        upgrade(db)
    assert 'private' not in str(exc.value).lower()
    assert_no_writes(statements)


def test_mysql_equivalent_fk_is_read_only_and_orphan_refuses(mysql_db):
    connection = mysql_db
    connection.exec_driver_sql("INSERT INTO segments VALUES (1, 'p1')")
    statements = record_sql(connection)
    upgrade(connection)
    assert_no_writes(statements)
    connection.exec_driver_sql('SET FOREIGN_KEY_CHECKS=0')
    connection.exec_driver_sql("INSERT INTO segments VALUES (2, 'private-orphan')")
    connection.exec_driver_sql('SET FOREIGN_KEY_CHECKS=1')
    statements = record_sql(connection)
    with pytest.raises(RuntimeError, match='Historical schema mismatch') as exc:
        upgrade(connection)
    assert 'private' not in str(exc.value).lower()
    assert_no_writes(statements)


def test_sqlite_post_comment_cascade_fk_is_accepted(db):
    db.exec_driver_sql('CREATE TABLE jobs (id VARCHAR(36) PRIMARY KEY, '
                       'project_id VARCHAR(36) NOT NULL, '
                       'FOREIGN KEY(project_id) REFERENCES projects(id) '
                       '/* historic comment */ ON DELETE CASCADE)')
    db.exec_driver_sql("INSERT INTO jobs VALUES ('j1', 'projects')")
    statements = record_sql(db)
    upgrade(db)
    assert_no_writes(statements)


def test_case_varied_optional_table_cannot_be_skipped(db):
    db.exec_driver_sql('CREATE TABLE Jobs (id VARCHAR(36) PRIMARY KEY, '
                       'project_id VARCHAR(36) NOT NULL)')
    db.exec_driver_sql("INSERT INTO Jobs VALUES ('j1', 'projects')")
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        upgrade(db)
    assert_no_writes(statements)
