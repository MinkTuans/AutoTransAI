"""Process-local lifecycle for independent Live Translation jobs."""

from __future__ import annotations

import asyncio
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Awaitable, Callable

from .audio import AudioInputError, convert_to_pcm
from .live_api import LiveTranslationError, translate_pcm


class SessionCapacityError(Exception):
    pass


@dataclass
class LiveJob:
    id: str
    directory: Path
    source: Path
    source_language: str = "auto"
    target_language: str = "vi"
    status: str = "queued"
    error_code: str | None = None
    task: asyncio.Task | None = field(default=None, repr=False)

    def public(self) -> dict:
        return {"id": self.id, "status": self.status, "error_code": self.error_code,
                "source_language": self.source_language, "target_language": self.target_language,
                "audio_url": f"/api/live-audio-translations/{self.id}/audio" if self.status == "completed" else None}


class LiveJobManager:
    def __init__(self, storage_root: Path, *,
                 convert: Callable[..., Awaitable[float]] = convert_to_pcm,
                 translate: Callable[..., Awaitable[None]] = translate_pcm,
                 max_active: int = 2, max_results: int = 10):
        self.directory = storage_root / "live_audio_translation"
        self.directory.mkdir(parents=True, exist_ok=True)
        # Aborted processes may leave files whose job IDs can no longer be queried.
        stale_before = time.time() - 24 * 60 * 60
        for path in self.directory.iterdir():
            if path.is_dir() and path.stat().st_mtime < stale_before:
                shutil.rmtree(path, ignore_errors=True)
        self.jobs: dict[str, LiveJob] = {}
        self.convert = convert
        self.translate = translate
        self.max_active = max_active
        self.max_results = max_results

    def _prune_results(self) -> None:
        terminal = [job for job in self.jobs.values()
                    if job.status in {"completed", "failed", "cancelled"}]
        for job in terminal[:max(0, len(terminal) - self.max_results + 1)]:
            self.jobs.pop(job.id, None)
            shutil.rmtree(job.directory, ignore_errors=True)

    def start(self, job_id: str, source: Path, directory: Path, *, key: str, model: str) -> LiveJob:
        active = sum(job.status in {"queued", "converting", "connecting", "streaming"}
                     for job in self.jobs.values())
        if active >= self.max_active:
            raise SessionCapacityError()
        self._prune_results()
        job = LiveJob(job_id, directory, source)
        self.jobs[job_id] = job
        job.task = asyncio.create_task(self._run(job, key=key, model=model))
        return job

    async def _run(self, job: LiveJob, *, key: str, model: str) -> None:
        pcm = job.directory / "input.pcm"
        try:
            job.status = "converting"
            await self.convert(job.source, pcm, max_seconds=300)
            job.status = "connecting"
            # The Live adapter owns one WebSocket for this job. Its send and
            # receive tasks do not touch any existing provider instance.
            await self.translate(pcm, job.directory / "translated.wav", key=key, model=model,
                                 on_connected=lambda: setattr(job, "status", "streaming"))
            job.status = "completed"
        except asyncio.CancelledError:
            job.status = "cancelled"
            (job.directory / "translated.wav").unlink(missing_ok=True)
            raise
        except (AudioInputError, LiveTranslationError) as error:
            job.status = "failed"
            job.error_code = error.code
        except Exception:
            job.status = "failed"
            job.error_code = "internal_error"
        finally:
            job.source.unlink(missing_ok=True)
            pcm.unlink(missing_ok=True)
            if job.status != "completed":
                shutil.rmtree(job.directory, ignore_errors=True)

    async def cancel(self, job_id: str) -> bool:
        job = self.jobs.get(job_id)
        if job is None or job.status not in {"queued", "converting", "connecting", "streaming"}:
            return False
        if job.task is not None:
            job.task.cancel()
            await asyncio.gather(job.task, return_exceptions=True)
        # A queued task can be cancelled before _run enters its finally block.
        job.status = "cancelled"
        job.source.unlink(missing_ok=True)
        (job.directory / "input.pcm").unlink(missing_ok=True)
        (job.directory / "translated.wav").unlink(missing_ok=True)
        shutil.rmtree(job.directory, ignore_errors=True)
        return True

    async def close(self) -> None:
        for job in self.jobs.values():
            if job.status in {"queued", "converting", "connecting", "streaming"}:
                await self.cancel(job.id)
            shutil.rmtree(job.directory, ignore_errors=True)
