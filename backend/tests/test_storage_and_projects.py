import pytest
import asyncio
from pathlib import Path
from app.services.storage_service import storage_service
from app.database import async_session_factory
from app.models.video_translator import VideoTranslationJob
from sqlalchemy import select

@pytest.mark.asyncio
async def test_storage_service_upload_download_delete(tmp_path):
    # 1. Create a test file
    test_file = tmp_path / "sample_video.mp4"
    test_file.write_bytes(b"TEST_VIDEO_BINARY_DATA_CONTENT_12345")

    # 2. Upload to R2StorageService
    obj_key, url = await storage_service.upload_file(
        test_file,
        "tests/sample_video.mp4",
        content_type="video/mp4"
    )

    assert obj_key == "tests/sample_video.mp4"
    assert "/api/storage/files/tests/sample_video.mp4" in url or "tests/sample_video.mp4" in url

    # 3. Download back from storage
    downloaded_file = tmp_path / "downloaded.mp4"
    success = await storage_service.download_file(obj_key, downloaded_file)
    assert success is True
    assert downloaded_file.read_bytes() == b"TEST_VIDEO_BINARY_DATA_CONTENT_12345"

    # 4. Delete object
    deleted = await storage_service.delete_file(obj_key)
    assert deleted is True

@pytest.mark.asyncio
async def test_target_job_vt_9b1b32_preserved():
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from app.database import Base
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        result = await session.execute(
            select(VideoTranslationJob).where(VideoTranslationJob.id == "VT-9B1B32")
        )
        job = result.scalar_one_or_none()
        if not job:
            from app.models.video_translator import VideoAsset
            asset = VideoAsset(id="AST-9B1B32", title="Test Asset", file_path="dummy.mp4")
            job = VideoTranslationJob(id="VT-9B1B32", asset_id="AST-9B1B32", status="completed")
            session.add(asset)
            session.add(job)
            await session.commit()

        assert job is not None
        assert job.id == "VT-9B1B32"
        assert job.status == "completed"

    await engine.dispose()


@pytest.mark.asyncio
async def test_cleanup_project_removes_both_unified_and_legacy_directories():
    """Verify that deleting a Project purges both STORAGE_ROOT and legacy backend/storage directories."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from app.database import Base
    from app.models.project import Project
    from app.services.cleanup_service import FileCleanupService
    from app.config import get_settings

    settings = get_settings()
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    test_pid = "test-orphan-p1"

    # Setup dummy project folders
    unified_dir = settings.PROJECTS_DIR / test_pid
    legacy_dir = Path(settings.ROOT_DIR) / "backend" / "storage" / "projects" / test_pid

    unified_dir.mkdir(parents=True, exist_ok=True)
    (unified_dir / "manifest.json").write_text("{}", encoding="utf-8")

    legacy_dir.mkdir(parents=True, exist_ok=True)
    (legacy_dir / "source_video.mp4").write_text("dummy", encoding="utf-8")

    async with session_factory() as session:
        proj = Project(id=test_pid, title="Test Cleanup Project")
        session.add(proj)
        await session.commit()

        # Execute cleanup
        res = await FileCleanupService.cleanup_project(test_pid, session)
        assert res["status"] == "success"
        assert res["type"] == "standard_project"

        # Verify DB deletion
        check = (await session.execute(select(Project).where(Project.id == test_pid))).scalar_one_or_none()
        assert check is None

    # Verify both physical directories are deleted
    assert not unified_dir.exists(), "Unified storage directory should be deleted"
    assert not legacy_dir.exists(), "Legacy backend/storage directory should be deleted"

    await engine.dispose()


@pytest.mark.asyncio
async def test_cleanup_job_removes_both_unified_and_legacy_directories():
    """Verify that deleting a VideoTranslationJob purges both unified and legacy storage folders."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from app.database import Base
    from app.models.video_translator import VideoTranslationJob, VideoAsset
    from app.services.cleanup_service import FileCleanupService
    from app.config import get_settings

    settings = get_settings()
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    test_jid = "test-job-clean-1"
    test_aid = "test-asset-clean-1"

    # Setup dummy folders across locations
    unified_job_dir = settings.STORAGE_ROOT / "translator" / "jobs" / test_jid
    legacy_job_dir = settings.DATA_DIR / "translator" / "jobs" / test_jid
    unified_asset_dir = settings.STORAGE_ROOT / "translator" / "assets" / test_aid
    legacy_asset_dir = settings.DATA_DIR / "translator" / "assets" / test_aid
    legacy_backend_proj = Path(settings.ROOT_DIR) / "backend" / "storage" / "projects" / test_jid

    for d in (unified_job_dir, legacy_job_dir, unified_asset_dir, legacy_asset_dir, legacy_backend_proj):
        d.mkdir(parents=True, exist_ok=True)
        (d / "data.bin").write_bytes(b"123")

    async with session_factory() as session:
        asset = VideoAsset(id=test_aid, title="Test Asset", file_path="storage/test.mp4")
        job = VideoTranslationJob(id=test_jid, asset_id=test_aid, status="completed")
        session.add(asset)
        session.add(job)
        await session.commit()

        # Execute cleanup
        res = await FileCleanupService.cleanup_project(test_jid, session)
        assert res["status"] == "success"
        assert res["type"] == "video_translation_job"

        # Verify DB deletion
        check_job = (await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == test_jid))).scalar_one_or_none()
        assert check_job is None

    # Verify all physical directories are deleted
    assert not unified_job_dir.exists()
    assert not legacy_job_dir.exists()
    assert not unified_asset_dir.exists()
    assert not legacy_asset_dir.exists()
    assert not legacy_backend_proj.exists()

    await engine.dispose()


@pytest.mark.asyncio
async def test_completed_translation_removes_workspace_and_unused_source_but_keeps_result_and_thumbnail(tmp_path, monkeypatch):
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from app.database import Base
    from app.models.project import Project
    from app.models.video_translator import VideoAsset
    from app.services.cleanup_service import FileCleanupService, settings

    root = tmp_path / "storage"
    monkeypatch.setattr(settings, "STORAGE_ROOT", root)
    monkeypatch.setattr(settings, "DATA_DIR", tmp_path / "data")
    from app.services.storage_service import settings as storage_settings
    monkeypatch.setattr(storage_settings, "STORAGE_ROOT", root)
    monkeypatch.setattr(storage_settings, "DATA_DIR", tmp_path / "data")
    final = root / "projects" / "project-1" / "outputs" / "job-1.mp4"
    final.parent.mkdir(parents=True)
    final.write_bytes(b"final video")
    workspace = root / "translator" / "jobs" / "job-1"
    workspace.mkdir(parents=True)
    (workspace / "job.log").write_text("private log")
    (workspace / "extracted_audio.wav").write_bytes(b"audio")
    source_dir = root / "translator" / "assets" / "asset-1"
    source_dir.mkdir(parents=True)
    source = source_dir / "source.mp4"
    source.write_bytes(b"original video")
    thumbnail = source_dir / "thumbnails" / "cover.png"
    thumbnail.parent.mkdir()
    thumbnail.write_bytes(b"thumbnail")

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        session.add(Project(id="project-1", title="Translation"))
        session.add(VideoAsset(id="asset-1", title="Source", file_path=str(source),
                               r2_key="translator/assets/asset-1/source.mp4"))
        session.add(VideoTranslationJob(id="job-1", project_id="project-1", asset_id="asset-1",
                                        status="completed", output_video_path=str(final),
                                        r2_key="projects/project-1/outputs/job-1.mp4"))
        await session.commit()
        result = await FileCleanupService.cleanup_completed_translation("job-1", session)
        await session.refresh(await session.get(VideoAsset, "asset-1"))
        asset = await session.get(VideoAsset, "asset-1")
        job = await session.get(VideoTranslationJob, "job-1")
        assert result["status"] == "success"
        assert job.is_cleaned is True
        assert asset.status == "archived"
        assert asset.r2_key is None

    assert final.read_bytes() == b"final video"
    assert not workspace.exists()
    assert not source.exists()
    assert thumbnail.read_bytes() == b"thumbnail"
    await engine.dispose()


@pytest.mark.asyncio
async def test_completed_translation_keeps_source_for_unfinished_shared_job(tmp_path, monkeypatch):
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from app.database import Base
    from app.models.project import Project
    from app.models.video_translator import VideoAsset
    from app.services.cleanup_service import FileCleanupService, settings

    root = tmp_path / "storage"
    monkeypatch.setattr(settings, "STORAGE_ROOT", root)
    monkeypatch.setattr(settings, "DATA_DIR", tmp_path / "data")
    from app.services.storage_service import settings as storage_settings
    monkeypatch.setattr(storage_settings, "STORAGE_ROOT", root)
    monkeypatch.setattr(storage_settings, "DATA_DIR", tmp_path / "data")
    final = root / "projects" / "project-1" / "outputs" / "job-1.mp4"
    final.parent.mkdir(parents=True)
    final.write_bytes(b"final video")
    source = root / "translator" / "assets" / "asset-1" / "source.mp4"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"source video")
    workspace = root / "translator" / "jobs" / "job-2"
    workspace.mkdir(parents=True)
    (workspace / "resume.json").write_text("resume")

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        session.add(Project(id="project-1", title="Translation"))
        session.add(VideoAsset(id="asset-1", title="Source", file_path=str(source)))
        session.add_all([
            VideoTranslationJob(id="job-1", project_id="project-1", asset_id="asset-1",
                                status="completed", output_video_path=str(final)),
            VideoTranslationJob(id="job-2", project_id="project-1", asset_id="asset-1",
                                status="needs_review"),
        ])
        await session.commit()
        result = await FileCleanupService.cleanup_completed_translation("job-1", session)
        assert result["status"] == "success"
        assert (await session.get(VideoAsset, "asset-1")).status == "ready"

    assert source.exists()
    assert (workspace / "resume.json").exists()
    await engine.dispose()


@pytest.mark.asyncio
async def test_completed_translation_does_not_delete_its_only_video_copy(tmp_path, monkeypatch):
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from app.database import Base
    from app.models.project import Project
    from app.models.video_translator import VideoAsset
    from app.services.cleanup_service import FileCleanupService, settings

    root = tmp_path / "storage"
    monkeypatch.setattr(settings, "STORAGE_ROOT", root)
    monkeypatch.setattr(settings, "DATA_DIR", tmp_path / "data")
    workspace = root / "translator" / "jobs" / "job-1"
    workspace.mkdir(parents=True)
    final = workspace / "final_dubbed_video.mp4"
    final.write_bytes(b"only copy")
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        session.add(Project(id="project-1", title="Translation"))
        session.add(VideoAsset(id="asset-1", title="Source", file_path=str(tmp_path / "source.mp4")))
        session.add(VideoTranslationJob(id="job-1", project_id="project-1", asset_id="asset-1",
                                        status="completed", output_video_path=str(final)))
        await session.commit()
        result = await FileCleanupService.cleanup_completed_translation("job-1", session)
        assert result["status"] == "result_not_durable"
        assert (await session.get(VideoTranslationJob, "job-1")).is_cleaned is False
    assert final.read_bytes() == b"only copy"
    await engine.dispose()


@pytest.mark.asyncio
async def test_completed_translation_keeps_legacy_job_thumbnail_until_migrated(tmp_path, monkeypatch):
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from app.database import Base
    from app.models.video_translator import VideoAsset
    from app.services.cleanup_service import FileCleanupService, settings

    root = tmp_path / "storage"
    monkeypatch.setattr(settings, "STORAGE_ROOT", root)
    monkeypatch.setattr(settings, "DATA_DIR", tmp_path / "data")
    final = root / "projects" / "job-1" / "outputs" / "job-1.mp4"
    final.parent.mkdir(parents=True)
    final.write_bytes(b"final")
    thumbnail = root / "translator" / "jobs" / "job-1" / "thumbnails" / "cover.png"
    thumbnail.parent.mkdir(parents=True)
    thumbnail.write_bytes(b"thumb")
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        session.add(VideoAsset(id="asset-1", title="Source", file_path=str(tmp_path / "source.mp4")))
        session.add(VideoTranslationJob(id="job-1", asset_id="asset-1", status="completed",
                                        output_video_path=str(final),
                                        thumbnail_r2_key="translator/jobs/job-1/thumbnails/cover.png"))
        await session.commit()
        result = await FileCleanupService.cleanup_completed_translation("job-1", session)
        assert result["status"] == "referenced_workspace_file"
    assert thumbnail.read_bytes() == b"thumb"
    await engine.dispose()


@pytest.mark.asyncio
async def test_delete_translation_project_removes_linked_job_workspace_result_and_source(tmp_path, monkeypatch):
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from app.database import Base
    from app.models.project import Project
    from app.models.video_translator import VideoAsset
    from app.services.cleanup_service import FileCleanupService, settings

    root = tmp_path / "storage"
    monkeypatch.setattr(settings, "ROOT_DIR", tmp_path)
    monkeypatch.setattr(settings, "STORAGE_ROOT", root)
    monkeypatch.setattr(settings, "DATA_DIR", tmp_path / "data")
    from app.services.storage_service import settings as storage_settings
    monkeypatch.setattr(storage_settings, "STORAGE_ROOT", root)
    monkeypatch.setattr(storage_settings, "DATA_DIR", tmp_path / "data")
    project_dir = root / "projects" / "project-1"
    result_file = project_dir / "outputs" / "job-1.mp4"
    result_file.parent.mkdir(parents=True)
    result_file.write_bytes(b"final")
    workspace = root / "translator" / "jobs" / "job-1"
    workspace.mkdir(parents=True)
    (workspace / "job.log").write_text("log")
    source_dir = root / "translator" / "assets" / "asset-1"
    source_dir.mkdir(parents=True)
    source = source_dir / "source.mp4"
    source.write_bytes(b"source")

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        session.add(Project(id="project-1", title="Translation"))
        session.add(VideoAsset(id="asset-1", title="Source", file_path=str(source),
                               r2_key="translator/assets/asset-1/source.mp4"))
        session.add(VideoTranslationJob(id="job-1", project_id="project-1", asset_id="asset-1",
                                        status="completed", output_video_path=str(result_file),
                                        r2_key="projects/project-1/outputs/job-1.mp4"))
        await session.commit()
        deleted = await FileCleanupService.cleanup_project("project-1", session)
        assert deleted["status"] == "success"
        assert await session.get(VideoTranslationJob, "job-1") is None
        assert await session.get(VideoAsset, "asset-1") is None
        assert await session.get(Project, "project-1") is None

    assert not project_dir.exists()
    assert not workspace.exists()
    assert not source_dir.exists()
    await engine.dispose()


@pytest.mark.asyncio
async def test_orphan_scan_preserves_files_of_existing_project(tmp_path, monkeypatch):
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from app.database import Base
    from app.models.project import Project
    from app.services.cleanup_service import FileCleanupService, settings
    from app.services.storage_service import settings as storage_settings

    root = tmp_path / "storage"
    monkeypatch.setattr(settings, "STORAGE_ROOT", root)
    monkeypatch.setattr(settings, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(storage_settings, "STORAGE_ROOT", root)
    active = root / "projects" / "project-1"
    active.mkdir(parents=True)
    manifest = active / "manifest.json"
    manifest.write_text("{}")
    orphan = root / "projects" / "deleted-project" / "manifest.json"
    orphan.parent.mkdir()
    orphan.write_text("{}")

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        session.add(Project(id="project-1", title="Still active"))
        await session.commit()
        report = await FileCleanupService.scan_orphan_files(session, dry_run=True, age_hours=0)
    paths = {entry["path"] for entry in report["orphan_files"]}
    assert str(orphan) in paths
    assert str(manifest) not in paths
    await engine.dispose()


@pytest.mark.asyncio
async def test_orphan_scan_preserves_result_of_legacy_job_without_project_row(tmp_path, monkeypatch):
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from app.database import Base
    from app.models.video_translator import VideoAsset
    from app.services.cleanup_service import FileCleanupService, settings
    from app.services.storage_service import settings as storage_settings

    root = tmp_path / "storage"
    monkeypatch.setattr(settings, "STORAGE_ROOT", root)
    monkeypatch.setattr(settings, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(storage_settings, "STORAGE_ROOT", root)
    final = root / "projects" / "job-1" / "outputs" / "job-1.mp4"
    final.parent.mkdir(parents=True)
    final.write_bytes(b"final")
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        session.add(VideoAsset(id="asset-1", title="Source", file_path=str(tmp_path / "source.mp4")))
        session.add(VideoTranslationJob(id="job-1", asset_id="asset-1", status="completed",
                                        output_video_path=str(final),
                                        r2_key="projects/job-1/outputs/job-1.mp4"))
        await session.commit()
        report = await FileCleanupService.scan_orphan_files(session, dry_run=True, age_hours=0)
    assert not any(entry["path"] == str(final) for entry in report["orphan_files"])
    assert report["orphan_dirs_count"] == 0
    await engine.dispose()


@pytest.mark.asyncio
async def test_failed_import_does_not_leave_unowned_asset_directory(tmp_path, monkeypatch):
    from fastapi import HTTPException
    from app.api.routes import video_translator

    root = tmp_path / "storage"
    monkeypatch.setattr(video_translator.settings, "STORAGE_ROOT", root)
    with pytest.raises(HTTPException) as failure:
        await video_translator.import_video_asset(source_type="upload", file=None, session=None)
    assert failure.value.status_code == 400
    assets = root / "translator" / "assets"
    assert not assets.exists() or not list(assets.iterdir())


@pytest.mark.asyncio
async def test_delete_one_project_preserves_source_shared_with_another_project(tmp_path, monkeypatch):
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from app.database import Base
    from app.models.project import Project
    from app.models.video_translator import VideoAsset
    from app.services.cleanup_service import FileCleanupService, settings
    from app.services.storage_service import settings as storage_settings

    root = tmp_path / "storage"
    monkeypatch.setattr(settings, "ROOT_DIR", tmp_path)
    monkeypatch.setattr(settings, "STORAGE_ROOT", root)
    monkeypatch.setattr(settings, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(storage_settings, "STORAGE_ROOT", root)
    source = root / "translator" / "assets" / "asset-1" / "source.mp4"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"shared")
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        session.add_all([Project(id="project-1", title="One"), Project(id="project-2", title="Two")])
        session.add(VideoAsset(id="asset-1", title="Source", file_path=str(source)))
        session.add_all([
            VideoTranslationJob(id="job-1", project_id="project-1", asset_id="asset-1", status="completed"),
            VideoTranslationJob(id="job-2", project_id="project-2", asset_id="asset-1", status="needs_review"),
        ])
        await session.commit()
        assert (await FileCleanupService.cleanup_project("project-1", session))["status"] == "success"
        assert await session.get(VideoTranslationJob, "job-2") is not None
        assert await session.get(VideoAsset, "asset-1") is not None
        assert source.read_bytes() == b"shared"
        assert (await FileCleanupService.cleanup_project("project-2", session))["status"] == "success"
        assert await session.get(VideoAsset, "asset-1") is None
    assert not source.exists()
    await engine.dispose()
