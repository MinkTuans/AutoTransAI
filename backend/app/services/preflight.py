"""
Preflight check system — validates all prerequisites before generation.

If ANY required check fails, the workflow MUST NOT start.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.config import get_settings
from app.core import get_logger
from app.media.ffprobe import is_ffmpeg_installed, get_ffmpeg_version
from app.providers.registry import get_registry
from app.schemas.workflow import PreflightCheck, PreflightResult
from app.services.file_manager import check_storage_writable, get_disk_space_mb

logger = get_logger(__name__)
settings = get_settings()


async def run_preflight(
    project_id: str,
    workflow_mode: str,
    audio_provider_id: str | None,
    video_provider_id: str | None,
    voice_id: str | None,
    total_segments: int,
) -> PreflightResult:
    """
    Run all preflight checks for a project.

    Returns:
        PreflightResult with pass/fail per check.
    """
    registry = get_registry()
    checks: list[PreflightCheck] = []

    # 1. Script validation
    checks.append(PreflightCheck(
        name="script_valid",
        description="Script is parsed and has segments",
        passed=total_segments > 0,
        required=True,
        error_code="EMPTY_SCRIPT" if total_segments == 0 else None,
        error_message="No segments found in script" if total_segments == 0 else None,
    ))

    # 2. Audio provider configured
    audio_provider = registry.get_audio(audio_provider_id) if audio_provider_id else None
    checks.append(PreflightCheck(
        name="audio_provider_configured",
        description=f"Audio provider '{audio_provider_id}' is registered",
        passed=audio_provider is not None,
        required=True,
        error_code="PROVIDER_NOT_CONFIGURED" if not audio_provider else None,
        error_message=f"Audio provider '{audio_provider_id}' not found" if not audio_provider else None,
    ))

    # 3. Audio provider reachable
    if audio_provider:
        audio_valid = await audio_provider.validate_configuration()
        checks.append(PreflightCheck(
            name="audio_provider_reachable",
            description=f"Audio provider '{audio_provider_id}' is reachable",
            passed=audio_valid,
            required=True,
            error_code="PROVIDER_UNREACHABLE" if not audio_valid else None,
            error_message=f"Cannot reach audio provider '{audio_provider_id}'" if not audio_valid else None,
        ))

    # 4. Voice selection
    checks.append(PreflightCheck(
        name="voice_selected",
        description="Voice is selected",
        passed=voice_id is not None and voice_id != "",
        required=True,
        error_code="INVALID_VOICE" if not voice_id else None,
        error_message="No voice selected" if not voice_id else None,
    ))

    # 5-7. Video provider checks (only if audio_video mode)
    if workflow_mode == "audio_video":
        video_provider = registry.get_video(video_provider_id) if video_provider_id else None

        checks.append(PreflightCheck(
            name="video_provider_configured",
            description=f"Video provider '{video_provider_id}' is registered",
            passed=video_provider is not None,
            required=True,
            error_code="PROVIDER_NOT_CONFIGURED" if not video_provider else None,
            error_message=f"Video provider '{video_provider_id}' not found" if not video_provider else None,
        ))

        if video_provider:
            video_valid = await video_provider.validate_configuration()
            checks.append(PreflightCheck(
                name="video_provider_reachable",
                description=f"Video provider '{video_provider_id}' is reachable",
                passed=video_valid,
                required=True,
                error_code="PROVIDER_UNREACHABLE" if not video_valid else None,
                error_message=f"Tài khoản {video_provider_id} hết số dư (Exhausted balance) hoặc API Key chưa đúng. Vui lòng chuyển sang 'Local FFmpeg Generator' để sử dụng miễn phí." if not video_valid else None,
            ))

            # Check duration support
            target_dur = settings.VIDEO_TARGET_DURATION
            supported = video_provider.max_duration_seconds >= target_dur
            checks.append(PreflightCheck(
                name="video_duration_supported",
                description=f"Video provider supports {target_dur}s duration",
                passed=supported,
                required=True,
                error_code="UNSUPPORTED_DURATION" if not supported else None,
                error_message=(
                    f"Provider supports max {video_provider.max_duration_seconds}s, "
                    f"but {target_dur}s requested"
                ) if not supported else None,
            ))

    # 8. FFmpeg installed
    ffmpeg_ok = is_ffmpeg_installed()
    checks.append(PreflightCheck(
        name="ffmpeg_installed",
        description="FFmpeg and FFprobe are installed",
        passed=ffmpeg_ok,
        required=True,
        error_code="FFMPEG_NOT_FOUND" if not ffmpeg_ok else None,
        error_message="FFmpeg not found in PATH" if not ffmpeg_ok else None,
    ))

    # 9. Storage writable
    storage_ok = check_storage_writable(project_id)
    checks.append(PreflightCheck(
        name="storage_writable",
        description="Project storage directory is writable",
        passed=storage_ok,
        required=True,
        error_code="STORAGE_NOT_WRITABLE" if not storage_ok else None,
        error_message="Cannot write to project directory" if not storage_ok else None,
    ))

    # 10. Disk space (warning only — estimate 50MB per segment)
    disk_mb = get_disk_space_mb(project_id)
    estimated_mb = total_segments * 50  # rough estimate
    if disk_mb is not None:
        disk_ok = disk_mb > estimated_mb
        checks.append(PreflightCheck(
            name="disk_space",
            description=f"Sufficient disk space ({disk_mb:.0f} MB free, ~{estimated_mb} MB needed)",
            passed=disk_ok,
            required=True,
            error_code="INSUFFICIENT_DISK_SPACE" if not disk_ok else None,
            error_message=(
                f"Only {disk_mb:.0f} MB free, estimated {estimated_mb} MB needed"
            ) if not disk_ok else None,
        ))

    # Compute result
    blocking_failures = [c for c in checks if c.required and not c.passed]
    passed = len(blocking_failures) == 0

    result = PreflightResult(
        project_id=project_id,
        passed=passed,
        checks=checks,
        blocking_failures=blocking_failures,
    )

    logger.info(
        "Preflight complete",
        project_id=project_id,
        passed=passed,
        total_checks=len(checks),
        failures=len(blocking_failures),
    )

    return result
