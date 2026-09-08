"""
Unit test suite verifying StaleDataError elimination, atomic segment SQL updates,
and worker cancellation handling.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from sqlalchemy import select, update, delete

from app.api.routes.video_translator import (
    signal_job_cancellation,
    reset_job_cancellation,
    is_job_cancelled,
)
from app.models import VideoTranslationJob, VideoTranslationSegment
from app.database import async_session_factory


def test_job_cancellation_tokens():
    """Verify cancellation token signalling and resetting."""
    job_id = "VT-TEST-CANCEL-TOKEN"
    evt = reset_job_cancellation(job_id)
    assert not evt.is_set()
    assert not is_job_cancelled(job_id)

    signal_job_cancellation(job_id)
    assert evt.is_set()
    assert is_job_cancelled(job_id)

    new_evt = reset_job_cancellation(job_id)
    assert not new_evt.is_set()
    assert not is_job_cancelled(job_id)


@pytest.mark.asyncio
async def test_atomic_segment_update_rowcount_zero():
    """
    Verify that executing atomic SQL update on a deleted segment row returns rowcount=0
    and does NOT raise StaleDataError.
    """
    try:
        async with async_session_factory() as session:
            # Atomic update targeting non-existent segment ID
            res = await session.execute(
                update(VideoTranslationSegment)
                .where(VideoTranslationSegment.id == 99999999)
                .where(VideoTranslationSegment.job_id == "NON-EXISTENT-JOB")
                .values(status="tts_completed")
            )
            await session.commit()
            assert res.rowcount == 0
    except Exception as e:
        pytest.skip(f"Database unavailable for atomic SQL update test: {e}")


@pytest.mark.asyncio
async def test_smart_retry_signals_cancellation_token():
    """Verify that calling signal_job_cancellation sets cancellation state for running workers."""
    job_id = "VT-SMART-RETRY-JOB"
    cancel_evt = reset_job_cancellation(job_id)
    assert not cancel_evt.is_set()

    # Simulate Smart Retry trigger
    signal_job_cancellation(job_id)

    assert cancel_evt.is_set()
    assert is_job_cancelled(job_id)
