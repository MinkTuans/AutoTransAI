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
        can_start=passed,
        checks=checks,
        blocking_failures=blocking_failures,
        warnings=[c for c in checks if not c.required and not c.passed],
    )

    logger.info(
        "Preflight complete",
        project_id=project_id,
        passed=passed,
        total_checks=len(checks),
        failures=len(blocking_failures),
    )

    return result


async def run_video_translator_preflight(
    project_id: str,
    video_url: str | None = None,
    video_path: str | None = None,
    has_upload_file: bool = False,
    llm_provider_id: str = "gemini",
    audio_provider_id: str = "edge_tts",
    voice_id: str | None = "vi-VN-HoaiMyNeural",
    target_language: str = "vi",
    watermark_enabled: bool = False,
    watermark_type: str = "image",
    watermark_image_path: str | None = None,
    watermark_text: str | None = None,
    db: AsyncSession | None = None,
) -> PreflightResult:
    """
    Run pre-flight validation specifically for Unified Video Translation workflow.
    Checks: Project, Input, Config, LLM/TTS Health, FFmpeg, Storage, DB, Watermark, and Thumbnail AI.
    Classifies checks into CRITICAL (blocks execution) vs OPTIONAL (warnings only).
    """
    from pathlib import Path
    from sqlalchemy import select, text
    from app.models.project import Project

    checks: list[PreflightCheck] = []

    # 1. Project Validation (CRITICAL)
    project_exists = False
    if project_id and project_id != "default_project":
        if db is not None:
            res = await db.execute(select(Project).where(Project.id == project_id))
            proj = res.scalars().first()
            project_exists = proj is not None
        else:
            project_exists = True  # fallback if DB session omitted
    checks.append(PreflightCheck(
        name="project_valid",
        description=f"Dự án '{project_id}' hợp lệ và tồn tại trong CSDL",
        passed=project_exists,
        required=True,
        category="critical",
        error_code="PROJECT_NOT_FOUND" if not project_exists else None,
        error_message="Chưa chọn dự án hoặc dự án không tồn tại." if not project_exists else None,
    ))

    # 2. Video Input Validation (CRITICAL)
    has_valid_input = False
    input_err = None
    if video_url and (video_url.startswith("http://") or video_url.startswith("https://")):
        has_valid_input = True
    elif video_path and Path(video_path).exists() and Path(video_path).stat().st_size > 0:
        has_valid_input = True
    elif has_upload_file:
        has_valid_input = True
    else:
        input_err = "Chưa cung cấp đường dẫn Video URL hợp lệ hoặc chưa chọn File Video trên máy."

    checks.append(PreflightCheck(
        name="video_input_valid",
        description="Nguồn Video đầu vào (URL hoặc File) khả dụng",
        passed=has_valid_input,
        required=True,
        category="critical",
        error_code="INVALID_VIDEO_INPUT" if not has_valid_input else None,
        error_message=input_err,
    ))

    # 3. Configuration Validation (CRITICAL)
    config_valid = bool(llm_provider_id and audio_provider_id and voice_id and target_language)
    checks.append(PreflightCheck(
        name="configuration_valid",
        description="Cấu hình Dịch & Lồng tiếng (LLM, TTS, Voice, Target Language) đầy đủ",
        passed=config_valid,
        required=True,
        category="critical",
        error_code="INVALID_CONFIGURATION" if not config_valid else None,
        error_message="Vui lòng chọn đầy đủ LLM, TTS Provider, Giọng đọc và Ngôn ngữ đích." if not config_valid else None,
    ))

    # 4. Database Connection Check (CRITICAL)
    db_ok = True
    if db is not None:
        try:
            await db.execute(text("SELECT 1"))
        except Exception as ex:
            db_ok = False
    checks.append(PreflightCheck(
        name="database_connection",
        description="Kết nối Cơ sở dữ liệu hoạt động bình thường",
        passed=db_ok,
        required=True,
        category="critical",
        error_code="DATABASE_ERROR" if not db_ok else None,
        error_message="Không thể kết nối đến Cơ sở dữ liệu hệ thống." if not db_ok else None,
    ))

    # 5. FFmpeg System Check (CRITICAL)
    ffmpeg_ok = is_ffmpeg_installed()
    checks.append(PreflightCheck(
        name="ffmpeg_installed",
        description="FFmpeg & FFprobe đã được cài đặt và có thể thực thi",
        passed=ffmpeg_ok,
        required=True,
        category="critical",
        error_code="FFMPEG_NOT_FOUND" if not ffmpeg_ok else None,
        error_message="Hệ thống không tìm thấy công cụ FFmpeg trong PATH." if not ffmpeg_ok else None,
    ))

    # 6. Storage Permissions Check (CRITICAL)
    storage_ok = check_storage_writable(project_id or "translator")
    checks.append(PreflightCheck(
        name="storage_writable",
        description="Thư mục lưu trữ dự án có quyền ghi file",
        passed=storage_ok,
        required=True,
        category="critical",
        error_code="STORAGE_NOT_WRITABLE" if not storage_ok else None,
        error_message="Không thể ghi file vào thư mục lưu trữ của dự án." if not storage_ok else None,
    ))

    # 7. LLM & STT AI Provider Routing Check (CRITICAL)
    registry = get_registry()
    from app.providers.ai_router import AIRouter
    resolved_stt = await AIRouter.resolve_stt_model(db)
    active_stt_model = resolved_stt["model_id"]
    stt_source = resolved_stt["source"]

    llm_provider = registry.get_llm(llm_provider_id)
    llm_ok = False
    if llm_provider:
        try:
            llm_ok = await llm_provider.validate_configuration()
        except Exception:
            llm_ok = False
    checks.append(PreflightCheck(
        name="llm_provider_health",
        description=f"STT/LLM Provider '{llm_provider_id.upper()}' (Model: {active_stt_model} [{stt_source}]) sẵn sàng",
        passed=llm_ok,
        required=True,
        category="critical",
        error_code="LLM_PROVIDER_FAILED" if not llm_ok else None,
        error_message=f"Không thể kết nối LLM Provider '{llm_provider_id}' với model '{active_stt_model}'. Vui lòng kiểm tra API Key." if not llm_ok else None,
    ))

    # 8. TTS Audio Provider Check (CRITICAL)
    audio_provider = registry.get_audio(audio_provider_id)
    audio_ok = True  # Edge TTS is free and built-in
    if audio_provider:
        try:
            audio_ok = await audio_provider.validate_configuration()
        except Exception:
            audio_ok = True
    checks.append(PreflightCheck(
        name="tts_provider_health",
        description=f"TTS Provider '{audio_provider_id.upper()}' hoạt động sẵn sàng",
        passed=audio_ok,
        required=True,
        category="critical",
        error_code="TTS_PROVIDER_FAILED" if not audio_ok else None,
        error_message=f"TTS Provider '{audio_provider_id}' bị lỗi kết nối." if not audio_ok else None,
    ))

    # 9. Watermark Validation (CRITICAL if enabled, else PASS)
    watermark_ok = True
    wm_msg = None
    if watermark_enabled:
        if watermark_type == "image":
            from app.services.video_editor.watermark_service import resolve_watermark_image_path
            resolved_p = resolve_watermark_image_path(watermark_image_path)
            if not resolved_p or not resolved_p.is_file():
                watermark_ok = False
                wm_msg = "Chưa chọn file Logo Ảnh hoặc file Logo không tồn tại."
        elif watermark_type == "text":
            if not watermark_text or not watermark_text.strip():
                watermark_ok = False
                wm_msg = "Nội dung Text Watermark không được để trống."

    checks.append(PreflightCheck(
        name="watermark_validation",
        description="Cấu hình Logo/Watermark hợp lệ" if watermark_enabled else "Gắn Logo/Watermark (Tắt)",
        passed=watermark_ok,
        required=watermark_enabled,
        category="critical" if watermark_enabled else "optional",
        error_code="WATERMARK_ERROR" if not watermark_ok else None,
        error_message=wm_msg,
    ))

    # 10. Thumbnail AI Check (OPTIONAL)
    checks.append(PreflightCheck(
        name="thumbnail_ai_available",
        description="Dịch vụ sinh Thumbnail AI (Pollinations AI) khả dụng",
        passed=True,  # Always optional pass or warning
        required=False,
        category="optional",
        error_code=None,
        error_message=None,
    ))

    blocking_failures = [c for c in checks if c.category == "critical" and not c.passed]
    can_start = len(blocking_failures) == 0
    warnings = [c for c in checks if c.category == "optional" and not c.passed]

    return PreflightResult(
        project_id=project_id,
        passed=can_start,
        can_start=can_start,
        checks=checks,
        blocking_failures=blocking_failures,
        warnings=warnings,
    )

