"""Frozen pre-catalog provider and legacy settings tables from 08ea050^."""
import hashlib
import re

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql.reflection import MySQLTableDefinitionParser


_CANONICAL = {'api_keys', 'ai_catalog_models', 'ai_key_model_access'}

# Exact SQLite DDL emitted by the startup ORM at this plan's cutover. Keeping
# these fingerprints here makes no-stamp startup adoption independent of mutable
# application models. Any schema drift fails closed before a catalog revision
# tries to create, alter, or overwrite an existing canonical table.
_STARTUP_SQLITE_DDL = {
    'providers': '1c45aee6e03ab458958aebc63ba490c48a58c4da376346c6ff2487bd47069a78',
    'ai_function_configs': 'd9833f7da4b7dd15a4a7ee1cf19d06a6a97160a8d39f2deabf3ae03518fc1fb9',
    'ai_models': 'e068ddf1e91c1fda6bd74f4aa5915d7282f5e35b692634e07852a9f1c98538a0',
    'api_keys': '86558a12db845fa36b7406f2f8d8e9bf952939079b38fa20d74f99c60a8d98e5',
    'ai_catalog_models': '85a9b8cfc423e74b49afae2e42cee6b9cd93b5490211c565501fb5b608e2f71b',
    'ai_key_model_access': '8266eb1e8603a2bdfc4c2109c8064604db5f96eeb10431f235ea6d32af37230b',
    'ai_catalog_refresh_runs': '349b26065ec88ccbc0f8c54490abe33241537ea4b63714834d3a0996c1520191',
}
_STARTUP_SQLITE_INDEX_DDL = {
    'ix_api_keys_provider_id': '4973f02052037d82256c941ede23b30730b1567539c2c6beb7cee068a46e332c',
    'ix_ai_catalog_models_provider_id': '3fd3cff6879c81bf6a0149982587e626c4d13d8fc9b9964861ce2b672db3b088',
    'ix_ai_key_model_access_model_id': 'fd304b79c3effdf7105ff4b134e0204e91f1bc7aa8801c10bf7fa7ca019234bc',
}
_STARTUP_SQLITE_AUTOINDEX_COUNTS = {
    'providers': 1, 'ai_function_configs': 1, 'ai_models': 1,
    'api_keys': 3, 'ai_catalog_models': 3, 'ai_key_model_access': 1,
    'ai_catalog_refresh_runs': 1,
}
_STARTUP_MYSQL_DDL = {
    # SHOW CREATE TABLE on a disposable MySQL 8.4 database created by the
    # startup ORM, using utf8mb4_0900_ai_ci. Other profiles refuse safely.
    'providers': 'd7d211c20b9e032271e9cad08cf5bee867130115d3855fdf7f8af609265fd7f0',
    'ai_function_configs': 'f9ed5adfc63f6120f19a0c537ccb08be47a174dde2ad3647e37096a8c2c70e7c',
    'ai_models': 'b0ecfde92a5992db762218b6c2651fa557f22358578f5c6b8b686f90db34226c',
    'api_keys': '7addc2c9c6d4824ea7896b4837b3fda9dafb22fd27ff56e0b97a5637be6ec63f',
    'ai_catalog_models': '465fdcce4a1ae2b882b89c78d11e2a980be8e5ad7269dd5c5554a01d9d058887',
    'ai_key_model_access': '9935e8206750c429695daa81a4bc2a8f5745a5cdb5d02863ba1067513f7d6270',
    'ai_catalog_refresh_runs': '72a7b4563260b0787f0bad138efc6a7da61fceb8424a1d98a44e7687d79a5f3e',
}


def is_startup_final(bind):
    """Accept only a complete frozen startup catalog, without writes."""
    if (not isinstance(bind, sa.engine.Connection)
            or bind.dialect.name not in ('sqlite', 'mysql')):
        return False
    inspector = sa.inspect(bind)
    names = set(inspector.get_table_names())
    if not _CANONICAL <= names:
        return False
    expected_names = set(_STARTUP_SQLITE_DDL)
    if not expected_names <= names:
        return False
    final_columns = {
        'providers': 'requires_api_key', 'ai_function_configs': 'configuration_error',
        'api_keys': 'priority', 'ai_catalog_models': 'discovery_metadata',
    }
    if any(column not in {item['name'] for item in inspector.get_columns(table)}
           for table, column in final_columns.items()):
        return False
    if any(name.lower() in expected_names and name not in expected_names
           for name in names | set(inspector.get_view_names())):
        _mismatch()
    if bind.dialect.name == 'mysql':
        if any(name in inspector.get_view_names() for name in expected_names):
            _mismatch()
        triggers = bind.execute(sa.text(
            'SELECT 1 FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=DATABASE() '
            'AND EVENT_OBJECT_TABLE IN ('
            + ','.join(f"'{name}'" for name in sorted(expected_names)) + ') LIMIT 1')).first()
        if triggers:
            _mismatch()
        for table, digest in _STARTUP_MYSQL_DDL.items():
            ddl = bind.exec_driver_sql(f'SHOW CREATE TABLE `{table}`').one()[1]
            if hashlib.sha256(ddl.encode()).hexdigest() != digest:
                _mismatch()
        for query in (
            'SELECT 1 FROM api_keys AS child LEFT JOIN providers AS parent '
            'ON parent.id=child.provider_id WHERE parent.id IS NULL LIMIT 1',
            'SELECT 1 FROM ai_catalog_models AS child LEFT JOIN providers AS parent '
            'ON parent.id=child.provider_id WHERE parent.id IS NULL LIMIT 1',
            'SELECT 1 FROM ai_key_model_access AS child LEFT JOIN api_keys AS parent '
            'ON parent.id=child.key_id AND parent.provider_id=child.provider_id '
            'WHERE parent.id IS NULL LIMIT 1',
            'SELECT 1 FROM ai_key_model_access AS child LEFT JOIN ai_catalog_models AS parent '
            'ON parent.id=child.model_id AND parent.provider_id=child.provider_id '
            'WHERE parent.id IS NULL LIMIT 1',
        ):
            if bind.execute(sa.text(query)).first():
                _mismatch()
        return True
    reserved = expected_names | set(_STARTUP_SQLITE_INDEX_DDL)
    if any(name.lower() in reserved for name in inspector.get_view_names()):
        _mismatch()
    if bind.execute(sa.text(
        "SELECT 1 FROM sqlite_temp_master WHERE lower(name) IN ("
        + ','.join(f"'{name}'" for name in sorted(reserved)) + ') LIMIT 1')).first():
        _mismatch()
    for table, digest in _STARTUP_SQLITE_DDL.items():
        objects = bind.execute(sa.text(
            "SELECT type, name, sql FROM sqlite_master WHERE tbl_name=:table "
            "AND type IN ('table', 'index', 'trigger')"), {'table': table}).all()
        expected = {('table', table)}
        expected |= {('index', f'sqlite_autoindex_{table}_{i}')
                     for i in range(1, _STARTUP_SQLITE_AUTOINDEX_COUNTS[table] + 1)}
        expected |= {('index', name) for name in _STARTUP_SQLITE_INDEX_DDL
                     if name.startswith('ix_' + table + '_')}
        if {(kind, name) for kind, name, _ in objects} != expected:
            _mismatch()
        for kind, name, sql in objects:
            known = digest if kind == 'table' else _STARTUP_SQLITE_INDEX_DDL.get(name)
            if (sql is None and known is not None or sql is not None and
                    (known is None or hashlib.sha256(sql.encode()).hexdigest() != known)):
                _mismatch()
    for table in expected_names:
        if bind.execute(sa.text('SELECT 1 FROM pragma_foreign_key_check(:table) LIMIT 1'),
                        {'table': table}).first():
            _mismatch()
    return True


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
