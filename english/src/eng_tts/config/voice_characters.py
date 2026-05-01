"""Curated catalog of the real Qwen3 voice originals.

The 0.6B CustomVoice checkpoint currently exposes nine named speakers. This
catalog keeps exactly one character per real speaker, with no aliases and no
DSP pitch/time tricks. Distinctness comes from the actual speaker id plus a
unique style prompt, default emotion, category, language, and metadata.

Voice-cloned characters can reference WAV files in ``voices/reference_assets/``
(drop LibriVox / Common Voice CC-0 clips there; characters fall back to their
base speaker until a clip is registered).

Naming follows a copyright-safe descriptor convention - no real celebrity
names. ``inspiration_note`` is for editorial flavour only.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, replace
from pathlib import Path
import re


_DEFAULT_QWEN3_MODEL = "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"

# Resolve absolute path to the reference-audio folder so the API layer can
# pass `speaker_wav=<absolute>` to the Qwen3 cloning entry point.
_REF_ROOT = Path(__file__).resolve().parent.parent / "voices" / "reference_assets"


# --- Persona metadata (kept for legacy /v1/personas endpoint) ------------
@dataclass(frozen=True)
class Persona:
    id: str
    label: str
    style_prompt: str
    default_emotion: str
    tags: tuple[str, ...]


CATEGORIES: tuple[tuple[str, str], ...] = (
    ("narrator", "Documentary narrators"),
    ("audiobook", "Audiobook readers"),
    ("news", "News anchors"),
    ("cinematic", "Cinematic & trailer"),
    ("animated", "Animated characters"),
    ("podcast", "Podcast & creator"),
    ("commercial", "Commercial & brand"),
    ("wellness", "Wellness & meditation"),
    ("multilingual", "Multilingual native"),
    ("educational", "Tutor & educational"),
)
CATEGORY_LABELS: dict[str, str] = dict(CATEGORIES)


# --- Voice character schema (v2) -----------------------------------------
@dataclass(frozen=True)
class VoiceCharacter:
    # identity
    id: str
    name: str
    tagline: str

    # voice production
    backend: str
    model: str
    speaker_id: str
    style_prompt: str
    default_emotion: str
    pitch_offset: float = 0.0
    speed_offset: float = 0.0
    reference_audio: str | None = None
    reference_text: str | None = None
    source_type: str = "qwen_named"      # qwen_named | qwen_clone | piper

    # categorisation
    category: str = "narrator"
    subcategory: str = ""
    language: str = "en-US"
    qwen_language: str = "English"
    region: str = "American English"
    accent: str = "American"
    gender: str = "female"
    age_range: str = "adult"

    # legacy-compatible fields
    persona_id: str = "narrator"
    persona_label: str = "Narrator"
    description: str = ""
    tags: tuple[str, ...] = ()
    inspiration_note: str | None = None
    license: str = "synthetic_only"
    source_url: str | None = None
    attribution_required: bool = False
    attribution_string: str | None = None
    speaker_embedding_sha: str | None = None


# --- Helpers -------------------------------------------------------------
def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return cleaned or "voice"


def _ref_path(filename: str | None) -> str | None:
    """Resolve a reference-audio filename. Supports both flat layout
    (``my_clip.wav``) and per-codename folders (``Oracle/clip.wav``).
    Returns the absolute path only when the file exists on disk.
    """
    if not filename:
        return None
    full = _REF_ROOT / filename
    return str(full) if full.exists() else None


def _make(
    id: str,
    name: str,
    tagline: str,
    *,
    speaker: str,
    style: str,
    emotion: str = "neutral",
    pitch: float = 0.0,
    speed: float = 0.0,
    category: str = "narrator",
    subcategory: str = "",
    language: str = "en-US",
    qwen_language: str = "English",
    region: str = "American English",
    accent: str = "American",
    gender: str = "female",
    age: str = "adult",
    tags: tuple[str, ...] = (),
    backend: str = "qwen3",
    inspiration: str | None = None,
    license: str = "synthetic_only",
    reference: str | None = None,
    reference_text: str | None = None,
    source_url: str | None = None,
    attribution_required: bool = False,
    attribution_string: str | None = None,
) -> VoiceCharacter:
    source = "qwen_clone" if reference else ("piper" if backend == "piper" else "qwen_named")
    description = f"{name} - {tagline}. {style}"
    return VoiceCharacter(
        id=id,
        name=name,
        tagline=tagline,
        backend=backend,
        model=_DEFAULT_QWEN3_MODEL,
        speaker_id=speaker,
        style_prompt=style,
        default_emotion=emotion,
        pitch_offset=pitch,
        speed_offset=speed,
        reference_audio=reference,
        reference_text=reference_text,
        source_type=source,
        category=category,
        subcategory=subcategory or category,
        language=language,
        qwen_language=qwen_language,
        region=region,
        accent=accent,
        gender=gender,
        age_range=age,
        persona_id=category,
        persona_label=CATEGORY_LABELS.get(category, category.title()),
        description=description,
        tags=("v2", category, gender, language, *tags),
        inspiration_note=inspiration,
        license=license,
        source_url=source_url,
        attribution_required=attribution_required,
        attribution_string=attribution_string,
    )


# --- Originals-only catalog ----------------------------------------------
# Exactly one VoiceCharacter per real Qwen3 speaker. No aliases, no DSP, no
# pitch/speed offsets. The set below is derived from the official
# `model.get_supported_speakers()` of Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice
# (see config.json `spk_id`). If you load a larger Qwen3 variant with more
# speakers, add one entry here per new speaker - never alias.
# fmt: off
_HANDCRAFTED: tuple[VoiceCharacter, ...] = (
    _make("qwen-aiden", "Aiden", "Qwen3 original - American male",
        speaker="aiden",
        style="Crisp American newsroom baritone with confident projection, clean consonants, brisk controlled pacing and a firm finish on important facts.",
        emotion="confident", category="news", subcategory="anchor", language="en-US",
          qwen_language="English", region="American English", accent="American",
        gender="male", age="adult", tags=("qwen3","original","english","anchor")),
    _make("qwen-ryan", "Ryan", "Qwen3 original - American male",
        speaker="ryan",
        style="Clear American documentary narrator with steady mid-range pitch, balanced warmth, patient pacing and transparent articulation for long-form explanations.",
        emotion="neutral", category="narrator", subcategory="documentary", language="en-US",
          qwen_language="English", region="American English", accent="American",
        gender="male", age="adult", tags=("qwen3","original","english","documentary")),
    _make("qwen-vivian", "Vivian", "Qwen3 original - Mandarin Chinese female",
        speaker="vivian",
        style="Bright Mandarin educational guide with friendly lift, precise vowels, gentle smiles in the delivery and a welcoming tutorial pace.",
        emotion="friendly", category="educational", subcategory="tutor", language="zh-CN",
          qwen_language="Chinese", region="Mandarin Chinese", accent="Mandarin",
        gender="female", age="adult", tags=("qwen3","original","chinese","tutor")),
    _make("qwen-serena", "Serena", "Qwen3 original - Mandarin Chinese female",
        speaker="serena",
        style="Soft Mandarin wellness narrator with calm breath, rounded vowels, low-energy pauses and a smooth cadence for reflective passages.",
        emotion="calm", category="wellness", subcategory="meditation", language="zh-CN",
          qwen_language="Chinese", region="Mandarin Chinese", accent="Mandarin",
        gender="female", age="adult", tags=("qwen3","original","chinese","wellness")),
    _make("qwen-uncle-fu", "Uncle Fu", "Qwen3 original - Mandarin Chinese male",
        speaker="uncle_fu",
        style="Mature Mandarin storyteller with grounded resonance, deliberate pacing, wise emphasis and unhurried phrasing for classic tales.",
        emotion="serious", category="audiobook", subcategory="classic-story", language="zh-CN",
          qwen_language="Chinese", region="Mandarin Chinese", accent="Mandarin",
        gender="male", age="senior", tags=("qwen3","original","chinese","storyteller")),
    _make("qwen-eric", "Eric", "Qwen3 original - Sichuan dialect male",
        speaker="eric",
        style="Lively Sichuan podcast host with playful energy, nimble timing, expressive turns and an upbeat conversational rhythm.",
        emotion="excited", category="podcast", subcategory="creator", language="zh-CN",
          qwen_language="Chinese", region="Sichuan Chinese", accent="Sichuan",
        gender="male", age="adult", tags=("qwen3","original","chinese","dialect","podcast")),
    _make("qwen-dylan", "Dylan", "Qwen3 original - Beijing dialect male",
        speaker="dylan",
        style="Animated Beijing character voice with quick reactions, elastic emphasis, theatrical pauses and a dry mischievous edge.",
        emotion="sarcastic", category="animated", subcategory="character", language="zh-CN",
          qwen_language="Chinese", region="Beijing Chinese", accent="Beijing",
        gender="male", age="adult", tags=("qwen3","original","chinese","dialect","animated")),
    _make("qwen-ono-anna", "Ono Anna", "Qwen3 original - Japanese female",
        speaker="ono_anna",
        style="Elegant Japanese brand voice with polished diction, graceful timing, soft confidence and a refined finish for product lines.",
        emotion="romantic", category="commercial", subcategory="brand", language="ja-JP",
          qwen_language="Japanese", region="Japanese", accent="Japanese",
        gender="female", age="adult", tags=("qwen3","original","japanese","brand")),
    _make("qwen-sohee", "Sohee", "Qwen3 original - Korean female",
        speaker="sohee",
        style="Cinematic Korean narrator with focused intensity, spacious pauses, rising suspense and clean emotional control.",
        emotion="serious", category="cinematic", subcategory="trailer", language="ko-KR",
          qwen_language="Korean", region="Korean", accent="Korean",
        gender="female", age="adult", tags=("qwen3","original","korean","cinematic")),
)
# fmt: on



# Legacy persona list - derived from categories so /v1/personas keeps working
PERSONAS: tuple[Persona, ...] = tuple(
    Persona(cat_id, label, "", "neutral", (cat_id,))
    for cat_id, label in CATEGORIES
)


@dataclass(frozen=True)
class Culture:
    code: str
    region: str
    qwen_language: str
    female_names: tuple[str, ...] = ()
    male_names: tuple[str, ...] = ()


def _derive_cultures() -> tuple[Culture, ...]:
    seen: dict[str, Culture] = {}
    for c in _HANDCRAFTED:
        if c.language in seen:
            continue
        seen[c.language] = Culture(c.language, c.region, c.qwen_language)
    return tuple(seen.values())


CULTURES: tuple[Culture, ...] = _derive_cultures()


# --- Public catalog API --------------------------------------------------
_CATALOG: tuple[VoiceCharacter, ...] | None = None


def all_characters() -> tuple[VoiceCharacter, ...]:
    """Resolve and cache the catalog. Reference-audio paths are re-resolved
    every cold start so dropping a WAV into reference_assets/ activates
    cloning on the next process restart.
    """
    global _CATALOG
    if _CATALOG is None:
        resolved: list[VoiceCharacter] = []
        for c in _HANDCRAFTED:
            ref = _ref_path(c.reference_audio) if c.reference_audio else None
            if ref:
                resolved.append(replace(c, reference_audio=ref, source_type="qwen_clone"))
            elif c.reference_audio:
                # Reference file declared but missing - fall back gracefully.
                resolved.append(replace(c, reference_audio=None, source_type="qwen_named"))
            else:
                resolved.append(c)
        _CATALOG = tuple(resolved)
    return _CATALOG


def get_character(character_id: str) -> VoiceCharacter | None:
    for c in all_characters():
        if c.id == character_id:
            return c
    return None


def character_to_dict(c: VoiceCharacter) -> dict:
    return asdict(c)


def filter_characters(
    *,
    language: str | None = None,
    gender: str | None = None,
    persona: str | None = None,
    category: str | None = None,
    accent: str | None = None,
    age_range: str | None = None,
    query: str | None = None,
    limit: int | None = None,
) -> list[VoiceCharacter]:
    out: list[VoiceCharacter] = []
    q = (query or "").strip().lower()
    for c in all_characters():
        if language and language not in (c.language, c.language.split("-")[0]):
            continue
        if gender and c.gender != gender:
            continue
        if persona and c.persona_id != persona:
            continue
        if category and c.category != category:
            continue
        if accent and accent.lower() not in c.accent.lower():
            continue
        if age_range and c.age_range != age_range:
            continue
        if q and not (q in c.name.lower() or q in c.description.lower()
                      or q in c.region.lower() or q in c.tagline.lower()
                      or any(q in t.lower() for t in c.tags)):
            continue
        out.append(c)
        if limit and len(out) >= limit:
            break
    return out


def list_personas() -> list[dict]:
    used = {c.category for c in all_characters()}
    return [
        {"id": p.id, "label": p.label, "style_prompt": "", "default_emotion": "neutral", "tags": list(p.tags)}
        for p in PERSONAS
        if p.id in used
    ]


def list_languages() -> list[dict]:
    return [{"code": c.code, "region": c.region, "qwen_language": c.qwen_language} for c in CULTURES]


def list_categories() -> list[dict]:
    used = {c.category for c in all_characters()}
    return [{"id": cid, "label": label} for cid, label in CATEGORIES if cid in used]


__all__ = [
    "VoiceCharacter",
    "Persona",
    "Culture",
    "PERSONAS",
    "CULTURES",
    "CATEGORIES",
    "all_characters",
    "get_character",
    "character_to_dict",
    "filter_characters",
    "list_personas",
    "list_languages",
    "list_categories",
]
