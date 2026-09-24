"""Disposable historical glossary prerequisites, without publishing the glossary revision."""
from pathlib import Path
from types import SimpleNamespace

import pytest
import sqlalchemy as sa
from alembic.util import load_python_file
from sqlalchemy.dialects import mysql
from sqlalchemy.dialects.mysql.reflection import MySQLTableDefinitionParser
from sqlalchemy.exc import IntegrityError

from tests.test_first_alembic_link import db, isolated, fixture_schema as first_fixture
from tests.test_progress_alembic_links import assert_no_writes, record_sql, snapshot


DIRECTORY = Path(__file__).parents[1] / 'alembic'
TABLES = ('project_glossaries', 'project_terminology_memory')


def helper():
    return load_python_file(str(DIRECTORY), 'glossary_prerequisites.py')


def prepare(db):
    first_fixture(db)


def fixture_schema(db, replace=None):
    sql = (Path(__file__).parent / 'fixtures/glossary_prerequisites_schema.sql').read_text()
    if replace:
        replacements = [replace] if isinstance(replace[0], str) else replace
        for old, new in replacements:
            sql = sql.replace(old, new)
    for statement in sql.split(';'):
        if statement.strip():
            db.exec_driver_sql(statement)


def populate(db):
    db.exec_driver_sql("INSERT INTO project_glossaries VALUES "
                       "('g1', 'projects', 'Tên riêng', 'private-fixture', 'other', 0.7, "
                       "'private context', 1, '2001-02-03 04:05:06', '2002-03-04 05:06:07')")
    db.exec_driver_sql("INSERT INTO project_terminology_memory VALUES "
                       "('m1', 'projects', 'Tên riêng', 'private-suggestion', 'other', 0.9, "
                       "0, 'private memory', '2003-04-05 06:07:08', '2004-05-06 07:08:09')")


def rows(db):
    return {table: [tuple(row) for row in db.exec_driver_sql(f'SELECT * FROM {table}').all()]
            for table in TABLES if table in sa.inspect(db).get_table_names()}


def reject_without_writes(db):
    before_rows = rows(db)
    before_schema = db.exec_driver_sql('SELECT type, name, tbl_name, sql FROM sqlite_master ORDER BY name').all()
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch.*reconcile.*backup') as exc:
        helper().ensure(db)
    assert 'private-' not in str(exc.value)
    assert rows(db) == before_rows
    assert db.exec_driver_sql('SELECT type, name, tbl_name, sql FROM sqlite_master ORDER BY name').all() == before_schema
    assert_no_writes(statements)


def test_absent_tables_match_independent_historical_contract(db):
    prepare(db)
    before = snapshot(db)
    helper().ensure(db)
    assert set(TABLES) <= set(sa.inspect(db).get_table_names())
    after = snapshot(db)
    assert {table: after[table] for table in before} == before
    engine = sa.create_engine('sqlite:///:memory:')
    try:
        with engine.begin() as expected:
            fixture_schema(expected)
            for table in TABLES:
                actual, frozen = sa.inspect(db), sa.inspect(expected)
                def columns(inspector):
                    return [(c['name'], str(c['type']), c['nullable'], c['default'], c['primary_key'])
                            for c in inspector.get_columns(table)]
                assert columns(actual) == columns(frozen)
                assert actual.get_pk_constraint(table) == frozen.get_pk_constraint(table)
                assert actual.get_foreign_keys(table) == frozen.get_foreign_keys(table)
                assert actual.get_indexes(table) == frozen.get_indexes(table)
    finally:
        engine.dispose()


def test_populated_compatible_tables_and_repeat_preserve_rows_without_writes(db):
    prepare(db)
    fixture_schema(db)
    populate(db)
    before = rows(db)
    statements = record_sql(db)
    module = helper()
    module.ensure(db)
    module.ensure(db)
    assert rows(db) == before
    assert_no_writes(statements)


@pytest.mark.parametrize('table', TABLES)
def test_partial_group_rejected_before_writes(db, table):
    prepare(db)
    fixture_schema(db)
    populate(db)
    db.exec_driver_sql(f'DROP TABLE {table}')
    reject_without_writes(db)


@pytest.mark.parametrize('replacement', [
    ('source_term VARCHAR(255) NOT NULL', 'source_term VARCHAR(200) NOT NULL'),
    ('suggested_term VARCHAR(255) NOT NULL', 'suggested_term VARCHAR(255)'),
    ('term_type VARCHAR(50) NOT NULL', "term_type VARCHAR(50) NOT NULL DEFAULT 'other'"),
    ('confidence FLOAT NOT NULL', 'confidence FLOAT NOT NULL DEFAULT 0.9'),
    ('approved BOOLEAN NOT NULL', 'approved BOOLEAN NOT NULL DEFAULT 1'),
    ('needs_review BOOLEAN NOT NULL', 'needs_review BOOLEAN NOT NULL DEFAULT 0'),
    ('created_at DATETIME NOT NULL', 'created_at DATETIME'),
    ('source_context TEXT', 'source_context TEXT, unexpected TEXT'),
    ('source_context TEXT', 'source_context VARCHAR(255)'),
    ('id VARCHAR(36) NOT NULL PRIMARY KEY', 'id VARCHAR(36) NOT NULL'),
    ('id VARCHAR(36) NOT NULL PRIMARY KEY', 'id VARCHAR(36) NOT NULL PRIMARY KEY ON CONFLICT REPLACE'),
    ('id VARCHAR(36) NOT NULL PRIMARY KEY', 'id VARCHAR(36) COLLATE NOCASE NOT NULL PRIMARY KEY'),
    ('id VARCHAR(36) NOT NULL PRIMARY KEY', 'id VARCHAR(36) NOT NULL PRIMARY KEY DESC'),
    ('REFERENCES projects(id) ON DELETE CASCADE', 'REFERENCES projects(id) ON DELETE RESTRICT'),
    ('REFERENCES projects(id) ON DELETE CASCADE', 'REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE'),
    ('source_term VARCHAR(255) NOT NULL', 'source_term VARCHAR(255) NOT NULL UNIQUE'),
    ('project_glossaries(project_id)', 'project_glossaries(project_id DESC)'),
    ('project_terminology_memory(project_id)', 'project_terminology_memory(source_term)'),
])
def test_unknown_existing_shape_fails_closed(db, replacement):
    prepare(db)
    fixture_schema(db, replacement)
    reject_without_writes(db)


def test_populated_index_drift_preserves_both_tables_and_rows(db):
    prepare(db)
    fixture_schema(db)
    populate(db)
    db.exec_driver_sql('DROP INDEX ix_project_terminology_memory_project_id')
    db.exec_driver_sql('CREATE INDEX ix_project_terminology_memory_project_id '
                       'ON project_terminology_memory(source_term)')
    reject_without_writes(db)


def test_column_collation_drift_cannot_hide_behind_binary_index(db):
    prepare(db)
    fixture_schema(db, (
        ('project_id VARCHAR(36) NOT NULL', 'project_id VARCHAR(36) COLLATE NOCASE NOT NULL'),
        ('project_glossaries(project_id)', 'project_glossaries(project_id COLLATE BINARY)'),
    ))
    reject_without_writes(db)


@pytest.mark.parametrize('name', ['projects', *TABLES, 'ix_project_glossaries_project_id',
                                  'ix_project_terminology_memory_project_id'])
def test_temporary_shadow_fails_closed(db, name):
    prepare(db)
    db.exec_driver_sql(f'CREATE TEMP VIEW {name} AS SELECT 1 AS id')
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        helper().ensure(db)
    assert_no_writes(statements)


@pytest.mark.parametrize('ddl', [
    'CREATE VIEW PROJECT_GLOSSARIES AS SELECT 1 AS id',
    'CREATE TABLE Project_Terminology_Memory (id TEXT)',
    'CREATE INDEX IX_PROJECT_GLOSSARIES_PROJECT_ID ON projects(id)',
    'CREATE VIEW ix_project_terminology_memory_project_id AS SELECT 1 AS id',
])
def test_case_and_global_index_collisions_fail_before_creation(db, ddl):
    prepare(db)
    db.exec_driver_sql(ddl)
    reject_without_writes(db)


def test_parent_identity_mismatch_fails_before_creation(db):
    db.exec_driver_sql('CREATE TABLE projects (id VARCHAR(36) COLLATE NOCASE PRIMARY KEY)')
    reject_without_writes(db)


def test_created_foreign_keys_enforce_cascade(db):
    prepare(db)
    helper().ensure(db)
    populate(db)
    with pytest.raises(IntegrityError):
        db.exec_driver_sql("UPDATE project_glossaries SET project_id='missing'")
    db.exec_driver_sql("DELETE FROM projects WHERE id='projects'")
    assert rows(db) == {table: [] for table in TABLES}


def test_import_refuses_offline_connection_and_destructive_downgrade(db):
    prepare(db)
    statements = record_sql(db)
    module = helper()
    with pytest.raises(RuntimeError, match='explicit online connection'):
        module.ensure(None)
    with pytest.raises(RuntimeError, match='verified backup'):
        module.refuse_downgrade()
    assert_no_writes(statements)


def test_mysql_ddl_compiles_offline(db):
    prepare(db)
    compiled = []
    def capture(conn, clause, multiparams, params, options):
        if isinstance(clause, sa.schema.DDLElement):
            compiled.append(str(clause.compile(dialect=mysql.dialect())))
    sa.event.listen(db, 'before_execute', capture)
    helper().ensure(db)
    ddl = '\n'.join(compiled)
    assert ddl.count('CREATE TABLE') == 2
    assert ddl.count('ON DELETE CASCADE') == 2
    assert 'DEFAULT' not in ddl
    assert 'ix_project_glossaries_project_id' in ddl
    assert 'ix_project_terminology_memory_project_id' in ddl


def test_mysql_boolean_alias_reflection_is_compatible_offline(db, monkeypatch):
    prepare(db)
    fixture_schema(db)
    populate(db)
    inspector = sa.inspect(db)
    names = inspector.get_table_names()
    columns = {name: [{key: value for key, value in column.items() if key != 'primary_key'}
                      for column in inspector.get_columns(name)] for name in names}
    dialect = mysql.dialect()
    parser = MySQLTableDefinitionParser(dialect, dialect.identifier_preparer)
    for table, field in [('project_glossaries', 'approved'),
                         ('project_terminology_memory', 'needs_review')]:
        parsed = parser.parse(
            f'CREATE TABLE `{table}` (\n  `{field}` tinyint(1) NOT NULL,\n'
            '  `id` varchar(36) NOT NULL,\n  PRIMARY KEY (`id`)\n) ENGINE=InnoDB',
            'utf8mb4').columns[0]
        columns[table] = [parsed if column['name'] == field else column
                          for column in columns[table]]
    pks = {name: inspector.get_pk_constraint(name) for name in names}
    fks = {name: inspector.get_foreign_keys(name) for name in names}
    indexes = {name: inspector.get_indexes(name) for name in names}
    reflected = SimpleNamespace(
        default_schema_name=None, get_table_names=lambda: names, get_view_names=lambda: [],
        get_columns=columns.__getitem__, get_pk_constraint=pks.__getitem__,
        get_foreign_keys=fks.__getitem__, get_indexes=indexes.__getitem__,
        get_check_constraints=lambda name: [], get_unique_constraints=lambda name: [],
    )
    def forbidden(*args, **kwargs):
        raise AssertionError('Offline MySQL ensure must not issue SQL')
    with monkeypatch.context() as patch:
        patch.setattr(db, 'dialect', dialect)
        patch.setattr(sa, 'inspect', lambda connection: reflected)
        patch.setattr(db, 'execute', forbidden)
        patch.setattr(db, 'exec_driver_sql', forbidden)
        helper().ensure(db)


@pytest.mark.parametrize('column_sql,compatible', [
    ('`id` varchar(36) NOT NULL', True),
    ("`id` varchar(36) NOT NULL DEFAULT 'generated'", False),
    ('`id` varchar(36) NOT NULL AUTO_INCREMENT', False),
])
def test_mysql_reflected_identity_profile_is_checked_offline(db, monkeypatch, column_sql, compatible):
    prepare(db)
    fixture_schema(db)
    populate(db)
    before = rows(db)
    inspector = sa.inspect(db)
    names = inspector.get_table_names()
    columns = {name: [{key: value for key, value in column.items() if key != 'primary_key'}
                      for column in inspector.get_columns(name)] for name in names}
    pks = {name: inspector.get_pk_constraint(name) for name in names}
    fks = {name: inspector.get_foreign_keys(name) for name in names}
    indexes = {name: inspector.get_indexes(name) for name in names}
    dialect = mysql.dialect()
    parser = MySQLTableDefinitionParser(dialect, dialect.identifier_preparer)
    columns['project_glossaries'][0] = parser.parse(
        f'CREATE TABLE `project_glossaries` (\n  {column_sql},\n  PRIMARY KEY (`id`)\n) ENGINE=InnoDB',
        'utf8mb4').columns[0]
    reflected = SimpleNamespace(
        default_schema_name=None, get_table_names=lambda: names, get_view_names=lambda: [],
        get_columns=columns.__getitem__, get_pk_constraint=pks.__getitem__,
        get_foreign_keys=fks.__getitem__, get_indexes=indexes.__getitem__,
        get_check_constraints=lambda name: [], get_unique_constraints=lambda name: [],
    )
    def forbidden(*args, **kwargs):
        raise AssertionError('Offline MySQL ensure must not issue SQL')
    with monkeypatch.context() as patch:
        patch.setattr(db, 'dialect', dialect)
        patch.setattr(sa, 'inspect', lambda connection: reflected)
        patch.setattr(db, 'execute', forbidden)
        patch.setattr(db, 'exec_driver_sql', forbidden)
        if compatible:
            helper().ensure(db)
        else:
            with pytest.raises(RuntimeError, match='Historical schema mismatch'):
                helper().ensure(db)
    assert rows(db) == before
