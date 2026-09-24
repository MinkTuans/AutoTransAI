"""Frozen pre-catalog provider and legacy settings tables from 08ea050^."""
import re

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql.reflection import MySQLTableDefinitionParser


_CANONICAL = {'api_keys', 'ai_catalog_models', 'ai_key_model_access'}


def _tables():
    metadata = sa.MetaData()
    provider = sa.Table(
        'providers', metadata,
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('provider_type', sa.String(20), nullable=False),
        sa.Column('quota_type', sa.String(50), nullable=False),
        sa.Column('quota_limit', sa.Integer()),
        sa.Column('quota_used_local', sa.Integer(), nullable=False),
        sa.Column('configured', sa.Boolean(), nullable=False),
        sa.Column('api_key_set', sa.Boolean(), nullable=False),
        sa.Column('last_verified', sa.DateTime()),
        sa.Column('capabilities', sa.Text()),
        sa.Column('supported', sa.Boolean(), nullable=False),
        sa.Column('is_custom', sa.Boolean(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('website_url', sa.String(255)),
        sa.Column('doc_url', sa.String(255)),
        sa.Column('base_url', sa.String(255)),
    )
    config = sa.Table(
        'ai_function_configs', metadata,
        sa.Column('function_id', sa.String(50), primary_key=True),
        sa.Column('function_name', sa.String(100), nullable=False),
        sa.Column('capability', sa.String(50), nullable=False),
        sa.Column('primary_provider_id', sa.String(50), nullable=False),
        sa.Column('model_id', sa.String(100), nullable=False),
        sa.Column('fallback_enabled', sa.Boolean(), nullable=False),
        sa.Column('fallback_provider_id', sa.String(50)),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    model = sa.Table(
        'ai_models', metadata,
        sa.Column('id', sa.String(100), primary_key=True),
        sa.Column('provider_id', sa.String(50), nullable=False),
        sa.Column('model_name', sa.String(100), nullable=False),
        sa.Column('capabilities', sa.Text(), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False),
        sa.Column('is_custom', sa.Boolean(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    return provider, config, model


def _mismatch():
    raise RuntimeError('Historical schema mismatch: inspect the legacy catalog tables '
                       'and reconcile from a verified backup before retrying.')


def _validate_table(bind, inspector, table):
    primary = next(column.name for column in table.primary_key.columns)
    columns = {item['name']: item for item in inspector.get_columns(table.name)}
    if (set(columns) != set(table.c.keys())
            or inspector.get_pk_constraint(table.name)['constrained_columns'] != [primary]
            or inspector.get_foreign_keys(table.name)
            or inspector.get_unique_constraints(table.name)
            or inspector.get_check_constraints(table.name)
            or inspector.get_indexes(table.name)):
        _mismatch()
    for expected in table.columns:
        actual = columns[expected.name]
        kind = actual['type'].compile(dialect=bind.dialect)
        boolean_alias = (bind.dialect.name == 'mysql' and isinstance(expected.type, sa.Boolean)
                         and kind == 'TINYINT(1)')
        if (kind != expected.type.compile(dialect=bind.dialect) and not boolean_alias
                or actual['nullable'] != expected.nullable
                or actual.get('default') is not None
                or actual.get('computed') or actual.get('identity')
                or (bind.dialect.name == 'mysql' and actual.get('autoincrement', False))):
            _mismatch()
    if bind.dialect.name == 'mysql':
        ddl = bind.exec_driver_sql(f'SHOW CREATE TABLE `{table.name}`').one()[1]
        parser = MySQLTableDefinitionParser(bind.dialect, bind.dialect.identifier_preparer)
        keys = [key for key in parser.parse(ddl, None).keys if key['type'] == 'PRIMARY']
        if len(keys) != 1 or keys[0]['columns'] != [(primary, None, '')]:
            _mismatch()
    else:
        indexes = bind.execute(sa.text('SELECT * FROM pragma_index_list(:table)'),
                               {'table': table.name}).mappings().all()
        if len(indexes) != 1 or indexes[0]['origin'] != 'pk':
            _mismatch()
        keys = bind.execute(sa.text(
            'SELECT name, "desc", coll FROM pragma_index_xinfo(:name) WHERE key = 1'),
            {'name': indexes[0]['name']}).all()
        if [(name, order, coll.lower() if isinstance(coll, str) else coll)
                for name, order, coll in keys] != [(primary, 0, 'binary')]:
            _mismatch()
        ddl = bind.execute(sa.text(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=:name"),
            {'name': table.name}).scalar_one()
        tokens = [token.upper() for token in re.findall(
            r'''--[^\r\n]*|/\*.*?\*/|'(?:''|[^'])*'|"(?:""|[^"])*"|`(?:``|[^`])*`|\[[^\]]*\]|[A-Za-z_][A-Za-z_0-9$]*|\S''',
            ddl, re.DOTALL) if not token.startswith(('--', '/*'))]
        if ('WITHOUT' in tokens or 'AUTOINCREMENT' in tokens or 'DESC' in tokens
                or any(tokens[i:i + 2] == ['ON', 'CONFLICT']
                       and tokens[i + 2:i + 3] != ['ABORT'] for i in range(len(tokens)))):
            _mismatch()
        for index, token in enumerate(tokens):
            if token == 'COLLATE' and tokens[index + 1].strip('`"[]\'') != 'BINARY':
                _mismatch()


def ensure(bind):
    if not isinstance(bind, sa.engine.Connection):
        if (not op.get_context().as_sql or getattr(bind, 'dialect', None) is None
                or bind.dialect.name not in ('sqlite', 'mysql')):
            _mismatch()
        # Preserve the historical offline contract: generated SQL assumes the
        # legacy group already exists. Online mode can inspect/create it.
        return
    if bind.dialect.name not in ('sqlite', 'mysql'):
        _mismatch()
    tables = _tables()
    expected = {table.name for table in tables}
    inspector = sa.inspect(bind)
    names = set(inspector.get_table_names())
    views = set(inspector.get_view_names())
    if any(name.lower() in _CANONICAL for name in names | views):
        _mismatch()
    if (expected & views or any(name.lower() in expected and name not in expected
                                for name in names | views)):
        _mismatch()
    present = names & expected
    if present not in (set(), expected):
        _mismatch()
    if present:
        for table in tables:
            _validate_table(bind, inspector, table)
        return
    for table in tables:
        table.create(bind, checkfirst=False)
