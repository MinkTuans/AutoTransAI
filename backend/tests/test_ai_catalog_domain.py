"""Catalog invariants against a disposable database, with real FK enforcement."""
import importlib.util
import io
from pathlib import Path

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.util import load_python_file
from sqlalchemy import create_engine, event, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import app.models as models


@pytest.fixture
def catalog():
    assert hasattr(models, "CatalogModel"), "canonical catalog model is missing"
    return models.CatalogModel, models.APIKey, models.KeyModelAccess


@pytest.fixture(params=["orm", "migration"])
def db(catalog, request):
    engine = create_engine("sqlite://")
    event.listen(engine, "connect", lambda connection, _: connection.execute("PRAGMA foreign_keys=ON"))
    if request.param == "migration":
        with engine.begin() as connection:
            legacy_helper().ensure(connection)
            with Operations.context(MigrationContext.configure(connection)):
                migration().upgrade()
                migration("20260923_catalog_refresh").upgrade()
                migration("20260923_catalog_evidence").upgrade()
                migration("20260923_provider_key_requirement").upgrade()
                migration("20260923_key_rotation_domain").upgrade()
    else:
        models.Provider.__table__.create(engine)
        for model in catalog[:2]:
            model.__table__.create(engine)
        catalog[2].__table__.create(engine)
    with Session(engine) as session:
        session.add_all([models.Provider(id=p, name=p, provider_type="llm") for p in ("one", "two")])
        session.commit()
        yield session
    engine.dispose()


def test_remote_identity_is_provider_scoped_and_unique(catalog, db):
    Model, _, _ = catalog
    db.add_all([Model(provider_id="one", remote_model_id="shared"), Model(provider_id="two", remote_model_id="shared")])
    db.commit()
    assert len(db.scalars(select(Model)).all()) == 2
    db.add(Model(provider_id="one", remote_model_id="shared"))
    with pytest.raises(IntegrityError):
        db.commit()


def test_multiple_keys_share_models_and_key_deletion_preserves_catalog(catalog, db):
    Model, Key, Access = catalog
    model = Model(provider_id="one", remote_model_id="shared")
    keys = [Key(provider_id="one", ciphertext="encrypted", fingerprint=str(n), masked_key="****") for n in range(2)]
    db.add_all([model, *keys])
    db.flush()
    model_id = model.id
    db.add_all([Access(key_id=key.id, model_id=model.id, provider_id="one") for key in keys])
    db.commit()
    db.delete(keys[0])
    db.commit()
    assert db.get(Model, model_id) is not None
    assert len(db.scalars(select(Access)).all()) == 1
    db.delete(keys[1])
    db.commit()
    assert db.get(Model, model_id) is not None
    assert db.scalars(select(Access)).all() == []


def test_access_pair_is_unique_and_cannot_reference_missing_rows(catalog, db):
    Model, Key, Access = catalog
    key = Key(provider_id="one", ciphertext="encrypted", fingerprint="f", masked_key="****")
    model = Model(provider_id="one", remote_model_id="remote")
    db.add_all([key, model])
    db.flush()
    ids = key.id, model.id
    db.add(Access(key_id=ids[0], model_id=ids[1], provider_id="one"))
    db.commit()
    db.add(Access(key_id=ids[0], model_id=ids[1], provider_id="one"))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    db.add(Access(key_id="missing", model_id=ids[1], provider_id="one"))
    with pytest.raises(IntegrityError):
        db.commit()


def test_remote_ids_keep_case_and_prefix_and_require_provider(catalog, db):
    Model, _, _ = catalog
    db.add_all([Model(provider_id="one", remote_model_id=remote) for remote in ("models/Case", "models/case")])
    db.commit()
    assert set(db.scalars(select(Model.remote_model_id))) == {"models/Case", "models/case"}
    db.add(Model(provider_id="absent", remote_model_id="remote"))
    with pytest.raises(IntegrityError):
        db.commit()


@pytest.mark.parametrize("claimed_provider", ["one", "two"])
def test_cross_provider_access_is_rejected_by_database(catalog, db, claimed_provider):
    Model, Key, Access = catalog
    key = Key(provider_id="one", ciphertext="encrypted", fingerprint="f", masked_key="****")
    model = Model(provider_id="two", remote_model_id="remote")
    db.add_all([key, model])
    db.flush()
    access = Access(key_id=key.id, model_id=model.id)
    access.provider_id = claimed_provider
    db.add(access)
    with pytest.raises(IntegrityError):
        db.flush()


def migration(name="20260923_ai_catalog"):
    path = Path(__file__).parents[1] / f"alembic/versions/{name}.py"
    assert path.exists(), "additive catalog migration is missing"
    spec = importlib.util.spec_from_file_location("catalog_migration", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def legacy_helper():
    return load_python_file(str(Path(__file__).parents[1] / 'alembic'),
                            'catalog_prerequisites.py')


def test_migration_is_additive_and_reversible_on_disposable_sqlite():
    revision = migration()
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        legacy_helper().ensure(connection)
        connection.execute(text("INSERT INTO ai_models VALUES "
                                "('historical-model', 'provider', 'Historical', '[\"LLM\"]', "
                                "0, 0, 1, NULL, '2001-02-03')"))
        with Operations.context(MigrationContext.configure(connection)):
            revision.upgrade()
            connection.execute(text("SELECT * FROM ai_key_model_access"))
            revision.downgrade()
        assert connection.execute(text("SELECT id FROM ai_models")).scalar() == "historical-model"
    engine.dispose()


def test_migration_emits_mysql_ddl_without_connecting():
    revision = migration()
    output = io.StringIO()
    context = MigrationContext.configure(dialect_name="mysql", opts={"as_sql": True, "output_buffer": output})
    with Operations.context(context):
        revision.upgrade()
    sql = output.getvalue()
    assert "CREATE TABLE ai_catalog_models" in sql
    assert "UNIQUE (provider_id, remote_model_id)" in sql
    assert "ON DELETE CASCADE" in sql
    assert "FOREIGN KEY(key_id, provider_id) REFERENCES api_keys (id, provider_id)" in sql
    assert "FOREIGN KEY(model_id, provider_id) REFERENCES ai_catalog_models (id, provider_id)" in sql
    assert "CREATE TABLE providers" not in sql
    assert "CREATE TABLE ai_function_configs" not in sql
    assert "CREATE TABLE ai_models" not in sql
    assert "DROP " not in sql and "ALTER " not in sql
