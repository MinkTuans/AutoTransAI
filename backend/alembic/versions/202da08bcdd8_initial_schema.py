"""initial schema

Revision ID: 202da08bcdd8
Revises: 
Create Date: 2026-08-21 21:26:15.781128

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '202da08bcdd8'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _prerequisites() -> list[sa.Table]:
    """Frozen subset, never import the application's evolving ORM or settings.

    Source: 2728d1a:backend/app/models/{project,segment,video_translator}.py.
    projects is unchanged from fd68d6d; segments already has its error columns.
    Only the four tables required by 20260822_sync_schema are reconstructed.
    Python ORM defaults are not server defaults and are intentionally omitted.
    """
    metadata = sa.MetaData()
    projects = sa.Table(
        'projects', metadata,
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('script_raw', sa.Text(), nullable=False),
        sa.Column('workflow_mode', sa.String(20), nullable=False),
        sa.Column('workflow_status', sa.String(30), nullable=False),
        sa.Column('audio_provider_id', sa.String(50)),
        sa.Column('video_provider_id', sa.String(50)),
        sa.Column('voice_id', sa.String(100)),
        sa.Column('voice_name', sa.String(100)),
        sa.Column('sync_strategy', sa.String(30), nullable=False),
        sa.Column('error_message', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    assets = sa.Table(
        'video_assets', metadata,
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('source_type', sa.String(20), nullable=False),
        sa.Column('source_url', sa.Text()),
        sa.Column('source_domain', sa.String(100)),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('original_filename', sa.String(255)),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('mime_type', sa.String(50)),
        sa.Column('file_size', sa.Integer()),
        sa.Column('duration', sa.Float()),
        sa.Column('width', sa.Integer()),
        sa.Column('height', sa.Integer()),
        sa.Column('audio_available', sa.Boolean(), nullable=False),
        sa.Column('status', sa.String(30), nullable=False),
        sa.Column('error_message', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    segments = sa.Table(
        'segments', metadata,
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('segment_number', sa.Integer(), nullable=False),
        sa.Column('text_content', sa.Text(), nullable=False),
        sa.Column('char_count', sa.Integer(), nullable=False),
        sa.Column('audio_status', sa.String(20), nullable=False),
        sa.Column('audio_duration', sa.Float()),
        sa.Column('audio_file_path', sa.String(500)),
        sa.Column('audio_error_message', sa.Text()),
        sa.Column('video_status', sa.String(20), nullable=False),
        sa.Column('video_duration', sa.Float()),
        sa.Column('video_file_path', sa.String(500)),
        sa.Column('video_error_message', sa.Text()),
        sa.Column('video_error_details', sa.Text()),
        sa.Column('target_duration', sa.Float()),
        sa.Column('sync_strategy_used', sa.String(30)),
        sa.Column('merged_file_path', sa.String(500)),
    )
    jobs = sa.Table(
        'video_translation_jobs', metadata,
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('asset_id', sa.String(36), sa.ForeignKey('video_assets.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('source_language', sa.String(20), nullable=False),
        sa.Column('detected_language', sa.String(20)),
        sa.Column('target_language', sa.String(20), nullable=False),
        sa.Column('audio_provider_id', sa.String(50)),
        sa.Column('voice_id', sa.String(100)),
        sa.Column('voice_name', sa.String(100)),
        sa.Column('original_audio_mode', sa.String(20), nullable=False),
        sa.Column('status', sa.String(30), nullable=False),
        sa.Column('progress_pct', sa.Float(), nullable=False),
        sa.Column('current_step', sa.String(100), nullable=False),
        sa.Column('output_video_path', sa.String(500)),
        sa.Column('error_message', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    return [projects, assets, segments, jobs]


def _mismatch() -> None:
    raise RuntimeError('Historical schema mismatch: inspect the first-link table definitions '
                       'and reconcile the schema from a backup before retrying.')


def upgrade() -> None:
    """Create a blank prerequisite subset, or validate known existing tables."""
    if op.get_context().as_sql:
        raise RuntimeError('Historical schema validation requires an explicit online connection.')
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = _prerequisites()
    names = {t.name for t in tables}
    existing = set(inspector.get_table_names()) - {'alembic_version'}
    views = set(inspector.get_view_names())
    # A partial installation needs operator reconciliation, never guessed repairs.
    # Views also make a database nonblank and may occupy a prerequisite name.
    if names & views or ((existing or views) and not names <= existing):
        _mismatch()
    for table in tables if existing else []:
        columns = {c['name']: c for c in inspector.get_columns(table.name)}
        if inspector.get_pk_constraint(table.name)['constrained_columns'] != ['id']:
            _mismatch()
        for expected in table.columns:
            actual = columns.get(expected.name)
            if actual is None:
                _mismatch()
            actual_type = actual['type'].compile(dialect=bind.dialect)
            expected_type = expected.type.compile(dialect=bind.dialect)
            # MySQL reflects SQLAlchemy Boolean as TINYINT(1).
            boolean_alias = (bind.dialect.name == 'mysql' and isinstance(expected.type, sa.Boolean)
                             and actual_type == 'TINYINT(1)')
            if ((actual_type != expected_type and not boolean_alias)
                    or actual['nullable'] != expected.nullable or actual.get('computed')):
                _mismatch()
        foreign_keys = inspector.get_foreign_keys(table.name)
        for fk in table.foreign_keys:
            if not any(key['constrained_columns'] == [fk.parent.name]
                       and key['referred_table'] == fk.column.table.name
                       and key['referred_columns'] == [fk.column.name]
                       and key.get('options', {}).get('ondelete', '').upper() == 'CASCADE'
                       for key in foreign_keys):
                _mismatch()
    if not existing:
        for table in tables:
            table.create(bind, checkfirst=False)


def downgrade() -> None:
    """Ownership of startup-created tables cannot be recovered safely."""
    raise RuntimeError('Cannot safely downgrade historical prerequisite tables; '
                       'restore a verified backup instead.')
