"""Actual voice revision on literal SQLite fixtures; no app/env.py/network."""
from pathlib import Path
from types import SimpleNamespace

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.dialects import mysql
from sqlalchemy.dialects.mysql.reflection import MySQLTableDefinitionParser
from sqlalchemy.exc import IntegrityError

from tests.test_first_alembic_link import db, isolated, revision
from tests.test_progress_alembic_links import assert_no_writes, record_sql, snapshot
from tests.test_tiktok_alembic_link import prerequisites, tiktok_link
from tests.test_voice_prerequisites import prepare, fixture_schema as pre_schema, populate as pre_populate


NAME = '20260916_character_voice_timeline'
TABLES = ('speaker_voice_mappings', 'video_translation_segments',
          'character_voice_profiles', 'voice_pool_entries')


def voice_link(db, downgrade=False):
    with Operations.context(MigrationContext.configure(db)):
        module = revision(NAME)
        (module.downgrade if downgrade else module.upgrade)()


def fixture_schema(db, startup=False, replace=None):
    sql = (Path(__file__).parent / 'fixtures/voice_timeline_schema.sql').read_text()
    if startup:
        for default in (" DEFAULT '0'", ' DEFAULT 0', ' DEFAULT 1',
                        " DEFAULT 'unknown'", " DEFAULT 'supporting'"):
            sql = sql.replace(default, '')
        sql = sql.replace('DATETIME,', 'DATETIME NOT NULL,')
    for old, new in replace or []:
        assert old in sql
        sql = sql.replace(old, new)
    for statement in sql.split(';'):
        if statement.strip():
            db.exec_driver_sql(statement)


def populate(db):
    db.exec_driver_sql("INSERT INTO speaker_voice_mappings VALUES "
                       "('speaker-1', 'projects', 'Speaker 1', 'Tên riêng', 'edge', 'voice-1', "
                       "'{\"rate\":1.25}', '2001-02-03', '2002-03-04', 'char-1', 0.75, 1)")
    db.exec_driver_sql("INSERT INTO video_translation_segments VALUES "
                       "(37, 'video_translation_jobs', 4, 1.25, 3.75, 'private-fixture', "
                       "'Bản dịch', 'tts/old.wav', 2.5, NULL, 'completed', 'Speaker 1', 'char-1', "
                       "'edge', 'voice-1', 0.5, NULL, 8, 10, 2, '[38]', 'shift', 0.8)")
    db.exec_driver_sql("INSERT INTO character_voice_profiles VALUES "
                       "('profile-1', 'char-1', 'projects', 'Tên riêng', 'female', 'lead', "
                       "'edge', 'voice-1', 0.9, 1, '2001-02-03', '2002-03-04')")
    db.exec_driver_sql("INSERT INTO voice_pool_entries VALUES "
                       "('pool-1', 'edge', 'vi', 'female', 'voice-1', 'Tên riêng', 0, "
                       "'{\"fixture\":1}', '2001-02-03', '2002-03-04')")


def reject_without_writes(db):
    before = snapshot(db)
    schema = db.exec_driver_sql('SELECT name, sql FROM sqlite_master ORDER BY name').all()
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch.*inspect.*before retrying') as exc:
        voice_link(db)
    assert 'private-fixture' not in str(exc.value)
    assert snapshot(db) == before
    assert db.exec_driver_sql('SELECT name, sql FROM sqlite_master ORDER BY name').all() == schema
    assert_no_writes(statements)


def test_blank_database_traverses_actual_revisions_through_voice(db):
    prerequisites(db)
    tiktok_link(db)
    voice_link(db)
    assert set(TABLES) <= set(sa.inspect(db).get_table_names())
    reference = sa.create_engine('sqlite:///:memory:')
    try:
        with reference.begin() as conn:
            fixture_schema(conn)
            for table in TABLES:
                actual, expected = sa.inspect(db), sa.inspect(conn)
                def columns(inspector):
                    return [{**c, 'type': str(c['type'])} for c in inspector.get_columns(table)]
                assert columns(actual) == columns(expected)
                assert actual.get_indexes(table) == expected.get_indexes(table)
                assert actual.get_foreign_keys(table) == expected.get_foreign_keys(table)
                assert actual.get_unique_constraints(table) == expected.get_unique_constraints(table)
    finally:
        reference.dispose()
    statements = record_sql(db)
    voice_link(db)
    assert_no_writes(statements)


def test_populated_pretimeline_backfills_without_changing_existing_values(db):
    prepare(db)
    pre_schema(db)
    pre_populate(db)
    before = snapshot(db)
    statements = record_sql(db)
    voice_link(db)
    assert not any(sql.lstrip().upper().startswith(('DROP', 'DELETE')) for sql in statements)
    after = snapshot(db)
    for table, rows in before.items():
        assert [{key: row[key] for key in old} for row, old in zip(after[table], rows)] == rows
    assert db.exec_driver_sql('SELECT original_start, original_end FROM video_translation_segments').one() == (1.25, 3.75)
    assert db.exec_driver_sql('SELECT confidence, needs_review FROM speaker_voice_mappings').one() == (0, 0)


@pytest.mark.parametrize('startup', [False, True], ids=['published', 'startup'])
def test_populated_posttimeline_backfills_null_only_then_replays_without_writes(db, startup):
    prepare(db)
    fixture_schema(db, startup)
    populate(db)
    expected = snapshot(db)
    expected['video_translation_segments'][0]['original_end'] = 3.75
    statements = record_sql(db)
    voice_link(db)
    assert not any(sql.lstrip().upper().startswith(('CREATE', 'ALTER', 'DROP')) for sql in statements)
    assert snapshot(db) == expected
    statements = record_sql(db)
    voice_link(db)
    assert_no_writes(statements)


def test_downgrade_refuses_without_deleting_populated_data(db):
    prepare(db)
    fixture_schema(db)
    populate(db)
    before = snapshot(db)
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Cannot safely downgrade.*verified backup'):
        voice_link(db, downgrade=True)
    assert snapshot(db) == before
    assert_no_writes(statements)


@pytest.mark.parametrize('children_present', [False, True])
@pytest.mark.parametrize('sql', [
    'CREATE VIEW voice_pool_entries AS SELECT 1 AS id',
    'CREATE TABLE Voice_Pool_Entries (id TEXT)',
    'CREATE INDEX ix_voice_pool_entries_language ON projects(title)',
    'CREATE TABLE character_voice_profiles (id TEXT)',
])
def test_later_object_mismatch_prevents_earlier_creates_or_backfill(db, sql, children_present):
    prepare(db)
    if children_present:
        pre_schema(db)
        pre_populate(db)
    db.exec_driver_sql(sql)
    reject_without_writes(db)


@pytest.mark.parametrize('replace', [
    [('enabled BOOLEAN NOT NULL DEFAULT 1', 'enabled BOOLEAN NOT NULL DEFAULT 0')],
    [('original_end FLOAT', 'original_end INTEGER')],
    [('confidence FLOAT NOT NULL', 'confidence FLOAT')],
    [("DEFAULT 'unknown'", "DEFAULT '(unknown)'")],
    [('created_at DATETIME,', 'created_at DATETIME NOT NULL,')],
    [('provider_metadata JSON', 'provider_metadata TEXT')],
    [('REFERENCES projects(id) ON DELETE CASCADE', 'REFERENCES projects(id) ON DELETE RESTRICT')],
    [('id VARCHAR(36) NOT NULL PRIMARY KEY', 'id VARCHAR(36) NOT NULL PRIMARY KEY ON CONFLICT REPLACE')],
    [('id INTEGER NOT NULL PRIMARY KEY', 'id INTEGER NOT NULL PRIMARY KEY DESC')],
    [('UNIQUE(provider, voice_id)', 'UNIQUE(provider, voice_id) ON CONFLICT IGNORE')],
    [('UNIQUE(provider, voice_id)', 'UNIQUE(voice_id)')],
    [('voice_pool_entries(language);', 'voice_pool_entries(language DESC);')],
    [('voice_pool_entries(language);', 'voice_pool_entries(language) WHERE enabled = 1;')],
    [('voice_pool_entries(language);', 'voice_pool_entries(lower(language));')],
    [('voice_id VARCHAR(100)', 'voice_id VARCHAR(100) COLLATE NOCASE')],
    [('CREATE TABLE voice_pool_entries (\n id VARCHAR(36) NOT NULL PRIMARY KEY',
      'CREATE TABLE voice_pool_entries (\n id VARCHAR(36) NOT NULL PRIMARY KEY ON CONFLICT REPLACE')],
    [('UNIQUE(project_id, character_id),\n FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE',
      'UNIQUE(project_id, character_id),\n FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE SET NULL')],
    [('needs_review BOOLEAN NOT NULL DEFAULT 0', 'needs_review BOOLEAN NOT NULL')],
])
def test_incompatible_posttimeline_rejects_before_any_update(db, replace):
    prepare(db)
    fixture_schema(db, replace=replace)
    populate(db)
    reject_without_writes(db)


@pytest.mark.parametrize('sql', [
    'DROP TABLE voice_pool_entries',
    'DROP INDEX ix_speaker_voice_mappings_character_id',
    'CREATE INDEX unexpected ON voice_pool_entries(display_name)',
    'ALTER TABLE voice_pool_entries ADD COLUMN extra TEXT',
])
def test_partial_posttimeline_is_not_repaired(db, sql):
    prepare(db)
    fixture_schema(db)
    populate(db)
    db.exec_driver_sql(sql)
    reject_without_writes(db)


def test_missing_second_prerequisite_is_ambiguous(db):
    prepare(db)
    pre_schema(db)
    pre_populate(db)
    db.exec_driver_sql('DROP TABLE video_translation_segments')
    reject_without_writes(db)


@pytest.mark.parametrize('name', [*TABLES, 'projects', 'ix_voice_pool_entries_language'])
def test_temporary_shadows_fail_before_writes(db, name):
    prepare(db)
    db.exec_driver_sql(f'CREATE TEMP VIEW {name} AS SELECT 1 AS id')
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        voice_link(db)
    assert_no_writes(statements)


def test_created_foreign_keys_uniques_and_defaults_are_enforced(db):
    prepare(db)
    voice_link(db)
    populate(db)
    for sql in (
        "UPDATE character_voice_profiles SET project_id = 'missing'",
        "INSERT INTO character_voice_profiles SELECT 'other', character_id, project_id, name, gender, role, voice_provider, voice_id, mapping_confidence, confirmed_by_user, created_at, updated_at FROM character_voice_profiles",
        "INSERT INTO voice_pool_entries SELECT 'other', provider, language, gender, voice_id, display_name, enabled, provider_metadata, created_at, updated_at FROM voice_pool_entries",
    ):
        with pytest.raises(IntegrityError):
            db.exec_driver_sql(sql)
    db.exec_driver_sql("INSERT INTO character_voice_profiles (id, character_id, project_id, name) VALUES ('defaults', 'char-2', 'projects', 'name')")
    assert db.exec_driver_sql("SELECT gender, role, mapping_confidence, confirmed_by_user FROM character_voice_profiles WHERE id = 'defaults'").one() == ('unknown', 'supporting', 0, 0)
    db.exec_driver_sql("INSERT INTO voice_pool_entries (id, provider, language, voice_id, display_name) VALUES ('defaults', 'edge', 'vi', 'voice-2', 'name')")
    assert db.exec_driver_sql("SELECT enabled FROM voice_pool_entries WHERE id = 'defaults'").scalar_one() == 1


def test_mysql_ddl_compiles_offline_from_actual_revision_operations(db):
    prepare(db)
    compiled = []
    def capture(conn, clause, multiparams, params, options):
        if isinstance(clause, sa.schema.DDLElement):
            compiled.append(str(clause.compile(dialect=mysql.dialect())))
    sa.event.listen(db, 'before_execute', capture)
    voice_link(db)
    ddl = '\n'.join(compiled)
    assert 'AUTO_INCREMENT' in ddl
    assert 'UNIQUE (project_id, character_id)' in ddl
    assert 'UNIQUE (provider, voice_id)' in ddl
    assert 'original_start FLOAT' in ddl
    assert not any('DROP ' in sql for sql in compiled)


@pytest.mark.parametrize('startup', [False, True])
def test_mysql_reflected_booleans_and_unique_indexes_replay_offline(db, monkeypatch, startup):
    prepare(db)
    fixture_schema(db, startup)
    populate(db)
    db.exec_driver_sql('UPDATE video_translation_segments SET original_end = end_time')
    before = snapshot(db)
    inspector, dialect = sa.inspect(db), mysql.dialect()
    names = inspector.get_table_names()
    columns = {name: inspector.get_columns(name) for name in names}
    parser = MySQLTableDefinitionParser(dialect, dialect.identifier_preparer)
    for table, name, ddl in (
        ('video_translation_segments', 'id', '`id` int NOT NULL AUTO_INCREMENT'),
        ('speaker_voice_mappings', 'needs_review', "`needs_review` tinyint(1) NOT NULL DEFAULT '0'"),
        ('character_voice_profiles', 'confirmed_by_user', "`confirmed_by_user` tinyint(1) NOT NULL DEFAULT '0'"),
        ('voice_pool_entries', 'enabled', "`enabled` tinyint(1) NOT NULL DEFAULT '1'"),
    ):
        if startup:
            ddl = ddl.split(' DEFAULT')[0]
        parsed = parser.parse('CREATE TABLE `fixture` (\n  ' + ddl + '\n) ENGINE=InnoDB', 'utf8mb4')
        columns[table] = [parsed.columns[0] if c['name'] == name else c for c in columns[table]]
    indexes = {name: inspector.get_indexes(name) for name in names}
    uniques = {name: inspector.get_unique_constraints(name) for name in names}
    # MySQL exposes UNIQUE constraints as indexes as well; no
    # duplicates_constraint marker is emitted by its get_indexes().
    for table, ddl in (
        ('character_voice_profiles', 'UNIQUE KEY `uq_character_profile_project_character` (`project_id`,`character_id`)'),
        ('voice_pool_entries', 'UNIQUE KEY `uq_voice_pool_provider_voice` (`provider`,`voice_id`)'),
    ):
        parsed = parser.parse('CREATE TABLE `fixture` (\n  ' + ddl + '\n) ENGINE=InnoDB', 'utf8mb4')
        with monkeypatch.context() as patch:
            patch.setattr(dialect, '_parsed_state_or_create', lambda *args, **kwargs: parsed)
            indexes[table] += dialect.get_indexes(None, table)
            uniques[table] = dialect.get_unique_constraints(None, table)
    reflected = SimpleNamespace(
        default_schema_name=None, get_table_names=lambda: names, get_view_names=lambda: [],
        has_table=lambda name: name in names, get_columns=columns.__getitem__,
        get_pk_constraint=inspector.get_pk_constraint, get_foreign_keys=inspector.get_foreign_keys,
        get_check_constraints=lambda name: [], get_indexes=indexes.__getitem__,
        get_unique_constraints=uniques.__getitem__,
    )
    # Read the remaining reflection while still on the real SQLite connection.
    pks = {name: inspector.get_pk_constraint(name) for name in names}
    fks = {name: inspector.get_foreign_keys(name) for name in names}
    reflected.get_pk_constraint, reflected.get_foreign_keys = pks.__getitem__, fks.__getitem__
    real_execute, sqlite_dialect = db.execute, db.dialect
    def reads_only(clause, *args, **kwargs):
        assert isinstance(clause, sa.sql.Select), 'Offline MySQL replay must never write'
        assert 'LIMIT' in str(clause.compile(dialect=dialect))
        with monkeypatch.context() as patch:
            patch.setattr(db, 'dialect', sqlite_dialect)
            return real_execute(clause, *args, **kwargs)
    with monkeypatch.context() as patch:
        patch.setattr(db, 'dialect', dialect)
        patch.setattr(sa, 'inspect', lambda connection: reflected)
        patch.setattr(db, 'execute', reads_only)
        voice_link(db)
    assert snapshot(db) == before


@pytest.mark.parametrize('replace', [
    [("DEFAULT '0'", 'DEFAULT (0.0)'), ('DEFAULT 0', 'DEFAULT false'), ('DEFAULT 1', 'DEFAULT true')],
    [('PRIMARY KEY', 'PRIMARY KEY ASC ON CONFLICT ABORT'),
     ('UNIQUE(provider, voice_id)', 'UNIQUE(provider, voice_id) ON CONFLICT ABORT'),
     ('voice_pool_entries(language);', 'voice_pool_entries(language COLLATE binary ASC);')],
])
def test_equivalent_sql_preserves_populated_posttimeline(db, replace):
    prepare(db)
    fixture_schema(db, replace=replace)
    populate(db)
    voice_link(db)
    assert db.exec_driver_sql('SELECT original_start, original_end FROM video_translation_segments').one() == (0.5, 3.75)


@pytest.mark.parametrize('table_name', [
    'video_translation_segments', 'VIDEO_TRANSLATION_SEGMENTS', 'Video_Translation_Segments',
])
@pytest.mark.parametrize('temporary', [False, True], ids=['permanent', 'temporary'])
def test_backfill_trigger_cannot_rewrite_existing_user_data(db, table_name, temporary):
    prepare(db)
    fixture_schema(db)
    populate(db)
    db.exec_driver_sql(f"CREATE {'TEMP ' if temporary else ''}TRIGGER corrupt_original AFTER UPDATE ON {table_name} "
                       "BEGIN UPDATE video_translation_segments SET original_start = 99; END")
    reject_without_writes(db)


@pytest.mark.parametrize('name', ['projects', 'video_translation_jobs'])
def test_missing_parent_identity_prevents_voice_creation(db, name):
    prepare(db)
    db.exec_driver_sql(f'ALTER TABLE {name} RENAME TO unrelated')
    reject_without_writes(db)


def test_partial_timeline_columns_on_prerequisites_fail_before_writes(db):
    prepare(db)
    pre_schema(db)
    pre_populate(db)
    db.exec_driver_sql('ALTER TABLE video_translation_segments ADD COLUMN original_start FLOAT')
    db.exec_driver_sql('UPDATE video_translation_segments SET original_start = 99')
    reject_without_writes(db)
