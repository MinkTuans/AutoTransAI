"""Official list endpoints verified 2026-09-23; no generated model-name guesses.

Contracts: ai.google.dev/api/models; developers.openai.com/api/reference/resources/models;
platform.claude.com/docs/en/api/models/list; elevenlabs.io/docs/api-reference/models/list;
fal.ai/docs/platform-apis/v1/models. See task report for full source links.
"""
from dataclasses import dataclass
import json
import re
import unicodedata
from urllib.parse import unquote

from .types import DiscoveredModel


class DiscoveryError(Exception):
    """Contains a locally defined code only, never an upstream message."""


def _contains_credential(value: str, secret: str | None) -> bool:
    # Check before decoding too: a credential may itself contain percent escapes.
    if not secret:
        return False
    return secret in value or secret in unquote(value)


def identity(value, secret: str | None, max_length=255) -> str:
    if (not isinstance(value, str) or not value or len(value) > max_length
            or value != value.strip() or any(unicodedata.category(c).startswith("C") for c in value)
            or _contains_credential(value, secret)):
        raise DiscoveryError("malformed")
    return value


def safe_text(value, secret: str | None) -> str | None:
    if not isinstance(value, str):
        return None
    value = "".join(c for c in value if not unicodedata.category(c).startswith("C"))
    if _contains_credential(value, secret):
        return "[redacted]"
    value = re.sub(r"https?://\S+", "[url]", value)
    return value[:255] or None


@dataclass(frozen=True)
class ListAdapter:
    provider: str
    url: str
    auth_header: str
    auth_prefix: str
    list_field: str | None
    id_field: str
    name_field: str | None = None
    cursor_field: str | None = None
    cursor_param: str | None = None
    page_size_param: str | None = None
    access_scope: str = "credential"

    def headers(self, secret: str | None) -> dict:
        headers = {"accept": "application/json", "accept-encoding": "identity"}
        if secret:
            headers[self.auth_header] = self.auth_prefix + secret
        if self.provider == "anthropic":
            headers["anthropic-version"] = "2023-06-01"
        return headers

    def page(self, payload, secret: str | None) -> tuple[list, str | None]:
        if self.list_field is None:
            rows = payload
            cursor = None
        else:
            if not isinstance(payload, dict) or "error" in payload:
                raise DiscoveryError("malformed")
            rows = payload.get(self.list_field)
            cursor = payload.get(self.cursor_field) if self.cursor_field else None
            if cursor is not None and not isinstance(cursor, str):
                raise DiscoveryError("malformed")
            if self.provider in {"anthropic", "fal"}:
                if type(payload.get("has_more")) is not bool:
                    raise DiscoveryError("malformed")
                if payload["has_more"] and not cursor:
                    raise DiscoveryError("incomplete")
                if not payload["has_more"]:
                    if self.provider == "fal" and cursor:
                        raise DiscoveryError("incomplete")
                    cursor = None
            elif self.provider == "openai" and any(
                payload.get(key) for key in ("has_more", "next", "next_cursor", "nextPageToken")
            ):
                raise DiscoveryError("malformed")
        if not isinstance(rows, list):
            raise DiscoveryError("malformed")
        if cursor is not None and cursor != "":
            cursor = identity(cursor, secret, max_length=2048)
        return rows, cursor or None

    def model(self, row, secret: str | None) -> DiscoveredModel:
        if not isinstance(row, dict):
            raise DiscoveryError("malformed")
        remote_id = row.get(self.id_field)
        if self.provider == "gemini":
            if not isinstance(remote_id, str) or not remote_id.startswith("models/"):
                raise DiscoveryError("malformed")
            remote_id = remote_id.removeprefix("models/")
        remote_id = identity(remote_id, secret)
        source = row.get("metadata", {}) if self.provider == "fal" else row
        if not isinstance(source, dict):
            raise DiscoveryError("malformed")
        return DiscoveredModel(remote_id, safe_text(source.get(self.name_field), secret), self.metadata(source, secret))

    def metadata(self, source, secret: str | None) -> dict:
        """Reapply provider allowlists at both HTTP and persistence boundaries.

        Ignore oversized input strings before scanning them; retain at most 8 KiB
        of UTF-8 JSON evidence, with fixed fields and bounded shallow structures.
        """
        if not isinstance(source, dict):
            return {}
        metadata = {}
        text_fields = {"gemini": ("baseModelId", "version"), "openai": ("owned_by",),
                       "anthropic": ("created_at",), "fal": ("category", "status")}
        int_fields = {"gemini": ("inputTokenLimit", "outputTokenLimit"), "openai": ("created",),
                      "anthropic": ("max_input_tokens", "max_tokens")}
        bool_fields = {"gemini": ("thinking",), "elevenlabs": (
            "can_do_text_to_speech", "can_do_voice_conversion", "requires_alpha_access")}
        for key in text_fields.get(self.provider, ()):
            raw = source.get(key)
            value = safe_text(raw, secret) if isinstance(raw, str) and len(raw) <= 4096 else None
            if value is not None:
                metadata[key] = value
        for key in int_fields.get(self.provider, ()):
            value = source.get(key)
            if type(value) is int and 0 <= value <= 2**63 - 1:
                metadata[key] = value
        for key in bool_fields.get(self.provider, ()):
            if type(source.get(key)) is bool:
                metadata[key] = source[key]
        if self.provider == "gemini" and isinstance(source.get("supportedGenerationMethods"), list):
            metadata["supportedGenerationMethods"] = [text for value in source["supportedGenerationMethods"][:32]
                if isinstance(value, str) and len(value) <= 4096
                if (text := safe_text(value, secret)) is not None]
        if self.provider == "anthropic" and isinstance(source.get("capabilities"), dict):
            evidence = {}
            for key in ("batch", "citations", "code_execution", "context_management", "effort",
                        "image_input", "pdf_input", "structured_outputs", "thinking"):
                value = source["capabilities"].get(key)
                if isinstance(value, dict) and type(value.get("supported")) is bool:
                    evidence[key] = {"supported": value["supported"]}
            if evidence:
                metadata["capabilities"] = evidence
        # Scalars/nested capability flags are fixed-size. Trim list tails to keep
        # useful initial capability evidence when multibyte strings fill the budget.
        methods = metadata.get("supportedGenerationMethods", [])
        while methods and len(json.dumps(metadata, ensure_ascii=False).encode("utf-8")) > 8192:
            methods.pop()
        return metadata


ADAPTERS = {adapter.provider: adapter for adapter in (
    ListAdapter("gemini", "https://generativelanguage.googleapis.com/v1beta/models", "x-goog-api-key", "",
                "models", "name", "displayName", "nextPageToken", "pageToken", "pageSize"),
    ListAdapter("openai", "https://api.openai.com/v1/models", "authorization", "Bearer ", "data", "id"),
    ListAdapter("anthropic", "https://api.anthropic.com/v1/models", "x-api-key", "", "data", "id",
                "display_name", "last_id", "after_id", "limit"),
    ListAdapter("elevenlabs", "https://api.elevenlabs.io/v1/models", "xi-api-key", "", None, "model_id",
                "name", access_scope="catalog"),
    ListAdapter("fal", "https://api.fal.ai/v1/models", "authorization", "Key ", "models", "endpoint_id",
                "display_name", "next_cursor", "cursor", "limit", "catalog"),
)}
