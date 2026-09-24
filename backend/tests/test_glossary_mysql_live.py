"""Opt-in integration test; requires a disposable MySQL container URL."""
import os
import uuid
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.engine import make_url

from tests.test_first_alembic_link import revision
from tests.test_progress_alembic_links import assert_no_writes, record_sql


@pytest.fixture
def mysql_db():
    raw = os.environ.get('AUTOTRANSAI_DISPOSABLE_MYSQL_URL')
    if not raw:
        pytest.skip('disposable MySQL URL not supplied')
    url = make_url(raw)
    if (url.get_backend_name() != 'mysql' or url.database != 'glossary_lab'
            or not (url.host or '').startswith('172.17.')):
        pytest.fail('integration test requires the isolated glossary_lab Docker MySQL')
    admin = sa.create_engine(url)
    name = 'glossary_test_' + uuid.uuid4().hex[:12]
    with admin.connect() as db:
        db.exec_driver_sql(f'CREATE DATABASE `{name}`')
    engine = sa.create_engine(url.set(database=name))
    try:
        with engine.connect() as db:
            db.exec_driver_sql('CREATE TABLE projects (id VARCHAR(36) NOT NULL PRIMARY KEY)')
            db.exec_driver_sql("INSERT INTO projects VALUES ('p1')")
            sql = (Path(__file__).parent / 'fixtures/glossary_prerequisites_schema.sql').read_text()
            for statement in sql.split(';'):
                if statement.strip():
                    db.exec_driver_sql(statement)
            yield db
    finally:
        engine.dispose()
        with admin.connect() as db:
            db.exec_driver_sql(f'DROP DATABASE `{name}`')
        admin.dispose()


def upgrade(db):
    with Operations.context(MigrationContext.configure(db)):
        revision('20260916_glossary_single_source').upgrade()


def test_mysql_shadow_copy_preserves_original_and_replays_read_only(mysql_db):
    db = mysql_db
    db.execute(sa.text(
        "INSERT INTO project_glossaries VALUES "
        "('g1', 'p1', '  Ａ\u200b ', ' X ', 'other', 0.7, 'private context', 1, "
        "'2001-02-03 04:05:06', '2002-03-04 05:06:07')"))
    db.execute(sa.text(
        "INSERT INTO project_terminology_memory VALUES "
        "('m1', 'p1', 'B', 'Y', 'other', 0.9, 1, 'private memory', "
        "'2003-04-05 06:07:08', '2004-05-06 07:08:09')"))
    original = db.exec_driver_sql('SELECT * FROM project_glossaries').all()
    memory = db.exec_driver_sql('SELECT * FROM project_terminology_memory').all()
    upgrade(db)
    names = set(sa.inspect(db).get_table_names())
    assert '__alembic_glossary_before_20260916' in names
    assert '__alembic_glossary_stage_20260916' not in names
    assert db.exec_driver_sql('SELECT * FROM __alembic_glossary_before_20260916').all() == original
    assert db.exec_driver_sql('SELECT * FROM project_terminology_memory').all() == memory
    converted = db.execute(sa.text(
        'SELECT id, source_term, translated_term, approved, source_key, translation_key '
        'FROM project_glossaries ORDER BY id')).all()
    assert [(row.id, row.source_term, row.translated_term, row.approved) for row in converted] == [
        ('g1', '  Ａ\u200b ', ' X ', 1), ('m1', 'B', 'Y', 0)]
    assert all(len(row.source_key) == len(row.translation_key) == 64 for row in converted)
    glossary_copy = db.exec_driver_sql(
        "SELECT * FROM project_glossaries WHERE id = 'g1'").one()
    assert tuple(glossary_copy[:10]) == tuple(original[0])
    memory_copy = db.exec_driver_sql(
        "SELECT * FROM project_glossaries WHERE id = 'm1'").one()
    assert tuple(memory_copy[:10]) == (
        memory[0].id, memory[0].project_id, memory[0].source_term,
        memory[0].suggested_term, memory[0].term_type, memory[0].confidence,
        memory[0].source_context, 0, memory[0].created_at, memory[0].updated_at)
    statements = record_sql(db)
    upgrade(db)
    assert_no_writes(statements)


def test_mysql_replay_refuses_missing_original_backup(mysql_db):
    db = mysql_db
    upgrade(db)
    db.exec_driver_sql('DROP TABLE __alembic_glossary_before_20260916')
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        upgrade(db)
    assert_no_writes(statements)


def test_mysql_replay_refuses_changed_backup_rows(mysql_db):
    db = mysql_db
    db.exec_driver_sql("INSERT INTO project_glossaries VALUES "
                       "('g1', 'p1', 'private-source', 'private-target', 'other', 0.7, NULL, 1, "
                       "'2001-02-03', '2002-03-04')")
    upgrade(db)
    db.exec_driver_sql("DELETE FROM __alembic_glossary_before_20260916 WHERE id='g1'")
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch') as exc:
        upgrade(db)
    assert 'private' not in str(exc.value).lower()
    assert_no_writes(statements)


def test_mysql_replay_refuses_missing_backup_audit(mysql_db):
    db = mysql_db
    upgrade(db)
    db.exec_driver_sql('DROP TABLE __alembic_glossary_audit_20260916')
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        upgrade(db)
    assert_no_writes(statements)


def test_mysql_replay_allows_later_edits_to_converted_rows(mysql_db):
    db = mysql_db
    db.exec_driver_sql("INSERT INTO project_glossaries VALUES "
                       "('g1', 'p1', 'A', 'X', 'other', 0.7, NULL, 1, "
                       "'2001-02-03', '2002-03-04')")
    upgrade(db)
    db.exec_driver_sql("UPDATE project_glossaries SET confidence=0.9 WHERE id='g1'")
    statements = record_sql(db)
    upgrade(db)
    assert_no_writes(statements)


def test_mysql_replay_refuses_stage_view_shadow(mysql_db):
    db = mysql_db
    upgrade(db)
    db.exec_driver_sql('CREATE VIEW __alembic_glossary_stage_20260916 AS SELECT 1 AS id')
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        upgrade(db)
    assert_no_writes(statements)


def test_mysql_original_row_added_during_stage_copy_blocks_swap(mysql_db):
    db = mysql_db
    module = revision('20260916_glossary_single_source')
    copy = module._mysql_copy_stage

    def copy_then_source_changes(*args):
        copy(*args)
        db.execute(sa.text(
            "INSERT INTO project_glossaries VALUES "
            "('g2', 'p1', 'private-added', 'target-added', 'other', 0.7, NULL, 1, "
            "'2001-02-03', '2002-03-04')"))

    module._mysql_copy_stage = copy_then_source_changes
    with Operations.context(MigrationContext.configure(db)):
        with pytest.raises(RuntimeError, match='Historical schema mismatch'):
            module.upgrade()
    names = set(sa.inspect(db).get_table_names())
    assert '__alembic_glossary_before_20260916' not in names
    assert '__alembic_glossary_stage_20260916' in names
    assert db.exec_driver_sql('SELECT id FROM project_glossaries').all() == [('g2',)]


def test_mysql_metadata_update_during_stage_copy_blocks_swap(mysql_db):
    db = mysql_db
    db.exec_driver_sql("INSERT INTO project_glossaries VALUES "
                       "('g1', 'p1', 'A', 'X', 'other', 0.7, 'before', 1, "
                       "'2001-02-03', '2002-03-04')")
    module = revision('20260916_glossary_single_source')
    copy = module._mysql_copy_stage

    def copy_then_metadata_changes(*args):
        copy(*args)
        db.exec_driver_sql("UPDATE project_glossaries SET source_context='after', "
                           "approved=0, updated_at='2005-06-07' WHERE id='g1'")

    module._mysql_copy_stage = copy_then_metadata_changes
    with Operations.context(MigrationContext.configure(db)):
        with pytest.raises(RuntimeError, match='Historical schema mismatch'):
            module.upgrade()
    assert db.exec_driver_sql(
        "SELECT source_context, approved FROM project_glossaries WHERE id='g1'").one() == (
            'after', 0)
    assert '__alembic_glossary_before_20260916' not in sa.inspect(db).get_table_names()


def test_mysql_schema_change_during_stage_copy_blocks_swap(mysql_db):
    db = mysql_db
    module = revision('20260916_glossary_single_source')
    copy = module._mysql_copy_stage

    def copy_then_schema_changes(*args):
        copy(*args)
        db.exec_driver_sql('ALTER TABLE project_glossaries ADD COLUMN private_note VARCHAR(20)')

    module._mysql_copy_stage = copy_then_schema_changes
    with Operations.context(MigrationContext.configure(db)):
        with pytest.raises(RuntimeError, match='Historical schema mismatch'):
            module.upgrade()
    assert 'private_note' in {c['name'] for c in sa.inspect(db).get_columns('project_glossaries')}
    assert '__alembic_glossary_before_20260916' not in sa.inspect(db).get_table_names()


def test_mysql_trigger_added_during_stage_copy_blocks_swap(mysql_db):
    db = mysql_db
    module = revision('20260916_glossary_single_source')
    copy = module._mysql_copy_stage

    def copy_then_trigger_changes(*args):
        copy(*args)
        db.exec_driver_sql('CREATE TRIGGER glossary_private_guard BEFORE INSERT '
                           'ON project_glossaries FOR EACH ROW SET @glossary_guard = 1')

    module._mysql_copy_stage = copy_then_trigger_changes
    with Operations.context(MigrationContext.configure(db)):
        with pytest.raises(RuntimeError, match='Historical schema mismatch'):
            module.upgrade()
    assert '__alembic_glossary_before_20260916' not in sa.inspect(db).get_table_names()


def test_mysql_source_conflict_refuses_before_stage_creation(mysql_db):
    db = mysql_db
    db.exec_driver_sql("INSERT INTO project_glossaries VALUES "
                       "('g1', 'p1', 'private-source', 'one', 'other', 0.7, NULL, 1, "
                       "'2001-02-03', '2002-03-04')")
    db.exec_driver_sql("INSERT INTO project_terminology_memory VALUES "
                       "('m1', 'p1', 'PRIVATE-SOURCE', 'two', 'other', 0.9, 0, NULL, "
                       "'2003-04-05', '2004-05-06')")
    with pytest.raises(RuntimeError, match='GLOSSARY_MIGRATION_CONFLICT') as exc:
        upgrade(db)
    assert 'private' not in str(exc.value).lower()
    assert '__alembic_glossary_stage_20260916' not in sa.inspect(db).get_table_names()


def test_mysql_stale_stage_refuses_before_writing_original(mysql_db):
    db = mysql_db
    db.exec_driver_sql('CREATE TABLE __alembic_glossary_stage_20260916 (id INT)')
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        upgrade(db)
    assert_no_writes(statements)


def test_mysql_mixed_id_collations_refuse_before_stage_creation(mysql_db):
    db = mysql_db
    db.exec_driver_sql('ALTER TABLE project_terminology_memory '
                       'MODIFY id VARCHAR(36) COLLATE utf8mb4_bin NOT NULL')
    db.exec_driver_sql("INSERT INTO project_glossaries VALUES "
                       "('abc', 'p1', 'A', 'X', 'other', 0.7, NULL, 1, "
                       "'2001-02-03', '2002-03-04')")
    db.exec_driver_sql("INSERT INTO project_terminology_memory VALUES "
                       "('ABC', 'p1', 'B', 'Y', 'other', 0.9, 0, NULL, "
                       "'2003-04-05', '2004-05-06')")
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        upgrade(db)
    assert '__alembic_glossary_stage_20260916' not in sa.inspect(db).get_table_names()


def test_mysql_empty_historical_children_are_created_and_backed_up(mysql_db):
    db = mysql_db
    db.exec_driver_sql('DROP TABLE project_terminology_memory')
    db.exec_driver_sql('DROP TABLE project_glossaries')
    upgrade(db)
    names = set(sa.inspect(db).get_table_names())
    assert {'project_glossaries', 'project_terminology_memory',
            '__alembic_glossary_before_20260916'} <= names
