"""sync model schema across video translation jobs, assets, projects, and segments

Revision ID: 20260822_sync_schema
Revises: 202da08bcdd8
Create Date: 2026-08-22 04:22:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260822_sync_schema'
down_revision: Union[str, Sequence[str], None] = '202da08bcdd8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add only missing columns; retain compatible startup-created equivalents.

    Definitions remain those published in 29cadc6. That commit's ORM also
    created these columns, often NOT NULL with Python rather than SQL defaults.
    Validate every target before any DDL; never rebuild a populated SQLite table.
    """
    if op.get_context().as_sql:
        raise RuntimeError('Historical schema validation requires an explicit online connection.')
    additions = {
        'video_translation_jobs': [
            sa.Column('llm_provider_id', sa.String(50), server_default='openai'),
            sa.Column('r2_key', sa.String(500)),
            sa.Column('output_url', sa.Text()),
            sa.Column('is_cleaned', sa.Boolean(), server_default='0'),
            sa.Column('stage', sa.String(50), server_default='QUEUED'),
            sa.Column('stage_progress_pct', sa.Float(), server_default='0.0'),
            sa.Column('overall_progress_pct', sa.Float(), server_default='0.0'),
            sa.Column('pid', sa.Integer()),
            sa.Column('last_heartbeat', sa.DateTime()),
            sa.Column('ffmpeg_stats_json', sa.Text()),
            sa.Column('completed_segments_count', sa.Integer(), server_default='0'),
            sa.Column('total_segments_count', sa.Integer(), server_default='0'),
        ],
        'video_assets': [sa.Column('r2_key', sa.String(500)), sa.Column('url', sa.Text())],
        'projects': [sa.Column('r2_key', sa.String(500)), sa.Column('media_url', sa.Text())],
        'segments': [sa.Column('audio_error_message', sa.Text()),
                     sa.Column('video_error_message', sa.Text()),
                     sa.Column('video_error_details', sa.Text())],
    }
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = set(inspector.get_table_names())
    missing = []
    orm_required = {'is_cleaned', 'stage', 'stage_progress_pct', 'overall_progress_pct',
                    'last_heartbeat', 'completed_segments_count', 'total_segments_count'}
    for table, expected_columns in additions.items():
        if table not in existing:
            _mismatch()
        columns = {c['name']: c for c in inspector.get_columns(table)}
        identity = columns.get('id')
        identity_type = sa.Integer() if table == 'segments' else sa.String(36)
        if (identity is None or identity['type'].compile(dialect=bind.dialect)
                != identity_type.compile(dialect=bind.dialect)
                or inspector.get_pk_constraint(table)['constrained_columns'] != ['id']):
            _mismatch()
        for expected in expected_columns:
            actual = columns.get(expected.name)
            if actual is None:
                missing.append((table, expected))
                continue
            actual_type = actual['type'].compile(dialect=bind.dialect)
            boolean_alias = (bind.dialect.name == 'mysql' and isinstance(expected.type, sa.Boolean)
                             and actual_type == 'TINYINT(1)')
            if ((actual_type != expected.type.compile(dialect=bind.dialect) and not boolean_alias)
                    or (not actual['nullable'] and expected.name not in orm_required)
                    or actual.get('computed') or actual.get('primary_key')):
                _mismatch()
            # Absent server defaults are known ORM-created equivalents. Present
            # defaults must agree with the published migration, never be rewritten.
            default = actual.get('default')
            if default is not None:
                allowed = ({str(expected.server_default.arg)} if expected.server_default else set())
                if allowed & {'0', '0.0'}:
                    allowed |= {'0', '0.0'}
                # Compare complete SQL literals; quote/parenthesis characters
                # inside a literal are data. Unknown expressions fail closed.
                allowed_sql = {"'" + value.replace("'", "''") + "'" for value in allowed}
                if isinstance(expected.type, (sa.Integer, sa.Float, sa.Boolean)):
                    allowed_sql |= allowed
                if str(default).strip() not in allowed_sql:
                    _mismatch()
    for table, column in missing:
        op.add_column(table, column)


def _mismatch() -> None:
    raise RuntimeError('Historical schema mismatch: inspect the first-link table definitions '
                       'and reconcile the schema from a backup before retrying.')


def downgrade() -> None:
    """Cannot distinguish columns created here from pre-existing ORM columns."""
    raise RuntimeError('Cannot safely downgrade historical sync columns; '
                       'restore a verified backup instead.')
