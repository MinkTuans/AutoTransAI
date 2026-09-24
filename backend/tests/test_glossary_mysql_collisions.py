"""Database-collation audit on disposable tables; MySQL checked separately."""
from pathlib import Path
from types import SimpleNamespace

from alembic.util import load_python_file
import pytest
import sqlalchemy as sa

from tests.test_progress_alembic_links import assert_no_writes, record_sql


def helper():
    return load_python_file(str(Path(__file__).parents[1] / 'alembic'),
                            'glossary_mysql_preflight.py')


@pytest.mark.parametrize('glossary,memory,expected', [
    (('private-id', 'p'), ('PRIVATE-ID', 'p'), ('ID_COLLISION',)),
    (('g1', 'private-p'), ('m1', 'PRIVATE-P'), ('PROJECT_COLLATION_COLLISION',)),
    (('g1', 'p'), ('m1', 'p'), ()),
])
def test_collation_aware_audit_uses_database_equality_without_leaking_values(
        glossary, memory, expected):
    engine = sa.create_engine('sqlite:///:memory:')
    with engine.begin() as db:
        db.exec_driver_sql('CREATE TABLE project_glossaries ('
                           'id VARCHAR(36) COLLATE NOCASE PRIMARY KEY, '
                           'project_id VARCHAR(36) COLLATE NOCASE NOT NULL)')
        db.exec_driver_sql('CREATE TABLE project_terminology_memory ('
                           'id VARCHAR(36) COLLATE NOCASE PRIMARY KEY, '
                           'project_id VARCHAR(36) COLLATE NOCASE NOT NULL)')
        db.execute(sa.text('INSERT INTO project_glossaries VALUES (:id, :project)'),
                   {'id': glossary[0], 'project': glossary[1]})
        db.execute(sa.text('INSERT INTO project_terminology_memory VALUES (:id, :project)'),
                   {'id': memory[0], 'project': memory[1]})
        statements = record_sql(db)
        actual = helper().collision_codes(db)
        assert actual == expected
        assert 'private' not in repr(actual)
        assert_no_writes(statements)
    engine.dispose()


def test_mysql_mixed_id_and_project_collations_refuse_before_join():
    def metadata_only(statement):
        assert 'information_schema.COLUMNS' in str(statement)
        rows = [{'COLUMN_NAME': 'id', 'n': 2, 'variants': 2},
                {'COLUMN_NAME': 'project_id', 'n': 2, 'variants': 2}]
        return SimpleNamespace(mappings=lambda: SimpleNamespace(all=lambda: rows))

    bind = SimpleNamespace(dialect=SimpleNamespace(name='mysql'), execute=metadata_only)
    assert helper().collision_codes(bind) == ('COLLATION_MISMATCH',)
