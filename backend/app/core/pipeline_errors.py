"""
PipelineError — Structured error classification for AI Pipeline operations.

Provides user-friendly error objects with error codes, localized messages,
and separated technical details for frontend 2-tier display.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


# ── Error Code Constants ──────────────────────────────────────────────────
AI_MODEL_NOT_AVAILABLE = "AI_MODEL_NOT_AVAILABLE"
AI_MODEL_NOT_FOUND = "AI_MODEL_NOT_FOUND"
AI_PROVIDER_API_ERROR = "AI_PROVIDER_API_ERROR"
AI_PROVIDER_AUTH_ERROR = "AI_PROVIDER_AUTH_ERROR"
AI_RATE_LIMIT = "AI_RATE_LIMIT"
AI_QUOTA_EXCEEDED = "AI_QUOTA_EXCEEDED"
AI_MODEL_CAPABILITY_MISMATCH = "AI_MODEL_CAPABILITY_MISMATCH"
AI_CONFIGURATION_ERROR = "AI_CONFIGURATION_ERROR"
NETWORK_ERROR = "NETWORK_ERROR"
PIPELINE_ERROR = "PIPELINE_ERROR"


# ── Human-readable titles per error code ──────────────────────────────────
ERROR_TITLES = {
    AI_MODEL_NOT_AVAILABLE: "AI Model không khả dụng",
    AI_MODEL_NOT_FOUND: "Không tìm thấy AI Model",
    AI_PROVIDER_API_ERROR: "Nhà cung cấp AI gặp lỗi",
    AI_PROVIDER_AUTH_ERROR: "API Key không hợp lệ",
    AI_RATE_LIMIT: "Đã vượt giới hạn API",
    AI_QUOTA_EXCEEDED: "Đã hết quota API",
    AI_MODEL_CAPABILITY_MISMATCH: "Model không hỗ trợ chức năng yêu cầu",
    AI_CONFIGURATION_ERROR: "Cấu hình AI chưa đúng",
    NETWORK_ERROR: "Không thể kết nối tới AI Provider",
    PIPELINE_ERROR: "Pipeline gặp lỗi",
}

# ── User action suggestions per error code ────────────────────────────────
ERROR_USER_ACTIONS = {
    AI_MODEL_NOT_AVAILABLE: "Model này có thể đã bị ngừng hỗ trợ. Hãy kiểm tra và cập nhật AI Model trong phần Cài đặt.",
    AI_MODEL_NOT_FOUND: "Vui lòng kiểm tra và cấu hình AI Model phù hợp trong phần Cài đặt.",
    AI_PROVIDER_API_ERROR: "Vui lòng thử lại sau hoặc kiểm tra trạng thái của nhà cung cấp AI.",
    AI_PROVIDER_AUTH_ERROR: "Vui lòng kiểm tra và cập nhật API Key trong phần Cài đặt.",
    AI_RATE_LIMIT: "Vui lòng đợi vài phút rồi thử lại.",
    AI_QUOTA_EXCEEDED: "Hãy kiểm tra quota/credit của tài khoản AI hoặc chuyển sang Provider khác.",
    AI_MODEL_CAPABILITY_MISMATCH: "Hãy chọn model có hỗ trợ chức năng này trong phần Cài đặt.",
    AI_CONFIGURATION_ERROR: "Vui lòng kiểm tra cấu hình AI trong phần Cài đặt.",
    NETWORK_ERROR: "Vui lòng kiểm tra kết nối mạng và thử lại.",
    PIPELINE_ERROR: "Vui lòng thử lại. Nếu lỗi tiếp tục, hãy kiểm tra Log chi tiết.",
}

# ── Capability display names ──────────────────────────────────────────────
CAPABILITY_DISPLAY = {
    "STT": "Speech-to-Text",
    "TRANSLATION": "Dịch thuật",
    "LLM": "Xử lý ngôn ngữ (LLM)",
    "TTS": "Text-to-Speech (Giọng nói)",
    "VIDEO_GENERATION": "Tạo Video",
    "IMAGE_GENERATION": "Tạo Hình ảnh",
}


class PipelineError(Exception):
    """
    Structured pipeline error with user-friendly and technical layers.

    Frontend displays `title`, `message`, `user_action` by default.
    `details` (technical_error, stack_trace) shown only on "Xem Log Chi Tiết".
    """

    def __init__(
        self,
        code: str = PIPELINE_ERROR,
        stage: str = "",
        message: str = "",
        provider: str = "",
        model: str = "",
        http_status: Optional[int] = None,
        technical_error: str = "",
        user_action: Optional[str] = None,
        title: Optional[str] = None,
    ):
        self.code = code
        self.stage = stage
        self.title = title or ERROR_TITLES.get(code, "Pipeline gặp lỗi")
        self.message = message
        self.provider = provider
        self.model = model
        self.http_status = http_status
        self.user_action = user_action or ERROR_USER_ACTIONS.get(code, "")
        self.technical_error = technical_error

        # Build human-readable summary for logging
        summary_parts = [self.title]
        if message:
            summary_parts.append(message)
        if model:
            summary_parts.append(f"Model: {model}")
        if http_status:
            summary_parts.append(f"HTTP {http_status}")
        super().__init__(" | ".join(summary_parts))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to structured JSON for API response."""
        result: Dict[str, Any] = {
            "code": self.code,
            "stage": self.stage,
            "title": self.title,
            "message": self.message,
            "provider": self.provider,
            "model": self.model,
            "user_action": self.user_action,
        }
        if self.http_status is not None:
            result["http_status"] = self.http_status
        # Technical details — frontend should hide behind "Xem Log Chi Tiết"
        result["details"] = {
            "technical_error": self.technical_error,
        }
        return result

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "PipelineError":
        """Deserialize from dict (e.g. stored error JSON)."""
        details = data.get("details", {})
        return PipelineError(
            code=data.get("code", PIPELINE_ERROR),
            stage=data.get("stage", ""),
            message=data.get("message", ""),
            provider=data.get("provider", ""),
            model=data.get("model", ""),
            http_status=data.get("http_status"),
            technical_error=details.get("technical_error", ""),
            user_action=data.get("user_action"),
            title=data.get("title"),
        )


def classify_http_error(
    status_code: int,
    response_text: str,
    provider: str,
    model: str,
    stage: str = "",
) -> PipelineError:
    """Classify an HTTP error response into a structured PipelineError."""
    if status_code == 404:
        return PipelineError(
            code=AI_MODEL_NOT_AVAILABLE,
            stage=stage,
            message=f"Model {model} không còn khả dụng hoặc không tồn tại.",
            provider=provider,
            model=model,
            http_status=status_code,
            technical_error=response_text[:500],
        )
    elif status_code == 401 or status_code == 403:
        return PipelineError(
            code=AI_PROVIDER_AUTH_ERROR,
            stage=stage,
            message=f"API Key cho {provider} không hợp lệ hoặc đã hết hạn.",
            provider=provider,
            model=model,
            http_status=status_code,
            technical_error=response_text[:500],
        )
    elif status_code == 429:
        return PipelineError(
            code=AI_RATE_LIMIT,
            stage=stage,
            message=f"Đã vượt giới hạn sử dụng API của {provider}.",
            provider=provider,
            model=model,
            http_status=status_code,
            technical_error=response_text[:500],
        )
    else:
        return PipelineError(
            code=AI_PROVIDER_API_ERROR,
            stage=stage,
            message=f"Nhà cung cấp {provider} trả về lỗi HTTP {status_code}.",
            provider=provider,
            model=model,
            http_status=status_code,
            technical_error=response_text[:500],
        )


def classify_exception(
    exc: Exception,
    provider: str = "",
    model: str = "",
    stage: str = "",
) -> PipelineError:
    """Classify a generic exception into a structured PipelineError."""
    import httpx

    err_str = str(exc)

    # Check for network errors
    if isinstance(exc, (httpx.TimeoutException, httpx.ConnectError, ConnectionError, OSError)):
        return PipelineError(
            code=NETWORK_ERROR,
            stage=stage,
            message=f"Không thể kết nối tới nhà cung cấp AI {provider}.",
            provider=provider,
            model=model,
            technical_error=err_str[:500],
        )

    # Check for quota exceeded patterns
    quota_patterns = ["quota", "credit", "billing", "exceeded"]
    if any(p in err_str.lower() for p in quota_patterns):
        return PipelineError(
            code=AI_QUOTA_EXCEEDED,
            stage=stage,
            message=f"Đã hết quota hoặc credit cho {provider}.",
            provider=provider,
            model=model,
            technical_error=err_str[:500],
        )

    # Check for rate limit patterns
    rate_patterns = ["rate limit", "rate_limit", "too many requests"]
    if any(p in err_str.lower() for p in rate_patterns):
        return PipelineError(
            code=AI_RATE_LIMIT,
            stage=stage,
            message=f"Đã vượt giới hạn sử dụng API của {provider}.",
            provider=provider,
            model=model,
            technical_error=err_str[:500],
        )

    # Check for auth patterns
    auth_patterns = ["api key", "api_key", "unauthorized", "forbidden", "invalid key", "authentication"]
    if any(p in err_str.lower() for p in auth_patterns):
        return PipelineError(
            code=AI_PROVIDER_AUTH_ERROR,
            stage=stage,
            message=f"API Key cho {provider} không hợp lệ hoặc chưa được cấu hình.",
            provider=provider,
            model=model,
            technical_error=err_str[:500],
        )

    # Check for model not available patterns
    unavailable_patterns = ["no longer available", "not found", "deprecated", "does not exist", "404"]
    if any(p in err_str.lower() for p in unavailable_patterns):
        return PipelineError(
            code=AI_MODEL_NOT_AVAILABLE,
            stage=stage,
            message=f"Model {model} không còn khả dụng.",
            provider=provider,
            model=model,
            technical_error=err_str[:500],
        )

    # Default — generic pipeline error
    return PipelineError(
        code=PIPELINE_ERROR,
        stage=stage,
        message=err_str[:300] if err_str else "Đã xảy ra lỗi không xác định trong Pipeline.",
        provider=provider,
        model=model,
        technical_error=err_str[:1000],
    )
