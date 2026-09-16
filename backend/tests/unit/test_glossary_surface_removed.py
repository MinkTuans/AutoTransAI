from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_ai_terminology_memory_runtime_surface_is_removed():
    runtime_files = [
        ROOT / "backend/app/models/workflow_engine.py",
        ROOT / "backend/app/api/routes/video_translator.py",
        ROOT / "backend/app/api/routes/projects.py",
        ROOT / "backend/app/workflow/stages/translate_stage.py",
        ROOT / "frontend/src/api.js",
        ROOT / "frontend/src/components/ProjectGlossaryManager.jsx",
        ROOT / "frontend/src/pages/VideoTranslator.jsx",
    ]
    forbidden = (
        "ProjectTerminologyMemory",
        "terminology-memory",
        "AI Auto Terminology Memory",
        "Glossary Thủ Công",
    )
    for path in runtime_files:
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, f"{token!r} remains in {path}"


def test_frontend_exposes_single_glossary_and_edit_api():
    api = (ROOT / "frontend/src/api.js").read_text(encoding="utf-8")
    manager = (ROOT / "frontend/src/components/ProjectGlossaryManager.jsx").read_text(
        encoding="utf-8"
    )
    assert "updateGlossary" in api
    assert "Edit" in manager
    assert "memoryTerms" not in manager
