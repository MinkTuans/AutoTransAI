"""Provider-neutral Character Voice Profile assignment and conflict validation."""

from dataclasses import dataclass
from typing import Any
import uuid
from sqlalchemy import select
from app.models.workflow_engine import CharacterVoiceProfile, VoicePoolEntry


@dataclass
class VoiceValidationResult:
    assignments: dict[str, dict[str, Any]]
    requires_review: bool
    conflicts: list[dict[str, Any]]

    @property
    def passed(self) -> bool:
        return not self.requires_review


def assign_voices(
    characters: list[dict[str, Any]],
    pool: list[dict[str, Any]],
    conflict_edges: set[tuple[str, str]],
    profiles: dict[str, dict[str, Any]] | None = None,
    target_language: str = "vi-VN",
    default_male_voice_id: str | None = None,
    default_female_voice_id: str | None = None,
) -> VoiceValidationResult:
    profiles = profiles or {}
    assignments: dict[str, dict[str, Any]] = {}
    conflicts: list[dict[str, Any]] = []
    neighbors: dict[str, set[str]] = {}
    for left, right in conflict_edges:
        neighbors.setdefault(left, set()).add(right)
        neighbors.setdefault(right, set()).add(left)

    # Filter pool by target language prefix/match (e.g. vi-VN or vi)
    norm_target = target_language.lower().split("-")[0]
    filtered_pool = [
        v for v in pool
        if str(v.get("language", "")).lower().startswith(norm_target) or str(v.get("language", "")).lower() == target_language.lower()
    ]

    for character in characters:
        character_id = character["character_id"]
        char_gender = str(character.get("gender", "unknown")).lower()
        existing = profiles.get(character_id)

        # Always preserve user-confirmed profile voice assignments
        if existing and existing.get("voice_id"):
            if existing.get("confirmed_by_user"):
                assignments[character_id] = dict(existing)
                continue
            ex_provider = existing.get("voice_provider", "edge_tts")
            ex_voice_id = existing["voice_id"]
            # Check if unconfirmed existing voice is compatible with target language & gender
            match_in_pool = next((v for v in pool if v.get("provider") == ex_provider and v.get("voice_id") == ex_voice_id), None)
            if match_in_pool:
                v_lang = str(match_in_pool.get("language", "")).lower()
                v_gender = str(match_in_pool.get("gender", "")).lower()
                if (v_lang.startswith(norm_target) or v_lang == target_language.lower()) and (char_gender == "unknown" or v_gender == char_gender):
                    assignments[character_id] = dict(existing)
                    continue

        if char_gender not in ("male", "female"):
            conflicts.append({"character_id": character_id, "reason": "gender_unresolved", "message": f"Nhân vật '{character.get('name', character_id)}' chưa xác định giới tính."})
            continue

        preferred = None
        if char_gender == "male":
            preferred = default_male_voice_id or "vi-VN-NamMinhNeural"
        elif char_gender == "female":
            preferred = default_female_voice_id or "vi-VN-HoaiMyNeural"

        used_tuples = {(assignments[n]["voice_provider"], assignments[n]["voice_id"]) for n in neighbors.get(character_id, set()) if n in assignments}
        choices = [v for v in filtered_pool if (v.get("provider"), v.get("voice_id")) not in used_tuples and str(v.get("gender", "")).lower() == char_gender]

        selected = (
            next((v for v in choices if v.get("voice_id") == preferred), None)
            or (choices[0] if choices else None)
        )
        if selected:
            assignments[character_id] = {
                "voice_provider": selected["provider"],
                "voice_id": selected["voice_id"],
                "confirmed_by_user": False,
            }
        else:
            conflicts.append({"character_id": character_id, "reason": "no_available_voice", "message": f"Không có giọng phù hợp cho nhân vật {char_gender}."})

    for left, right in conflict_edges:
        if left in assignments and right in assignments:
            l_key = (assignments[left].get("voice_provider"), assignments[left].get("voice_id"))
            r_key = (assignments[right].get("voice_provider"), assignments[right].get("voice_id"))
            if l_key == r_key:
                # Auto-resolve voice conflict for unconfirmed assignment by assigning a distinct voice from filtered_pool
                if not assignments[right].get("confirmed_by_user"):
                    right_char_gender = str(next((c.get("gender") for c in characters if c["character_id"] == right), "unknown")).lower()
                    alt_choices = [v for v in filtered_pool if (v.get("provider"), v.get("voice_id")) != l_key and str(v.get("gender", "")).lower() == right_char_gender]
                    if alt_choices:
                        assignments[right]["voice_provider"] = alt_choices[0]["provider"]
                        assignments[right]["voice_id"] = alt_choices[0]["voice_id"]
                        continue
                if not assignments[left].get("confirmed_by_user"):
                    left_char_gender = str(next((c.get("gender") for c in characters if c["character_id"] == left), "unknown")).lower()
                    alt_choices = [v for v in filtered_pool if (v.get("provider"), v.get("voice_id")) != r_key and str(v.get("gender", "")).lower() == left_char_gender]
                    if alt_choices:
                        assignments[left]["voice_provider"] = alt_choices[0]["provider"]
                        assignments[left]["voice_id"] = alt_choices[0]["voice_id"]
                        continue

                if assignments[left].get("confirmed_by_user") or assignments[right].get("confirmed_by_user"):
                    conflicts.append({"characters": [left, right], "reason": "confirmed_voice_conflict"})
                else:
                    conflicts.append({"characters": [left, right], "reason": "voice_conflict"})

    return VoiceValidationResult(assignments, bool(conflicts), conflicts)


async def assign_project_voices(
    db,
    project_id: str,
    segments: list[dict[str, Any]],
    target_language: str = "vi-VN",
    default_male_voice_id: str | None = None,
    default_female_voice_id: str | None = None,
) -> VoiceValidationResult:
    defaults = [
        ("vi-VN-NamMinhNeural", "male", "vi-VN"),
        ("vi-VN-HoaiMyNeural", "female", "vi-VN"),
        ("en-US-GuyNeural", "male", "en-US"),
        ("en-US-AriaNeural", "female", "en-US"),
    ]
    for voice_id, gender, language in defaults:
        row = (await db.execute(select(VoicePoolEntry).where(VoicePoolEntry.provider == "edge_tts", VoicePoolEntry.voice_id == voice_id))).scalar_one_or_none()
        if not row:
            db.add(VoicePoolEntry(id=str(uuid.uuid4()), provider="edge_tts", language=language, gender=gender, voice_id=voice_id, display_name=voice_id))
    await db.flush()

    profiles_rows = (await db.execute(select(CharacterVoiceProfile).where(CharacterVoiceProfile.project_id == project_id))).scalars().all()
    profiles = {p.character_id: {"voice_provider": p.voice_provider, "voice_id": p.voice_id, "confirmed_by_user": p.confirmed_by_user} for p in profiles_rows if p.voice_id}
    characters = [{"character_id": p.character_id, "name": p.name, "gender": p.gender, "role": p.role} for p in profiles_rows]
    existing_char_ids = {c["character_id"] for c in characters}
    for seg in segments:
        cid = seg.get("character_id") or (f"character-{seg['speaker_id'].lower()}" if seg.get("speaker_id") else None)
        if cid and cid not in existing_char_ids:
            characters.append({"character_id": cid, "name": cid, "gender": "unknown", "role": "supporting"})
            existing_char_ids.add(cid)

    pool_rows = (await db.execute(select(VoicePoolEntry).where(VoicePoolEntry.enabled.is_(True)))).scalars().all()
    pool = [{"provider": p.provider, "voice_id": p.voice_id, "gender": p.gender, "language": p.language} for p in pool_rows]

    edges = set()
    ordered = sorted(segments, key=lambda s: s["original_start"])
    for i, left in enumerate(ordered):
        for right in ordered[i + 1:]:
            if right["original_start"] >= left["original_end"]:
                break
            if left.get("character_id") and right.get("character_id") and left["character_id"] != right["character_id"]:
                edges.add((left["character_id"], right["character_id"]))

    result = assign_voices(
        characters,
        pool,
        edges,
        profiles,
        target_language=target_language,
        default_male_voice_id=default_male_voice_id,
        default_female_voice_id=default_female_voice_id,
    )
    for profile in profiles_rows:
        assignment = result.assignments.get(profile.character_id)
        if assignment and not profile.confirmed_by_user:
            profile.voice_provider = assignment["voice_provider"]
            profile.voice_id = assignment["voice_id"]
    await db.flush()
    return result

