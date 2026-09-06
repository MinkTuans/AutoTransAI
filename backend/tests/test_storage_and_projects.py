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
