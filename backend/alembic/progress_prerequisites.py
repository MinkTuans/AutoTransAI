"""Frozen prerequisites shared only by the two 20260908 progress revisions.

Source: eec0ef5 (ead6ad9 parent), models/video_editor.py and workflow_engine.py.
The four table definitions also match 9a4e0bb. Non-Optional mapped attributes
are NOT NULL, and Python defaults are deliberately not SQL server defaults.
Do not replace these definitions with imports from the application's ORM.
"""
from pathlib import Path

from alembic import op
from alembic.util import load_python_file
import sqlalchemy as sa


def _tables():
    # Reuse the already-frozen first-link project definition for its FK contract.
    initial = load_python_file(str(Path(__file__).parent / 'versions'),
                               '202da08bcdd8_initial_schema.py')
    projects = initial._prerequisites()[0]
    metadata = projects.metadata
    channels = sa.Table(
        'youtube_channels', metadata,
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('channel_name', sa.String(200), nullable=False),
        sa.Column('channel_id', sa.String(100)),
        sa.Column('credentials_json', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    publications = sa.Table(
        'youtube_publications', metadata,
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('job_id', sa.String(36), index=True),
        sa.Column('channel_id', sa.String(36),
                  sa.ForeignKey('youtube_channels.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('tags_json', sa.Text()),
        sa.Column('category_id', sa.String(20), nullable=False),
        sa.Column('thumbnail_path', sa.String(500)),
        sa.Column('privacy_status', sa.String(20), nullable=False),
        sa.Column('scheduled_publish_time', sa.DateTime()),
        sa.Column('youtube_video_id', sa.String(100)),
        sa.Column('youtube_url', sa.Text()),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('error_message', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    executions = sa.Table(
        'workflow_executions', metadata,
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('workflow_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(30), nullable=False),
        sa.Column('current_stage', sa.String(50)),
        sa.Column('current_step', sa.String(50)),
        sa.Column('context_data', sa.JSON()),
        sa.Column('error_message', sa.Text()),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime()),
    )
    stages = sa.Table(
        'workflow_stage_executions', metadata,
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workflow_execution_id', sa.String(36),
                  sa.ForeignKey('workflow_executions.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('stage_name', sa.String(50), nullable=False),
        sa.Column('status', sa.String(30), nullable=False),
        sa.Column('error', sa.Text()),
        sa.Column('qc_report', sa.JSON()),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    return projects, (channels, publications), (executions, stages)


def _additions():
    # Exact published migration defaults/nullability, not evolving ORM fields.
    return {
        'youtube_publications': [
            sa.Column('progress', sa.Integer(), server_default='0', nullable=False)],
        'workflow_executions': [
            sa.Column('overall_progress_pct', sa.Integer(), server_default='0', nullable=False)],
        'workflow_stage_executions': [
            sa.Column('progress_percentage', sa.Integer(), server_default='0', nullable=False),
            sa.Column('current_item', sa.Integer(), server_default='0', nullable=False),
            sa.Column('total_items', sa.Integer(), server_default='0', nullable=False),
            sa.Column('message', sa.String(255), nullable=True)],
    }


def _mismatch():
    raise RuntimeError('Historical schema mismatch: inspect the progress-link table definitions '
                       'and reconcile the schema from a backup before retrying.')


def _validate_column(actual, expected, dialect):
    actual_type = actual['type'].compile(dialect=dialect)
    boolean_alias = (dialect.name == 'mysql' and isinstance(expected.type, sa.Boolean)
                     and actual_type == 'TINYINT(1)')
    if ((actual_type != expected.type.compile(dialect=dialect) and not boolean_alias)
            or actual['nullable'] != expected.nullable
            or bool(actual.get('primary_key')) != expected.primary_key
            or actual.get('computed') or actual.get('identity')):
        _mismatch()
    # ead6ad9 startup-created progress has no server default; migration-created
    # progress has zero. Compare complete literals, never strip literal contents.
    allowed_defaults = {None}
    if expected.server_default is not None:
        allowed_defaults |= {'0', "'0'"}
    default = actual.get('default')
    if (str(default).strip() if default is not None else None) not in allowed_defaults:
        _mismatch()


def _validate_table(inspector, table, additions, dialect):
    columns = {column['name']: column for column in inspector.get_columns(table.name)}
    if inspector.get_pk_constraint(table.name)['constrained_columns'] != ['id']:
        _mismatch()
    for expected in table.columns:
        if expected.name not in columns:
            _mismatch()
        _validate_column(columns[expected.name], expected, dialect)
    optional = list(additions)
    # Added alongside progress by ead6ad9 startup, but not by this revision.
    if table.name == 'youtube_publications':
        optional.append(sa.Column('project_id', sa.String(36)))
    for expected in optional:
        if expected.name in columns:
            _validate_column(columns[expected.name], expected, dialect)
    if table.name != 'projects' and set(columns) - {
            column.name for column in (*table.columns, *optional)}:
        _mismatch()
    expected_fks = {(fk.parent.name, fk.column.table.name, fk.column.name)
                    for fk in table.foreign_keys}
    actual_fks = inspector.get_foreign_keys(table.name)
    if len(actual_fks) != len(expected_fks):
        _mismatch()
    for fk in actual_fks:
        options = fk.get('options', {})
        if (len(fk['constrained_columns']) != 1 or len(fk['referred_columns']) != 1
                or (fk['constrained_columns'][0], fk['referred_table'], fk['referred_columns'][0])
                not in expected_fks
                or fk.get('referred_schema') not in (None, inspector.default_schema_name)
                or options.get('ondelete', '').upper() != 'CASCADE'
                or options.get('onupdate', 'NO ACTION').upper() != 'NO ACTION'
                or options.get('deferrable')):
            _mismatch()
    indexes = inspector.get_indexes(table.name)
    for index in table.indexes:
        if not any(i['column_names'] == [c.name for c in index.columns]
                   and bool(i['unique']) == bool(index.unique) for i in indexes):
            _mismatch()


def upgrade_group(group):
    """Preflight both groups before any write, then create/add only this group.

    Entirely absent historical groups are supported; partial groups require
    reconciliation. No table rebuild, row update, or guessed schema repair.
    """
    if op.get_context().as_sql:
        raise RuntimeError('Historical schema validation requires an explicit online connection.')
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    projects, youtube, workflow = _tables()
    groups = {'youtube': youtube, 'workflow': workflow}
    additions = _additions()
    existing = set(inspector.get_table_names())
    views = set(inspector.get_view_names())
    if ({projects.name, *(t.name for t in (*youtube, *workflow))} & views
            or projects.name not in existing):
        _mismatch()
    _validate_table(inspector, projects, [], bind.dialect)
    for tables in groups.values():
        names = {table.name for table in tables}
        if names & existing and not names <= existing:
            _mismatch()
        for table in tables:
            if table.name in existing:
                _validate_table(inspector, table, additions.get(table.name, []), bind.dialect)
    # All validation above is read-only. Parent-first ordering is explicit.
    for table in groups[group]:
        if table.name not in existing:
            table.create(bind, checkfirst=False)
            columns = set()
        else:
            columns = {c['name'] for c in inspector.get_columns(table.name)}
        for column in additions.get(table.name, []):
            if column.name not in columns:
                op.add_column(table.name, column)


def refuse_downgrade():
    raise RuntimeError('Cannot safely downgrade historical progress schema; '
                       'restore a verified backup instead.')
