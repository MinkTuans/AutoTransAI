"""
Quota manager — validates resource availability before generation.

Rules:
1. If provider has API to check quota → use it.
2. If no API → display "Unknown".
3. NEVER fabricate quota numbers.
4. Block workflow if estimated usage exceeds known remaining quota.
5. Allow user override when quota is unknown (with explicit confirmation).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core import get_logger
from app.providers.base import AudioProvider, VideoProvider, QuotaInfo, UsageEstimate
from app.providers.registry import get_registry

logger = get_logger(__name__)


@dataclass
class QuotaCheckResult:
    """Result of checking quota for one provider + resource type."""
    provider_id: str
    provider_name: str
    resource_type: str
    unit: str
    estimated_usage: float
    available: float | None  # None = unknown
    sufficient: bool | None  # None = cannot determine


@dataclass
class QuotaValidation:
    """Overall quota validation result."""
    can_proceed: bool
    results: list[QuotaCheckResult]
    warnings: list[str]
    blocking_issues: list[str]


async def check_audio_quota(
    provider: AudioProvider,
    total_characters: int,
) -> list[QuotaCheckResult]:
    """Check if audio provider has enough quota."""
    results = []
    estimates = await provider.estimate_usage("x" * min(total_characters, 100))
    quotas = await provider.get_quota()

    # Match estimates to quotas by resource type
    for est in estimates:
        # Scale estimate to actual character count
        if est.resource_type == "characters":
            actual_estimate = float(total_characters)
        else:
            actual_estimate = est.estimated_amount

        matching_quota = next(
            (q for q in quotas if q.resource_type == est.resource_type),
            None,
        )

        if matching_quota and matching_quota.remaining is not None:
            sufficient = actual_estimate <= matching_quota.remaining
            available = matching_quota.remaining
        else:
            sufficient = None  # Cannot determine
            available = None

        results.append(QuotaCheckResult(
            provider_id=provider.provider_id,
            provider_name=provider.provider_name,
            resource_type=est.resource_type,
            unit=est.unit,
            estimated_usage=actual_estimate,
            available=available,
            sufficient=sufficient,
        ))

    return results


async def check_video_quota(
    provider: VideoProvider,
    total_clips: int,
    clip_duration: int,
) -> list[QuotaCheckResult]:
    """Check if video provider has enough quota."""
    results = []
    estimates = await provider.estimate_usage(clip_duration)
    quotas = await provider.get_quota()

    for est in estimates:
        # Scale to total clips
        total_estimate = est.estimated_amount * total_clips

        matching_quota = next(
            (q for q in quotas if q.resource_type == est.resource_type),
            None,
        )

        if matching_quota and matching_quota.remaining is not None:
            sufficient = total_estimate <= matching_quota.remaining
            available = matching_quota.remaining
        else:
            sufficient = None
            available = None

        results.append(QuotaCheckResult(
            provider_id=provider.provider_id,
            provider_name=provider.provider_name,
            resource_type=est.resource_type,
            unit=est.unit,
            estimated_usage=total_estimate,
            available=available,
            sufficient=sufficient,
        ))

    return results


async def validate_quota(
    audio_provider: AudioProvider | None,
    video_provider: VideoProvider | None,
    total_characters: int,
    total_clips: int,
    clip_duration: int,
) -> QuotaValidation:
    """
    Run full quota validation for a project.

    Returns:
        QuotaValidation with can_proceed, results, warnings, and blocking issues.
    """
    results: list[QuotaCheckResult] = []
    warnings: list[str] = []
    blocking: list[str] = []

    if audio_provider:
        audio_results = await check_audio_quota(audio_provider, total_characters)
        results.extend(audio_results)

        for r in audio_results:
            if r.sufficient is False:
                blocking.append(
                    f"Insufficient {r.resource_type} for {r.provider_name}: "
                    f"need {r.estimated_usage}, have {r.available}"
                )
            elif r.sufficient is None:
                warnings.append(
                    f"Cannot verify {r.resource_type} quota for {r.provider_name}"
                )

    if video_provider:
        video_results = await check_video_quota(
            video_provider, total_clips, clip_duration
        )
        results.extend(video_results)

        for r in video_results:
            if r.sufficient is False:
                blocking.append(
                    f"Insufficient {r.resource_type} for {r.provider_name}: "
                    f"need {r.estimated_usage}, have {r.available}"
                )
            elif r.sufficient is None:
                warnings.append(
                    f"Cannot verify {r.resource_type} quota for {r.provider_name}"
                )

    can_proceed = len(blocking) == 0

    validation = QuotaValidation(
        can_proceed=can_proceed,
        results=results,
        warnings=warnings,
        blocking_issues=blocking,
    )

    logger.info(
        "Quota validation complete",
        can_proceed=can_proceed,
        checks=len(results),
        warnings=len(warnings),
        blocking=len(blocking),
    )

    return validation
