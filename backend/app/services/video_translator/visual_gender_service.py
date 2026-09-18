import asyncio
import logging
from typing import Dict, Any, List
from pathlib import Path
import tempfile
import base64
import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

async def extract_speaker_keyframe(video_path: str, timestamp: float, output_path: str):
    """Extract a single frame from the video at the given timestamp using FFmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(timestamp),
        "-i", video_path,
        "-frames:v", "1",
        "-q:v", "2",
        output_path
    ]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        logger.error(f"FFmpeg keyframe extraction failed: {stderr.decode()}")
        raise RuntimeError(f"FFmpeg keyframe extraction failed with exit code {process.returncode}")

async def detect_gender_from_image(image_path: str) -> str:
    """Send image to Gemini Vision to detect gender (Male/Female)."""
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    prompt = (
        "Đây là khung hình cắt từ video tại thời điểm nhân vật đang nói. "
        "Hãy cho biết nhân vật chính, người đang phát biểu trong hình là Nam (Male) hay Nữ (Female). "
        "Chỉ trả về MALE hoặc FEMALE, hoặc UNKNOWN nếu không thể xác định rõ ràng."
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": base64_image,
                        }
                    },
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 10,
        },
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        res = await client.post(url, json=payload)
        if res.status_code == 200:
            data = res.json()
            parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            if parts:
                text = parts[0].get("text", "").strip().lower()
                if "male" in text and "female" not in text:
                    return "male"
                elif "female" in text:
                    return "female"
        return "unknown"

async def detect_speakers_gender(video_path: str, segments: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Given a list of STT segments with speaker_id, extract one frame per speaker and detect gender.
    Returns a dict mapping speaker_id to 'male', 'female', or 'unknown'.
    """
    if not video_path or not Path(video_path).is_file():
        logger.warning(f"Video path invalid or not provided for visual gender detection: {video_path}")
        return {}

    # Find the longest segment for each speaker to ensure they are likely on screen and speaking
    speaker_segments = {}
    for seg in segments:
        spk = seg.get("speaker_id")
        if not spk:
            continue
        duration = float(seg.get("end_time", 0)) - float(seg.get("start_time", 0))
        if spk not in speaker_segments or duration > speaker_segments[spk]["duration"]:
            speaker_segments[spk] = {
                "start_time": float(seg.get("start_time", 0)),
                "end_time": float(seg.get("end_time", 0)),
                "duration": duration
            }

    results = {}
    with tempfile.TemporaryDirectory() as tmpdir:
        for spk, seg_info in speaker_segments.items():
            if "UNRESOLVED" in spk:
                continue # Skip fallback unresolved speakers
            
            # Use the middle of the segment
            mid_time = seg_info["start_time"] + (seg_info["duration"] / 2.0)
            img_path = Path(tmpdir) / f"{spk}.jpg"
            
            try:
                await extract_speaker_keyframe(video_path, mid_time, str(img_path))
                if img_path.exists():
                    gender = await detect_gender_from_image(str(img_path))
                    if gender in ("male", "female"):
                        results[spk] = gender
                        logger.info(f"[Visual Gender] {spk} at {mid_time:.2f}s detected as {gender}")
                else:
                    logger.warning(f"[Visual Gender] Failed to generate keyframe for {spk}")
            except Exception as e:
                logger.error(f"[Visual Gender Error] for {spk}: {e}")

    return results
