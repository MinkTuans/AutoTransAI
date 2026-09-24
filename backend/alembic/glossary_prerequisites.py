"""Frozen pre-glossary tables from 93200e6^, without application imports.

Only project_glossaries and project_terminology_memory belong here. The ORM
defaults/onupdate are Python-only, so neither table has SQL defaults.
"""
from pathlib import Path
import re

from alembic.util import load_python_file
import sqlalchemy as sa
from sqlalchemy.dialects.mysql.reflection import MySQLTableDefinitionParser


def _tables():
    metadata = sa.MetaData()
    parent = sa.Table('projects', metadata, sa.Column('id', sa.String(36), primary_key=True))
    glossary = sa.Table(
        'project_glossaries', metadata,
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('source_term', sa.String(255), nullable=False),
        sa.Column('translated_term', sa.String(255), nullable=False),
        sa.Column('term_type', sa.String(50), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('source_context', sa.Text()),
        sa.Column('approved', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    memory = sa.Table(
        'project_terminology_memory', metadata,
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('source_term', sa.String(255), nullable=False),
        sa.Column('suggested_term', sa.String(255), nullable=False),
        sa.Column('term_type', sa.String(50), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('needs_review', sa.Boolean(), nullable=False),
        sa.Column('source_context', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    return parent, (glossary, memory)


def _mismatch():
    raise RuntimeError('Historical schema mismatch: inspect the glossary prerequisite table and index '
                       'definitions and reconcile the schema from a backup before retrying.')


def _validate_column(actual, expected, dialect):
    kind = actual['type'].compile(dialect=dialect) if actual else None
    boolean_alias = (dialect.name == 'mysql' and isinstance(expected.type, sa.Boolean)
                     and kind == 'TINYINT(1)')
    if (actual is None
            or (kind != expected.type.compile(dialect=dialect) and not boolean_alias)
            or actual['nullable'] != expected.nullable
            or actual.get('default') is not None
            or actual.get('computed') or actual.get('identity')):
        _mismatch()
    # Historical string identity and all other fields do not generate values.
    if dialect.name == 'mysql' and actual.get('autoincrement', False) is not False:
        _mismatch()


def _validate_identity(bind, inspector, table):
    if inspector.get_pk_constraint(table.name)['constrained_columns'] != ['id']:
        _mismatch()
    columns = {column['name']: column for column in inspector.get_columns(table.name)}
    _validate_column(columns.get('id'), table.c.id, bind.dialect)
    if bind.dialect.name == 'sqlite':
        load_python_file(str(Path(__file__).parent), 'historical_sqlite_pk.py').validate_primary_key(
            bind, table, _mismatch)
    elif bind.dialect.name == 'mysql':
        # MySQL's portable PK reflection reports the column name but drops a
        # prefix length, so inspect the real SHOW CREATE key definition too.
        try:
            ddl = bind.exec_driver_sql(f'SHOW CREATE TABLE `{table.name}`').one()[1]
            parser = MySQLTableDefinitionParser(bind.dialect, bind.dialect.identifier_preparer)
            keys = [key for key in parser.parse(ddl, None).keys if key['type'] == 'PRIMARY']
            if len(keys) != 1 or keys[0]['columns'] != [('id', None, '')]:
                _mismatch()
        except (IndexError, KeyError, TypeError, ValueError):
            _mismatch()
    return columns


def _validate_table(bind, inspector, table):
    columns = _validate_identity(bind, inspector, table)
    if set(columns) != set(table.c.keys()) or inspector.get_check_constraints(table.name):
        _mismatch()
    for expected in table.columns:
        _validate_column(columns[expected.name], expected, bind.dialect)
    expected_fks = {(fk.parent.name, fk.column.table.name, fk.column.name)
                    for fk in table.foreign_keys}
    foreign_keys = inspector.get_foreign_keys(table.name)
    if len(foreign_keys) != len(expected_fks):
        _mismatch()
    for fk in foreign_keys:
        options = fk.get('options', {})
        if (len(fk['constrained_columns']) != 1 or len(fk['referred_columns']) != 1
                or (fk['constrained_columns'][0], fk['referred_table'], fk['referred_columns'][0])
                not in expected_fks
                or fk.get('referred_schema') not in (None, inspector.default_schema_name)
                or options.get('ondelete', '').upper() != 'CASCADE'
                or options.get('onupdate', 'NO ACTION').upper() != 'NO ACTION'
                or options.get('deferrable') or options.get('initially')
                or options.get('match', 'NONE').upper() != 'NONE'):
            _mismatch()
    expected_indexes = {index.name: [column.name for column in index.columns]
                        for index in table.indexes}
    if bind.dialect.name == 'sqlite':
        # Reflection drops column collations and can omit expression indexes.
        ddl = bind.execute(sa.text(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = :table"),
            {'table': table.name}).scalar_one()
        tokens = [token.upper() for token in re.findall(
            r'''--[^\r\n]*|/\*.*?\*/|'(?:''|[^'])*'|"(?:""|[^"])*"|`(?:``|[^`])*`|\[[^\]]*\]|[A-Za-z_][A-Za-z_0-9$]*|\S''',
            ddl, re.DOTALL) if not token.startswith(('--', '/*'))]
        if 'DEFERRABLE' in tokens or 'INITIALLY' in tokens:
            _mismatch()
        # SQLAlchemy's SQLite FK parser can stop at a comment and omit later
        # ON UPDATE clauses. PRAGMA reports the actual referential actions.
        raw_fks = bind.execute(sa.text('SELECT * FROM pragma_foreign_key_list(:table)'),
                               {'table': table.name}).mappings().all()
        if (len(raw_fks) != 1 or raw_fks[0]['seq'] != 0
                or raw_fks[0]['table'] != 'projects'
                or raw_fks[0]['from'] != 'project_id' or raw_fks[0]['to'] != 'id'
                or raw_fks[0]['on_delete'].upper() != 'CASCADE'
                or raw_fks[0]['on_update'].upper() != 'NO ACTION'
                or raw_fks[0]['match'].upper() != 'NONE'):
            _mismatch()
        for offset, token in enumerate(tokens):
            if token == 'COLLATE':
                collation = tokens[offset + 1]
                if collation[:1] in ('"', "'", '`', '['):
                    collation = collation[1:-1]
                if collation != 'BINARY':
                    _mismatch()
        inventory = bind.execute(sa.text('SELECT * FROM pragma_index_list(:table)'),
                                 {'table': table.name}).mappings().all()
        if any(index['origin'] == 'u' for index in inventory):
            _mismatch()
        ordinary = [index for index in inventory if index['origin'] != 'pk']
        if {index['name'] for index in ordinary} != set(expected_indexes):
            _mismatch()
        for index in ordinary:
            if index['unique'] or index['partial'] or index['origin'] != 'c':
                _mismatch()
            keys = bind.execute(sa.text(
                'SELECT name, "desc", coll FROM pragma_index_xinfo(:name) WHERE key = 1'),
                {'name': index['name']}).all()
            if [(name, order, coll.lower() if isinstance(coll, str) else coll)
                    for name, order, coll in keys] != [
                        (name, 0, 'binary') for name in expected_indexes[index['name']]]:
                _mismatch()
    if inspector.get_unique_constraints(table.name):
        _mismatch()
    indexes = inspector.get_indexes(table.name)
    if len(indexes) != len(expected_indexes):
        _mismatch()
    for index in indexes:
        if (index['name'] not in expected_indexes
                or index['column_names'] != expected_indexes[index['name']]
                or index['unique'] or index.get('dialect_options') or index.get('column_sorting')):
            _mismatch()


def ensure(bind):
    """Validate parent and both children before any write; never commit."""
    if not isinstance(bind, sa.engine.Connection):
        raise RuntimeError('Historical schema validation requires an explicit online connection.')
    if bind.dialect.name not in ('sqlite', 'mysql'):
        _mismatch()
    parent, tables = _tables()
    inspector = sa.inspect(bind)
    existing = set(inspector.get_table_names())
    views = set(inspector.get_view_names())
    for table in (parent, *tables):
        names = (table.name, *(index.name for index in table.indexes))
        if bind.dialect.name == 'sqlite':
            for name in names:
                if bind.execute(sa.text(
                    'SELECT 1 FROM sqlite_temp_master WHERE name = :name COLLATE NOCASE '
                    "AND type IN ('table', 'view', 'index') LIMIT 1"), {'name': name}).first():
                    _mismatch()
                objects = bind.execute(sa.text(
                    'SELECT name, type, tbl_name FROM sqlite_master WHERE name = :name COLLATE NOCASE'),
                    {'name': name}).all()
                owner = table.name
                kind = 'table' if name == table.name else 'index'
                if objects and objects != [(name, kind, owner)]:
                    _mismatch()
        if table.name in views or (table.name not in existing and inspector.has_table(table.name)):
            _mismatch()
        if any(name.lower() == table.name.lower() and name != table.name
               for name in existing | views):
            _mismatch()
    if parent.name not in existing:
        _mismatch()
    _validate_identity(bind, inspector, parent)
    present = {table.name for table in tables} & existing
    if present and len(present) != len(tables):
        _mismatch()
    for table in tables:
        if table.name in present:
            _validate_table(bind, inspector, table)
    for table in tables:
        if table.name not in present:
            table.create(bind, checkfirst=False)


def refuse_downgrade():
    raise RuntimeError('Cannot safely downgrade historical glossary prerequisites; '
                       'restore a verified backup instead.')
