"""Evidence based, provider scoped capability decisions for catalog routing."""
from __future__ import annotations

from dataclasses import dataclass
import re

CAPABILITIES = frozenset({"STT", "TRANSLATION", "LLM", "TTS", "VIDEO_GENERATION", "IMAGE_GENERATION", "VISUAL_GENDER"})

# Exact model cards document image/audio input and text output. Keep previews,
# image generators and TTS variants unknown unless discovery provides evidence.
_KNOWN_GEMINI_CHAT = frozenset({
    "gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro",
    "gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-3.5-flash-lite",
    "gemini-3.6-flash", "gemini-3.7-flash", "gemini-3.8-flash",
})


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
        if (remote_model_id in _KNOWN_GEMINI_CHAT
                and (not isinstance(methods, list) or "generateContent" in methods)):
            positive.update(("TRANSLATION", "LLM", "STT", "VISUAL_GENDER"))
    elif provider_id == "openrouter":
        architecture = data.get("architecture")
        if isinstance(architecture, dict):
            inputs = architecture.get("input_modalities")
            outputs = architecture.get("output_modalities")
            inputs = set(inputs) if isinstance(inputs, list) and all(isinstance(v, str) for v in inputs) else set()
            outputs = set(outputs) if isinstance(outputs, list) and all(isinstance(v, str) for v in outputs) else set()
            if "text" in inputs and "text" in outputs:
                positive.update(("TRANSLATION", "LLM"))
            if "image" in inputs and "text" in outputs:
                positive.add("VISUAL_GENDER")
            if "transcription" in outputs:
                if "audio" in inputs:
                    positive.add("STT")
                else:
                    negative.add("STT")
            if "speech" in outputs:
                voices = data.get("supported_voices")
                if ("text" in inputs and isinstance(voices, list) and voices
                        and all(isinstance(voice, str) and voice for voice in voices)):
                    positive.add("TTS")
                else:
                    negative.add("TTS")
            if "image" in outputs:
                if (remote_model_id.startswith("recraft/")
                        and re.search(r"-vector(?:$|[-:])", remote_model_id)):
                    negative.add("IMAGE_GENERATION")
                elif "text" not in inputs:
                    negative.add("IMAGE_GENERATION")
                else:
                    positive.add("IMAGE_GENERATION")
            if "video" in outputs:
                video = data.get("video")
                durations = video.get("supported_durations") if isinstance(video, dict) else None
                if ("text" in inputs and isinstance(durations, list) and durations
                        and all(type(value) is int and value > 0 for value in durations)):
                    positive.add("VIDEO_GENERATION")
                else:
                    negative.add("VIDEO_GENERATION")
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
    if model.source != "discovered" and model.capability_status != "FULL_UNKNOWN":
        positive = set(model.capabilities or ())
        if "LLM" in positive:
            positive.add("TRANSLATION")
        positive = frozenset(positive)
        complete = model.capability_status in ("KNOWN", "COMPLETE")
        return CapabilityEvidence(positive, "KNOWN" if complete else "PARTIAL" if positive else "FULL_UNKNOWN",
                                  CAPABILITIES - positive if complete else frozenset())
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
