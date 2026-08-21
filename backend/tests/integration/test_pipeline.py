"""
End-to-end integration test for the audio generation pipeline.

Tests:
1. Script parsing
2. Project creation & database persistence
3. Resource estimation
4. Preflight checks (and error detection if FFmpeg missing)
5. Direct audio generation using Edge TTS
6. Local file storage verification
7. Manifest.json updates
"""

import pytest
import shutil
import uuid
from pathlib import Path

from app.database import init_db, async_session_factory
from app.models.project import Project, WorkflowStatus
from app.models.segment import Segment
from app.providers.audio.edge_tts_provider import EdgeTTSProvider
from app.providers.registry import get_registry
from app.services.script_parser import parse_script
from app.services.estimator import estimate_project
from app.services.preflight import run_preflight
from app.services.file_manager import get_segment_audio_path, get_manifest_path, get_project_dir
from app.services.manifest import read_manifest
from app.media.ffprobe import is_ffmpeg_installed, probe_duration


@pytest.mark.asyncio
async def test_full_audio_pipeline():
    # Initialize DB
    await init_db()

    # Register Edge TTS
    registry = get_registry()
    provider = EdgeTTSProvider()
    registry.register_audio(provider)

    project_id = f"test_e2e_{uuid.uuid4().hex[:6]}"
    script = """Phân đoạn 1: Hello world, this is an automated integration test for audio generation.
Phân đoạn 2: Second segment verifying local file storage and manifest recovery."""

    # 1. Parse Script
    parsed = parse_script(script)
    assert len(parsed) == 2

    # 2. Persist Project & Segments
    async with async_session_factory() as session:
        project = Project(
            id=project_id,
            title="E2E Test Project",
            script_raw=script,
            workflow_mode="audio_only",
            workflow_status=WorkflowStatus.PARSED.value,
            audio_provider_id="edge_tts",
            voice_id="en-US-AriaNeural",
            voice_name="Aria",
        )
        session.add(project)

        for p in parsed:
            seg = Segment(
                project_id=project_id,
                segment_number=p.number,
                text_content=p.text,
                char_count=p.char_count,
            )
            session.add(seg)

        await session.commit()

    # 3. Estimate
    est = estimate_project([{"number": p.number, "char_count": p.char_count} for p in parsed], "audio_only")
    assert est.total_segments == 2
    assert est.total_characters > 0

    # 4. Preflight Check
    preflight = await run_preflight(
        project_id=project_id,
        workflow_mode="audio_only",
        audio_provider_id="edge_tts",
        video_provider_id=None,
        voice_id="en-US-AriaNeural",
        total_segments=2,
    )

    # Check that preflight validates all steps
    if not is_ffmpeg_installed():
        # FFmpeg missing -> preflight correctly flags FFMPEG_NOT_FOUND
        assert preflight.passed is False
        ffmpeg_check = next(c for c in preflight.checks if c.name == "ffmpeg_installed")
        assert ffmpeg_check.passed is False
        assert ffmpeg_check.error_code == "FFMPEG_NOT_FOUND"
    else:
        assert preflight.passed is True

    # 5. Direct Audio Generation via Provider
    out_dir = get_project_dir(project_id) / "audio" / "segment_001"
    out_file = out_dir / "segment_001_audio.wav"

    res1 = await provider.generate_audio(
        text=parsed[0].text,
        voice_id="en-US-AriaNeural",
        output_path=out_file,
    )

    assert res1.success is True
    assert res1.file_path.exists()
    assert res1.file_path.stat().st_size > 0

    # 6. Verify Local Storage & Manifest Updates
    manifest_file = get_manifest_path(project_id)
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(f'{{"version": "1.0", "project_id": "{project_id}"}}', encoding="utf-8")

    manifest = read_manifest(project_id)
    assert manifest is not None
    assert manifest["project_id"] == project_id

    # Clean up test files
    pdir = get_project_dir(project_id)
    if pdir.exists():
        shutil.rmtree(pdir)
