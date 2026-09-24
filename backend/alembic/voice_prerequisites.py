"""Frozen pre-timeline prerequisites; not yet wired into a published revision.

Source: 8ae030a^, models/workflow_engine.py::SpeakerVoiceMapping and
models/video_translator.py::VideoTranslationSegment. Non-Optional attributes
are NOT NULL; Python defaults/onupdate are deliberately not SQL defaults.
Parent identities are unchanged from D1; their other fields belong to earlier
links. Never import application ORM/configuration or run DDL at import time.
"""
from pathlib import Path
import re

from alembic.util import load_python_file
import sqlalchemy as sa


def _tables():
    metadata = sa.MetaData()
    parents = tuple(sa.Table(name, metadata, sa.Column('id', sa.String(36), primary_key=True))
                    for name in ('projects', 'video_translation_jobs'))
    mappings = sa.Table(
        'speaker_voice_mappings', metadata,
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('speaker_id', sa.String(100), nullable=False),
        sa.Column('speaker_name', sa.String(100)),
        sa.Column('voice_provider', sa.String(50), nullable=False),
        sa.Column('voice_id', sa.String(100), nullable=False),
        sa.Column('voice_settings', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    segments = sa.Table(
        'video_translation_segments', metadata,
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('job_id', sa.String(36),
                  sa.ForeignKey('video_translation_jobs.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('segment_number', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.Float(), nullable=False),
        sa.Column('end_time', sa.Float(), nullable=False),
        sa.Column('original_text', sa.Text(), nullable=False),
        sa.Column('translated_text', sa.Text(), nullable=False),
        sa.Column('tts_audio_path', sa.String(500)),
        sa.Column('tts_audio_duration', sa.Float()),
        sa.Column('synced_audio_path', sa.String(500)),
        sa.Column('status', sa.String(30), nullable=False),
    )
    return parents, (mappings, segments)


def _mismatch():
    raise RuntimeError('Historical schema mismatch: inspect the voice prerequisite table and index '
                       'definitions and reconcile the schema from a backup before retrying.')


def _validate_column(actual, expected, dialect):
    if (actual is None or actual['type'].compile(dialect=dialect) != expected.type.compile(dialect=dialect)
            or actual['nullable'] != expected.nullable or actual.get('default') is not None
            or actual.get('computed') or actual.get('identity')):
        _mismatch()


def _validate_identity(bind, inspector, table):
    if inspector.get_pk_constraint(table.name)['constrained_columns'] != ['id']:
        _mismatch()
    columns = {column['name']: column for column in inspector.get_columns(table.name)}
    _validate_column(columns.get('id'), table.c.id, bind.dialect)
    if bind.dialect.name == 'sqlite':
        load_python_file(str(Path(__file__).parent), 'historical_sqlite_pk.py').validate_primary_key(
            bind, table, _mismatch)
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
    expected_indexes = {index.name: [column.name for column in index.columns] for index in table.indexes}
    if bind.dialect.name == 'sqlite':
        # Reflection omits column collations. An explicit BINARY index can hide
        # a NOCASE column, so check declarations independently of index keys.
        ddl = bind.execute(sa.text(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = :table"),
            {'table': table.name}).scalar_one()
        tokens = [token.upper() for token in re.findall(
            r'''--[^\r\n]*|/\*.*?\*/|'(?:''|[^'])*'|"(?:""|[^"])*"|`(?:``|[^`])*`|\[[^\]]*\]|[A-Za-z_][A-Za-z_0-9$]*|\S''',
            ddl, re.DOTALL) if not token.startswith(('--', '/*'))]
        for offset, token in enumerate(tokens):
            if token == 'COLLATE':
                collation = tokens[offset + 1]
                if collation[:1] in ('"', "'", '`', '['):
                    collation = collation[1:-1]
                if collation != 'BINARY':
                    _mismatch()
        # Reflection can omit expression indexes. Check the complete inventory
        # and index keys first, including collation, sort order and predicates.
        indexes = bind.execute(sa.text('SELECT * FROM pragma_index_list(:table)'),
                               {'table': table.name}).mappings().all()
        ordinary = [index for index in indexes if index['origin'] != 'pk']
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
    elif inspector.get_unique_constraints(table.name):
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
    """Validate the complete group and existing parents, then create absent children.

    Only both-absent and both-compatible states have established provenance.
    A single surviving table is ambiguous and requires backup reconciliation.
    This helper never commits, rebuilds tables, or updates existing rows.
    """
    if not isinstance(bind, sa.engine.Connection):
        raise RuntimeError('Historical schema validation requires an explicit online connection.')
    if bind.dialect.name not in ('sqlite', 'mysql'):
        _mismatch()
    parents, tables = _tables()
    inspector = sa.inspect(bind)
    if bind.dialect.name == 'sqlite':
        # Temporary relations resolve before main-schema relations. Reject
        # shadows before any unqualified identity or table inspection.
        for table in (*parents, *tables):
            for name in (table.name, *(index.name for index in table.indexes)):
                if bind.execute(sa.text(
                        'SELECT 1 FROM sqlite_temp_master WHERE name = :name COLLATE NOCASE '
                        "AND type IN ('table', 'view', 'index') LIMIT 1"), {'name': name}).first():
                    _mismatch()
    existing = set(inspector.get_table_names())
    views = set(inspector.get_view_names())
    for table in (*parents, *tables):
        if table.name in views or (table.name not in existing and inspector.has_table(table.name)):
            _mismatch()
    for parent in parents:
        if parent.name not in existing:
            _mismatch()
        _validate_identity(bind, inspector, parent)
    present = {table.name for table in tables} & existing
    if present and len(present) != len(tables):
        _mismatch()
    for table in tables:
        if table.name in present:
            _validate_table(bind, inspector, table)
        elif bind.dialect.name == 'sqlite':
            # SQLite names are database-global, including indexes created after
            # each table. Inspect the whole group before its first CREATE.
            for name in (table.name, *(index.name for index in table.indexes)):
                if bind.execute(sa.text(
                        'SELECT 1 FROM sqlite_master WHERE name = :name COLLATE NOCASE '
                        "AND type IN ('table', 'view', 'index') LIMIT 1"), {'name': name}).first():
                    _mismatch()
    # Both existing parents were validated first; the children are independent.
    for table in tables:
        if table.name not in present:
            table.create(bind, checkfirst=False)


def refuse_downgrade():
    raise RuntimeError('Cannot safely downgrade historical voice prerequisites; '
                       'restore a verified backup instead.')
