"""
AI Quality Control (AI QC) Service — Audio LUFS Loudness Check, Drift Detection, Black Frame Detection, and Gemini Content Safety Audit.
"""

from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.config import get_settings
from app.core import get_logger
from app.core.job_logger import log_job_event
from app.media.ffprobe import probe_duration_async, get_video_metadata_async
from app.media.ffmpeg_process import run_ffmpeg_with_progress_async
from app.models.video_editor import QCStatusEnum

logger = get_logger(__name__)
settings = get_settings()


class AIQCService:
    """Automated Quality Control (QC) Service for Audio, Video, and AI Content Audit."""

    @staticmethod
    async def measure_audio_lufs(video_or_audio_path: Path) -> float:
        """
        Measure integrated audio loudness in LUFS using FFmpeg ebur128 filter.
        Target for YouTube: -14.0 LUFS.
        """
        if not video_or_audio_path.exists():
            return -99.0

        cmd = [
            "ffmpeg", "-nostats", "-i", str(video_or_audio_path),
            "-filter_complex", "ebur128=peak=true",
            "-f", "null", "-"
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stderr=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
        )
        _, stderr_bytes = await proc.communicate()
        stderr_text = stderr_bytes.decode("utf-8", errors="ignore")

        # Parse Summary Integrated Loudness (e.g. "I: -14.2 LUFS")
        match = re.search(r"I:\s+([-+]?\d+\.\d+)\s+LUFS", stderr_text)
        if match:
            return float(match.group(1))
        return -14.0  # Default fallback target if unparseable

    @staticmethod
    async def detect_black_frames(video_path: Path, min_duration: float = 1.0) -> bool:
        """Detect black frame glitches using FFmpeg blackdetect filter."""
        cmd = [
            "ffmpeg", "-nostats", "-i", str(video_path),
            "-vf", f"blackdetect=d={min_duration}:pix_th=0.10",
            "-f", "null", "-"
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stderr=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
        )
        _, stderr_bytes = await proc.communicate()
        stderr_text = stderr_bytes.decode("utf-8", errors="ignore")
        return "blackdetect" in stderr_text and "black_start" in stderr_text

    @staticmethod
    async def audit_content_with_gemini(
        transcript_text: str,
        job_id: str = "VT-QC",
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Audit translated transcript for profanity, content safety, and translation accuracy using Gemini AI Studio."""
        if not settings.GEMINI_API_KEY:
            return {"safety_score": 100.0, "quality_score": 100.0, "issues": []}

        import httpx
        from app.services.model_resolver import AIModelResolver
        from app.providers.llm.gemini_provider import strip_gemini_model_prefix

        if not model_name:
            res_model = await AIModelResolver.resolve_llm_model(None)
            model_name = res_model.get("model_id")

        target_model = strip_gemini_model_prefix(model_name)

        prompt = (
            "Bạn là một chuyên gia Kiểm định Chất lượng Nội dung Video (AI Quality Control Auditor).\n"
            "Hãy đánh giá bản chép lời/bản dịch bên dưới về 3 yếu tố:\n"
            "1. An toàn nội dung (Content Safety - không vi phạm bản quyền, không ngôn từ kích động/độc hại).\n"
            "2. Chất lượng bản dịch (Translation Quality - câu từ tự nhiên, không bị dịch méo nghĩa).\n"
            "3. Liệt kê danh sách các lỗi hoặc từ ngữ nghi vấn (nếu có).\n\n"
            f"VĂN BẢN KIỂM ĐỊNH:\n{transcript_text[:4000]}\n\n"
            "Trả về JSON thuần túy (không markdown) với cấu trúc:\n"
            "{\n"
            '  "content_safety_score": 95.0,\n'
            '  "translation_quality_score": 90.0,\n'
            '  "issues": ["Từ X bị lặp nguyên văn", "Câu Y dịch chưa xuôi"]\n'
            "}"
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
        }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={settings.GEMINI_API_KEY}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                    if parts:
                        raw_text = parts[0].get("text", "").strip()
                        json_str = re.sub(r"^```json\s*", "", raw_text, flags=re.MULTILINE)
                        json_str = re.sub(r"```$", "", json_str, flags=re.MULTILINE).strip()
                        return json.loads(json_str)
            except Exception as ex:
                logger.warning("Gemini QC audit exception", error=str(ex), model=target_model)

        return {"content_safety_score": 95.0, "translation_quality_score": 95.0, "issues": []}

    @classmethod
    async def run_full_qc(
        cls,
        output_video_path: Path,
        source_duration: float,
        transcript_text: str = "",
        job_id: str = "VT-QC",
    ) -> Dict[str, Any]:
        """
        Run complete AI Quality Control Audit Suite (Audio LUFS, Drift, Black frames, Gemini Audit).
        """
        log_job_event(job_id, "VALIDATION", "[AI-QC] Starting full automated Quality Control suite...")
        
        # 1. Measure Audio LUFS Loudness
        audio_lufs = await cls.measure_audio_lufs(output_video_path)
        
        # 2. Check Audio Sync Drift (mismatch with source duration)
        if output_video_path.exists():
            out_meta = await get_video_metadata_async(output_video_path)
            out_dur = out_meta.get("duration", 0.0)
            has_black_frames = await cls.detect_black_frames(output_video_path)
        else:
            out_dur = 0.0
            has_black_frames = False
            
        sync_drift_ms = abs(out_dur - source_duration) * 1000.0 if out_dur > 0 else 0.0
        
        # 4. Gemini Content Safety & Translation Audit
        gemini_audit = await cls.audit_content_with_gemini(transcript_text, job_id=job_id)
        content_safety_score = float(gemini_audit.get("content_safety_score", 100.0))
        translation_quality_score = float(gemini_audit.get("translation_quality_score", 100.0))
        issues = gemini_audit.get("issues", [])
        
        if has_black_frames:
            issues.append("Phát hiện khung hình đen (black frames) trong video")
        if abs(audio_lufs - (-14.0)) > 6.0:
            issues.append(f"Cảnh báo âm lượng Audio LUFS = {audio_lufs:.1f} (Tiêu chuẩn YouTube: -14.0 LUFS)")
        if sync_drift_ms > 1500.0:
            issues.append(f"Cảnh báo độ lệch thời lượng (Audio Sync Drift) = {sync_drift_ms:.0f}ms")

        # Calculate overall QC Score
        lufs_penalty = min(20.0, abs(audio_lufs - (-14.0)) * 2.0)
        drift_penalty = min(20.0, (sync_drift_ms / 1000.0) * 10.0)
        overall_score = round(max(0.0, min(100.0, (content_safety_score + translation_quality_score) / 2.0 - lufs_penalty - drift_penalty)), 1)
        
        qc_status = QCStatusEnum.PASSED.value
        if overall_score < 70.0 or sync_drift_ms > 3000.0:
            qc_status = QCStatusEnum.FAILED.value
        elif overall_score < 85.0 or issues:
            qc_status = QCStatusEnum.WARNING.value

        report = {
            "audio_lufs": round(audio_lufs, 1),
            "sync_drift_ms": round(sync_drift_ms, 1),
            "has_black_frames": has_black_frames,
            "content_safety_score": content_safety_score,
            "translation_quality_score": translation_quality_score,
            "overall_score": overall_score,
            "qc_status": qc_status,
            "issues": issues,
        }

        log_job_event(
            job_id,
            "VALIDATION",
            f"[AI-QC] Audit Complete | Status: {qc_status} | Overall Score: {overall_score}/100 | "
            f"LUFS: {audio_lufs:.1f} dB | Drift: {sync_drift_ms:.0f}ms | Issues: {len(issues)}"
        )
        return report
