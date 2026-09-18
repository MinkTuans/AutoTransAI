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


async def map_and_persist(db, project_id: str, segments: list[dict[str, Any]], llm, video_path: str | None = None) -> CharacterMappingResult:
    setting = (await db.execute(select(SystemSetting).where(SystemSetting.key == "character_mapping_confidence_threshold"))).scalar_one_or_none()
    try:
        threshold = float(setting.value) if setting else 0.85
    except (TypeError, ValueError):
        threshold = 0.85
    speakers = sorted({str(s["speaker_id"]) for s in segments})
    transcript = [{"speaker_id": s["speaker_id"], "text": s.get("translated_text") or s.get("text", "")} for s in segments]

    visual_genders = {}
    if video_path:
        try:
            from app.services.video_translator.visual_gender_service import detect_speakers_gender
            visual_genders = await detect_speakers_gender(video_path, segments)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to detect visual genders: {e}")

    # Priority 1: Query existing persistent SpeakerVoiceMapping records for this project
    existing_mappings = (
        await db.execute(
            select(SpeakerVoiceMapping).where(SpeakerVoiceMapping.project_id == project_id)
        )
    ).scalars().all()
    mapping_by_speaker = {m.speaker_id: m for m in existing_mappings if m.character_id}

    # Query existing CharacterVoiceProfile records for this project
    existing_profiles = (
        await db.execute(
            select(CharacterVoiceProfile).where(CharacterVoiceProfile.project_id == project_id)
        )
    ).scalars().all()
    profile_by_char_id = {p.character_id: p for p in existing_profiles}

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
        cand_speakers = [str(spk) for spk in candidate.get("speaker_ids", [])]
        resolved_cid = None
        # Priority 1: reuse existing persistent character_id mapped to stable speaker_id
        for spk in cand_speakers:
            if spk in mapping_by_speaker:
                resolved_cid = mapping_by_speaker[spk].character_id
                break

        # Priority 2: candidate matches existing character_id
        if not resolved_cid:
            raw_cid = candidate.get("character_id")
            if raw_cid and raw_cid in profile_by_char_id:
                resolved_cid = raw_cid

        # Priority 3: create new UUID only if no existing persistent mapping found
        if not resolved_cid:
            raw_character_id = str(candidate.get("character_id") or candidate.get("name") or "unknown")
            resolved_cid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{project_id}:{raw_character_id}"))

        candidate["character_id"] = resolved_cid

    result = validate_character_mapping(speakers, candidates, threshold)

    # Ensure result decisions strictly respect stable speaker_id persistent mappings
    for speaker_id, decision in result.by_speaker.items():
        if speaker_id in mapping_by_speaker:
            decision["character_id"] = mapping_by_speaker[speaker_id].character_id

    for speaker_id, decision in result.by_speaker.items():
        mapping = mapping_by_speaker.get(speaker_id)
        if not mapping:
            mapping = (await db.execute(select(SpeakerVoiceMapping).where(SpeakerVoiceMapping.project_id == project_id, SpeakerVoiceMapping.speaker_id == speaker_id))).scalar_one_or_none()

        if not mapping:
            mapping = SpeakerVoiceMapping(
                id=str(uuid.uuid4()),
                project_id=project_id,
                speaker_id=speaker_id,
                speaker_name=speaker_id,
                voice_provider="edge_tts",
                voice_id="",
                character_id=decision["character_id"]
            )
            db.add(mapping)
        else:
            decision["character_id"] = mapping.character_id

        mapping.character_id = decision["character_id"]
        mapping.confidence = decision["confidence"]
        mapping.needs_review = decision["confidence"] < threshold

        profile = profile_by_char_id.get(decision["character_id"])
        if not profile:
            profile = (await db.execute(select(CharacterVoiceProfile).where(CharacterVoiceProfile.project_id == project_id, CharacterVoiceProfile.character_id == decision["character_id"]))).scalar_one_or_none()

        visual_gender = visual_genders.get(speaker_id)
        norm_gender = str(visual_gender or decision.get("gender", "unknown")).lower()
        if norm_gender not in ("male", "female"):
            norm_gender = "unknown"

        if not profile:
            new_prof = CharacterVoiceProfile(
                id=str(uuid.uuid4()),
                project_id=project_id,
                character_id=decision["character_id"],
                name=decision.get("name") or speaker_id,
                gender=norm_gender,
                role=decision.get("role", "supporting"),
                mapping_confidence=decision["confidence"]
            )
            db.add(new_prof)
            profile_by_char_id[decision["character_id"]] = new_prof
        elif not profile.confirmed_by_user:
            # Update unconfirmed profile with higher confidence LLM metadata
            if decision.get("name") and decision["name"] != speaker_id:
                profile.name = decision["name"]
            if norm_gender != "unknown":
                profile.gender = norm_gender
            profile.mapping_confidence = max(profile.mapping_confidence or 0.0, decision["confidence"])
        # If profile.confirmed_by_user is True: preserve all user-confirmed data intact

    await db.flush()
    return result
