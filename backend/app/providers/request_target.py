"""Resolve a catalog invocation without storing request credentials on providers."""
from __future__ import annotations

from app.services.ai_routing import RouteTarget


def resolve_request_target(
    target: RouteTarget | None,
    api_key: str | None,
    *,
    provider_id: str,
    capabilities: tuple[str, ...],
    legacy_model: str | None,
    legacy_key: str | None,
) -> tuple[str | None, str | None]:
    if target is None:
        if api_key is not None:
            raise ValueError("A request credential requires a route target.")
        return legacy_model, legacy_key
    if target.provider_id != provider_id or target.capability not in capabilities:
        raise ValueError("Route target does not match this provider or capability.")
    if not target.remote_model_id or not api_key:
        raise ValueError("Route target requires a remote model and request credential.")
    return target.remote_model_id, api_key
