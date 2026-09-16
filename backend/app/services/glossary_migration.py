"""Pure legacy glossary audit used by the data migration and audit tooling."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Iterable

from app.services.glossary_service import normalize_glossary_text


@dataclass(frozen=True)
class LegacyGlossaryAudit:
    conflicts: list[dict[str, Any]]
    canonical_ids: set[str]
    duplicate_ids: set[str]


def audit_legacy_glossary_rows(rows: Iterable[dict[str, Any]]) -> LegacyGlossaryAudit:
    materialized = list(rows)
    by_source: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    by_translation: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in materialized:
        project_id = str(row["project_id"])
        by_source[(project_id, normalize_glossary_text(row["source_term"]))].append(row)
        by_translation[(project_id, normalize_glossary_text(row["translated_term"]))].append(row)

    conflicts: list[dict[str, Any]] = []
    for (project_id, normalized_source), group in by_source.items():
        targets = {normalize_glossary_text(row["translated_term"]) for row in group}
        if len(targets) > 1:
            conflicts.append(
                {
                    "code": "SOURCE_CONFLICT",
                    "project_id": project_id,
                    "normalized_source": normalized_source,
                    "record_ids": [row["id"] for row in group],
                    "records": [
                        {
                            "table": row.get("table"),
                            "id": row["id"],
                            "source_term": row["source_term"],
                            "translated_term": row["translated_term"],
                        }
                        for row in group
                    ],
                }
            )
    for (project_id, normalized_translation), group in by_translation.items():
        sources = {normalize_glossary_text(row["source_term"]) for row in group}
        if len(sources) > 1:
            conflicts.append(
                {
                    "code": "TRANSLATION_CONFLICT",
                    "project_id": project_id,
                    "normalized_translation": normalized_translation,
                    "record_ids": [row["id"] for row in group],
                    "records": [
                        {
                            "table": row.get("table"),
                            "id": row["id"],
                            "source_term": row["source_term"],
                            "translated_term": row["translated_term"],
                        }
                        for row in group
                    ],
                }
            )
    if conflicts:
        return LegacyGlossaryAudit(conflicts, set(), set())

    by_mapping: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in materialized:
        by_mapping[
            (
                str(row["project_id"]),
                normalize_glossary_text(row["source_term"]),
                normalize_glossary_text(row["translated_term"]),
            )
        ].append(row)

    canonical_ids: set[str] = set()
    duplicate_ids: set[str] = set()
    for group in by_mapping.values():
        ordered = sorted(
            group,
            key=lambda row: (row.get("table") != "project_glossaries", str(row["id"])),
        )
        canonical_ids.add(str(ordered[0]["id"]))
        duplicate_ids.update(str(row["id"]) for row in ordered[1:])
    return LegacyGlossaryAudit(conflicts, canonical_ids, duplicate_ids)
