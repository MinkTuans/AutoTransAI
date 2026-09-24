"""Validate historical project foreign keys without rebuilding populated tables.

Revision ID: 20260918_add_fk
Revises: 20260916_glossary_single_source
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '20260918_add_fk'
down_revision: Union[str, None] = '20260916_glossary_single_source'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _mismatch() -> None:
    raise RuntimeError('Historical schema mismatch: inspect the foreign key tables and '
                       'reconcile from a verified backup before retrying.')


def _require_fk(bind, inspector, table, column, parent):
    columns = {item['name'] for item in inspector.get_columns(table)}
    if column not in columns:
        _mismatch()
    matches = [fk for fk in inspector.get_foreign_keys(table)
               if column in fk['constrained_columns']]
    if (len(matches) != 1 or matches[0]['constrained_columns'] != [column]
            or matches[0]['referred_table'] != parent
            or matches[0]['referred_columns'] != ['id']
            or matches[0].get('referred_schema') not in (None, inspector.default_schema_name)):
        _mismatch()
    if bind.dialect.name == 'sqlite':
        # SQLite's reflected FK parser can miss actions after SQL comments.
        raw = bind.execute(sa.text('SELECT * FROM pragma_foreign_key_list(:table)'),
                           {'table': table}).mappings().all()
        actual = [fk for fk in raw if fk['from'] == column]
        if (len(actual) != 1 or actual[0]['seq'] != 0
                or actual[0]['table'] != parent or actual[0]['to'] != 'id'
                or actual[0]['on_delete'].upper() != 'CASCADE'
                or actual[0]['on_update'].upper() != 'NO ACTION'):
            _mismatch()
    elif (matches[0].get('options', {}).get('ondelete', '').upper() != 'CASCADE'
          or matches[0].get('options', {}).get('onupdate', 'NO ACTION').upper()
          != 'NO ACTION'):
        _mismatch()


def upgrade() -> None:
    if op.get_context().as_sql:
        raise RuntimeError('Historical schema validation requires an explicit online connection.')
    bind = op.get_bind()
    if bind.dialect.name not in ('sqlite', 'mysql'):
        _mismatch()
    inspector = sa.inspect(bind)
    names = set(inspector.get_table_names())
    views = set(inspector.get_view_names())
    reserved = {'projects', 'segments', 'jobs', 'assets', 'video_edit_configs',
                'workflow_engine'}
    if any(name.lower() in reserved and name not in reserved for name in names | views):
        _mismatch()
    if ({'projects', 'segments'} - names or 'workflow_engine' in names | views
            or {'jobs', 'assets', 'video_edit_configs', 'projects', 'segments'} & views):
        _mismatch()
    required = [('segments', 'project_id', 'projects')]
    for table in ('jobs', 'assets'):
        if table in names:
            required.append((table, 'project_id', 'projects'))
    if 'video_edit_configs' in names:
        if 'jobs' not in names:
            _mismatch()
        required.extend([('video_edit_configs', 'project_id', 'projects'),
                         ('video_edit_configs', 'job_id', 'jobs')])
    for table, column, parent in required:
        _require_fk(bind, inspector, table, column, parent)
        if bind.execute(sa.text(
            f'SELECT 1 FROM {table} AS child LEFT JOIN {parent} AS parent '
            f'ON child.{column} = parent.id '
            f'WHERE child.{column} IS NOT NULL AND parent.id IS NULL LIMIT 1')).first():
            _mismatch()
    if bind.dialect.name == 'sqlite':
        for table in {item[0] for item in required}:
            if bind.execute(sa.text('SELECT 1 FROM pragma_foreign_key_check(:table) LIMIT 1'),
                            {'table': table}).first():
                _mismatch()


def downgrade() -> None:
    raise RuntimeError('Cannot safely downgrade historical foreign keys; '
                       'restore a verified backup instead.')
