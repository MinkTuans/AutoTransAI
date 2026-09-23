"""Evidence based, provider scoped capability decisions for catalog routing."""
from __future__ import annotations

from dataclasses import dataclass

CAPABILITIES = frozenset({"STT", "TRANSLATION", "LLM", "TTS", "VIDEO_GENERATION", "IMAGE_GENERATION", "VISUAL_GENDER"})


@dataclass(frozen=True)
class CapabilityEvidence:
    capabilities: frozenset[str]
    status: str
    incompatible: frozenset[str] = frozenset()


def classify(provider_id: str, metadata: dict | None, *, remote_model_id: str = "") -> CapabilityEvidence:
    """Interpret only evidence captured by discovery or narrowly documented services.

    An empty result is fully unknown, including for providers with mixed model
    families. A positive service flag narrows the set; it does not invent audio
    input or output support from a generic text generation method.
    """
    data = metadata if isinstance(metadata, dict) else {}
    positive: set[str] = set()
    negative: set[str] = set()
    if provider_id == "edge_tts":
        positive.add("TTS")
        negative.update(CAPABILITIES - {"TTS"})
    elif provider_id == "elevenlabs":
        flag = data.get("can_do_text_to_speech")
        if type(flag) is bool:
            if flag:
                positive.add("TTS")
            else:
                negative.add("TTS")
    elif provider_id == "gemini":
        methods = data.get("supportedGenerationMethods")
        if isinstance(methods, list):
            if "generateContent" in methods:
                positive.update(("TRANSLATION", "LLM"))
            else:
                negative.update(("TRANSLATION", "LLM"))
    elif provider_id == "anthropic":
        flags = data.get("capabilities")
        if isinstance(flags, dict):
            image = flags.get("image_input")
            if isinstance(image, dict) and type(image.get("supported")) is bool:
                positive.update(("TRANSLATION", "LLM"))
                if image["supported"]:
                    positive.add("VISUAL_GENDER")
                else:
                    negative.add("VISUAL_GENDER")
    elif provider_id == "fal":
        category = data.get("category")
        if category in ("image", "text-to-image", "image-to-image"):
            positive.add("IMAGE_GENERATION")
            negative.add("VIDEO_GENERATION")
        elif category in ("video", "text-to-video", "image-to-video"):
            positive.add("VIDEO_GENERATION")
            negative.add("IMAGE_GENERATION")
    status = "KNOWN" if len(positive | negative) == len(CAPABILITIES) else \
             "PARTIAL" if positive or negative else "FULL_UNKNOWN"
    return CapabilityEvidence(frozenset(positive), status, frozenset(negative))


def compatible(capability: str, evidence: CapabilityEvidence) -> bool:
    if capability not in CAPABILITIES:
        return False
    return capability not in evidence.incompatible


def model_evidence(model) -> CapabilityEvidence:
    """An explicit complete annotation wins; discovery fields stay per-capability."""
    if model.capability_status != "FULL_UNKNOWN":
        positive = set(model.capabilities or ())
        if "LLM" in positive:
            positive.add("TRANSLATION")
        positive = frozenset(positive)
        return CapabilityEvidence(positive, "KNOWN", CAPABILITIES - positive)
    return classify(model.provider_id, model.discovery_metadata, remote_model_id=model.remote_model_id)


def catalog_capability_summary(model) -> dict[str, str | list[str]]:
    """Task 7 catalog DTO source; never serialize raw persisted capability columns.

    Discovery metadata is retained as evidence, while this view is recomputed
    using the current registry so a refresh or rule correction cannot leave a
    stale capability label in catalog search responses.
    """
    evidence = model_evidence(model)
    return {
        "status": evidence.status,
        "capabilities": sorted(evidence.capabilities),
        "incompatible_capabilities": sorted(evidence.incompatible),
        "unknown_capabilities": sorted(CAPABILITIES - evidence.capabilities - evidence.incompatible),
    }
