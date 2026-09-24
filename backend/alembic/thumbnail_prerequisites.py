"""Frozen VideoThumbnail schema from 08ea050^, before model identity widening."""
from pathlib import Path

from alembic.util import load_python_file
import sqlalchemy as sa


def _tables(length):
    metadata = sa.MetaData()
    parents = tuple(sa.Table(name, metadata, sa.Column('id', sa.String(36), primary_key=True))
                    for name in ('projects', 'video_translation_jobs', 'video_assets'))
    thumbnail = sa.Table(
        'video_thumbnails', metadata,
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'), index=True),
        sa.Column('job_id', sa.String(36), sa.ForeignKey('video_translation_jobs.id', ondelete='CASCADE'), index=True),
        sa.Column('asset_id', sa.String(36), sa.ForeignKey('video_assets.id', ondelete='CASCADE'), index=True),
        sa.Column('source_title', sa.String(255), nullable=False),
        sa.Column('source_description', sa.Text()),
        sa.Column('selected_style', sa.String(50), nullable=False),
        sa.Column('custom_instruction', sa.Text()),
        sa.Column('ai_analysis_json', sa.Text()),
        sa.Column('generated_prompt', sa.Text()),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('model', sa.String(length), nullable=False),
        sa.Column('r2_key', sa.String(500)),
        sa.Column('thumbnail_url', sa.Text()),
        sa.Column('width', sa.Integer(), nullable=False),
        sa.Column('height', sa.Integer(), nullable=False),
        sa.Column('aspect_ratio', sa.String(20), nullable=False),
        sa.Column('status', sa.String(30), nullable=False),
        sa.Column('error_message', sa.Text()),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    return parents, thumbnail


def _mismatch():
    raise RuntimeError('Historical schema mismatch: inspect the thumbnail table and '
                       'reconcile the schema from a verified backup before retrying.')


def _dependent_objects(bind):
    if bind.dialect.name == 'sqlite':
        # SQLite reparses every view during the batch table rename. Even a view
        # on another table can depend on this one through a nested view.
        views = bind.execute(sa.text(
            "SELECT 1 FROM sqlite_master WHERE type='view' LIMIT 1")).first()
        trigger = bind.execute(sa.text(
            "SELECT 1 FROM sqlite_master WHERE type='trigger' AND tbl_name='video_thumbnails' LIMIT 1"
        )).first()
        references = any(
            fk['referred_table'] == 'video_thumbnails'
            for name in sa.inspect(bind).get_table_names() if name != 'video_thumbnails'
            for fk in sa.inspect(bind).get_foreign_keys(name)
        )
        return bool(views or trigger or references)
    schema = bind.execute(sa.text('SELECT DATABASE()')).scalar_one()
    trigger = bind.execute(sa.text(
        'SELECT 1 FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=:schema '
        "AND EVENT_OBJECT_TABLE='video_thumbnails' LIMIT 1"), {'schema': schema}).first()
    reference = bind.execute(sa.text(
        'SELECT 1 FROM information_schema.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA=:schema '
        "AND REFERENCED_TABLE_NAME='video_thumbnails' LIMIT 1"), {'schema': schema}).first()
    return bool(trigger or reference)


def preflight(bind):
    """Return absent, historical or current after read-only schema validation."""
    voice = load_python_file(str(Path(__file__).parent), 'voice_prerequisites.py')
    parents, historical = _tables(100)
    _, current = _tables(255)
    try:
        inspector, present = voice.preflight_namespace(bind, parents, (historical,))
        if not present:
            return 'absent'
        columns = {column['name']: column for column in inspector.get_columns(historical.name)}
        model = columns.get('model')
        length = getattr(model['type'], 'length', None) if model else None
        if length not in (100, 255):
            _mismatch()
        voice._validate_table(bind, inspector, historical if length == 100 else current)
        if length == 100 and _dependent_objects(bind):
            _mismatch()
        return 'historical' if length == 100 else 'current'
    except RuntimeError:
        _mismatch()


def create_current(bind):
    _tables(255)[1].create(bind, checkfirst=False)
