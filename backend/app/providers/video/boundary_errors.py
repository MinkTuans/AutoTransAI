"""Video request outcomes without media or HTTP dependencies."""

from app.services.ai_routing import RoutePending


class VideoBoundaryError(Exception):
    """Safe local error; provider body and exception text are never retained."""

    def __init__(self, code: str, status_code: int | None = None, *, definitive: bool = False):
        self.code = code
        self.status_code = status_code
        self.definitive = definitive
        super().__init__(f"Video generation failed: {code}")


class VideoRoutePending(RoutePending):
    """Accepted or uncertain task; outcome is a local classification only."""

    def __init__(self, outcome: str = "pending"):
        self.outcome = outcome
        super().__init__("Video generation pending")
