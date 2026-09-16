import asyncio

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.models.project import Project
from app.services.glossary_service import (
    GlossaryConflictError,
    create_glossary_entry,
    normalize_glossary_text,
    update_glossary_entry,
)


@pytest.fixture
async def sessions(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'glossary.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        session.add(Project(id="project-1", title="Project"))
        await session.commit()
    try:
        yield factory
    finally:
        await engine.dispose()


def test_normalize_glossary_text_handles_unicode_invisible_whitespace_and_case():
    assert normalize_glossary_text("  ＬÝ\u200b   ĐẠO\tTHIÊN  ") == "lý đạo thiên"
    assert normalize_glossary_text("Ly Đạo Thiên") != normalize_glossary_text("Lý Đạo Thiên")


@pytest.mark.asyncio
async def test_create_is_idempotent_for_same_normalized_mapping(sessions):
    async with sessions() as session:
        first, created = await create_glossary_entry(
            session, "project-1", "李道天", "Lý Đạo Thiên", "character"
        )
    async with sessions() as session:
        second, created_again = await create_glossary_entry(
            session, "project-1", " 李道天\u200b ", "LÝ  ĐẠO THIÊN", "character"
        )
    assert created is True
    assert created_again is False
    assert second.id == first.id


@pytest.mark.asyncio
async def test_create_rejects_same_source_with_different_translation(sessions):
    async with sessions() as session:
        await create_glossary_entry(session, "project-1", "李道天", "Lý Đạo Thiên", "character")
    async with sessions() as session:
        with pytest.raises(GlossaryConflictError) as exc:
            await create_glossary_entry(session, "project-1", "李道天", "Lý Đạo Thiện", "character")
    assert exc.value.code == "GLOSSARY_SOURCE_CONFLICT"


@pytest.mark.asyncio
async def test_create_rejects_different_source_with_same_translation(sessions):
    async with sessions() as session:
        await create_glossary_entry(session, "project-1", "李道天", "Lý Đạo Thiên", "character")
    async with sessions() as session:
        with pytest.raises(GlossaryConflictError) as exc:
            await create_glossary_entry(session, "project-1", "李道仙", "Lý Đạo Thiên", "character")
    assert exc.value.code == "GLOSSARY_TRANSLATION_CONFLICT"


@pytest.mark.asyncio
async def test_update_excludes_current_row_but_rejects_other_rows(sessions):
    async with sessions() as session:
        first, _ = await create_glossary_entry(session, "project-1", "甲", "Giáp", "character")
        await create_glossary_entry(session, "project-1", "乙", "Ất", "character")
    async with sessions() as session:
        updated = await update_glossary_entry(
            session, "project-1", first.id, " 甲 ", "GIÁP", "location"
        )
        assert updated.term_type == "location"
    async with sessions() as session:
        with pytest.raises(GlossaryConflictError) as exc:
            await update_glossary_entry(session, "project-1", first.id, "乙", "Giáp", "location")
    assert exc.value.code == "GLOSSARY_SOURCE_CONFLICT"


@pytest.mark.asyncio
async def test_database_constraint_makes_concurrent_identical_create_idempotent(sessions):
    async def insert_once():
        async with sessions() as session:
            row, _ = await create_glossary_entry(
                session, "project-1", "并发名", "Tên Đồng Thời", "character"
            )
            return row.id

    ids = await asyncio.gather(insert_once(), insert_once())
    assert ids[0] == ids[1]


@pytest.mark.asyncio
async def test_database_constraint_allows_only_one_concurrent_source_mapping(sessions):
    async def insert_target(target):
        async with sessions() as session:
            try:
                row, _ = await create_glossary_entry(
                    session, "project-1", "竞态名", target, "character"
                )
                return ("saved", row.translated_term)
            except GlossaryConflictError as exc:
                return ("conflict", exc.code)

    outcomes = await asyncio.gather(
        insert_target("Tên Một"), insert_target("Tên Hai")
    )
    assert sorted(kind for kind, _ in outcomes) == ["conflict", "saved"]
    assert next(value for kind, value in outcomes if kind == "conflict") == "GLOSSARY_SOURCE_CONFLICT"


@pytest.mark.asyncio
async def test_glossary_api_returns_409_and_supports_edit(sessions):
    from fastapi import HTTPException
    from app.api.routes.video_translator import (
        GlossaryTermCreate,
        add_project_glossary_api,
        update_project_glossary_api,
    )

    async with sessions() as session:
        created = await add_project_glossary_api(
            "project-1",
            GlossaryTermCreate(
                source_term="李道天",
                translated_term="Lý Đạo Thiên",
                term_type="character",
            ),
            session,
        )
        entry_id = created["data"]["id"]
    async with sessions() as session:
        edited = await update_project_glossary_api(
            "project-1",
            entry_id,
            GlossaryTermCreate(
                source_term="李道天",
                translated_term="Lý Đạo Thiên",
                term_type="location",
            ),
            session,
        )
        assert edited["data"]["term_type"] == "location"
    async with sessions() as session:
        with pytest.raises(HTTPException) as exc:
            await add_project_glossary_api(
                "project-1",
                GlossaryTermCreate(
                    source_term="李道天",
                    translated_term="Lý Đạo Thiện",
                    term_type="character",
                ),
                session,
            )
    assert exc.value.status_code == 409
    assert exc.value.detail["code"] == "GLOSSARY_SOURCE_CONFLICT"
