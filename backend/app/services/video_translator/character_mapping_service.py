"""Conservative validation for whole-transcript Speaker → Character mapping."""

from dataclasses import dataclass
from typing import Any
import json
import uuid
from sqlalchemy import select

from app.models.settings import SystemSetting
from app.models.workflow_engine import CharacterVoiceProfile, SpeakerVoiceMapping


@dataclass
class CharacterMappingResult:
    by_speaker: dict[str, dict[str, Any]]
    requires_review: bool
    issues: list[dict[str, Any]]


def validate_character_mapping(speaker_ids: list[str], candidates: list[dict[str, Any]], threshold: float) -> CharacterMappingResult:
    known = set(speaker_ids)
    mapped: dict[str, dict[str, Any]] = {}
    issues: list[dict[str, Any]] = []
    for candidate in candidates:
        members = [str(value) for value in candidate.get("speaker_ids", []) if str(value) in known]
        confidence = max(0.0, min(1.0, float(candidate.get("confidence", 0.0))))
        if confidence < threshold:
            issues.append({"speaker_ids": members, "reason": "low_confidence", "confidence": confidence})
            continue
        for speaker_id in members:
            if speaker_id in mapped:
                issues.append({"speaker_ids": [speaker_id], "reason": "duplicate_assignment"})
                continue
            mapped[speaker_id] = {**candidate, "speaker_id": speaker_id, "confidence": confidence}

    for speaker_id in speaker_ids:
        if speaker_id not in mapped:
            mapped[speaker_id] = {
                "speaker_id": speaker_id,
                "character_id": f"character-{speaker_id.lower()}",
                "name": speaker_id,
                "gender": "unknown",
                "role": "supporting",
                "confidence": 0.0,
            }
            issues.append({"speaker_ids": [speaker_id], "reason": "unresolved_speaker"})
    return CharacterMappingResult(mapped, bool(issues), issues)


async def map_and_persist(db, project_id: str, segments: list[dict[str, Any]], llm) -> CharacterMappingResult:
    setting = (await db.execute(select(SystemSetting).where(SystemSetting.key == "character_mapping_confidence_threshold"))).scalar_one_or_none()
    try:
        threshold = float(setting.value) if setting else 0.85
    except (TypeError, ValueError):
        threshold = 0.85
    speakers = sorted({str(s["speaker_id"]) for s in segments})
    transcript = [{"speaker_id": s["speaker_id"], "text": s.get("translated_text") or s.get("text", "")} for s in segments]
    prompt = (
        "Analyze the complete dialogue and map speakers to characters conservatively. "
        "Only merge speakers when strongly supported. Return JSON only: "
        '{"characters":[{"character_id":"...","name":"...","gender":"male|female|unknown",'
        '"role":"main|supporting","speaker_ids":["..."],"confidence":0.0}]}\n'
        + json.dumps(transcript, ensure_ascii=False)
    )
    try:
        raw = await llm.generate_text(prompt)
        parsed = json.loads(raw.strip().removeprefix("```json").removesuffix("```").strip())
        candidates = parsed.get("characters", [])
    except Exception:
        candidates = []
    for candidate in candidates:
        raw_character_id = str(candidate.get("character_id") or candidate.get("name") or "unknown")
        candidate["character_id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{project_id}:{raw_character_id}"))
    result = validate_character_mapping(speakers, candidates, threshold)
    for decision in result.by_speaker.values():
        if len(str(decision["character_id"])) != 36:
            decision["character_id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{project_id}:{decision['character_id']}"))
    for speaker_id, decision in result.by_speaker.items():
        mapping = (await db.execute(select(SpeakerVoiceMapping).where(SpeakerVoiceMapping.project_id == project_id, SpeakerVoiceMapping.speaker_id == speaker_id))).scalar_one_or_none()
        if not mapping:
            mapping = SpeakerVoiceMapping(id=str(uuid.uuid4()), project_id=project_id, speaker_id=speaker_id, speaker_name=speaker_id, voice_provider="edge_tts", voice_id="", character_id=decision["character_id"])
            db.add(mapping)
        mapping.character_id = decision["character_id"]
        mapping.confidence = decision["confidence"]
        mapping.needs_review = decision["confidence"] < threshold
        profile = (await db.execute(select(CharacterVoiceProfile).where(CharacterVoiceProfile.project_id == project_id, CharacterVoiceProfile.character_id == decision["character_id"]))).scalar_one_or_none()
        if not profile:
            db.add(CharacterVoiceProfile(id=str(uuid.uuid4()), project_id=project_id, character_id=decision["character_id"], name=decision.get("name") or speaker_id, gender=decision.get("gender", "unknown"), role=decision.get("role", "supporting"), mapping_confidence=decision["confidence"]))
    await db.flush()
    return result
