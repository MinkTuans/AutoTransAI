"""Discovery outcomes do not authorize persistence or prove generation entitlement."""
from dataclasses import dataclass, field
import math
from typing import Literal


@dataclass(frozen=True)
class DiscoveredModel:
    remote_model_id: str
    display_name: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class DiscoveryResult:
    status: Literal["complete", "partial", "unsupported", "failed"]
    models: tuple[DiscoveredModel, ...] = ()
    error_code: str | None = None
    pages_fetched: int = 0
    # credential = returned to this credential, not verified by generation.
    access_scope: Literal["credential", "catalog", "verified_catalog", "unknown"] = "unknown"


@dataclass(frozen=True)
class DiscoveryLimits:
    max_pages: int = 100
    max_models: int = 10_000
    max_bytes: int = 8 * 1024 * 1024
    request_timeout: float = 10.0
    total_timeout: float = 60.0

    def __post_init__(self):
        for value in (self.max_pages, self.max_models, self.max_bytes):
            if type(value) is not int or value <= 0:
                raise ValueError("Discovery count limits must be positive integers")
        for value in (self.request_timeout, self.total_timeout):
            if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise ValueError("Discovery timeouts must be finite and positive")
