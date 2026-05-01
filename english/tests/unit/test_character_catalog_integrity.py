"""Catalog integrity & distinctness checks for the handcrafted voice catalog.

These tests run quickly without any model loading and guard against silent
regressions when editing ``voice_characters.py`` (e.g. accidental duplicate
ids, two characters with identical signatures).
"""
from __future__ import annotations

from eng_tts.config.voice_characters import (
    all_characters,
    get_character,
    list_categories,
)


def test_catalog_is_originals_only() -> None:
    chars = all_characters()
    # Exactly one entry per real Qwen3 supported speaker (0.6B-CustomVoice = 9).
    assert len(chars) == 9, f"expected 9 originals, got {len(chars)}"
    expected = {
        "aiden", "dylan", "eric", "ono_anna", "ryan",
        "serena", "sohee", "uncle_fu", "vivian",
    }
    assert {c.speaker_id for c in chars} == expected


def test_character_ids_are_unique() -> None:
    ids = [c.id for c in all_characters()]
    assert len(ids) == len(set(ids)), "duplicate character ids in catalog"


def test_category_coverage() -> None:
    cats_in_catalog = {c.category for c in all_characters()}
    listed_categories = {row["id"] for row in list_categories()}
    assert len(cats_in_catalog) >= 6, "catalog should expose distinct voice roles"
    assert listed_categories == cats_in_catalog, "do not expose empty voice categories"


def test_character_signatures_are_distinct() -> None:
    """Every character must map to a unique Qwen3 speaker - no aliasing."""
    speakers = [c.speaker_id for c in all_characters()]
    assert len(speakers) == len(set(speakers)), "two characters share a speaker_id"


def test_character_metadata_is_distinct() -> None:
    chars = all_characters()
    styles = [c.style_prompt for c in chars]
    names = [c.name for c in chars]
    signatures = [
        (c.speaker_id, c.style_prompt, c.default_emotion, c.category, c.accent)
        for c in chars
    ]
    assert len(styles) == len(set(styles)), "two characters share the same style prompt"
    assert len(names) == len(set(names)), "two characters share the same display name"
    assert len(signatures) == len(set(signatures)), "two characters share a voice signature"


def test_get_character_round_trip() -> None:
    sample = all_characters()[0]
    assert get_character(sample.id) is sample or get_character(sample.id).id == sample.id


def test_v2_fields_present() -> None:
    c = all_characters()[0]
    assert hasattr(c, "tagline")
    assert hasattr(c, "pitch_offset")
    assert hasattr(c, "speed_offset")
    assert hasattr(c, "reference_audio")
    assert hasattr(c, "source_type")
    assert hasattr(c, "category")
