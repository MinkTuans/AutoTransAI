"""add tiktok_accounts for Login Kit OAuth

Revision ID: 20260915_tiktok_accounts
Revises: 20260908_workflow_progress
Create Date: 2026-09-15 12:30:00.000000

"""
import re

from alembic import op
import sqlalchemy as sa

revision = "20260915_tiktok_accounts"
down_revision = "20260908_workflow_progress"
branch_labels = None
depends_on = None


def _table():
    # Frozen from first publication 1ebccbb; never import mutable ORM metadata.
    table = sa.Table(
        "tiktok_accounts",
        sa.MetaData(),
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("open_id", sa.String(length=128), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=False, server_default="TikTok"),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("credentials_json", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    sa.Index("ix_tiktok_accounts_open_id", table.c.open_id, unique=True)
    return table


def _mismatch():
    raise RuntimeError('Historical schema mismatch: inspect the TikTok table and index '
                       'definitions and reconcile the schema from a backup before retrying.')


def _validate_sqlite_primary_key(bind, indexes):
    primary = [index for index in indexes if index['origin'] == 'pk']
    if len(primary) != 1 or primary[0]['unique'] != 1 or primary[0]['partial'] != 0:
        _mismatch()
    keys = bind.execute(sa.text(
        'SELECT name, "desc", coll FROM pragma_index_xinfo(:name) WHERE key = 1'),
        {'name': primary[0]['name']}).all()
    if keys != [('id', 0, 'BINARY')]:
        _mismatch()
    # SQLite reflection omits ON CONFLICT. Both frozen profiles use ABORT for
    # every constraint; explicit ABORT is equivalent, all other policies differ.
    ddl = bind.execute(sa.text(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'tiktok_accounts'"
    )).scalar_one()
    # Scan only conflict-clause keywords in this already-valid table DDL. Keep
    # quoted strings/identifiers as opaque tokens and discard SQL comments, so
    # their contents cannot impersonate or conceal an active conflict clause.
    tokens = [token.upper() for token in re.findall(
        r'''--[^\r\n]*|/\*.*?\*/|'(?:''|[^'])*'|"(?:""|[^"])*"|`(?:``|[^`])*`|\[[^\]]*\]|[A-Za-z_][A-Za-z_0-9$]*|\S''',
        ddl, re.DOTALL) if not token.startswith(('--', '/*'))]
    for offset in range(len(tokens) - 1):
        if tokens[offset:offset + 2] == ['ON', 'CONFLICT']:
            if tokens[offset + 2:offset + 3] != ['ABORT']:
                _mismatch()


def _validate_existing(bind, inspector, table):
    columns = {column['name']: column for column in inspector.get_columns(table.name)}
    if (set(columns) != set(table.c.keys())
            or inspector.get_pk_constraint(table.name)['constrained_columns'] != ['id']
            or inspector.get_foreign_keys(table.name)
            or inspector.get_check_constraints(table.name)):
        _mismatch()
    # 1ebccbb startup has Python-only defaults and NOT NULL timestamps.
    # Accept complete proven profiles, not arbitrary mixtures of the two.
    startup = all(not columns[name]['nullable'] for name in ('created_at', 'updated_at'))
    for expected in table.columns:
        actual = columns[expected.name]
        kind = actual['type'].compile(dialect=bind.dialect)
        boolean_alias = (bind.dialect.name == 'mysql' and isinstance(expected.type, sa.Boolean)
                         and kind == 'TINYINT(1)')
        nullable = False if startup and expected.name in ('created_at', 'updated_at') else expected.nullable
        if ((kind != expected.type.compile(dialect=bind.dialect) and not boolean_alias)
                or actual['nullable'] != nullable
                or actual.get('computed') or actual.get('identity')):
            _mismatch()
        defaults = {None}
        if not startup and expected.name == 'display_name':
            defaults = {"'TikTok'"}
        elif not startup and expected.name == 'is_active':
            defaults = {'1', "'1'", 'true'}
        default = actual.get('default')
        if (str(default).strip() if default is not None else None) not in defaults:
            _mismatch()
    if bind.dialect.name == 'sqlite':
        # Reflection skips expression indexes; inventory first so none are hidden.
        indexes = bind.exec_driver_sql('PRAGMA index_list(tiktok_accounts)').mappings().all()
        _validate_sqlite_primary_key(bind, indexes)
        ordinary = [index for index in indexes if index['origin'] != 'pk']
        if (len(ordinary) != 1 or ordinary[0]['name'] != 'ix_tiktok_accounts_open_id'
                or ordinary[0]['unique'] != 1 or ordinary[0]['partial'] != 0):
            _mismatch()
        keys = bind.exec_driver_sql('PRAGMA index_xinfo(ix_tiktok_accounts_open_id)').mappings()
        if [(key['name'], key['desc'], key['coll']) for key in keys if key['key']] != [
                ('open_id', 0, 'BINARY')]:
            _mismatch()
    indexes = inspector.get_indexes(table.name)
    if (len(indexes) != 1 or indexes[0]['name'] != 'ix_tiktok_accounts_open_id'
            or indexes[0]['column_names'] != ['open_id'] or not indexes[0]['unique']
            or indexes[0].get('dialect_options') or indexes[0].get('column_sorting')):
        _mismatch()
    # MySQL reflects a unique index as a duplicate unique constraint.
    for constraint in inspector.get_unique_constraints(table.name):
        if (bind.dialect.name != 'mysql'
                or constraint.get('duplicates_index') != 'ix_tiktok_accounts_open_id'
                or constraint['column_names'] != ['open_id']):
            _mismatch()


def upgrade() -> None:
    if op.get_context().as_sql:
        raise RuntimeError('Historical schema validation requires an explicit online connection.')
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table = _table()
    existing = set(inspector.get_table_names())
    if table.name in inspector.get_view_names():
        _mismatch()
    if table.name in existing:
        _validate_existing(bind, inspector, table)
        return
    # has_table delegates alias/case resolution to the actual dialect.
    if inspector.has_table(table.name):
        _mismatch()
    if bind.dialect.name == 'sqlite':
        # SQLite index names are global; reject either name before table DDL.
        for name in (table.name, 'ix_tiktok_accounts_open_id'):
            if bind.execute(sa.text(
                    "SELECT 1 FROM sqlite_master WHERE name = :name COLLATE NOCASE "
                    "AND type IN ('table', 'view', 'index') LIMIT 1"), {'name': name}).first():
                _mismatch()
    table.create(bind, checkfirst=False)


def downgrade() -> None:
    raise RuntimeError('Cannot safely downgrade historical TikTok schema; '
                       'restore a verified backup instead.')
