"""Frozen pre-timeline prerequisites only; no published voice revision activation."""
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic.util import load_python_file
from sqlalchemy.dialects import mysql
from sqlalchemy.exc import IntegrityError

from tests.test_first_alembic_link import db, isolated, fixture_schema as first_fixture
from tests.test_progress_alembic_links import assert_no_writes, record_sql, snapshot
from tests.test_tiktok_alembic_link import prerequisites, tiktok_link


TABLES = ('speaker_voice_mappings', 'video_translation_segments')
PARENTS = ('projects', 'video_translation_jobs')
DIRECTORY = Path(__file__).parents[1] / 'alembic'


def helper():
    assert (DIRECTORY / 'voice_prerequisites.py').is_file(), 'Frozen voice prerequisite helper missing'
    return load_python_file(str(DIRECTORY), 'voice_prerequisites.py')


def prepare(db):
    first_fixture(db)  # Populated independent first-link parents, not current ORM.
    prerequisites(db)
    tiktok_link(db)


def fixture_schema(db, replace=None):
    sql = (Path(__file__).parent / 'fixtures/voice_prerequisites_schema.sql').read_text()
    if replace:
        replacements = [replace] if isinstance(replace[0], str) else replace
        for old, new in replacements:
            sql = sql.replace(old, new)
    for statement in sql.split(';'):
        if statement.strip():
            db.exec_driver_sql(statement)


def populate(db):
    db.exec_driver_sql("INSERT INTO speaker_voice_mappings "
                       "(id, project_id, speaker_id, speaker_name, voice_provider, voice_id, "
                       "voice_settings, created_at, updated_at) VALUES "
                       "('speaker-1', 'projects', 'Speaker 1', 'Tên riêng', 'edge', 'voice-1', "
                       "'{\"rate\":1.25}', '2001-02-03 04:05:06', '2002-03-04 05:06:07')")
    db.exec_driver_sql("INSERT INTO video_translation_segments VALUES "
                       "(37, 'video_translation_jobs', 4, 1.25, 3.75, 'private-fixture', "
                       "'Bản dịch', 'tts/old.wav', 2.5, NULL, 'completed')")


def reject_without_writes(db):
    before = snapshot(db)
    schema = db.exec_driver_sql('SELECT name, sql FROM sqlite_master ORDER BY name').all()
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch.*inspect.*before retrying') as exc:
        helper().ensure(db)
    assert 'private-fixture' not in str(exc.value)
    assert snapshot(db) == before
    assert db.exec_driver_sql('SELECT name, sql FROM sqlite_master ORDER BY name').all() == schema
    assert_no_writes(statements)


def test_absent_tables_match_independent_historical_contract_after_tiktok(db):
    prepare(db)
    before = snapshot(db)
    helper().ensure(db)
    assert set(sa.inspect(db).get_table_names()) == set(before) | set(TABLES)
    for table, rows in before.items():
        assert snapshot(db)[table] == rows
    engine = sa.create_engine('sqlite:///:memory:')
    try:
        with engine.begin() as reference:
            fixture_schema(reference)
            actual, expected = sa.inspect(db), sa.inspect(reference)
            for table in TABLES:
                def columns(inspector):
                    return [(c['name'], str(c['type']), c['nullable'], c['default'], c['primary_key'])
                            for c in inspector.get_columns(table)]
                assert columns(actual) == columns(expected)
                assert actual.get_pk_constraint(table) == expected.get_pk_constraint(table)
                assert actual.get_foreign_keys(table) == expected.get_foreign_keys(table)
                assert actual.get_indexes(table) == expected.get_indexes(table)
    finally:
        engine.dispose()


def test_populated_compatible_tables_and_repeat_preserve_all_rows_without_writes(db):
    prepare(db)
    fixture_schema(db)
    populate(db)
    before = snapshot(db)
    statements = record_sql(db)
    module = helper()
    assert_no_writes(statements)  # Loading the helper cannot create schema.
    module.ensure(db)
    module.ensure(db)
    assert snapshot(db) == before
    assert_no_writes(statements)


@pytest.mark.parametrize('table', TABLES)
def test_one_absent_table_is_ambiguous_and_leaves_populated_table_unchanged(db, table):
    prepare(db)
    fixture_schema(db)
    populate(db)
    db.exec_driver_sql(f'DROP TABLE {table}')
    reject_without_writes(db)


@pytest.mark.parametrize('replace', [
    ('speaker_id VARCHAR(100)', 'speaker_id VARCHAR(20)'),
    ('voice_provider VARCHAR(50) NOT NULL', 'voice_provider VARCHAR(50)'),
    ('voice_provider VARCHAR(50) NOT NULL', "voice_provider VARCHAR(50) NOT NULL DEFAULT 'edge'"),
    ('start_time FLOAT NOT NULL', 'start_time FLOAT NOT NULL DEFAULT 0.0'),
    ('updated_at DATETIME NOT NULL', 'updated_at DATETIME'),
    ('voice_settings JSON', 'voice_settings TEXT'),
    ('voice_settings JSON', 'voice_settings JSON, extra TEXT'),
    ('tts_audio_duration FLOAT', 'unknown FLOAT'),
    ('segment_number INTEGER NOT NULL', 'segment_number BIGINT NOT NULL'),
    ('status VARCHAR(30) NOT NULL', 'status VARCHAR(30) NOT NULL CHECK (length(status) > 0)'),
    ('speaker_id VARCHAR(100) NOT NULL', 'speaker_id VARCHAR(100) NOT NULL UNIQUE'),
    ('id VARCHAR(36) NOT NULL PRIMARY KEY', 'id VARCHAR(36) NOT NULL'),
    ('id VARCHAR(36) NOT NULL PRIMARY KEY', 'id VARCHAR(36) NOT NULL PRIMARY KEY ON CONFLICT REPLACE'),
    ('id VARCHAR(36) NOT NULL PRIMARY KEY', 'id VARCHAR(36) COLLATE NOCASE NOT NULL PRIMARY KEY'),
    ('id VARCHAR(36) NOT NULL PRIMARY KEY', 'id VARCHAR(36) NOT NULL PRIMARY KEY DESC'),
    ('id INTEGER NOT NULL PRIMARY KEY', 'id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT'),
    ('id INTEGER NOT NULL PRIMARY KEY', 'id INT NOT NULL PRIMARY KEY'),
    ('id INTEGER NOT NULL PRIMARY KEY', 'id INTEGER NOT NULL PRIMARY KEY DESC'),
    ('id INTEGER NOT NULL PRIMARY KEY', 'id INTEGER NOT NULL PRIMARY KEY ON CONFLICT IGNORE'),
    ('REFERENCES projects(id) ON DELETE CASCADE', 'REFERENCES projects(id) ON DELETE RESTRICT'),
    ('REFERENCES video_translation_jobs(id) ON DELETE CASCADE', 'REFERENCES video_translation_jobs(id)'),
    ('REFERENCES video_translation_jobs(id) ON DELETE CASCADE',
     'REFERENCES video_translation_jobs(id) ON DELETE CASCADE ON UPDATE CASCADE'),
    ('REFERENCES projects(id) ON DELETE CASCADE',
     'REFERENCES projects(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED'),
    ('CREATE INDEX ix_speaker_voice', 'CREATE UNIQUE INDEX ix_speaker_voice'),
    ('speaker_voice_mappings(project_id);', 'speaker_voice_mappings(project_id DESC);'),
    ('speaker_voice_mappings(project_id);', 'speaker_voice_mappings(project_id COLLATE NOCASE);'),
    ('video_translation_segments(job_id);', 'video_translation_segments(job_id) WHERE id > 0;'),
    ('video_translation_segments(job_id);', 'video_translation_segments(job_id, status);'),
    ('ix_video_translation_segments_job_id', 'unknown_index'),
])
def test_incompatible_contract_rejects_before_writes(db, replace):
    prepare(db)
    fixture_schema(db, replace)
    populate(db)
    reject_without_writes(db)


@pytest.mark.parametrize('sql', [
    'DROP INDEX ix_speaker_voice_mappings_project_id',
    'CREATE INDEX extra_expression ON video_translation_segments(lower(status))',
    'CREATE INDEX extra_index ON speaker_voice_mappings(voice_id)',
    'ALTER TABLE video_translation_segments ADD COLUMN character_id VARCHAR(36)',
])
def test_missing_or_extra_schema_rejects_populated_state(db, sql):
    prepare(db)
    fixture_schema(db)
    populate(db)
    db.exec_driver_sql(sql)
    reject_without_writes(db)


@pytest.mark.parametrize('name', [*TABLES, 'Speaker_Voice_Mappings', 'Video_Translation_Segments',
                                 'ix_speaker_voice_mappings_project_id',
                                 'IX_Video_Translation_Segments_Job_ID'])
@pytest.mark.parametrize('kind', ['TABLE', 'VIEW', 'INDEX'])
def test_namespace_collision_in_either_table_preflights_before_any_creation(db, name, kind):
    prepare(db)
    if kind == 'INDEX':
        db.exec_driver_sql(f'CREATE INDEX {name} ON projects(title)')
    else:
        db.exec_driver_sql(f"CREATE {kind} {name} AS SELECT 'private-fixture' AS id")
    reject_without_writes(db)


@pytest.mark.parametrize('parent', PARENTS)
@pytest.mark.parametrize('change', ['missing', 'case-alias', 'view', 'type', 'default', 'collation', 'pk'])
def test_invalid_parent_identity_prevents_creating_both_children(db, parent, change):
    # A minimal standalone parent fixture isolates identity checking from D1/D2.
    for name in PARENTS:
        kind = 'VARCHAR(36) NOT NULL PRIMARY KEY'
        if name == parent:
            if change == 'missing':
                continue
            if change == 'case-alias':
                name = name.upper()
            elif change == 'view':
                db.exec_driver_sql(f"CREATE VIEW {name} AS SELECT 'private-fixture' AS id")
                continue
            elif change == 'type':
                kind = 'VARCHAR(20) NOT NULL PRIMARY KEY'
            elif change == 'default':
                kind += " DEFAULT 'private-fixture'"
            elif change == 'collation':
                kind += ' COLLATE NOCASE'
            elif change == 'pk':
                kind += ' ON CONFLICT REPLACE'
        db.exec_driver_sql(f'CREATE TABLE {name} (id {kind})')
    reject_without_writes(db)


@pytest.mark.parametrize('replace', [
    ('id VARCHAR(36) NOT NULL PRIMARY KEY',
     'id VARCHAR(36) COLLATE BiNaRy NOT NULL PRIMARY KEY ASC ON CONFLICT ABORT'),
    (('id INTEGER NOT NULL PRIMARY KEY', 'id INTEGER NOT NULL'),
     ('FOREIGN KEY(job_id)', 'PRIMARY KEY (id ASC), FOREIGN KEY(job_id)')),
    ('PRIMARY KEY', 'CONSTRAINT "ON CONFLICT REPLACE" PRIMARY KEY /* ignored */'),
    ('speaker_voice_mappings(project_id);', 'speaker_voice_mappings(project_id COLLATE binary ASC);'),
])
def test_equivalent_identity_and_index_syntax_preserves_rows(db, replace):
    prepare(db)
    fixture_schema(db, replace)
    populate(db)
    before = snapshot(db)
    statements = record_sql(db)
    helper().ensure(db)
    assert snapshot(db) == before
    assert_no_writes(statements)


@pytest.mark.parametrize('replace', [
    ('voice_id VARCHAR(100)', 'voice_id VARCHAR(100) COLLATE NOCASE'),
    (('job_id VARCHAR(36)', 'job_id VARCHAR(36) COLLATE NOCASE'),
     ('video_translation_segments(job_id);', 'video_translation_segments(job_id COLLATE BINARY);')),
])
def test_nonhistorical_column_collation_cannot_hide_behind_index_collation(db, replace):
    prepare(db)
    fixture_schema(db, replace)
    populate(db)
    reject_without_writes(db)


@pytest.mark.parametrize('name', [*PARENTS, *TABLES, 'ix_video_translation_segments_job_id'])
def test_temporary_relation_cannot_shadow_preflight_or_created_relations(db, name):
    prepare(db)
    db.exec_driver_sql(f'CREATE TEMPORARY VIEW {name} AS SELECT 1 AS id')
    # Snapshot only the main schema; the temporary parent view deliberately
    # shadows row reads, but is never a proven migration parent.
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        helper().ensure(db)
    assert_no_writes(statements)


def test_created_tables_enforce_foreign_keys_cascade_and_rowid_allocation(db):
    prepare(db)
    helper().ensure(db)
    populate(db)
    for table, column in zip(TABLES, ('project_id', 'job_id')):
        with pytest.raises(IntegrityError):
            db.exec_driver_sql(f"UPDATE {table} SET {column} = 'missing'")
    with pytest.raises(IntegrityError):
        db.exec_driver_sql('INSERT INTO speaker_voice_mappings SELECT * FROM speaker_voice_mappings')
    db.exec_driver_sql('INSERT INTO video_translation_segments SELECT NULL, job_id, segment_number, '
                       'start_time, end_time, original_text, translated_text, tts_audio_path, '
                       'tts_audio_duration, synced_audio_path, status FROM video_translation_segments')
    assert db.exec_driver_sql('SELECT id FROM video_translation_segments ORDER BY id').all() == [(37,), (38,)]
    db.exec_driver_sql("DELETE FROM projects WHERE id = 'projects'")
    assert db.exec_driver_sql('SELECT * FROM speaker_voice_mappings').all() == []
    db.exec_driver_sql("DELETE FROM video_translation_jobs WHERE id = 'video_translation_jobs'")
    assert db.exec_driver_sql('SELECT * FROM video_translation_segments').all() == []


def test_import_and_downgrade_do_not_write_and_explicit_connection_is_required(db):
    prepare(db)
    statements = record_sql(db)
    module = helper()
    with pytest.raises(RuntimeError, match='explicit online connection'):
        module.ensure(None)
    with pytest.raises(RuntimeError, match='Cannot safely downgrade.*verified backup'):
        module.refuse_downgrade()
    assert_no_writes(statements)


def test_mysql_ddl_compiles_offline_from_actual_sqlite_creates(db):
    prepare(db)
    compiled = []
    def capture(conn, clause, multiparams, params, options):
        if isinstance(clause, sa.schema.DDLElement):
            compiled.append(str(clause.compile(dialect=mysql.dialect())))
    sa.event.listen(db, 'before_execute', capture)
    helper().ensure(db)
    ddl = '\n'.join(compiled)
    assert 'id INTEGER NOT NULL AUTO_INCREMENT' in ddl
    assert 'REFERENCES projects (id) ON DELETE CASCADE' in ddl
    assert 'REFERENCES video_translation_jobs (id) ON DELETE CASCADE' in ddl
    assert 'DEFAULT' not in ddl
    assert sum('CREATE TABLE' in sql for sql in compiled) == 2
