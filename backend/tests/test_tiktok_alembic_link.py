"""Actual historical operations, disposable SQLite, no env.py or application imports."""
from io import StringIO
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.dialects import mysql
from sqlalchemy.exc import IntegrityError

from tests.test_first_alembic_link import db, isolated, revision, traverse as first_link
from tests.test_progress_alembic_links import (
    assert_no_writes, progress_links, record_sql, snapshot,
)


NAME = '20260915_add_tiktok_accounts'


def tiktok_link(db):
    with Operations.context(MigrationContext.configure(db)):
        revision(NAME).upgrade()


def prerequisites(db):
    first_link(db)
    progress_links(db)


def fixture_schema(db, startup=False, replace=None):
    sql = (Path(__file__).parent / 'fixtures/tiktok_link_schema.sql').read_text()
    if startup:
        # 1ebccbb TikTokAccount uses Python defaults and non-optional timestamps.
        sql = sql.replace(" DEFAULT 'TikTok'", '').replace(' DEFAULT 1', '')
        sql = sql.replace('DATETIME', 'DATETIME NOT NULL')
    if replace:
        sql = sql.replace(*replace)
    for statement in sql.split(';'):
        if statement.strip():
            db.exec_driver_sql(statement)


def populate(db):
    db.exec_driver_sql("INSERT INTO tiktok_accounts VALUES "
                       "('account-1', 'open-1', 'Tên riêng', NULL, 'synthetic-ciphertext-1', "
                       "0, '2001-02-03 04:05:06', '2002-03-04 05:06:07'), "
                       "('account-2', 'open-2', 'Another', 'https://invalid.test/avatar', "
                       "'synthetic-ciphertext-2', 1, '2003-04-05 06:07:08', '2004-05-06 07:08:09')")


def assert_rejected_without_writes(db):
    before = snapshot(db)
    schema = db.exec_driver_sql('SELECT name, sql FROM sqlite_master ORDER BY name').all()
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch.*inspect.*before retrying') as exc:
        tiktok_link(db)
    assert 'synthetic-ciphertext' not in str(exc.value)
    assert snapshot(db) == before
    assert db.exec_driver_sql('SELECT name, sql FROM sqlite_master ORDER BY name').all() == schema
    assert_no_writes(statements)


def test_blank_database_traverses_actual_revisions_through_tiktok(db):
    prerequisites(db)
    tiktok_link(db)
    assert revision(NAME).down_revision == '20260908_workflow_progress'
    assert revision(NAME).revision == '20260915_tiktok_accounts'
    reference_engine = sa.create_engine('sqlite:///:memory:')
    try:
        with reference_engine.begin() as reference:
            fixture_schema(reference)
            actual, frozen = sa.inspect(db), sa.inspect(reference)
            def columns(inspector):
                return [{**column, 'type': str(column['type'])}
                        for column in inspector.get_columns('tiktok_accounts')]
            assert columns(actual) == columns(frozen)
            assert actual.get_indexes('tiktok_accounts') == frozen.get_indexes('tiktok_accounts')
    finally:
        reference_engine.dispose()
    db.exec_driver_sql("INSERT INTO tiktok_accounts (id, open_id, credentials_json) "
                       "VALUES ('defaults', 'default-open', 'synthetic-ciphertext')")
    assert db.exec_driver_sql('SELECT display_name, is_active, created_at, updated_at '
                              'FROM tiktok_accounts').one() == ('TikTok', 1, None, None)
    with pytest.raises(IntegrityError):
        db.exec_driver_sql("INSERT INTO tiktok_accounts (id, open_id, credentials_json) "
                           "VALUES ('duplicate', 'default-open', 'synthetic-ciphertext')")


@pytest.mark.parametrize('startup', [False, True], ids=['historical', 'startup-created'])
def test_populated_compatible_schema_preserves_every_value_without_writes(db, startup):
    prerequisites(db)
    fixture_schema(db, startup)
    populate(db)
    before = snapshot(db)
    statements = record_sql(db)
    tiktok_link(db)
    tiktok_link(db)  # Direct operation replay, not version-table stamping.
    assert snapshot(db) == before
    assert_no_writes(statements)


@pytest.mark.parametrize('replace', [
    ('open_id VARCHAR(128)', 'open_id VARCHAR(64)'),
    ('credentials_json TEXT NOT NULL', 'credentials_json TEXT'),
    ('id VARCHAR(36) NOT NULL PRIMARY KEY', 'id VARCHAR(36) NOT NULL'),
    ('avatar_url VARCHAR(500)', 'unknown VARCHAR(500)'),
    ('updated_at DATETIME', 'updated_at DATETIME, extra TEXT'),
    ("DEFAULT 'TikTok'", "DEFAULT '(TikTok)'"),
    ("DEFAULT 'TikTok'", "DEFAULT 'private-fixture'"),
    ('DEFAULT 1', 'DEFAULT 0'),
    ('DEFAULT 1', "DEFAULT '(1)'"),
    ('created_at DATETIME', 'created_at DATETIME NOT NULL'),
    ('UNIQUE INDEX', 'INDEX'),
    ('(open_id);', '(display_name);'),
    ('(open_id);', '(open_id, display_name);'),
    ('(open_id);', '(open_id) WHERE is_active = 1;'),
    ('(open_id);', '(open_id COLLATE NOCASE);'),
    ('(open_id);', '(open_id DESC);'),
    ('ix_tiktok_accounts_open_id', 'unknown_index'),
    ('updated_at DATETIME', 'updated_at DATETIME, CHECK (is_active = 1)'),
])
def test_incompatible_contract_fails_closed_without_writes(db, replace):
    prerequisites(db)
    fixture_schema(db, replace=replace)
    assert_rejected_without_writes(db)


@pytest.mark.parametrize('sql', [
    'DROP INDEX ix_tiktok_accounts_open_id',
    'CREATE INDEX extra_index ON tiktok_accounts(display_name)',
    'CREATE INDEX extra_expression ON tiktok_accounts(lower(display_name))',
])
def test_missing_or_extra_index_preserves_populated_table_on_rejection(db, sql):
    prerequisites(db)
    fixture_schema(db)
    populate(db)
    db.exec_driver_sql(sql)
    assert_rejected_without_writes(db)


@pytest.mark.parametrize('kind', ['TABLE', 'VIEW'])
@pytest.mark.parametrize('name', ['tiktok_accounts', 'TikTok_Accounts'])
def test_partial_relation_or_view_including_alias_rejects_before_ddl(db, kind, name):
    prerequisites(db)
    db.exec_driver_sql(f"CREATE {kind} {name} AS SELECT 'synthetic-ciphertext' AS id")
    assert_rejected_without_writes(db)


@pytest.mark.parametrize('name', ['tiktok_accounts', 'ix_tiktok_accounts_open_id',
                                 'IX_TikTok_Accounts_Open_ID'])
def test_global_sqlite_index_collision_rejects_before_creating_table(db, name):
    prerequisites(db)
    db.exec_driver_sql(f'CREATE INDEX {name} ON projects(title)')
    assert_rejected_without_writes(db)


@pytest.mark.parametrize('kind', ['TABLE', 'VIEW'])
def test_index_name_occupied_by_relation_rejects_before_creating_table(db, kind):
    prerequisites(db)
    db.exec_driver_sql(f'CREATE {kind} ix_tiktok_accounts_open_id AS SELECT 1 AS id')
    assert_rejected_without_writes(db)


@pytest.mark.parametrize('startup', [False, True])
def test_downgrade_refuses_ambiguous_ownership_without_writes(db, startup):
    prerequisites(db)
    fixture_schema(db, startup)
    populate(db)
    before = snapshot(db)
    statements = record_sql(db)
    with Operations.context(MigrationContext.configure(db)):
        with pytest.raises(RuntimeError, match='Cannot safely downgrade'):
            revision(NAME).downgrade()
    assert snapshot(db) == before
    assert_no_writes(statements)


def test_blind_offline_upgrade_requires_explicit_online_connection():
    output = StringIO()
    with Operations.context(MigrationContext.configure(
            dialect_name='mysql', opts={'as_sql': True, 'output_buffer': output})):
        with pytest.raises(RuntimeError, match='explicit online connection'):
            revision(NAME).upgrade()
    assert output.getvalue() == ''


def test_mysql_ddl_compiles_offline_from_actual_sqlite_operations(db):
    prerequisites(db)
    compiled = []
    def capture(conn, clause, multiparams, params, options):
        if isinstance(clause, sa.schema.DDLElement):
            compiled.append(str(clause.compile(dialect=mysql.dialect())))
    sa.event.listen(db, 'before_execute', capture)
    tiktok_link(db)
    ddl = '\n'.join(compiled)
    assert 'CREATE TABLE tiktok_accounts' in ddl
    assert "display_name VARCHAR(200) NOT NULL DEFAULT 'TikTok'" in ddl
    assert 'is_active BOOL NOT NULL DEFAULT true' in ddl
    assert 'CREATE UNIQUE INDEX ix_tiktok_accounts_open_id ON tiktok_accounts (open_id)' in ddl
    assert 'DROP' not in ddl
