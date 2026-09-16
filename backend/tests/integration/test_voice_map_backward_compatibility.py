import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.models.project import Project
from app.api.routes.video_translator import VoiceMapPayload, get_speaker_voice_map_api, save_speaker_voice_map_api


@pytest.mark.asyncio
async def test_legacy_voice_map_payload_and_response_remain_compatible():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions() as session:
        session.add(Project(id="project-legacy", title="Legacy"))
        await session.commit()
        saved = await save_speaker_voice_map_api("project-legacy", VoiceMapPayload(
            speaker_id="SPEAKER_00", speaker_name="Speaker 0",
            voice_provider="edge", voice_id="vi-VN-HoaiMyNeural",
        ), session)
        listed = await get_speaker_voice_map_api("project-legacy", session)
    await engine.dispose()
    assert {"id", "speaker_id"} <= saved["data"].keys()
    assert {"speaker_id", "speaker_name", "voice_provider", "voice_id"} <= listed["data"][0].keys()
    assert listed["data"][0]["voice_provider"] == "edge"
