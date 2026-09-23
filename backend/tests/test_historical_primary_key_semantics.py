"""PK preflight through actual D1/D2 operations, independent disposable fixtures."""
from pathlib import Path
from types import SimpleNamespace

import pytest
import sqlalchemy as sa
from alembic import op
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects import mysql

from tests.test_first_alembic_link import db, isolated, revision
from tests.test_progress_alembic_links import assert_no_writes, record_sql, snapshot


INITIAL = '202da08bcdd8_initial_schema'
PROGRESS = ('20260908_add_youtube_progress', '20260908_workflow_progress')
FIRST_TABLES = ('projects', 'video_assets', 'segments', 'video_translation_jobs')
PROGRESS_TABLES = ('projects', 'youtube_channels', 'youtube_publications',
                   'workflow_executions', 'workflow_stage_executions')
CASES = [(INITIAL, table) for table in FIRST_TABLES] + [
    (link, table) for link in PROGRESS for table in PROGRESS_TABLES]


def fixture_schema(db, link, table, declaration, table_pk=None, suffix=''):
    """Change only the target PK in literal historical DDL, then populate it."""
    fixtures = Path(__file__).parent / 'fixtures'
    sql = (fixtures / 'first_link_schema.sql').read_text()
    if link in PROGRESS:
        sql += (fixtures / 'progress_link_schema.sql').read_text()
    kind = 'INTEGER' if table == 'segments' else 'VARCHAR(36)'
    for statement in sql.split(';'):
        if not statement.strip():
            continue
        if f'CREATE TABLE {table} (' in statement:
            statement = statement.replace(f'id {kind} NOT NULL PRIMARY KEY', declaration, 1)
            if table_pk:
                body, _, end = statement.rpartition(')')
                statement = body + ',\n ' + table_pk + ')' + end
            statement += suffix
        db.exec_driver_sql(statement)
    parents = {
        'segments': ('project_id', 'projects'),
        'video_translation_jobs': ('asset_id', 'video_assets'),
        'youtube_publications': ('channel_id', 'youtube_channels'),
        'workflow_executions': ('project_id', 'projects'),
        'workflow_stage_executions': ('workflow_execution_id', 'workflow_executions'),
    }
    tables = FIRST_TABLES + (PROGRESS_TABLES[1:] if link in PROGRESS else ())
    for name in tables:
        values = {}
        for column in sa.inspect(db).get_columns(name):
            kind = column['type']
            values[column['name']] = (1 if isinstance(kind, (sa.Integer, sa.Float, sa.Boolean))
                                     else '2000-01-01 00:00:00' if isinstance(kind, sa.DateTime)
                                     else '{"fixture": "private"}' if isinstance(kind, sa.JSON)
                                     else 'private-fixture')
        values['id'] = 1 if name == 'segments' else name
        if name in parents:
            column, parent = parents[name]
            values[column] = parent
        db.execute(sa.text(f'INSERT INTO {name} ({", ".join(values)}) VALUES '
                           f'({", ".join(":" + key for key in values)})'), values)


def upgrade(db, link):
    with Operations.context(MigrationContext.configure(db)):
        revision(link).upgrade()


def assert_rejected(db, link):
    before = snapshot(db)
    schema = db.exec_driver_sql('SELECT name, sql FROM sqlite_master ORDER BY name').all()
    statements = record_sql(db)
    expected = ('Historical schema mismatch: inspect the '
                + ('first-link' if link == INITIAL else 'progress-link')
                + ' table definitions and reconcile the schema from a backup before retrying.')
    with pytest.raises(RuntimeError) as exc:
        upgrade(db, link)
    assert str(exc.value) == expected
    assert snapshot(db) == before
    assert db.exec_driver_sql('SELECT name, sql FROM sqlite_master ORDER BY name').all() == schema
    assert_no_writes(statements)


@pytest.mark.parametrize('link,table', CASES)
@pytest.mark.parametrize('variant', ['nocase', 'desc', 'replace', 'ignore', 'fail', 'rollback',
                                    'table-replace', 'without-rowid'])
def test_incompatible_pk_is_rejected_before_any_write(db, link, table, variant):
    kind = 'INTEGER' if table == 'segments' else 'VARCHAR(36)'
    declaration = f'id {kind} NOT NULL PRIMARY KEY'
    table_pk = None
    suffix = ''
    if variant == 'nocase':
        declaration += ' COLLATE NOCASE'
    elif variant == 'desc':
        declaration += ' DESC'
    elif variant == 'table-replace':
        declaration = f'id {kind} NOT NULL'
        table_pk = 'PRIMARY KEY (id) ON CONFLICT REPLACE'
    elif variant == 'without-rowid':
        suffix = ' WITHOUT ROWID'
    else:
        declaration += ' ON CONFLICT ' + variant.upper()
    fixture_schema(db, link, table, declaration, table_pk, suffix)
    assert_rejected(db, link)


@pytest.mark.parametrize('link,table', CASES)
@pytest.mark.parametrize('form', ['column', 'abort', 'table', 'table-abort', 'quoted-comments'])
def test_equivalent_pk_forms_preserve_rows_and_abort_duplicate_id(db, link, table, form):
    kind = 'INTEGER' if table == 'segments' else 'VARCHAR(36)'
    declaration = f'id {kind} NOT NULL PRIMARY KEY'
    table_pk = None
    if form == 'abort':
        declaration += ' ASC ON CONFLICT ABORT COLLATE BINARY'
    elif form in ('table', 'table-abort'):
        declaration = f'id {kind} NOT NULL COLLATE BINARY'
        table_pk = 'PRIMARY KEY (id)' + (' ON CONFLICT ABORT' if form == 'table-abort' else '')
    elif form == 'quoted-comments':
        declaration = (f'"id" {kind} NOT NULL CONSTRAINT "ON CONFLICT REPLACE" '
                       'PRIMARY /* ON CONFLICT IGNORE */ KEY ASC '
                       'ON -- ON CONFLICT FAIL\n CONFLICT ABORT COLLATE "BINARY"')
    fixture_schema(db, link, table, declaration, table_pk)
    before = snapshot(db)
    upgrade(db, link)
    after = snapshot(db)
    for name, rows in before.items():
        assert [{key: row[key] for key in rows[0]} for row in after[name]] == rows
    # Exact duplicate IDs must fail, preserving parent rows and cascading children.
    with pytest.raises(IntegrityError):
        db.exec_driver_sql(f'INSERT INTO {table} SELECT * FROM {table}')
    assert snapshot(db) == after
    assert db.exec_driver_sql('PRAGMA foreign_key_check').all() == []
    if table == 'segments':
        with db.begin_nested() as probe:
            columns = ', '.join(key for key in after[table][0] if key != 'id')
            db.exec_driver_sql(f'INSERT INTO segments ({columns}) SELECT {columns} FROM segments')
            assert db.exec_driver_sql('SELECT id, rowid FROM segments ORDER BY id').all() == [(1, 1), (2, 2)]
            probe.rollback()
    else:
        assert db.execute(sa.text(f'SELECT id FROM {table} WHERE id = :id'),
                          {'id': table.upper()}).first() is None
    statements = record_sql(db)
    upgrade(db, link)
    assert_no_writes(statements)


@pytest.mark.parametrize('link,table', [(INITIAL, 'projects'), (PROGRESS[0], 'youtube_channels')])
def test_replace_fixture_demonstrates_cascaded_data_loss_then_preflight_rejects(db, link, table):
    fixture_schema(db, link, table, 'id VARCHAR(36) NOT NULL PRIMARY KEY ON CONFLICT REPLACE')
    before = snapshot(db)
    child = 'segments' if table == 'projects' else 'youtube_publications'
    # Prove the dangerous behavior only inside a rolled-back disposable savepoint.
    with db.begin_nested() as probe:
        db.exec_driver_sql(f'INSERT INTO {table} SELECT * FROM {table}')
        assert db.exec_driver_sql(f'SELECT COUNT(*) FROM {child}').scalar_one() == 0
        probe.rollback()
    assert snapshot(db) == before
    assert_rejected(db, link)


@pytest.mark.parametrize('declaration,table_pk', [
    ('id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT', None),
    ('id INTEGER NOT NULL', 'PRIMARY KEY (id DESC)'),
    ('id INT NOT NULL PRIMARY KEY', None),
])
def test_segments_rejects_nonhistorical_rowid_forms(db, declaration, table_pk):
    fixture_schema(db, INITIAL, 'segments', declaration, table_pk)
    assert_rejected(db, INITIAL)


@pytest.mark.parametrize('link,table', [(INITIAL, 'video_translation_jobs'),
                                       (PROGRESS[0], 'youtube_publications')])
def test_binary_pk_index_does_not_hide_nocase_column_comparison(db, link, table):
    fixture_schema(db, link, table, 'id VARCHAR(36) NOT NULL COLLATE NOCASE',
                   'PRIMARY KEY (id COLLATE BINARY)')
    assert db.execute(sa.text(f'SELECT id FROM {table} WHERE id = :id'),
                      {'id': table.upper()}).scalar_one() == table
    assert_rejected(db, link)


@pytest.mark.parametrize('link', [INITIAL, *PROGRESS])
def test_mysql_reflection_path_never_uses_sqlite_queries(db, link, monkeypatch):
    fixture_schema(db, PROGRESS[0], 'projects', 'id VARCHAR(36) NOT NULL PRIMARY KEY')
    for progress in PROGRESS:
        upgrade(db, progress)
    inspector = sa.inspect(db)
    names = inspector.get_table_names()
    # Freeze actual fixture reflection, removing SQLite-only column PK flags.
    # No connection exists behind this offline MySQL-shaped inspector.
    columns = {name: [{k: v for k, v in column.items() if k != 'primary_key'}
                      for column in inspector.get_columns(name)] for name in names}
    pks = {name: inspector.get_pk_constraint(name) for name in names}
    fks = {name: inspector.get_foreign_keys(name) for name in names}
    indexes = {name: inspector.get_indexes(name) for name in names}
    reflected = SimpleNamespace(
        default_schema_name=None, get_table_names=lambda: names, get_view_names=lambda: [],
        get_columns=columns.__getitem__, get_pk_constraint=pks.__getitem__,
        get_foreign_keys=fks.__getitem__, get_indexes=indexes.__getitem__,
    )

    def forbidden(*args, **kwargs):
        raise AssertionError('Existing compatible MySQL schema must not execute SQLite SQL or DDL')

    bind = SimpleNamespace(dialect=mysql.dialect(), execute=forbidden, exec_driver_sql=forbidden)
    module = revision(link)
    with Operations.context(MigrationContext.configure(db)):
        monkeypatch.setattr(op, 'get_bind', lambda: bind)
        monkeypatch.setattr(sa, 'inspect', lambda connection: reflected)
        module.upgrade()
