"""Extract terminology from transcripts and write it to the project glossary."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import get_settings
from app.core import get_logger
from app.models import APIKey, CatalogModel, CatalogRefreshRun
from app.models.settings import AIFunctionConfig
from app.providers.registry import get_registry
from app.services.ai_routing import (
    RouteConfigurationError, RouteTarget, UnsupportedModalityError, build_route, invoke_route,
)
from app.services.glossary_service import create_glossary_entry

logger = get_logger(__name__)

_CJK_RUN_RE = re.compile(r"[\u4e00-\u9fff]+")

_CJK_STOP = {
    "一个", "我们", "他们", "什么", "不是", "可以", "因为", "所以", "这个", "那个",
    "没有", "已经", "现在", "自己", "知道", "出来", "起来", "时候", "这样", "那样",
    "学校", "今天", "什么", "什麼", "怎么", "怎麼",
    "弟子", "哥哥", "弟弟", "姐姐", "妹妹", "师父", "师傅", "朋友", "人心",
    "山门", "山門", "门派", "門派", "宗门", "宗門",
    "爬上", "上车", "上車", "下去", "上来", "进去", "进去", "过去", "过来",
    "回去", "冰發", "究冰",
}

# Particles / function chars: n-grams containing these are clauses, not names.
_CJK_FUNC_CHARS = set(
    "了的是我不在有这那就会也和与把被要去来到从对给让还只很太最更"
    "你他她它吗呢啊吧着过没可所因什麼么們们叫想走先看而且爬"
)

_CJK_BAD_PREFIXES = (
    "而且", "但是", "然后", "然後", "于是", "於是", "就是", "还是", "還是",
    "或者", "虽然", "雖然", "如果", "因为", "所以", "只是", "可是", "并且", "以及",
)

# 2-char CJK is only a name when it starts with a common surname (张三, 姜男, 李四).
_CJK_SURNAMES = set(
    "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜"
    "戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍史"
    "唐费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卞齐康伍余元卜顾孟"
    "黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝"
    "董梁杜阮蓝闵季贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍"
    "虞万支柯昝管卢莫经房裘缪干解应宗丁宣贲邓郁单杭洪包诸左石崔吉钮"
    "龚程嵇邢滑裴陆荣翁荀羊於惠甄曲家封芮羿储靳汲邴糜松井段富巫乌焦"
    "巴弓牧隗山谷车侯宓蓬全郗班仰秋仲伊宫宁仇栾暴甘斜厉戎祖武符刘景"
    "詹束龙叶幸司韶郜黎蓟薄印宿白怀蒲邰从鄂索咸籍赖卓蔺屠蒙池乔阴鬱"
    "胥能苍双闻莘党翟谭贡劳逄姬申扶堵冉宰郦雍卻璩桑桂濮牛寿通边扈燕"
    "冀郏浦尚农温别庄晏柴瞿阎充慕连茹习宦艾鱼容向古易慎戈廖庾终暨居"
    "衡步都耿满弘匡国文寇广禄阙东欧殳沃利蔚越夔隆师巩厍聂晁勾敖融冷"
    "訾辛阚那简饶空曾毋沙乜养鞠须丰巢关蒯相查后荆红游竺权逯盖益桓公"
    "趙錢孫李週吳鄭王馮陳衛蔣韓楊許呂張嚴華金魏姜謝鄒範魯韋馬鳳俞劉"
    "黃蕭羅畢鄔齊顧黃穆姚鄧單龔鍾駱劉葉喬閻聶關"
)

_CJK_NAME_SUFFIXES = (
    "城", "宫", "殿", "宗", "谷", "岛", "國", "国",
    "府", "院", "寺", "观", "鎮", "镇", "村", "庄", "樓", "楼", "閣", "阁",
    "峰", "湖", "海", "河", "江", "寨", "营", "盟",
)

PROPER_NAME_TYPES = frozenset({"character", "location", "organization"})
EXTENDED_TERM_TYPES = frozenset({"creature", "skill", "weapon", "item", "technique", "title", "other"})

_CHINESE_LANG_CODES = {
    "zh", "chinese", "zh-cn", "zh-tw", "zh-hans", "zh-hant", "zh_cn", "zh_tw",
    "tiếng trung", "tieng trung", "trung", "mandarin", "cantonese",
}


def is_chinese_language(lang: str = "") -> bool:
    """True if language code or name represents Chinese."""
    clean = str(lang or "").lower().strip()
    return clean in _CHINESE_LANG_CODES


def has_cjk_characters(text: str) -> bool:
    """True if text contains any CJK (Han) characters."""
    if not text:
        return False
    return bool(_CJK_RUN_RE.search(str(text)))


def is_pure_cjk(text: str) -> bool:
    """True if text consists entirely of CJK characters (ignoring whitespace/punctuation)."""
    if not text:
        return False
    cleaned = re.sub(r"[\s\W\d_]+", "", str(text))
    return bool(cleaned and _CJK_RUN_RE.fullmatch(cleaned))


def is_self_mapped_cjk(source_term: str, translated_term: str, target_lang: str = "") -> bool:
    """True when a CJK source term maps to itself or remains untranslated CJK and target language is NOT Chinese.

    This catches invalid glossary entries like source_term=安妮, translated_term=安妮
    when target is Vietnamese/English. Returns False for legitimate same-term mappings
    like AI→AI or Netflix→Netflix (which are not CJK).
    """
    from app.services.glossary_service import normalize_glossary_text

    src = str(source_term or "").strip()
    tgt = str(translated_term or "").strip()
    if not src or not tgt:
        return False
    if is_chinese_language(target_lang):
        return False
    if has_cjk_characters(src):
        # 1. Compare normalized forms (e.g. 安妮 == 安妮)
        if normalize_glossary_text(src) == normalize_glossary_text(tgt):
            return True
        # 2. Translated term is still pure CJK characters (untranslated)
        if is_pure_cjk(tgt):
            return True
    return False


def is_valid_glossary_mapping(source_term: str, required: str, target_language: str = "") -> bool:
    """True if source_term -> required is a valid, enforceable glossary mapping.

    - Rejects empty source or required.
    - Rejects CJK source mapping to itself or untranslated CJK when target language is NOT Chinese (e.g. 安妮 -> 安妮).
    - Accepts legitimate same-term mappings (e.g. AI -> AI, Netflix -> Netflix, John -> John).
    - Accepts CJK -> CJK when target language IS Chinese.
    - Accepts CJK -> target translation (e.g. 安妮 -> Annie).
    """
    src = str(source_term or "").strip()
    req = str(required or "").strip()
    if not src or not req:
        return False
    if is_self_mapped_cjk(src, req, target_language):
        return False
    return True


def looks_like_cjk_name(term: str) -> bool:
    """True for 张三 / 青云城 / 李飞羽; false for 爬上 / 弟子 / 而且門派."""
    if not term or not _CJK_RUN_RE.fullmatch(term):
        return False
    if term in _CJK_STOP:
        return False
    if any(term.startswith(p) for p in _CJK_BAD_PREFIXES):
        return False
    if any(ch in _CJK_FUNC_CHARS for ch in term):
        return False
    if not (2 <= len(term) <= 6):
        return False
    if len(term) == 2:
        return term[0] in _CJK_SURNAMES
    return True


def filter_proper_names(terms: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep characters / places / orgs only. Drop verbs, kinship, conjunction+sect n-grams."""
    kept: list[dict[str, Any]] = []
    for item in normalize_extracted_terms(terms):
        source = item["source_term"]
        suggested = item["suggested_term"]
        translated = suggested != source
        term_type = item["term_type"] if item["term_type"] in PROPER_NAME_TYPES else ""
        if _CJK_RUN_RE.fullmatch(source):
            if not looks_like_cjk_name(source):
                continue
            if len(source) == 2 and not translated and source[0] not in _CJK_SURNAMES:
                continue
            if not term_type:
                term_type = "location" if source.endswith(_CJK_NAME_SUFFIXES) else "character"
        elif not term_type:
            words = source.split()
            if len(words) >= 2 and source[0].isupper() and not source.isupper():
                term_type = "character"
            else:
                continue
        if term_type not in PROPER_NAME_TYPES:
            continue
        item["term_type"] = term_type
        kept.append(item)
    return kept


def filter_terminology(terms: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep proper names plus explicitly translated domain terminology."""
    normalized = normalize_extracted_terms(terms)
    extended = [
        item
        for item in normalized
        if item["term_type"] in EXTENDED_TERM_TYPES
        and item["suggested_term"].casefold() != item["source_term"].casefold()
    ]
    extended_sources = {item["source_term"].casefold() for item in extended}
    return extended + [
        item
        for item in filter_proper_names(normalized)
        if item["source_term"].casefold() not in extended_sources
    ]

# Function words that look title-case in Vietnamese/English subtitles but are not names.
_NAME_STOP = {
    "tôi", "anh", "em", "bạn", "hắn", "nàng", "ta", "y", "gã", "lão", "thị",
    "người", "ông", "bà", "cô", "chú", "bác", "thầy", "cậu",
    "không", "có", "và", "hoặc", "nhưng", "nếu", "khi", "để", "được",
    "của", "trong", "ngoài", "một", "này", "đó", "đây", "rồi", "thì", "là",
    "bị", "vì", "do", "từ", "đến", "với", "cho", "về", "như", "sẽ", "đã",
    "đang", "rất", "nhiều", "ít", "hơn", "nhất", "vậy", "thế", "nên", "cũng",
    "nói", "làm", "đi", "lại", "ra", "vào", "lên", "xuống",
    "the", "a", "an", "and", "or", "but", "if", "when", "this", "that",
    "he", "she", "they", "we", "you", "i", "it", "his", "her", "their",
}


def normalize_extracted_terms(raw: Iterable[dict[str, Any]], target_lang: str = "") -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for item in raw or []:
        source = str(
            item.get("source_term")
            or item.get("source")
            or item.get("name")
            or item.get("term")
            or ""
        ).strip()
        if len(source) < 2:
            continue
        key = source.casefold()
        if key in seen:
            continue
        seen.add(key)
        raw_suggested = (
            item.get("suggested_term")
            or item.get("translation")
            or item.get("translated_term")
            or item.get("target")
        )
        if raw_suggested is not None and str(raw_suggested).strip():
            suggested = str(raw_suggested).strip()
        else:
            # If target language is NOT Chinese and source has CJK, do not guess or default to source
            if has_cjk_characters(source) and not is_chinese_language(target_lang):
                suggested = ""
            else:
                suggested = source
        term_type = str(item.get("term_type") or item.get("type") or "other").strip().lower() or "other"
        try:
            confidence = float(item.get("confidence") or 0.8)
        except (TypeError, ValueError):
            confidence = 0.8
        out.append(
            {
                "source_term": source,
                "suggested_term": suggested,
                "term_type": term_type[:50],
                "confidence": min(max(confidence, 0.0), 1.0),
                "source_context": (item.get("source_context") or None),
            }
        )
    return out


def _title_case_runs(text: str) -> list[str]:
    """Unicode title-case spans: 'Lý Tiêu Dao', 'Thanh Vân Thành', 'John Smith'."""
    runs: list[str] = []
    clauses = re.split(r"[.!?。！？;；,，、\n]+", text or "")
    for clause in clauses:
        tokens = re.findall(r"[^\W\d_]+", clause, flags=re.UNICODE)
        current: list[str] = []
        for tok in tokens:
            if tok and tok[0].isupper() and not tok.isupper():
                current.append(tok)
            else:
                if current:
                    runs.append(" ".join(current))
                    current = []
        if current:
            runs.append(" ".join(current))
    return runs


def heuristic_extract_terms(text: str, target_lang: str = "vi") -> list[dict[str, Any]]:
    """Fallback extractor: repeated CJK spans and Latin proper names."""
    blob = text or ""
    grams: list[str] = []
    for run in _CJK_RUN_RE.findall(blob):
        max_n = min(4, len(run))
        for n in range(2, max_n + 1):
            for i in range(0, len(run) - n + 1):
                grams.append(run[i : i + n])
    counts = Counter(grams)
    raw: list[dict[str, Any]] = []
    is_target_zh = is_chinese_language(target_lang)
    for term, n in counts.items():
        if not looks_like_cjk_name(term):
            continue
        has_place_suffix = term.endswith(_CJK_NAME_SUFFIXES)
        if n < 2 and not has_place_suffix:
            continue
        raw.append(
            {
                "source_term": term,
                "suggested_term": term if is_target_zh else "",
                "term_type": "location" if has_place_suffix else "character",
                "confidence": min(0.55 + 0.05 * n + (0.15 if has_place_suffix else 0), 0.9),
                "source_context": f"appeared {n} times",
            }
        )
    title_counts = Counter(_title_case_runs(blob))
    for term, n in title_counts.items():
        key = term.casefold()
        words = term.split()
        if key in _NAME_STOP:
            continue
        if len(words) == 1 and (len(term) < 3 or key in _NAME_STOP):
            continue
        raw.append(
            {
                "source_term": term,
                "suggested_term": term,
                "term_type": "character" if len(words) >= 2 else "other",
                "confidence": min(0.55 + 0.08 * n + (0.12 if len(words) >= 2 else 0), 0.9),
                "source_context": f"appeared {n} times",
            }
        )
    return normalize_extracted_terms(raw, target_lang=target_lang)


class InvalidTerminologyOutput(ValueError):
    code = "invalid_output"


def _parse_llm_terms(payload: str, target_lang: str = "", *, strict: bool = False) -> list[dict[str, Any]]:
    if not payload:
        if strict:
            raise InvalidTerminologyOutput() from None
        return []
    text = payload.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\[[\s\S]*\]", text)
        if not match:
            if strict:
                raise InvalidTerminologyOutput() from None
            return []
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            if strict:
                raise InvalidTerminologyOutput() from None
            return []
    if isinstance(data, dict):
        if strict and not any(key in data for key in ("terms", "entities", "names", "glossary", "items")):
            raise InvalidTerminologyOutput() from None
        data = (
            data.get("terms")
            or data.get("entities")
            or data.get("names")
            or data.get("glossary")
            or data.get("items")
            or []
        )
    if not isinstance(data, list):
        if strict:
            raise InvalidTerminologyOutput() from None
        return []
    return normalize_extracted_terms([x for x in data if isinstance(x, dict)], target_lang=target_lang)


async def llm_extract_terms(
    text: str, target_lang: str = "vi", *,
    sessions: async_sessionmaker[AsyncSession] | None = None,
    data_dir: Path | None = None,
) -> list[dict[str, Any]]:
    blob = (text or "").strip()
    if len(blob) < 8:
        return []
    route = None
    prompt_limit = 6000
    if sessions is not None:
        async with sessions() as catalog_db:
            catalog_model = await catalog_db.scalar(select(CatalogModel.id).where(
                CatalogModel.source != "system",
                CatalogModel.provider_id.in_(("gemini", "openai", "anthropic")),
            ).limit(1))
            catalog_key = await catalog_db.scalar(select(APIKey.id).where(
                APIKey.provider_id.in_(("gemini", "openai", "anthropic")),
            ).limit(1))
            await catalog_db.scalar(select(CatalogRefreshRun.id).limit(1))
            configured = await catalog_db.get(AIFunctionConfig, "translation")
            canonical_default = (await catalog_db.get(CatalogModel, configured.model_id)
                                 if configured and configured.model_id else None)
            if catalog_model is not None or catalog_key is not None or canonical_default is not None:
                if configured is None or not configured.model_id:
                    raise RouteConfigurationError("LLM default is not configured.")
                route = await build_route(catalog_db, "LLM")
                limits = []
                for target in route.targets:
                    model = await catalog_db.get(CatalogModel, target.model_id)
                    metadata = model.discovery_metadata if isinstance(model.discovery_metadata, dict) else {}
                    for field in ("inputTokenLimit", "max_input_tokens"):
                        value = metadata.get(field)
                        if type(value) is int and value > 0:
                            limits.append(value)
                            break
                prompt_limit = min(6000, max(0, min(limits) - 512)) if limits else 6000

    prompt_prefix = (
        "Extract important canonical terminology: people/characters, creatures, place names, "
        "organizations, skills, weapons, items, techniques, titles, and important domain terms.\n"
        "Do NOT extract sentences, clauses, verbs, pronouns, or random subtitle fragments "
        "(e.g. 我先走了, 看来今天, 只是想给).\n"
        f"Lines may include source transcript and the {target_lang} translation.\n"
        'Return ONLY JSON: {{"terms":[{{"source_term":"...","suggested_term":"...","term_type":"character","confidence":0.9}}]}}\n'
        "source_term is the original-language name; suggested_term MUST be the translated/transliterated name "
        f"in {target_lang} (keep {target_lang} diacritics). "
        "IMPORTANT: If source_term is in Chinese (e.g. 安妮, 詹森, 路斯), suggested_term MUST be the "
        f"{target_lang} rendering (e.g. Annie, Jensen, Ruth), NOT the original Chinese characters. "
        "Never set suggested_term equal to source_term when they are in different scripts. "
        "If you do not have enough information to determine the target name, do NOT guess; omit the term.\n"
        "term_type must be one of: character, creature, location, organization, skill, weapon, "
        "item, technique, title, other.\n\n"
        "Subtitles:\n"
    )
    if route is not None:
        room = prompt_limit - len(prompt_prefix.encode("utf-8"))
        if room < 8:
            raise RouteConfigurationError("Terminology prompt exceeds catalog context budget.")
        bounded_blob = blob.encode("utf-8")[:room].decode("utf-8", errors="ignore")
    else:
        bounded_blob = blob[:6000]
    prompt = prompt_prefix + bounded_blob

    if route is not None:
        async def transport(target: RouteTarget, secret: str | None) -> list[dict[str, Any]]:
            adapter = get_registry().get_llm(target.provider_id)
            if adapter is None:
                raise UnsupportedModalityError("No terminology LLM adapter for this provider.")
            response = await adapter.generate_text(prompt, route_target=target, api_key=secret)
            return _parse_llm_terms(response if isinstance(response, str) else str(response),
                                    target_lang=target_lang, strict=True)

        parsed = await invoke_route(route, transport, sessions, data_dir or get_settings().DATA_DIR,
                                    max_attempts=2, timeout=60.0)
        logger.info("LLM terminology extraction parsed terms", count=len(parsed))
        return parsed
    try:
        registry = get_registry()
        llm = registry.get_llm("gemini") or next(iter(registry._llm.values()), None)
        if not llm:
            return []
        model = getattr(llm, "_resolved_model_id", None)
        raw = await llm.generate_text(prompt, model=model)
        parsed = _parse_llm_terms(raw if isinstance(raw, str) else str(raw), target_lang=target_lang)
        logger.info("LLM terminology extraction parsed terms", count=len(parsed))
        return parsed
    except Exception as exc:
        logger.warning("LLM terminology extraction failed", error=str(exc))
        return []


async def persist_detected_terms(
    db: Optional[AsyncSession],
    project_id: str,
    terms: list[dict[str, Any]],
    target_lang: str = "",
) -> int:
    if db is None or not project_id or project_id == "default_project" or not terms:
        return 0
    saved = 0
    for item in filter_terminology(terms):
        source = item["source_term"]
        suggested = item["suggested_term"]
        # Reject invalid glossary entries (e.g. CJK self-mapped when target is not Chinese)
        if not is_valid_glossary_mapping(source, suggested, target_lang):
            logger.info("Rejected invalid glossary entry")
            continue
        await create_glossary_entry(
            db,
            project_id,
            source,
            suggested,
            item["term_type"],
            confidence=item["confidence"],
            source_context=item.get("source_context"),
        )
        saved += 1
    return saved


def _segment_source_text(seg: dict[str, Any]) -> str:
    return str(seg.get("text") or seg.get("original_text") or "").strip()


def _segment_translated_text(seg: dict[str, Any]) -> str:
    return str(seg.get("translated_text") or "").strip()


def segments_transcript_blob(segments: Optional[Iterable[dict[str, Any]]]) -> str:
    parts: list[str] = []
    for seg in segments or []:
        src = _segment_source_text(seg)
        tgt = _segment_translated_text(seg)
        if src:
            parts.append(src)
        if tgt and tgt != src:
            parts.append(tgt)
    return "\n".join(parts)


def get_source_only_blob(segments: Optional[Iterable[dict[str, Any]]]) -> str:
    parts: list[str] = []
    for seg in segments or []:
        src = _segment_source_text(seg)
        if src:
            parts.append(src)
    return "\n".join(parts)


def validate_and_align_extracted_terms(terms: Iterable[dict[str, Any]], source_blob: str) -> list[dict[str, Any]]:
    """
    Validates extracted terms against the original source text.
    - Discards terms that do not appear in the source text (e.g. hallucinations, diacritic errors).
    - Aligns the casing to the exact string found in the source text.
    - Deduplicates the validated terms.
    """
    aligned_terms = []
    seen = set()
    for item in terms:
        raw_source = item.get("source_term", "")
        if not raw_source:
            continue
            
        # Try exact match first
        if raw_source in source_blob:
            exact_match = raw_source
        else:
            # Try case-insensitive match
            match = re.search(re.escape(raw_source), source_blob, re.IGNORECASE)
            if match:
                exact_match = match.group(0)
            else:
                # Reject if not found in source
                logger.warning("Extracted term rejected: not found exactly in source text")
                continue
                
        # Deduplicate
        if exact_match in seen:
            continue
        seen.add(exact_match)
        
        # Update term with exact source string
        aligned_item = dict(item)
        aligned_item["source_term"] = exact_match
        aligned_terms.append(aligned_item)
        
    return aligned_terms


async def extract_and_persist_from_segments(
    db: Optional[AsyncSession],
    project_id: str,
    segments: Optional[Iterable[dict[str, Any]]],
    target_lang: str = "vi",
    *,
    sessions: async_sessionmaker[AsyncSession] | None = None,
    data_dir: Path | None = None,
) -> int:
    """Used by the Studio Auto job pipeline (startJob), which never hits TranslateStage."""
    blob = segments_transcript_blob(segments)
    if len(blob.strip()) < 4:
        logger.info(
            "Terminology extract skipped: empty transcript",
            project_id=project_id,
        )
        return 0
    heuristic = filter_terminology(heuristic_extract_terms(blob, target_lang))
    llm_terms = filter_terminology(await llm_extract_terms(blob, target_lang, sessions=sessions, data_dir=data_dir))
    llm_keys = {t["source_term"].casefold() for t in llm_terms}
    merged = llm_terms + [t for t in heuristic if t["source_term"].casefold() not in llm_keys]
    
    # Global filter: Reject invalid glossary mappings (e.g. CJK untranslated when target is not Chinese)
    merged = [
        item for item in merged
        if is_valid_glossary_mapping(item["source_term"], item.get("suggested_term", ""), target_lang)
    ]
    
    # Rigorously validate against source text only
    source_blob = get_source_only_blob(segments)
    if not source_blob:
        source_blob = blob
        
    validated_merged = validate_and_align_extracted_terms(merged, source_blob)
    
    logger.info(
        "Terminology extract merged terms",
        project_id=project_id,
        merged=len(validated_merged),
        original_merged=len(merged),
        heuristic=len(heuristic),
        llm=len(llm_terms),
        blob_chars=len(blob),
    )
    try:
        return await persist_detected_terms(db, project_id, validated_merged, target_lang=target_lang)
    except TypeError:
        return await persist_detected_terms(db, project_id, validated_merged)


def transcript_blob(ctx: Any) -> str:
    parts: list[str] = []
    if getattr(ctx, "raw_transcript", None):
        parts.append(str(ctx.raw_transcript))
    segs = list(getattr(ctx, "source_segments", None) or [])
    segs.extend(getattr(ctx, "translated_segments", None) or [])
    blob = segments_transcript_blob(segs)
    if blob:
        parts.append(blob)
    return "\n".join(parts)
