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

