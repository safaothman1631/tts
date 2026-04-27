"""Sentence segmentation. Tries pysbd → spaCy → regex fallback."""
from __future__ import annotations

import re
from typing import Optional

from ..core.interfaces import ISegmenter
from ..core.registry import register

# Stdlib re does not support variable-width lookbehind, so we use a simple
# split on sentence-ending punctuation followed by a space and an uppercase
# letter, then post-filter common abbreviations.
_RE_SENT_SPLIT = re.compile(r'(?<=[.!?])\s+(?=[A-Z"\'])')
_ABBREV = {"mr", "mrs", "ms", "dr", "st", "sr", "jr", "vs", "etc", "i.e", "e.g", "prof", "mt"}


def _looks_like_abbrev_end(prev: str) -> bool:
    last = prev.split()[-1].lower().rstrip(".") if prev.split() else ""
    return last in _ABBREV


@register("segmenter", "regex")
class RegexSegmenter(ISegmenter):
    name = "regex"

    def segment(self, text: str) -> list[str]:
        text = text.strip()
        if not text:
            return []
        parts = _RE_SENT_SPLIT.split(text)
        # Re-merge parts that ended with an abbreviation
        merged: list[str] = []
        for p in parts:
            if merged and _looks_like_abbrev_end(merged[-1]):
                merged[-1] = merged[-1] + " " + p
            else:
                merged.append(p)
        return [p.strip() for p in merged if p.strip()]


@register("segmenter", "pysbd")
class PySBDSegmenter(ISegmenter):
    name = "pysbd"

    def __init__(self, language: str = "en") -> None:
        try:
            import pysbd
        except ImportError as e:
            raise ImportError("pysbd not installed. `pip install pysbd`") from e
        self._seg = pysbd.Segmenter(language=language, clean=False)

    def segment(self, text: str) -> list[str]:
        text = text.strip()
        if not text:
            return []
        return [s.strip() for s in self._seg.segment(text) if s.strip()]


@register("segmenter", "spacy")
class SpacySegmenter(ISegmenter):
    name = "spacy"

    def __init__(self, model: str = "en_core_web_sm") -> None:
        from .linguistic import _ensure_spacy
        self._nlp = _ensure_spacy(model, disable=["ner", "tagger", "lemmatizer"])

    def segment(self, text: str) -> list[str]:
        doc = self._nlp(text)
        return [s.text.strip() for s in doc.sents if s.text.strip()]


def make_segmenter(name: str = "pysbd") -> ISegmenter:
    """Factory with graceful degradation."""
    try:
        if name == "pysbd":
            return PySBDSegmenter()
        if name == "spacy":
            return SpacySegmenter()
    except ImportError:
        pass
    return RegexSegmenter()
