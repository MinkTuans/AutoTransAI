"""Widen Alembic's MySQL version column before the first long revision ID."""
from copy import copy

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.dialects.mysql.reflection import MySQLTableDefinitionParser


def _mismatch():
    raise RuntimeError('Historical schema mismatch: inspect the Alembic version table '
                       'and reconcile from a verified backup before retrying.')


def ensure(bind, predecessor, revision):
    if bind.dialect.name != 'mysql':
        return
    context = op.get_context()
    if context.version_table_schema is not None:
        _mismatch()
    name = context.version_table
    inspector = sa.inspect(bind)
    if name not in inspector.get_table_names():
        # Direct revision-operation tests have no Alembic version table.
        return
    columns = inspector.get_columns(name)
    if (len(columns) != 1 or columns[0]['name'] != 'version_num'
            or type(columns[0]['type']) is not VARCHAR
            or columns[0]['type'].length not in (32, 64)
            or columns[0]['nullable'] or columns[0].get('default') is not None
            or columns[0].get('computed') or columns[0].get('identity')
            or inspector.get_pk_constraint(name)['constrained_columns'] != ['version_num']
            or inspector.get_foreign_keys(name) or inspector.get_check_constraints(name)
            or inspector.get_unique_constraints(name) or inspector.get_indexes(name)):
        _mismatch()
    quoted = bind.dialect.identifier_preparer.quote(name)
    ddl = bind.exec_driver_sql(f'SHOW CREATE TABLE {quoted}').one()[1]
    parser = MySQLTableDefinitionParser(bind.dialect, bind.dialect.identifier_preparer)
    keys = [key for key in parser.parse(ddl, None).keys if key['type'] == 'PRIMARY']
    if len(keys) != 1 or keys[0]['columns'] != [('version_num', None, '')]:
        _mismatch()
    rows = bind.exec_driver_sql(f'SELECT version_num FROM {quoted}').all()
    allowed = ({predecessor} if columns[0]['type'].length == 32
               else {predecessor, revision})
    if len(rows) != 1 or rows[0].version_num not in allowed:
        _mismatch()
    if columns[0]['type'].length == 64:
        return
    wider = copy(columns[0]['type'])
    wider.length = 64
    op.alter_column(name, 'version_num', type_=wider,
                    existing_type=columns[0]['type'], existing_nullable=False)
