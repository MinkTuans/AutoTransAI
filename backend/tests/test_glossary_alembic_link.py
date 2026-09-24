"""Actual published glossary revision against disposable historical SQLite."""
import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

from tests.test_first_alembic_link import db, revision
from tests.test_glossary_prerequisites import prepare, fixture_schema, rows
from tests.test_progress_alembic_links import assert_no_writes, record_sql


def upgrade(db):
    with Operations.context(MigrationContext.configure(db)):
        revision('20260916_glossary_single_source').upgrade()


def seed(db, table, identity, source, target):
    if table == 'project_glossaries':
        db.execute(sa.text("INSERT INTO project_glossaries VALUES "
                           "(:id, 'projects', :source, :target, 'other', 0.7, "
                           "'private context', 1, '2001-02-03', '2002-03-04')"),
                   dict(id=identity, source=source, target=target))
    else:
        db.execute(sa.text("INSERT INTO project_terminology_memory VALUES "
                           "(:id, 'projects', :source, :target, 'other', 0.9, "
                           "0, 'private memory', '2003-04-05', '2004-05-06')"),
                   dict(id=identity, source=source, target=target))


def test_clean_memory_copy_preserves_both_original_tables_and_terms(db):
    prepare(db)
    fixture_schema(db)
    seed(db, 'project_glossaries', 'g1', '  Ａ\u200b ', ' X ')
    seed(db, 'project_terminology_memory', 'm1', 'B', 'Y')
    before = rows(db)
    upgrade(db)
    assert 'project_terminology_memory' in sa.inspect(db).get_table_names()
    assert rows(db)['project_terminology_memory'] == before['project_terminology_memory']
    actual = db.execute(sa.text('SELECT id, source_term, translated_term FROM project_glossaries ORDER BY id')).all()
    assert actual == [('g1', '  Ａ\u200b ', ' X '), ('m1', 'B', 'Y')]
    assert {column['name'] for column in sa.inspect(db).get_columns('project_glossaries')} >= {
        'source_key', 'translation_key'}


def test_duplicate_glossary_refuses_before_any_write_without_term_leak(db):
    prepare(db)
    fixture_schema(db)
    seed(db, 'project_glossaries', 'g1', 'private-term', 'private-target')
    seed(db, 'project_glossaries', 'g2', 'PRIVATE-TERM', 'PRIVATE-TARGET')
    before = rows(db)
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='GLOSSARY_MIGRATION_CONFLICT') as exc:
        upgrade(db)
    assert 'private' not in str(exc.value).lower()
    assert rows(db) == before
    assert_no_writes(statements)


def test_cross_table_equivalent_mapping_keeps_both_rows(db):
    prepare(db)
    fixture_schema(db)
    seed(db, 'project_glossaries', 'g1', 'A', 'X')
    seed(db, 'project_terminology_memory', 'm1', 'a', 'x')
    before = rows(db)
    upgrade(db)
    assert rows(db)['project_terminology_memory'] == before['project_terminology_memory']
    assert [row.id for row in db.execute(sa.text('SELECT id FROM project_glossaries'))] == ['g1']


def test_missing_historical_children_are_created_without_touching_parent(db):
    prepare(db)
    before = db.execute(sa.text('SELECT * FROM projects')).all()
    upgrade(db)
    assert {'project_glossaries', 'project_terminology_memory'} <= set(
        sa.inspect(db).get_table_names())
    assert db.execute(sa.text('SELECT * FROM projects')).all() == before


def test_partial_historical_children_refuse_before_schema_write(db):
    prepare(db)
    fixture_schema(db)
    db.exec_driver_sql('DROP TABLE project_terminology_memory')
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        upgrade(db)
    assert_no_writes(statements)


def test_replay_of_complete_conversion_is_read_only(db):
    prepare(db)
    fixture_schema(db)
    seed(db, 'project_terminology_memory', 'm1', 'A', 'X')
    upgrade(db)
    before = rows(db)
    statements = record_sql(db)
    upgrade(db)
    assert rows(db) == before
    assert_no_writes(statements)


def test_partial_canonical_keys_refuse_before_any_write(db):
    prepare(db)
    fixture_schema(db)
    db.exec_driver_sql('ALTER TABLE project_glossaries ADD COLUMN source_key VARCHAR(64)')
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        upgrade(db)
    assert_no_writes(statements)


def test_replay_with_corrupt_canonical_key_refuses_without_writes(db):
    prepare(db)
    fixture_schema(db)
    seed(db, 'project_glossaries', 'g1', 'A', 'X')
    upgrade(db)
    db.exec_driver_sql("UPDATE project_glossaries SET source_key = 'bad' WHERE id = 'g1'")
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        upgrade(db)
    assert_no_writes(statements)


def test_incoming_foreign_key_refuses_before_batch_table_rebuild(db):
    prepare(db)
    fixture_schema(db)
    db.exec_driver_sql('CREATE TABLE glossary_notes (id INTEGER PRIMARY KEY, '
                       'glossary_id VARCHAR(36) REFERENCES project_glossaries(id))')
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        upgrade(db)
    assert_no_writes(statements)


def test_batch_temporary_name_collision_refuses_before_any_write(db):
    prepare(db)
    fixture_schema(db)
    db.exec_driver_sql('CREATE TABLE _alembic_tmp_project_glossaries (id INTEGER)')
    statements = record_sql(db)
    with pytest.raises(RuntimeError, match='Historical schema mismatch'):
        upgrade(db)
    assert_no_writes(statements)


def test_unreviewed_memory_copy_stays_unapproved_and_original_metadata_survives(db):
    prepare(db)
    fixture_schema(db)
    seed(db, 'project_terminology_memory', 'm1', 'A', 'X')
    db.exec_driver_sql("UPDATE project_terminology_memory SET needs_review = 1 WHERE id = 'm1'")
    original = db.exec_driver_sql('SELECT * FROM project_terminology_memory').one()
    upgrade(db)
    assert db.exec_driver_sql('SELECT * FROM project_terminology_memory').one() == original
    copy = db.execute(sa.text(
        'SELECT term_type, confidence, source_context, approved, created_at, updated_at '
        'FROM project_glossaries WHERE id=:id'), {'id': 'm1'}).one()
    assert copy == ('other', 0.9, 'private memory', 0,
                    '2003-04-05', '2004-05-06')
