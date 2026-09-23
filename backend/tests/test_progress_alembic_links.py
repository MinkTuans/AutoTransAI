"""Disposable SQLite only, actual revision operations without env.py or app imports."""
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.dialects import mysql
from sqlalchemy.exc import IntegrityError

from tests.test_first_alembic_link import (
    db, fixture_schema as first_link_fixture, isolated, revision, traverse as first_link,
)


NAMES = ('20260908_add_youtube_progress', '20260908_workflow_progress')
TABLES = ('youtube_channels', 'youtube_publications', 'workflow_executions',
          'workflow_stage_executions')
ADDITIONS = {
    'youtube_publications': {'progress': 'INTEGER NOT NULL'},
    'workflow_executions': {'overall_progress_pct': 'INTEGER NOT NULL'},
    'workflow_stage_executions': {
        'progress_percentage': 'INTEGER NOT NULL', 'current_item': 'INTEGER NOT NULL',
        'total_items': 'INTEGER NOT NULL', 'message': 'VARCHAR(255)'},
}


def progress_links(db):
    with Operations.context(MigrationContext.configure(db)):
        for name in NAMES:
            revision(name).upgrade()


def fixture_schema(db, startup=False, replace=None):
    first_link(db)
    sql = (Path(__file__).parent / 'fixtures/progress_link_schema.sql').read_text()
    if replace:
        sql = sql.replace(*replace)
    for statement in sql.split(';'):
        if statement.strip():
            db.exec_driver_sql(statement)
    if startup:
        for table, columns in ADDITIONS.items():
            for name, kind in columns.items():
                db.exec_driver_sql(f'ALTER TABLE {table} ADD COLUMN {name} {kind}')
        # ead6ad9 startup also added this unrelated nullable, indexed column.
        db.exec_driver_sql('ALTER TABLE youtube_publications ADD COLUMN project_id VARCHAR(36)')
        db.exec_driver_sql('CREATE INDEX ix_youtube_publications_project_id ON youtube_publications(project_id)')
    populate(db)


def populate(db):
    for table in ('projects', *TABLES):
        values = {}
        for column in sa.inspect(db).get_columns(table):
            kind = column['type']
            values[column['name']] = (7 if isinstance(kind, (sa.Integer, sa.Boolean))
                                     else '2000-01-01 00:00:00' if isinstance(kind, sa.DateTime)
                                     else '{"fixture": "private"}' if isinstance(kind, sa.JSON)
                                     else 'private-fixture')
        values['id'] = table
        if table == 'youtube_publications':
            values['channel_id'] = 'youtube_channels'
        if table == 'workflow_executions':
            values['project_id'] = 'projects'
        if table == 'workflow_stage_executions':
            values['workflow_execution_id'] = 'workflow_executions'
        db.execute(sa.text(f'INSERT INTO {table} ({", ".join(values)}) VALUES '
                           f'({", ".join(":" + key for key in values)})'), values)


def snapshot(db):
    return {table: [dict(row) for row in db.exec_driver_sql(f'SELECT * FROM {table}').mappings()]
            for table in sa.inspect(db).get_table_names()}


def record_sql(db):
    statements = []
    sa.event.listen(db, 'before_cursor_execute',
                    lambda c, cur, sql, p, ctx, many: statements.append(sql))
    return statements


def assert_no_writes(statements):
    assert not any(sql.lstrip().upper().startswith(
        ('CREATE', 'ALTER', 'DROP', 'INSERT', 'UPDATE', 'DELETE', 'REPLACE')) for sql in statements)


def test_blank_database_traverses_first_link_and_both_progress_revisions(db):
    first_link(db)
    progress_links(db)
    assert set(sa.inspect(db).get_table_names()) == {
        'projects', 'segments', 'video_assets', 'video_translation_jobs', *TABLES}
    for table, columns in ADDITIONS.items():
        actual = {column['name']: column for column in sa.inspect(db).get_columns(table)}
        for name, kind in columns.items():
            assert str(actual[name]['type']) == kind.replace(' NOT NULL', '')
            assert actual[name]['nullable'] == (name == 'message')
            assert actual[name]['default'] == (None if name == 'message' else "'0'")
    assert revision(NAMES[0]).down_revision == '20260822_sync_schema'
    assert revision(NAMES[1]).down_revision == revision(NAMES[0]).revision


@pytest.mark.parametrize('startup', [False, True], ids=['historical', 'startup-created'])
def test_populated_compatible_tables_keep_every_value_and_add_only_missing_columns(db, startup):
    fixture_schema(db, startup)
    before = snapshot(db)
    statements = record_sql(db)
    first_link(db)
    progress_links(db)
    after = snapshot(db)
    for table, rows in before.items():
        if rows:
            assert [{key: row[key] for key in rows[0]} for row in after[table]] == rows
        else:
            assert not after[table]
    assert not any(sql.lstrip().upper().startswith(('CREATE', 'DROP', 'DELETE', 'UPDATE'))
                   for sql in statements)
    if startup:
        assert_no_writes(statements)
    else:
        assert after['youtube_publications'][0]['progress'] == 0
        assert after['workflow_executions'][0]['overall_progress_pct'] == 0
        assert after['workflow_stage_executions'][0]['message'] is None
    assert db.exec_driver_sql('PRAGMA foreign_key_check').all() == []
    statements.clear()
    progress_links(db)
    assert snapshot(db) == after
    assert_no_writes(statements)


@pytest.mark.parametrize('table', TABLES)
def test_created_prerequisite_matches_independent_historical_fixture(db, table):
    first_link(db)
    progress_links(db)
    reference_engine = sa.create_engine('sqlite:///:memory:')
    try:
        with reference_engine.begin() as reference:
            fixture_schema(reference)
            actual, frozen = sa.inspect(db), sa.inspect(reference)
            def columns(inspector):
                return [(c['name'], str(c['type']), c['nullable'], c['default'], c['primary_key'])
                        for c in inspector.get_columns(table) if c['name'] not in ADDITIONS.get(table, {})]
            assert columns(actual) == columns(frozen)
            assert actual.get_foreign_keys(table) == frozen.get_foreign_keys(table)
            assert actual.get_indexes(table) == frozen.get_indexes(table)
    finally:
        reference_engine.dispose()


@pytest.mark.parametrize('table,column', [
    ('youtube_publications', 'channel_id'), ('workflow_executions', 'project_id'),
    ('workflow_stage_executions', 'workflow_execution_id')])
def test_created_foreign_keys_are_enforced(db, table, column):
    first_link(db)
    progress_links(db)
    populate(db)
    with pytest.raises(IntegrityError):
        db.exec_driver_sql(f"UPDATE {table} SET {column} = 'missing'")


@pytest.mark.parametrize('sql', [
    'ALTER TABLE youtube_channels RENAME COLUMN credentials_json TO unknown',
    'ALTER TABLE workflow_stage_executions RENAME COLUMN id TO other_id',
    'ALTER TABLE projects RENAME COLUMN title TO unknown',
    'ALTER TABLE youtube_publications ADD COLUMN progress TEXT NOT NULL DEFAULT 0',
    'ALTER TABLE workflow_executions ADD COLUMN overall_progress_pct INTEGER DEFAULT 0',
    "ALTER TABLE workflow_stage_executions ADD COLUMN total_items INTEGER NOT NULL DEFAULT '(0)'",
    "ALTER TABLE workflow_stage_executions ADD COLUMN message VARCHAR(255) DEFAULT 'private-fixture'",
])
def test_mismatch_anywhere_rejects_both_revisions_before_any_write(db, sql):
    fixture_schema(db)
    db.exec_driver_sql(sql)
    before = snapshot(db)
    schema = db.exec_driver_sql('SELECT name, sql FROM sqlite_master ORDER BY name').all()
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch.*inspect.*before retrying') as exc:
        progress_links(db)
    assert 'private-fixture' not in str(exc.value)
    assert snapshot(db) == before
    assert db.exec_driver_sql('SELECT name, sql FROM sqlite_master ORDER BY name').all() == schema
    assert_no_writes(statements)


@pytest.mark.parametrize('target', TABLES)
@pytest.mark.parametrize('kind', ['TABLE', 'VIEW'])
def test_unknown_partial_table_or_view_fails_before_any_creation(db, target, kind):
    first_link(db)
    db.exec_driver_sql(f'CREATE {kind} {target} AS SELECT 1 AS id')
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        progress_links(db)
    assert_no_writes(statements)


@pytest.mark.parametrize('kind', ['TABLE', 'VIEW'])
def test_case_insensitive_relation_collision_is_rejected_before_any_write(db, kind):
    first_link_fixture(db)
    first_link(db)
    db.exec_driver_sql(f"CREATE {kind} YouTube_Publications AS SELECT 'private-fixture' AS id")
    before = snapshot(db)
    schema = db.exec_driver_sql('SELECT name, sql FROM sqlite_master ORDER BY name').all()
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        progress_links(db)
    assert snapshot(db) == before
    assert db.exec_driver_sql('SELECT name, sql FROM sqlite_master ORDER BY name').all() == schema
    assert_no_writes(statements)


@pytest.mark.parametrize('index_name', [
    'ix_youtube_publications_job_id', 'IX_YouTube_Publications_Job_ID',
    'ix_workflow_executions_project_id',
    'ix_workflow_stage_executions_workflow_execution_id',
])
def test_global_sqlite_index_collision_is_rejected_before_any_write(db, index_name):
    first_link_fixture(db)
    first_link(db)
    db.exec_driver_sql(f'CREATE INDEX {index_name} ON projects(title)')
    before = snapshot(db)
    schema = db.exec_driver_sql('SELECT name, sql FROM sqlite_master ORDER BY name').all()
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        progress_links(db)
    assert snapshot(db) == before
    assert db.exec_driver_sql('SELECT name, sql FROM sqlite_master ORDER BY name').all() == schema
    assert_no_writes(statements)


def test_reflected_columns_without_sqlite_only_primary_key_flag_are_validated(db, monkeypatch):
    fixture_schema(db, startup=True)
    inspector_type = sa.engine.reflection.Inspector
    get_columns = inspector_type.get_columns

    def portable_columns(self, *args, **kwargs):
        # MySQL exposes PK membership through get_pk_constraint, not columns.
        return [{key: value for key, value in column.items() if key != 'primary_key'}
                for column in get_columns(self, *args, **kwargs)]

    monkeypatch.setattr(inspector_type, 'get_columns', portable_columns)
    before = snapshot(db)
    statements = record_sql(db)
    progress_links(db)
    assert snapshot(db) == before
    assert_no_writes(statements)


@pytest.mark.parametrize('replace', [
    (',\n FOREIGN KEY(channel_id) REFERENCES youtube_channels(id) ON DELETE CASCADE', ''),
    ('REFERENCES workflow_executions(id) ON DELETE CASCADE', 'REFERENCES projects(id) ON DELETE CASCADE'),
    ('REFERENCES projects(id) ON DELETE CASCADE', 'REFERENCES projects(id) ON DELETE RESTRICT'),
    ('channel_name VARCHAR(200) NOT NULL', 'channel_name VARCHAR(20) NOT NULL'),
    ('retry_count INTEGER NOT NULL', 'retry_count INTEGER NOT NULL DEFAULT 0'),
    ('credentials_json TEXT NOT NULL', 'credentials_json TEXT'),
])
def test_mismatched_prerequisite_contract_rejects_before_writes(db, replace):
    # Wrong FK uses an otherwise-valid parent value so fixture inserts succeed.
    if replace[0].startswith('REFERENCES workflow_executions'):
        first_link(db)
        sql = (Path(__file__).parent / 'fixtures/progress_link_schema.sql').read_text().replace(*replace)
        for statement in sql.split(';'):
            if statement.strip():
                db.exec_driver_sql(statement)
    else:
        fixture_schema(db, replace=replace)
    before = snapshot(db)
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        progress_links(db)
    assert snapshot(db) == before
    assert_no_writes(statements)


def test_missing_child_table_in_known_group_requires_reconciliation(db):
    first_link(db)
    sql = (Path(__file__).parent / 'fixtures/progress_link_schema.sql').read_text()
    db.exec_driver_sql(sql.split(';')[0])  # Complete historical parent, absent child.
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        progress_links(db)
    assert_no_writes(statements)


def test_known_partial_progress_columns_keep_defaults_and_values(db):
    fixture_schema(db)
    db.exec_driver_sql('ALTER TABLE workflow_stage_executions ADD COLUMN current_item INTEGER NOT NULL DEFAULT 0')
    db.exec_driver_sql('UPDATE workflow_stage_executions SET current_item = 42')
    progress_links(db)
    assert db.exec_driver_sql('SELECT current_item, total_items FROM workflow_stage_executions').one() == (42, 0)
    columns = {c['name']: c for c in sa.inspect(db).get_columns('workflow_stage_executions')}
    assert columns['current_item']['default'] == '0'
    assert columns['total_items']['default'] == "'0'"


@pytest.mark.parametrize('name', NAMES)
def test_downgrade_refuses_without_writes(db, name):
    fixture_schema(db, startup=True)
    before = snapshot(db)
    statements = record_sql(db)
    with Operations.context(MigrationContext.configure(db)):
        with pytest.raises(RuntimeError, match='Cannot safely downgrade'):
            revision(name).downgrade()
    assert snapshot(db) == before
    assert_no_writes(statements)


def test_mysql_ddl_compiles_offline_from_actual_sqlite_operations(db):
    first_link(db)
    compiled = []
    def capture(conn, clause, multiparams, params, options):
        if isinstance(clause, sa.schema.DDLElement):
            compiled.append(str(clause.compile(dialect=mysql.dialect())))
    sa.event.listen(db, 'before_execute', capture)
    progress_links(db)
    ddl = '\n'.join(compiled)
    for table in TABLES:
        assert f'CREATE TABLE {table}' in ddl
    assert "ADD COLUMN progress INTEGER NOT NULL DEFAULT '0'" in ddl
    assert 'ADD COLUMN message VARCHAR(255)' in ddl
    assert 'REFERENCES youtube_channels (id) ON DELETE CASCADE' in ddl
    assert 'REFERENCES workflow_executions (id) ON DELETE CASCADE' in ddl
    assert 'REFERENCES projects (id) ON DELETE CASCADE' in ddl
    assert 'DROP' not in ddl
