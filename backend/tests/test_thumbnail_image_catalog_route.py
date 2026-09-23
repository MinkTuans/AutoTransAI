"""Thumbnail image catalog cutover with synthetic credentials and no outbound traffic."""

import asyncio
import socket
from io import BytesIO

import httpx
import pytest
from PIL import Image
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.models import CatalogModel, KeyModelAccess, Provider, Project
from app.models.settings import AIFunctionConfig
from app.models.video_thumbnail import ThumbnailStatus, VideoThumbnail
from app.providers.base import GenerationResult
from app.providers.image.pollinations_provider import PollinationsImageProvider
from app.providers.image.local_image_provider import LocalImageProvider
from app.services.credential_service import CredentialService
from app.services.thumbnail_service import ThumbnailService


def png(width=3, height=2):
    output = BytesIO()
    Image.new("RGB", (width, height), (10, 20, 30)).save(output, format="PNG")
    return output.getvalue()


@pytest.fixture(autouse=True)
def no_outbound_network(monkeypatch, tmp_path):
    def reject(*args, **kwargs):
        raise AssertionError("thumbnail image test attempted outbound network")
    monkeypatch.setattr(socket.socket, "connect", reject)
    monkeypatch.setattr(httpx.AsyncClient, "request", reject)
    monkeypatch.setattr(httpx.AsyncClient, "get", reject)
    monkeypatch.setattr(httpx.AsyncClient, "post", reject)
    from app.services import thumbnail_service
    monkeypatch.setattr(thumbnail_service.settings, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(thumbnail_service.storage_service, "upload_file", reject)


@pytest.fixture
async def image_catalog(tmp_path):
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{tmp_path / 'images.db'}",
        pool_size=1, max_overflow=0, pool_timeout=0.3,
    )
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions.begin() as db:
        db.add_all(Provider(id=p, name=p, provider_type="image") for p in
                   ("openai", "fal", "pollinations", "local_image"))
        db.add(Project(id="project", title="Synthetic project"))
    yield sessions, tmp_path
    await engine.dispose()


async def add_keyed_model(db, path, provider, remote, secret):
    model = CatalogModel(provider_id=provider, remote_model_id=remote,
                         source="manual", capability_status="KNOWN", capabilities=["IMAGE_GENERATION"])
    db.add(model)
    await db.flush()
    key = await (await CredentialService.open(db, path)).create(provider, secret)
    await db.flush()
    db.add(KeyModelAccess(key_id=key.id, model_id=model.id, provider_id=provider))
    return model


def fake_registry(monkeypatch, adapters):
    from app.services import thumbnail_service
    monkeypatch.setattr(thumbnail_service, "get_registry", lambda: type("Registry", (), {
        "get_image": lambda _, provider_id: adapters.get(provider_id),
    })())


def fake_analysis(monkeypatch):
    async def analyze(*args, **kwargs):
        return {"title": "Story", "main_subject": "Subject", "main_event": "Event",
                "thumbnail_hook": "Hook", "important_visual_elements": []}
    monkeypatch.setattr(ThumbnailService, "analyze_content_with_llm", analyze)


@pytest.mark.asyncio
async def test_catalog_image_fallback_stores_actual_provider_format_and_dimensions(image_catalog, monkeypatch):
    sessions, path = image_catalog
    async with sessions.begin() as db:
        first = await add_keyed_model(db, path, "openai", "image-first", "synthetic-openai")
        await add_keyed_model(db, path, "fal", "fal-ai/image-backup", "synthetic-fal")
        db.add(AIFunctionConfig(function_id="image_generation", function_name="Image",
                                capability="IMAGE_GENERATION", primary_provider_id="openai", model_id=first.id))
    calls = []

    class Adapter:
        def __init__(self, provider):
            self.provider = provider

        async def generate_image(self, prompt, *, route_target, api_key, **kwargs):
            calls.append((self.provider, route_target.remote_model_id, api_key))
            if self.provider == "openai":
                return GenerationResult(False, provider_id="openai", error_code="HTTP_503",
                                        error_message="secret upstream body")
            return GenerationResult(True, provider_id="fal", metadata={"image_bytes": png()})

    fake_registry(monkeypatch, {p: Adapter(p) for p in ("openai", "fal")})
    fake_analysis(monkeypatch)
    from app.services import thumbnail_service
    monkeypatch.setattr(thumbnail_service.settings, "DATA_DIR", path)
    uploads = []

    async def upload_file(*, local_path, object_key, content_type, is_public):
        uploads.append((local_path.suffix, object_key, content_type, local_path.read_bytes()))
        return object_key, "/public/thumbnail.png"

    monkeypatch.setattr(thumbnail_service.storage_service, "upload_file", upload_file)
    async with sessions() as db:
        record = await ThumbnailService.create_thumbnail(db, project_id="project", sessions=sessions, data_dir=path)
    assert record.status == ThumbnailStatus.COMPLETED.value
    assert record.provider == "fal" and record.model == "fal-ai/image-backup"
    assert (record.width, record.height, record.aspect_ratio) == (3, 2, "3:2")
    assert calls == [("openai", "image-first", "synthetic-openai"),
                     ("fal", "fal-ai/image-backup", "synthetic-fal")]
    assert uploads == [(".png", uploads[0][1], "image/png", png())]
    assert uploads[0][1].endswith(".png")


@pytest.mark.asyncio
async def test_fal_pending_is_visible_and_blocks_duplicate_without_touching_active(image_catalog, monkeypatch):
    from app.services.ai_routing import RoutePending
    sessions, path = image_catalog
    async with sessions.begin() as db:
        selected = await add_keyed_model(db, path, "fal", "fal-ai/pending", "synthetic-fal")
        db.add(AIFunctionConfig(function_id="image_generation", function_name="Image",
                                capability="IMAGE_GENERATION", primary_provider_id="fal", model_id=selected.id))
        db.add(VideoThumbnail(id="old", project_id="project", status="completed", is_active=True,
                              thumbnail_url="/old.png", r2_key="old.png"))
    calls = []

    class PendingAdapter:
        async def generate_image(self, prompt, *, route_target, api_key, **kwargs):
            calls.append((route_target.remote_model_id, api_key))
            raise RoutePending("synthetic-fal should not leak")

    fake_registry(monkeypatch, {"fal": PendingAdapter()})
    fake_analysis(monkeypatch)
    from app.services import thumbnail_service
    monkeypatch.setattr(thumbnail_service.storage_service, "upload_file", lambda **kwargs: (
        (_ for _ in ()).throw(AssertionError("pending must not upload"))))
    async with sessions() as db:
        record = await ThumbnailService.create_thumbnail(db, project_id="project", sessions=sessions, data_dir=path)
        assert record.status == "provider_pending" and record.thumbnail_url is None
        assert record.is_active is False
        assert "synthetic-fal" not in (record.error_message or "")
        with pytest.raises(ValueError, match="already in progress"):
            await ThumbnailService.create_thumbnail(db, project_id="project", sessions=sessions, data_dir=path)
        old = await db.get(VideoThumbnail, "old")
        assert old.is_active and old.thumbnail_url == "/old.png"
    assert calls == [("fal-ai/pending", "synthetic-fal")]


@pytest.mark.asyncio
@pytest.mark.parametrize("in_progress", [ThumbnailStatus.GENERATING_PROMPT.value,
                                             ThumbnailStatus.UPLOADING.value])
async def test_intermediate_thumbnail_status_blocks_duplicate_launch(image_catalog, in_progress):
    sessions, path = image_catalog
    async with sessions.begin() as db:
        db.add(VideoThumbnail(id="working", project_id="project", status=in_progress, is_active=False))
    async with sessions() as db:
        with pytest.raises(ValueError, match="already in progress"):
            await ThumbnailService.create_thumbnail(db, project_id="project", sessions=sessions, data_dir=path)


@pytest.mark.asyncio
@pytest.mark.parametrize("override_provider,override_model", [
    ("fal", None), ("openai", "not-the-default"),
])
async def test_canonical_image_rejects_explicit_override_without_invoking_adapter(
    image_catalog, monkeypatch, override_provider, override_model,
):
    sessions, path = image_catalog
    async with sessions.begin() as db:
        selected = await add_keyed_model(db, path, "openai", "image-default", "synthetic-openai")
        db.add(AIFunctionConfig(function_id="image_generation", function_name="Image",
                                capability="IMAGE_GENERATION", primary_provider_id="openai", model_id=selected.id))
    called = []

    class Adapter:
        async def generate_image(self, *args, **kwargs):
            called.append(1)
            return GenerationResult(True, metadata={"image_bytes": png()})

    fake_registry(monkeypatch, {"openai": Adapter()})
    fake_analysis(monkeypatch)
    async with sessions() as db:
        record = await ThumbnailService.create_thumbnail(
            db, project_id="project", provider_id=override_provider, model_id=override_model,
            sessions=sessions, data_dir=path,
        )
    assert record.status == ThumbnailStatus.FAILED.value
    assert "differs from the configured image default" in (record.error_message or "")
    assert called == []


@pytest.mark.asyncio
@pytest.mark.parametrize("provider_hint,model_hint", [
    ("openai", None), (None, "image-default"),
])
async def test_canonical_image_accepts_matching_partial_override(
    image_catalog, monkeypatch, provider_hint, model_hint,
):
    sessions, path = image_catalog
    async with sessions.begin() as db:
        selected = await add_keyed_model(db, path, "openai", "image-default", "synthetic-openai")
        db.add(AIFunctionConfig(function_id="image_generation", function_name="Image",
                                capability="IMAGE_GENERATION", primary_provider_id="openai", model_id=selected.id))

    class Adapter:
        async def generate_image(self, prompt, *, route_target, api_key, **kwargs):
            return GenerationResult(True, provider_id="openai", metadata={"image_bytes": png()})

    fake_registry(monkeypatch, {"openai": Adapter()})
    fake_analysis(monkeypatch)
    from app.services import thumbnail_service

    async def upload_file(*, local_path, object_key, content_type, is_public):
        return object_key, "/public/partial.png"

    monkeypatch.setattr(thumbnail_service.storage_service, "upload_file", upload_file)
    async with sessions() as db:
        record = await ThumbnailService.create_thumbnail(
            db, project_id="project", provider_id=provider_hint, model_id=model_hint,
            sessions=sessions, data_dir=path,
        )
    assert record.status == "completed"
    assert record.provider == "openai" and record.model == "image-default"


@pytest.mark.asyncio
async def test_studio_legacy_pollinations_hint_does_not_override_catalog_default(image_catalog, monkeypatch):
    sessions, path = image_catalog
    async with sessions.begin() as db:
        selected = await add_keyed_model(db, path, "openai", "image-default", "synthetic-openai")
        db.add(AIFunctionConfig(function_id="image_generation", function_name="Image",
                                capability="IMAGE_GENERATION", primary_provider_id="openai", model_id=selected.id))
    calls = []

    class Adapter:
        async def generate_image(self, prompt, *, route_target, api_key, **kwargs):
            calls.append((route_target.remote_model_id, api_key))
            return GenerationResult(True, provider_id="openai", metadata={"image_bytes": png()})

    fake_registry(monkeypatch, {"openai": Adapter()})
    fake_analysis(monkeypatch)
    from app.services import thumbnail_service

    async def upload_file(*, local_path, object_key, content_type, is_public):
        return object_key, "/public/studio.png"

    monkeypatch.setattr(thumbnail_service.storage_service, "upload_file", upload_file)
    async with sessions() as db:
        record = await ThumbnailService.create_thumbnail(
            db, project_id="project", provider_id="pollinations", model_id="default",
            sessions=sessions, data_dir=path,
        )
    assert record.status == ThumbnailStatus.COMPLETED.value
    assert record.provider == "openai" and record.model == "image-default"
    assert calls == [("image-default", "synthetic-openai")]


@pytest.mark.asyncio
async def test_regenerate_historical_selection_hint_uses_current_default(image_catalog, monkeypatch):
    sessions, path = image_catalog
    async with sessions.begin() as db:
        selected = await add_keyed_model(db, path, "openai", "new-default", "synthetic-openai")
        db.add(AIFunctionConfig(function_id="image_generation", function_name="Image",
                                capability="IMAGE_GENERATION", primary_provider_id="openai", model_id=selected.id))
        db.add(VideoThumbnail(id="old", project_id="project", status="completed", is_active=True,
                              provider="fal", model="fal-ai/old", thumbnail_url="/old.png"))
    calls = []

    class Adapter:
        async def generate_image(self, prompt, *, route_target, api_key, **kwargs):
            calls.append(route_target.remote_model_id)
            return GenerationResult(True, provider_id="openai", metadata={"image_bytes": png()})

    fake_registry(monkeypatch, {"openai": Adapter()})
    fake_analysis(monkeypatch)
    from app.services import thumbnail_service

    async def upload_file(*, local_path, object_key, content_type, is_public):
        return object_key, "/public/new.png"

    monkeypatch.setattr(thumbnail_service.storage_service, "upload_file", upload_file)
    async with sessions() as db:
        record = await ThumbnailService.create_thumbnail(
            db, project_id="project", provider_id="fal", model_id="fal-ai/old",
            historical_selection_hint=True, sessions=sessions, data_dir=path,
        )
    assert record.status == ThumbnailStatus.COMPLETED.value
    assert record.provider == "openai" and record.model == "new-default"
    assert calls == ["new-default"]


@pytest.mark.asyncio
async def test_regenerate_endpoint_marks_only_implicit_old_selection_as_history(image_catalog, monkeypatch):
    from app.api.routes import thumbnail as route
    sessions, _ = image_catalog
    async with sessions.begin() as db:
        db.add(VideoThumbnail(id="old", project_id="project", status="completed",
                              provider="fal", model="fal-ai/old"))
    forwarded = []

    async def capture(**kwargs):
        forwarded.append(kwargs)
        return VideoThumbnail(id="new", project_id="project", status="provider_pending")

    monkeypatch.setattr(route.ThumbnailService, "create_thumbnail", capture)
    async with sessions() as db:
        await route.regenerate_thumbnail_endpoint("old", route.RegenerateThumbnailRequest(), db=db)
        await route.regenerate_thumbnail_endpoint(
            "old", route.RegenerateThumbnailRequest(provider_id="openai", model_id="new-default"), db=db,
        )
    assert forwarded[0]["provider_id"] == "fal"
    assert forwarded[0]["model_id"] == "fal-ai/old"
    assert forwarded[0]["historical_selection_hint"] is True
    assert forwarded[1]["provider_id"] == "openai"
    assert forwarded[1]["model_id"] == "new-default"
    assert forwarded[1]["historical_selection_hint"] is False


@pytest.mark.asyncio
@pytest.mark.parametrize("payload,expected_provider,expected_model", [
    ({"provider_id": "openai"}, "openai", None),
    ({"model_id": "new-default"}, None, "new-default"),
])
async def test_regenerate_partial_override_does_not_inherit_other_historical_field(
    image_catalog, monkeypatch, payload, expected_provider, expected_model,
):
    from app.api.routes import thumbnail as route
    sessions, _ = image_catalog
    async with sessions.begin() as db:
        db.add(VideoThumbnail(id="old", project_id="project", status="completed",
                              provider="fal", model="fal-ai/old"))
    forwarded = []

    async def capture(**kwargs):
        forwarded.append(kwargs)
        return VideoThumbnail(id="new", project_id="project", status="provider_pending")

    monkeypatch.setattr(route.ThumbnailService, "create_thumbnail", capture)
    async with sessions() as db:
        await route.regenerate_thumbnail_endpoint(
            "old", route.RegenerateThumbnailRequest(**payload), db=db,
        )
    assert forwarded[0]["provider_id"] == expected_provider
    assert forwarded[0]["model_id"] == expected_model
    assert forwarded[0]["historical_selection_hint"] is False


@pytest.mark.asyncio
@pytest.mark.parametrize("payload,expected_provider,expected_model", [
    ({"provider_id": "pollinations"}, "pollinations", "legacy-model"),
    ({"model_id": "new-model"}, "local_image", "new-model"),
])
async def test_legacy_regenerate_partial_override_retains_unsupplied_old_selection(
    image_catalog, monkeypatch, payload, expected_provider, expected_model,
):
    from app.api.routes import thumbnail as route
    from app.services import thumbnail_service

    sessions, path = image_catalog
    async with sessions.begin() as db:
        db.add(VideoThumbnail(id="old", project_id="project", status="completed",
                              provider="local_image", model="legacy-model"))
    fake_analysis(monkeypatch)
    monkeypatch.setattr(route, "async_session_factory", sessions)
    monkeypatch.setattr(route.settings, "DATA_DIR", path)

    class Adapter:
        requires_api_key = False

        def __init__(self, provider_id):
            self.provider_id = provider_id

        async def generate_image(self, prompt, *, model, **kwargs):
            return GenerationResult(True, provider_id=self.provider_id,
                                    metadata={"image_bytes": png(), "model": model})

    fake_registry(monkeypatch, {name: Adapter(name) for name in ("pollinations", "local_image")})

    async def upload_file(*, local_path, object_key, content_type, is_public):
        return object_key, "/public/legacy-regenerate.png"

    monkeypatch.setattr(thumbnail_service.storage_service, "upload_file", upload_file)
    async with sessions() as db:
        result = await route.regenerate_thumbnail_endpoint(
            "old", route.RegenerateThumbnailRequest(**payload), db=db,
        )
    assert result["success"] is True
    assert result["thumbnail"]["provider"] == expected_provider
    assert result["thumbnail"]["model"] == expected_model


@pytest.mark.asyncio
@pytest.mark.parametrize("payload,expected_provider,expected_model", [
    ({"provider_id": "pollinations"}, "pollinations", "legacy-model"),
    ({"model_id": "new-model"}, "local_image", "new-model"),
])
async def test_failed_legacy_partial_regenerate_persists_resolved_selection(
    image_catalog, monkeypatch, payload, expected_provider, expected_model,
):
    from app.api.routes import thumbnail as route
    from app.services import thumbnail_service

    sessions, path = image_catalog
    async with sessions.begin() as db:
        db.add(VideoThumbnail(id="old", project_id="project", status="completed",
                              provider="local_image", model="legacy-model"))
    fake_analysis(monkeypatch)
    monkeypatch.setattr(route, "async_session_factory", sessions)
    monkeypatch.setattr(route.settings, "DATA_DIR", path)

    async def no_sleep(_):
        return None

    monkeypatch.setattr(thumbnail_service.asyncio, "sleep", no_sleep)

    class FailingAdapter:
        requires_api_key = False

        def __init__(self, provider_id):
            self.provider_id = provider_id

        async def generate_image(self, prompt, *, model="default", **kwargs):
            return GenerationResult(False, provider_id=self.provider_id,
                                    error_code="HTTP_503", error_message="synthetic-secret upstream body")

    fake_registry(monkeypatch, {name: FailingAdapter(name) for name in ("pollinations", "local_image")})
    async with sessions() as db:
        result = await route.regenerate_thumbnail_endpoint(
            "old", route.RegenerateThumbnailRequest(**payload), db=db,
        )
    assert result["success"] is False
    assert result["thumbnail"]["status"] == "failed"
    assert result["thumbnail"]["provider"] == expected_provider
    assert result["thumbnail"]["model"] == expected_model
    assert "synthetic-secret" not in (result["thumbnail"]["error_message"] or "")
    async with sessions() as db:
        failed = await db.get(VideoThumbnail, result["thumbnail"]["id"])
        assert failed.provider == expected_provider and failed.model == expected_model


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", [
    {"provider_id": "openai"}, {"model_id": "image-default"},
])
async def test_canonical_regenerate_partial_override_ignores_historical_selection(
    image_catalog, monkeypatch, payload,
):
    from app.api.routes import thumbnail as route
    from app.services import thumbnail_service

    sessions, path = image_catalog
    async with sessions.begin() as db:
        selected = await add_keyed_model(db, path, "openai", "image-default", "synthetic-openai")
        db.add(AIFunctionConfig(function_id="image_generation", function_name="Image",
                                capability="IMAGE_GENERATION", primary_provider_id="openai", model_id=selected.id))
        db.add(VideoThumbnail(id="old", project_id="project", status="completed",
                              provider="fal", model="fal-ai/old"))
    fake_analysis(monkeypatch)
    monkeypatch.setattr(route, "async_session_factory", sessions)
    monkeypatch.setattr(route.settings, "DATA_DIR", path)

    class Adapter:
        async def generate_image(self, prompt, *, route_target, api_key, **kwargs):
            return GenerationResult(True, provider_id="openai", metadata={"image_bytes": png()})

    fake_registry(monkeypatch, {"openai": Adapter()})

    async def upload_file(*, local_path, object_key, content_type, is_public):
        return object_key, "/public/canonical-regenerate.png"

    monkeypatch.setattr(thumbnail_service.storage_service, "upload_file", upload_file)
    async with sessions() as db:
        result = await route.regenerate_thumbnail_endpoint(
            "old", route.RegenerateThumbnailRequest(**payload), db=db,
        )
    assert result["success"] is True, result["thumbnail"]["error_message"]
    assert result["thumbnail"]["provider"] == "openai"
    assert result["thumbnail"]["model"] == "image-default"


@pytest.mark.asyncio
async def test_thumbnail_target_id_cannot_escape_storage_path(image_catalog, monkeypatch):
    sessions, path = image_catalog
    fake_analysis(monkeypatch)
    with pytest.raises(ValueError, match="Invalid thumbnail target identifier"):
        async with sessions() as db:
            await ThumbnailService.create_thumbnail(
                db, project_id="../escape", sessions=sessions, data_dir=path,
            )


@pytest.mark.asyncio
async def test_existing_duplicate_in_progress_rows_still_block_new_launch(image_catalog):
    sessions, path = image_catalog
    async with sessions.begin() as db:
        db.add_all([
            VideoThumbnail(id="working-one", project_id="project", status="analyzing"),
            VideoThumbnail(id="working-two", project_id="project", status="uploading"),
        ])
    async with sessions() as db:
        with pytest.raises(ValueError, match="already in progress"):
            await ThumbnailService.create_thumbnail(db, project_id="project", sessions=sessions, data_dir=path)


@pytest.mark.asyncio
async def test_same_second_failed_regenerate_cannot_overwrite_active_object(image_catalog, monkeypatch):
    from datetime import datetime, timezone
    from app.services import thumbnail_service, storage_service as storage_module

    sessions, path = image_catalog
    async with sessions.begin() as db:
        selected = await add_keyed_model(db, path, "openai", "image-default", "synthetic-openai")
        db.add(AIFunctionConfig(function_id="image_generation", function_name="Image",
                                capability="IMAGE_GENERATION", primary_provider_id="openai", model_id=selected.id))

    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 9, 23, 12, 0, 0, tzinfo=tz or timezone.utc)

    monkeypatch.setattr(thumbnail_service, "datetime", FixedDatetime)
    monkeypatch.setattr(storage_module.settings, "STORAGE_ROOT", path / "storage")
    original_upload = storage_module.LocalStorageService.upload_file
    keys = []

    async def upload_file(*, local_path, object_key, content_type, is_public):
        keys.append(object_key)
        result = await original_upload(local_path, object_key, content_type, is_public)
        if len(keys) == 2:
            raise RuntimeError("synthetic upload completion failure")
        return result

    monkeypatch.setattr(thumbnail_service.storage_service, "upload_file", upload_file)
    images = [png(3, 2), png(4, 2)]

    class Adapter:
        async def generate_image(self, prompt, *, route_target, api_key, **kwargs):
            return GenerationResult(True, provider_id="openai",
                                    metadata={"image_bytes": images.pop(0)})

    fake_registry(monkeypatch, {"openai": Adapter()})
    fake_analysis(monkeypatch)
    async with sessions() as db:
        first = await ThumbnailService.create_thumbnail(db, project_id="project", sessions=sessions, data_dir=path)
        first_key, first_url = first.r2_key, first.thumbnail_url
        second = await ThumbnailService.create_thumbnail(db, project_id="project", sessions=sessions, data_dir=path)
        await db.refresh(first)
    assert first.is_active and first.thumbnail_url == first_url
    assert second.status == "failed" and not second.is_active
    assert len(keys) == 2 and keys[0] != keys[1]
    assert (path / "storage" / first_key).read_bytes() == png(3, 2)


@pytest.mark.asyncio
async def test_system_pollinations_catalog_identity_uses_keyless_default_argument(image_catalog, monkeypatch):
    sessions, path = image_catalog
    async with sessions.begin() as db:
        model = CatalogModel(provider_id="pollinations", remote_model_id="pollinations-default",
                             source="system", capability_status="KNOWN", capabilities=["IMAGE_GENERATION"])
        db.add(model)
        await db.flush()
        db.add(AIFunctionConfig(function_id="image_generation", function_name="Image",
                                capability="IMAGE_GENERATION", primary_provider_id="pollinations", model_id=model.id))
    seen = []

    class Keyless:
        async def generate_image(self, prompt, *, model, **kwargs):
            seen.append(model)
            return GenerationResult(True, provider_id="pollinations", metadata={"image_bytes": png()})

    fake_registry(monkeypatch, {"pollinations": Keyless()})
    fake_analysis(monkeypatch)
    from app.services import thumbnail_service

    async def upload_file(*, local_path, object_key, content_type, is_public):
        return object_key, "/public/system.png"

    monkeypatch.setattr(thumbnail_service.storage_service, "upload_file", upload_file)
    async with sessions() as db:
        record = await ThumbnailService.create_thumbnail(db, project_id="project", sessions=sessions, data_dir=path)
    assert record.status == ThumbnailStatus.COMPLETED.value
    assert record.provider == "pollinations" and record.model == "pollinations-default"
    assert seen == ["default"]


@pytest.mark.asyncio
async def test_legacy_pollinations_default_remains_on_legacy_path_until_import(image_catalog, monkeypatch):
    sessions, path = image_catalog
    async with sessions.begin() as db:
        await add_keyed_model(db, path, "openai", "keyed-but-unselected", "synthetic-openai")
        db.add(AIFunctionConfig(function_id="image_generation", function_name="Image",
                                capability="IMAGE_GENERATION", primary_provider_id="pollinations",
                                model_id="pollinations-default"))
    calls = []

    class LegacyPollinations:
        provider_id = "pollinations"
        requires_api_key = False

        async def generate_image(self, prompt, *, model, **kwargs):
            calls.append(model)
            return GenerationResult(True, provider_id="pollinations",
                                    metadata={"image_bytes": png(), "model": model})

    fake_registry(monkeypatch, {"pollinations": LegacyPollinations()})
    fake_analysis(monkeypatch)
    from app.services import thumbnail_service

    async def upload_file(*, local_path, object_key, content_type, is_public):
        return object_key, "/public/legacy.png"

    monkeypatch.setattr(thumbnail_service.storage_service, "upload_file", upload_file)
    async with sessions() as db:
        record = await ThumbnailService.create_thumbnail(db, project_id="project", sessions=sessions, data_dir=path)
    assert record.status == ThumbnailStatus.COMPLETED.value
    assert record.provider == "pollinations" and calls == ["default"]


@pytest.mark.asyncio
async def test_invalid_canonical_image_bytes_advance_to_compatible_backup(image_catalog, monkeypatch):
    sessions, path = image_catalog
    async with sessions.begin() as db:
        first = await add_keyed_model(db, path, "openai", "image-invalid", "synthetic-openai")
        await add_keyed_model(db, path, "fal", "fal-ai/image-valid", "synthetic-fal")
        db.add(AIFunctionConfig(function_id="image_generation", function_name="Image",
                                capability="IMAGE_GENERATION", primary_provider_id="openai", model_id=first.id))
    calls = []

    class Adapter:
        def __init__(self, provider):
            self.provider = provider

        async def generate_image(self, prompt, *, route_target, api_key, **kwargs):
            calls.append(route_target.remote_model_id)
            content = b"\x89PNG\r\n\x1a\n" + b"x" * 24 if self.provider == "openai" else png()
            return GenerationResult(True, provider_id=self.provider, metadata={"image_bytes": content})

    fake_registry(monkeypatch, {p: Adapter(p) for p in ("openai", "fal")})
    fake_analysis(monkeypatch)
    from app.services import thumbnail_service

    async def upload_file(*, local_path, object_key, content_type, is_public):
        return object_key, "/public/valid.png"

    monkeypatch.setattr(thumbnail_service.storage_service, "upload_file", upload_file)
    async with sessions() as db:
        record = await ThumbnailService.create_thumbnail(db, project_id="project", sessions=sessions, data_dir=path)
    assert record.status == ThumbnailStatus.COMPLETED.value and record.provider == "fal"
    assert calls == ["image-invalid", "fal-ai/image-valid"]


@pytest.mark.asyncio
async def test_keyless_adapter_logs_and_errors_omit_prompt_and_upstream_exception(monkeypatch, capsys, tmp_path):
    async def reject_get(*args, **kwargs):
        raise RuntimeError("synthetic-secret in exception")

    async def reject_ffmpeg(*args, **kwargs):
        raise RuntimeError("synthetic-secret in ffmpeg")

    monkeypatch.setattr(httpx.AsyncClient, "get", reject_get)
    from app.providers.image import local_image_provider
    monkeypatch.setattr(local_image_provider, "run_ffmpeg_with_progress_async", reject_ffmpeg)
    from types import SimpleNamespace
    monkeypatch.setattr(local_image_provider, "get_settings", lambda: SimpleNamespace(DATA_DIR=tmp_path))
    prompt = "synthetic-secret in prompt"
    pollinations = await PollinationsImageProvider().generate_image(prompt)
    local = await LocalImageProvider().generate_image(prompt)
    output = capsys.readouterr().out
    assert not pollinations.success and not local.success
    assert "synthetic-secret" not in output
    assert "synthetic-secret" not in (pollinations.error_message or "")
    assert "synthetic-secret" not in (local.error_message or "")


@pytest.mark.asyncio
async def test_generate_endpoint_exposes_pending_status_without_success(monkeypatch):
    from app.api.routes import thumbnail as route

    async def create(**kwargs):
        return VideoThumbnail(id="pending", project_id="project", status="provider_pending",
                              error_message="Image provider accepted the request; completion is not yet confirmed.",
                              is_active=False)

    monkeypatch.setattr(route.ThumbnailService, "create_thumbnail", create)
    result = await route.generate_thumbnail_endpoint(
        route.GenerateThumbnailRequest(project_id="project"), db=object(),
    )
    assert result["success"] is False
    assert result["thumbnail"]["status"] == "provider_pending"
    assert result["thumbnail"]["thumbnail_url"] is None


@pytest.mark.asyncio
async def test_generate_endpoint_unexpected_error_does_not_leak_exception(monkeypatch, capsys):
    from fastapi import HTTPException
    from app.api.routes import thumbnail as route

    async def create(**kwargs):
        raise RuntimeError("synthetic-secret provider body")

    monkeypatch.setattr(route.ThumbnailService, "create_thumbnail", create)
    with pytest.raises(HTTPException) as error:
        await route.generate_thumbnail_endpoint(
            route.GenerateThumbnailRequest(project_id="project"), db=object(),
        )
    assert error.value.status_code == 500
    assert "synthetic-secret" not in str(error.value.detail)
    assert "synthetic-secret" not in capsys.readouterr().out
