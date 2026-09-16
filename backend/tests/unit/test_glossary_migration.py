import pytest
import importlib.util
from pathlib import Path
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text

from app.services.glossary_migration import audit_legacy_glossary_rows


def row(table, row_id, project, source, target):
    return {
        "table": table,
        "id": row_id,
        "project_id": project,
        "source_term": source,
        "translated_term": target,
    }


def test_audit_merges_only_identical_normalized_mapping():
    result = audit_legacy_glossary_rows(
        [
            row("project_glossaries", "g1", "p1", "李道天", "Lý Đạo Thiên"),
            row("project_terminology_memory", "m1", "p1", " 李道天\u200b", "LÝ  ĐẠO THIÊN"),
        ]
    )
    assert result.conflicts == []
    assert result.canonical_ids == {"g1"}
    assert result.duplicate_ids == {"m1"}


@pytest.mark.parametrize(
    "rows,code",
    [
        (
            [
                row("project_glossaries", "g1", "p1", "A", "X"),
                row("project_terminology_memory", "m1", "p1", "A", "Y"),
            ],
            "SOURCE_CONFLICT",
        ),
        (
            [
                row("project_glossaries", "g1", "p1", "A", "X"),
                row("project_terminology_memory", "m1", "p1", "B", "X"),
            ],
            "TRANSLATION_CONFLICT",
        ),
    ],
)
def test_audit_reports_real_conflict_without_selecting_winner(rows, code):
    result = audit_legacy_glossary_rows(rows)
    assert result.conflicts[0]["code"] == code
    assert result.canonical_ids == set()
    assert result.duplicate_ids == set()


def _legacy_schema(connection):
    connection.execute(text("CREATE TABLE projects (id VARCHAR(36) PRIMARY KEY)"))
    connection.execute(text("INSERT INTO projects (id) VALUES ('p1')"))
    connection.execute(text("""
        CREATE TABLE project_glossaries (
            id VARCHAR(36) PRIMARY KEY, project_id VARCHAR(36) NOT NULL,
            source_term VARCHAR(255) NOT NULL, translated_term VARCHAR(255) NOT NULL,
            term_type VARCHAR(50) NOT NULL, confidence FLOAT NOT NULL,
            source_context TEXT, approved BOOLEAN NOT NULL,
            created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL
        )
    """))
    connection.execute(text("""
        CREATE TABLE project_terminology_memory (
            id VARCHAR(36) PRIMARY KEY, project_id VARCHAR(36) NOT NULL,
            source_term VARCHAR(255) NOT NULL, suggested_term VARCHAR(255) NOT NULL,
            term_type VARCHAR(50) NOT NULL, confidence FLOAT NOT NULL,
            needs_review BOOLEAN NOT NULL, source_context TEXT,
            created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL
        )
    """))


def test_alembic_upgrade_moves_clean_memory_rows_and_drops_legacy_table(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'migration.db'}")
    migration_path = (
        Path(__file__).resolve().parents[2]
        / "alembic/versions/20260916_glossary_single_source.py"
    )
    spec = importlib.util.spec_from_file_location("glossary_migration_revision", migration_path)
    migration = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(migration)
    with engine.begin() as connection:
        _legacy_schema(connection)
        connection.execute(text("""
            INSERT INTO project_terminology_memory
            (id, project_id, source_term, suggested_term, term_type, confidence,
             needs_review, source_context, created_at, updated_at)
            VALUES ('m1','p1','李道天','Lý Đạo Thiên','character',0.9,0,NULL,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)
        """))
        migration.op = Operations(MigrationContext.configure(connection))
        migration.upgrade()

        assert "project_terminology_memory" not in inspect(connection).get_table_names()
        saved = connection.execute(text(
            "SELECT source_term, translated_term, source_key, translation_key FROM project_glossaries"
        )).one()
        assert saved.source_term == "李道天"
        assert saved.translated_term == "Lý Đạo Thiên"
        assert len(saved.source_key) == len(saved.translation_key) == 64
        unique_indexes = [index for index in inspect(connection).get_unique_constraints("project_glossaries")]
        assert len(unique_indexes) == 2
