"""Only the first two revisions, explicit in-memory SQLite, no application imports."""
import builtins
import importlib.util
from pathlib import Path
import socket

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.dialects import mysql
from sqlalchemy.exc import IntegrityError


VERSIONS = Path(__file__).parents[1] / "alembic/versions"
NAMES = ("202da08bcdd8_initial_schema", "20260822_sync_schema")
TABLES = {"projects", "segments", "video_assets", "video_translation_jobs"}
ADDITIONS = {
    "video_translation_jobs": {
        "llm_provider_id": "VARCHAR(50)", "r2_key": "VARCHAR(500)",
        "output_url": "TEXT", "is_cleaned": "BOOLEAN", "stage": "VARCHAR(50)",
        "stage_progress_pct": "FLOAT", "overall_progress_pct": "FLOAT", "pid": "INTEGER",
        "last_heartbeat": "DATETIME", "ffmpeg_stats_json": "TEXT",
        "completed_segments_count": "INTEGER", "total_segments_count": "INTEGER",
    },
    "video_assets": {"r2_key": "VARCHAR(500)", "url": "TEXT"},
    "projects": {"r2_key": "VARCHAR(500)", "media_url": "TEXT"},
    "segments": {"audio_error_message": "TEXT", "video_error_message": "TEXT", "video_error_details": "TEXT"},
}


@pytest.fixture(autouse=True)
def isolated(monkeypatch):
    original = builtins.__import__

    def guarded(name, *args, **kwargs):
        if name == "app" or name.startswith(("app.", "shared.", "dotenv")):
            raise AssertionError("Migration must not import configured application code")
        return original(name, *args, **kwargs)

    def no_network(*args, **kwargs):
        raise AssertionError("Migration tests cannot use the network")

    monkeypatch.setattr(builtins, "__import__", guarded)
    monkeypatch.setattr(socket.socket, "connect", no_network)
    monkeypatch.setattr(socket, "create_connection", no_network)


@pytest.fixture
def db():
    engine = sa.create_engine("sqlite:///:memory:")
    try:
        with engine.begin() as connection:
            connection.exec_driver_sql("PRAGMA foreign_keys=ON")
            assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one() == 1
            yield connection
    finally:
        engine.dispose()


def revision(name):
    spec = importlib.util.spec_from_file_location(name, VERSIONS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def traverse(db):
    with Operations.context(MigrationContext.configure(db)):
        for name in NAMES:
            revision(name).upgrade()


def fixture_schema(db, current=False, without_job_fk=False):
    sql = (Path(__file__).parent / "fixtures/first_link_schema.sql").read_text()
    if without_job_fk:
        sql = sql.replace(",\n FOREIGN KEY(asset_id) REFERENCES video_assets(id) ON DELETE CASCADE", "")
    for statement in sql.split(";"):
        if statement.strip():
            db.exec_driver_sql(statement)
    if current:
        for table, columns in ADDITIONS.items():
            existing = {c["name"] for c in sa.inspect(db).get_columns(table)}
            for name, kind in columns.items():
                if name not in existing:
                    # Historical ORM create_all has client defaults, no server defaults.
                    required = name in {"stage", "stage_progress_pct", "overall_progress_pct",
                                        "last_heartbeat", "completed_segments_count",
                                        "total_segments_count", "is_cleaned"}
                    db.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {name} {kind}" +
                                       (" NOT NULL" if required else ""))
    # Populate every column, including synthetic private text, before migration.
    for table in ("projects", "video_assets", "segments", "video_translation_jobs"):
        columns = sa.inspect(db).get_columns(table)
        values = {}
        for c in columns:
            name = c["name"]
            values[name] = (1 if isinstance(c["type"], (sa.Integer, sa.Float, sa.Boolean))
                            else "2000-01-01 00:00:00" if isinstance(c["type"], sa.DateTime)
                            else "private-fixture")
        values["id"] = 1 if table == "segments" else table
        if table == "segments":
            values["project_id"] = "projects"
        if table == "video_translation_jobs":
            values["asset_id"] = "video_assets"
        names = ", ".join(values)
        params = ", ".join(":" + n for n in values)
        db.execute(sa.text(f"INSERT INTO {table} ({names}) VALUES ({params})"), values)


def snapshot(db):
    return {t: [dict(r) for r in db.execute(sa.text(f"SELECT * FROM {t}")).mappings()]
            for t in TABLES}


def test_blank_database_traverses_only_first_two_revisions(db):
    traverse(db)
    assert set(sa.inspect(db).get_table_names()) == TABLES
    for table, additions in ADDITIONS.items():
        assert additions.keys() <= {c["name"] for c in sa.inspect(db).get_columns(table)}
    assert revision(NAMES[0]).down_revision is None
    assert revision(NAMES[1]).down_revision == revision(NAMES[0]).revision
    with pytest.raises(IntegrityError):
        db.exec_driver_sql("INSERT INTO segments (id, project_id, segment_number, text_content, "
                           "char_count, audio_status, video_status) VALUES (1, 'missing', 1, '', 0, '', '')")


def test_initial_schema_matches_independent_frozen_git_fixture(db):
    reference_engine = sa.create_engine("sqlite:///:memory:")
    try:
        with reference_engine.begin() as reference:
            fixture_schema(reference)
            with Operations.context(MigrationContext.configure(db)):
                revision(NAMES[0]).upgrade()
            for table in TABLES:
                actual, frozen = sa.inspect(db), sa.inspect(reference)
                def shape(inspector):
                    return [(c['name'], str(c['type']), c['nullable'], c['default'], c['primary_key'])
                            for c in inspector.get_columns(table)]
                assert shape(actual) == shape(frozen)
                assert actual.get_foreign_keys(table) == frozen.get_foreign_keys(table)
                assert actual.get_indexes(table) == frozen.get_indexes(table)
    finally:
        reference_engine.dispose()


@pytest.mark.parametrize("current", [False, True], ids=["pre-sync", "schema-created-current-subset"])
def test_populated_known_schema_preserves_rows_without_recreating_tables(db, current):
    fixture_schema(db, current)
    before = snapshot(db)
    statements = []
    sa.event.listen(db, "before_cursor_execute", lambda c, cur, sql, p, ctx, many: statements.append(sql))
    traverse(db)
    for table, rows in before.items():
        after = snapshot(db)[table][0]
        assert {key: after[key] for key in rows[0]} == rows[0]
    if not current:
        row = snapshot(db)["video_translation_jobs"][0]
        assert (row["llm_provider_id"], row["stage"], row["is_cleaned"], row["total_segments_count"]) == (
            "openai", "QUEUED", 0, 0)
    assert db.exec_driver_sql("PRAGMA foreign_key_check").all() == []
    assert not any(s.lstrip().upper().startswith(("DROP", "DELETE", "UPDATE", "CREATE")) for s in statements)
    stable = snapshot(db)
    statements.clear()
    traverse(db)  # Direct operation idempotence, not Alembic version-table replay.
    assert snapshot(db) == stable
    assert not any(s.lstrip().upper().startswith("ALTER") for s in statements)


@pytest.mark.parametrize("mismatch", ["missing-column", "wrong-identity", "missing-fk", "wrong-added-type",
                                      "wrong-added-default", "wrong-added-nullability"])
def test_unknown_schema_fails_before_any_schema_change_without_row_values(db, mismatch):
    fixture_schema(db, without_job_fk=mismatch == "missing-fk")
    if mismatch == "missing-column":
        db.exec_driver_sql("ALTER TABLE projects RENAME COLUMN title TO unknown_title")
    elif mismatch == "wrong-identity":
        db.exec_driver_sql("ALTER TABLE video_translation_jobs RENAME COLUMN id TO other_id")
    elif mismatch == "wrong-added-type":
        db.exec_driver_sql("ALTER TABLE segments ADD COLUMN irrelevant TEXT")
        db.exec_driver_sql("ALTER TABLE video_translation_jobs ADD COLUMN llm_provider_id INTEGER")
    elif mismatch == "wrong-added-default":
        db.exec_driver_sql("ALTER TABLE projects ADD COLUMN media_url TEXT DEFAULT 'private-fixture'")
    elif mismatch == "wrong-added-nullability":
        db.exec_driver_sql("ALTER TABLE projects ADD COLUMN media_url TEXT NOT NULL DEFAULT ''")
    before = snapshot(db)
    schema = db.exec_driver_sql("SELECT name, sql FROM sqlite_master ORDER BY name").all()
    with pytest.raises(RuntimeError, match="Historical schema mismatch.*inspect.*before retrying") as exc:
        traverse(db)
    assert "private-fixture" not in str(exc.value)
    assert snapshot(db) == before
    assert db.exec_driver_sql("SELECT name, sql FROM sqlite_master ORDER BY name").all() == schema


def test_partial_installation_is_not_silently_completed(db):
    db.exec_driver_sql("CREATE TABLE projects (id VARCHAR(36) NOT NULL PRIMARY KEY)")
    with Operations.context(MigrationContext.configure(db)):
        with pytest.raises(RuntimeError, match="Historical schema mismatch"):
            revision(NAMES[0]).upgrade()
    assert sa.inspect(db).get_table_names() == ['projects']


def test_generated_ddl_compiles_for_mysql_without_execution(db):
    compiled = []

    def capture(conn, clause, multiparams, params, options):
        if isinstance(clause, sa.schema.DDLElement):
            compiled.append(str(clause.compile(dialect=mysql.dialect())))

    sa.event.listen(db, "before_execute", capture)
    traverse(db)
    ddl = "\n".join(compiled)
    assert "CREATE TABLE projects" in ddl and "CREATE TABLE video_translation_jobs" in ddl
    assert "ADD COLUMN llm_provider_id VARCHAR(50)" in ddl
    assert "FOREIGN KEY(asset_id) REFERENCES video_assets (id) ON DELETE CASCADE" in ddl
    assert "DROP" not in ddl and "DELETE FROM" not in ddl


@pytest.mark.parametrize("name", NAMES)
def test_downgrade_refuses_ambiguous_ownership_without_deleting_data(db, name):
    fixture_schema(db, current=True)
    before = snapshot(db)
    with Operations.context(MigrationContext.configure(db)):
        with pytest.raises(RuntimeError, match="Cannot safely downgrade"):
            revision(name).downgrade()
    assert snapshot(db) == before
