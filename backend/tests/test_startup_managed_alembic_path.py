"""Actual Alembic traversal of an isolated startup-created schema."""
import hashlib
import sqlalchemy as sa
from alembic import command
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.util import load_python_file
from pathlib import Path
import pytest
from sqlalchemy.orm import Session

from app.database import Base
import app.models  # noqa: F401 - register the startup ORM tables in Base metadata
from app.models import APIKey, CatalogModel, CatalogRefreshRun, KeyModelAccess, Provider
from app.models.settings import AIModel, AIFunctionConfig
from tests.test_catalog_alembic_link import config_for


def test_startup_profile_rejects_duplicate_job_fk_without_project_fk():
    engine = sa.create_engine('sqlite:///:memory:')
    try:
        with engine.begin() as db:
            Base.metadata.create_all(db)
            inspector = sa.inspect(db)
            actual = inspector.get_foreign_keys('youtube_publications')
            job = next(fk for fk in actual if fk['constrained_columns'] == ['job_id'])
            reflected = [fk for fk in actual if fk['constrained_columns'] != ['project_id']]
            reflected.append({**job, 'name': 'duplicate_job_fk'})
            inspector.get_foreign_keys = lambda name: (
                reflected if name == 'youtube_publications' else sa.inspect(db).get_foreign_keys(name))
            helper = load_python_file(str(Path(__file__).parents[1] / 'alembic'),
                                      'progress_prerequisites.py')
            publication = helper._tables()[1][1]
            with pytest.raises(RuntimeError, match='schema'):
                helper._validate_table(inspector, publication,
                                       helper._additions()['youtube_publications'], db.dialect)
    finally:
        engine.dispose()


@pytest.mark.parametrize('definition', ['project_id) WHERE 0', 'project_id COLLATE NOCASE)'])
def test_startup_profile_rejects_unusable_project_index(definition):
    engine = sa.create_engine('sqlite:///:memory:')
    try:
        with engine.begin() as db:
            Base.metadata.create_all(db)
            db.exec_driver_sql('DROP INDEX ix_youtube_publications_project_id')
            db.exec_driver_sql('CREATE INDEX ix_youtube_publications_project_id '
                               f'ON youtube_publications({definition}')
            module = load_python_file(str(Path(__file__).parents[1] / 'alembic' / 'versions'),
                                      '20260908_add_youtube_progress.py')
            with Operations.context(MigrationContext.configure(db)):
                with pytest.raises(RuntimeError, match='schema'):
                    module.upgrade()
            assert db.exec_driver_sql('SELECT COUNT(*) FROM youtube_publications').scalar_one() == 0
    finally:
        engine.dispose()


def test_current_startup_schema_traverses_youtube_progress_without_rebuild(tmp_path):
    url = f'sqlite:///{tmp_path / "startup.sqlite"}'
    engine = sa.create_engine(url)
    with engine.begin() as db:
        Base.metadata.create_all(db)
        db.exec_driver_sql("INSERT INTO youtube_channels "
                           "(id, channel_name, credentials_json, is_active, created_at) "
                           "VALUES ('channel', 'Private', 'private-credential-fixture', 1, '2001-01-01')")
        db.exec_driver_sql("INSERT INTO youtube_publications "
                           "(id, channel_id, title, description, category_id, privacy_status, "
                           "status, progress, created_at, updated_at) "
                           "VALUES ('publication', 'channel', 'Private title', 'Private description', "
                           "'22', 'private', 'pending', 17, '2001-01-01', '2001-01-01')")
        before_row = db.exec_driver_sql(
            "SELECT * FROM youtube_publications WHERE id='publication'").one()
        before = set(sa.inspect(db).get_table_names())
    engine.dispose()
    command.upgrade(config_for(url, tmp_path), '20260908_youtube_progress')
    engine = sa.create_engine(url)
    try:
        with engine.connect() as db:
            assert before <= set(sa.inspect(db).get_table_names())
            assert db.exec_driver_sql(
                "SELECT * FROM youtube_publications WHERE id='publication'").one() == before_row
            assert db.exec_driver_sql('SELECT version_num FROM alembic_version').scalar_one() == (
                '20260908_youtube_progress')
    finally:
        engine.dispose()


@pytest.mark.parametrize('corrupt', [False, True])
def test_current_startup_converted_glossary_without_memory_replays_read_only(corrupt):
    engine = sa.create_engine('sqlite:///:memory:')
    try:
        with engine.begin() as db:
            Base.metadata.create_all(db)
            assert 'project_terminology_memory' not in sa.inspect(db).get_table_names()
            source, target = 'private source', 'private target'
            source_key = hashlib.sha256(source.encode()).hexdigest()
            target_key = hashlib.sha256(target.encode()).hexdigest()
            db.execute(sa.text(
                'INSERT INTO project_glossaries '
                '(id, project_id, source_term, translated_term, source_key, translation_key, '
                'term_type, confidence, approved, created_at, updated_at) VALUES '
                '(:id, :project, :source, :target, :source_key, :target_key, '
                ":type, 1.0, 1, '2001-01-01', '2001-01-01')"),
                {'id': 'g1', 'project': 'p1', 'source': source, 'target': target,
                 'source_key': '0' * 64 if corrupt else source_key,
                 'target_key': target_key, 'type': 'other'})
            before = db.exec_driver_sql(
                "SELECT sql FROM sqlite_master WHERE name='project_glossaries'").scalar_one()
            row_before = db.exec_driver_sql('SELECT * FROM project_glossaries').one()
            statements = []
            sa.event.listen(db, 'before_cursor_execute',
                            lambda c, cur, sql, p, ctx, many: statements.append(sql))
            module = load_python_file(str(Path(__file__).parents[1] / 'alembic' / 'versions'),
                                      '20260916_glossary_single_source.py')
            with Operations.context(MigrationContext.configure(db)):
                if corrupt:
                    with pytest.raises(RuntimeError, match='Historical schema mismatch') as exc:
                        module.upgrade()
                    assert source not in str(exc.value) and target not in str(exc.value)
                else:
                    module.upgrade()
            assert db.exec_driver_sql(
                "SELECT sql FROM sqlite_master WHERE name='project_glossaries'").scalar_one() == before
            assert db.exec_driver_sql('SELECT * FROM project_glossaries').one() == row_before
            assert not any(sql.lstrip().upper().startswith(
                ('CREATE', 'ALTER', 'DROP', 'INSERT', 'UPDATE', 'DELETE')) for sql in statements)
    finally:
        engine.dispose()


def test_current_startup_schema_traverses_catalog_chain_without_rebuild(tmp_path):
    url = f'sqlite:///{tmp_path / "startup-catalog.sqlite"}'
    engine = sa.create_engine(url)
    with engine.begin() as db:
        Base.metadata.create_all(db)
        with Session(db) as session:
            session.add(Provider(id='p1', name='Private provider', provider_type='llm'))
            session.add(AIModel(id='remote', provider_id='p1', model_name='Private model',
                                capabilities='["LLM"]'))
            session.add(AIFunctionConfig(function_id='translation', function_name='Translation',
                                         capability='LLM', primary_provider_id='p1', model_id='remote'))
            session.flush()
            session.add(APIKey(id='key1', provider_id='p1', ciphertext='synthetic-only',
                               fingerprint='a' * 64, masked_key='****'))
            session.add(CatalogModel(id='model1', provider_id='p1', remote_model_id='remote',
                                     source='discovered', capabilities=['LLM'],
                                     capability_status='KNOWN'))
            session.add(CatalogRefreshRun(id='run1', mode='explicit', status='complete', summary={}))
            session.flush()
            session.add(KeyModelAccess(key_id='key1', model_id='model1', provider_id='p1'))
            session.flush()
        tables = ('providers', 'ai_function_configs', 'ai_models', 'api_keys',
                  'ai_catalog_models', 'ai_key_model_access', 'ai_catalog_refresh_runs')
        before = {table: db.exec_driver_sql(
            'SELECT sql FROM sqlite_master WHERE type="table" AND name=:name',
            {'name': table}).scalar_one() for table in tables}
        before_rows = {table: db.exec_driver_sql(f'SELECT * FROM {table} ORDER BY 1').all()
                       for table in tables}
    engine.dispose()
    command.upgrade(config_for(url, tmp_path), 'head')
    engine = sa.create_engine(url)
    try:
        with engine.connect() as db:
            for table, ddl in before.items():
                assert db.exec_driver_sql(
                    'SELECT sql FROM sqlite_master WHERE type="table" AND name=:name',
                    {'name': table}).scalar_one() == ddl
                assert db.exec_driver_sql(f'SELECT * FROM {table} ORDER BY 1').all() == before_rows[table]
    finally:
        engine.dispose()


def test_current_startup_catalog_refuses_partial_index_before_writes():
    engine = sa.create_engine('sqlite:///:memory:')
    try:
        with engine.begin() as db:
            Base.metadata.create_all(db)
            db.exec_driver_sql('DROP INDEX ix_ai_catalog_models_provider_id')
            db.exec_driver_sql('CREATE INDEX ix_ai_catalog_models_provider_id '
                               'ON ai_catalog_models(provider_id) WHERE 0')
            module = load_python_file(str(Path(__file__).parents[1] / 'alembic' / 'versions'),
                                      '20260923_ai_catalog.py')
            statements = []
            sa.event.listen(db, 'before_cursor_execute',
                            lambda c, cur, sql, p, ctx, many: statements.append(sql))
            with Operations.context(MigrationContext.configure(db)):
                with pytest.raises(RuntimeError, match='Historical schema mismatch'):
                    module.upgrade()
            assert not any(sql.lstrip().upper().startswith(
                ('CREATE', 'ALTER', 'DROP', 'INSERT', 'UPDATE', 'DELETE')) for sql in statements)
    finally:
        engine.dispose()


def test_startup_catalog_validation_checks_only_catalog_foreign_keys():
    engine = sa.create_engine('sqlite:///:memory:')
    try:
        with engine.begin() as db:
            Base.metadata.create_all(db)
            helper = load_python_file(str(Path(__file__).parents[1] / 'alembic'),
                                      'catalog_prerequisites.py')
            assert helper.is_startup_final(db)
            db.exec_driver_sql(
                "INSERT INTO project_glossaries (id, project_id, source_term, translated_term, "
                "source_key, translation_key, term_type, confidence, approved, created_at, updated_at) "
                "VALUES ('g1', 'missing', 'a', 'b', :source, :target, 'other', 1, 1, "
                "'2001-01-01', '2001-01-01')",
                {'source': hashlib.sha256(b'a').hexdigest(),
                 'target': hashlib.sha256(b'b').hexdigest()})
            assert helper.is_startup_final(db)
            db.exec_driver_sql(
                "INSERT INTO api_keys (id, provider_id, ciphertext, fingerprint, masked_key, "
                "enabled, priority, runtime_status, request_count, success_count, failure_count, "
                "revision, created_at, updated_at) VALUES ('key', 'missing', 'synthetic', "
                ":fingerprint, '****', 1, 100, 'ready', 0, 0, 0, 1, '2001-01-01', '2001-01-01')",
                {'fingerprint': 'a' * 64})
            with pytest.raises(RuntimeError, match='Historical schema mismatch'):
                helper.is_startup_final(db)
    finally:
        engine.dispose()
