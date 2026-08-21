import asyncio
from pathlib import Path

from app.core import get_logger
from app.core.exceptions import FFmpegNotFoundError
from app.core.security import safe_subprocess_run, safe_subprocess_run_async
from app.media.ffprobe import is_ffmpeg_installed

logger = get_logger(__name__)


async def trim_video_async(input_path: Path, output_path: Path, duration: float) -> Path:
    """Trim a video to a specific duration (non-blocking async)."""
    _check_ffmpeg()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    await safe_subprocess_run_async([
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-t", str(duration),
        "-c", "copy",
        str(output_path),
    ], timeout=120)

    logger.info("Video trimmed", input=str(input_path), duration=duration)
    return output_path


async def loop_video_async(input_path: Path, output_path: Path, target_duration: float) -> Path:
    """Loop a video to fill a target duration (non-blocking async)."""
    _check_ffmpeg()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    await safe_subprocess_run_async([
        "ffmpeg", "-y",
        "-stream_loop", "-1",
        "-i", str(input_path),
        "-t", str(target_duration),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        str(output_path),
    ], timeout=180)

    logger.info("Video looped", input=str(input_path), target_duration=target_duration)
    return output_path


async def pad_video_with_black_async(
    input_path: Path,
    output_path: Path,
    target_duration: float,
) -> Path:
    """Extend video with black frames to reach target duration (non-blocking async)."""
    _check_ffmpeg()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    await safe_subprocess_run_async([
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vf", f"tpad=stop_mode=clone:stop_duration={target_duration}",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        str(output_path),
    ], timeout=180)

    logger.info("Video padded", input=str(input_path), target_duration=target_duration)
    return output_path


async def merge_audio_video_async(
    audio_path: Path,
    video_path: Path,
    output_path: Path,
) -> Path:
    """Merge an audio file with a video file (non-blocking async)."""
    _check_ffmpeg()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    await safe_subprocess_run_async([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_path),
    ], timeout=180)

    logger.info(
        "Audio+Video merged",
        audio=str(audio_path),
        video=str(video_path),
        output=str(output_path),
    )
    return output_path


async def concatenate_videos_async(
    input_paths: list[Path],
    output_path: Path,
    tmp_dir: Path,
) -> Path:
    """Concatenate multiple video files (non-blocking async)."""
    _check_ffmpeg()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    concat_file = tmp_dir / "concat_list.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for path in input_paths:
            escaped = str(path.resolve()).replace("\\", "/").replace("'", "'\\''")
            f.write(f"file '{escaped}'\n")

    result = await safe_subprocess_run_async(
        [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(output_path),
        ],
        timeout=300,
        check=False,
    )

    if result.returncode != 0:
        logger.warning(
            "Concat copy failed, re-encoding",
            stderr=result.stderr[:500] if result.stderr else "",
        )
        await safe_subprocess_run_async(
            [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "192k",
                str(output_path),
            ],
            timeout=600,
        )

    logger.info(
        "Videos concatenated",
        input_count=len(input_paths),
        output=str(output_path),
    )
    return output_path


def trim_video(input_path: Path, output_path: Path, duration: float) -> Path:
    """Trim a video to a specific duration."""
    _check_ffmpeg()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    safe_subprocess_run([
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-t", str(duration),
        "-c", "copy",
        str(output_path),
    ], timeout=120)

    logger.info("Video trimmed", input=str(input_path), duration=duration)
    return output_path


def loop_video(input_path: Path, output_path: Path, target_duration: float) -> Path:
    """Loop a video to fill a target duration."""
    _check_ffmpeg()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    safe_subprocess_run([
        "ffmpeg", "-y",
        "-stream_loop", "-1",
        "-i", str(input_path),
        "-t", str(target_duration),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        str(output_path),
    ], timeout=180)

    logger.info("Video looped", input=str(input_path), target_duration=target_duration)
    return output_path


def pad_video_with_black(
    input_path: Path,
    output_path: Path,
    target_duration: float,
) -> Path:
    """Extend video with black frames to reach target duration."""
    _check_ffmpeg()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    safe_subprocess_run([
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vf", f"tpad=stop_mode=clone:stop_duration={target_duration}",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        str(output_path),
    ], timeout=180)

    logger.info("Video padded", input=str(input_path), target_duration=target_duration)
    return output_path


def merge_audio_video(
    audio_path: Path,
    video_path: Path,
    output_path: Path,
) -> Path:
    """Merge an audio file with a video file."""
    _check_ffmpeg()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    safe_subprocess_run([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_path),
    ], timeout=180)

    logger.info(
        "Audio+Video merged",
        audio=str(audio_path),
        video=str(video_path),
        output=str(output_path),
    )
    return output_path


def concatenate_videos(
    input_paths: list[Path],
    output_path: Path,
    tmp_dir: Path,
) -> Path:
    """Concatenate multiple video files into one final video."""
    _check_ffmpeg()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    concat_file = tmp_dir / "concat_list.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for path in input_paths:
            escaped = str(path.resolve()).replace("\\", "/").replace("'", "'\\''")
            f.write(f"file '{escaped}'\n")

    result = safe_subprocess_run(
        [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(output_path),
        ],
        timeout=300,
        check=False,
    )

    if result.returncode != 0:
        logger.warning(
            "Concat copy failed, re-encoding",
            stderr=result.stderr[:500] if result.stderr else "",
        )
        safe_subprocess_run(
            [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "192k",
                str(output_path),
            ],
            timeout=600,
        )

    logger.info(
        "Videos concatenated",
        input_count=len(input_paths),
        output=str(output_path),
    )
    return output_path


def _check_ffmpeg() -> None:
    """Raise FFmpegNotFoundError if FFmpeg is not available."""
    if not is_ffmpeg_installed():
        raise FFmpegNotFoundError()

