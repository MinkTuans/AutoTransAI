"""Frozen pre-timeline prerequisites and shared voice schema preflight.

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
    kind = actual['type'].compile(dialect=dialect) if actual else None
    boolean_alias = dialect.name == 'mysql' and isinstance(expected.type, sa.Boolean) and kind == 'TINYINT(1)'
    if (actual is None or (kind != expected.type.compile(dialect=dialect) and not boolean_alias)
            or actual['nullable'] != expected.nullable
            or not _default_matches(actual.get('default'), expected, dialect)
            or actual.get('computed') or actual.get('identity')):
        _mismatch()
    # MySQL reflection distinguishes integer PKs that generate an omitted ID
    # from ordinary integer PKs. Only the frozen segment ID uses AUTO_INCREMENT;
    # noninteger columns may omit the reflected flag entirely.
    if (dialect.name == 'mysql'
            and actual.get('autoincrement', False) is not (expected.autoincrement is True)):
        _mismatch()


def _default_matches(actual, expected, dialect):
    if expected.server_default is None:
        return actual is None
    value = expected.server_default.arg
    literal = value if isinstance(value, str) else str(value.compile(dialect=dialect))
    if not isinstance(value, str) and literal in ('false', 'true'):
        literal = '0' if literal == 'false' else '1'
    # Only complete published literals and documented numeric/boolean SQL
    # equivalents. Never strip quotes/parentheses from inside a string value.
    forms = {repr(literal)}
    if literal in ('0', '1'):
        forms |= {literal, literal + '.0', repr(literal + '.0'),
                  'false' if literal == '0' else 'true', 'FALSE' if literal == '0' else 'TRUE'}
    forms |= {'(' + form + ')' for form in tuple(forms)}
    return actual is not None and str(actual).strip() in forms


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
    expected_uniques = {constraint.name: tuple(column.name for column in constraint.columns)
                        for constraint in table.constraints if isinstance(constraint, sa.UniqueConstraint)}
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
        unique_indexes = [index for index in indexes if index['origin'] == 'u']
        if len(unique_indexes) != len(expected_uniques):
            _mismatch()
        for index in unique_indexes:
            keys = bind.execute(sa.text(
                'SELECT name, "desc", coll FROM pragma_index_xinfo(:name) WHERE key = 1'),
                {'name': index['name']}).all()
            if (not index['unique'] or index['partial']
                    or tuple(name for name, _, _ in keys) not in expected_uniques.values()
                    or any(order or coll.lower() != 'binary' for _, order, coll in keys)):
                _mismatch()
        ordinary = [index for index in indexes if index['origin'] not in ('pk', 'u')]
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
    uniques = inspector.get_unique_constraints(table.name)
    if (len(uniques) != len(expected_uniques)
            or {item['name']: tuple(item['column_names']) for item in uniques} != expected_uniques):
        _mismatch()
    indexes = [index for index in inspector.get_indexes(table.name)
               if not (bind.dialect.name == 'mysql' and index['name'] in expected_uniques
                       and index['unique'] and tuple(index['column_names']) == expected_uniques[index['name']]
                       and not index.get('dialect_options') and not index.get('column_sorting'))]
    if len(indexes) != len(expected_indexes):
        _mismatch()
    for index in indexes:
        if (index['name'] not in expected_indexes
                or index['column_names'] != expected_indexes[index['name']]
                or index['unique'] or index.get('dialect_options') or index.get('column_sorting')):
            _mismatch()


def preflight_namespace(bind, parents, tables):
    """Read-only relation/index inventory and parent identities, shared by B1/B2."""
    if not isinstance(bind, sa.engine.Connection):
        raise RuntimeError('Historical schema validation requires an explicit online connection.')
    if bind.dialect.name not in ('sqlite', 'mysql'):
        _mismatch()
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
        if bind.dialect.name == 'sqlite':
            expected_names = {table.name: ('table', table.name),
                              **{index.name: ('index', table.name) for index in table.indexes}}
            for name, (kind, owner) in expected_names.items():
                objects = bind.execute(sa.text(
                    'SELECT name, type, tbl_name FROM sqlite_master WHERE name = :name COLLATE NOCASE'),
                    {'name': name}).all()
                if objects and objects != [(name, kind, owner)]:
                    _mismatch()
    for parent in parents:
        if parent.name not in existing:
            _mismatch()
        _validate_identity(bind, inspector, parent)
    present = {table.name for table in tables} & existing
    return inspector, present


def ensure(bind):
    """Validate both pre-timeline children before creating either; never commit."""
    parents, tables = _tables()
    inspector, present = preflight_namespace(bind, parents, tables)
    if present and len(present) != len(tables):
        _mismatch()
    for table in tables:
        if table.name in present:
            _validate_table(bind, inspector, table)
    # Both existing parents were validated first; the children are independent.
    for table in tables:
        if table.name not in present:
            table.create(bind, checkfirst=False)


def refuse_downgrade():
    raise RuntimeError('Cannot safely downgrade historical voice prerequisites; '
                       'restore a verified backup instead.')
