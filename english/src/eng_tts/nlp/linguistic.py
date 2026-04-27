"""Linguistic analyzer: spaCy when available, regex fallback otherwise.

Always returns Utterance with Token list — backends downstream are agnostic.
"""
from __future__ import annotations

import re
from typing import Any

from ..core.frame import Token, Utterance
from ..core.interfaces import ILinguisticAnalyzer
from ..core.registry import register

_NLP_CACHE: dict[str, Any] = {}


def _ensure_spacy(model: str = "en_core_web_sm", disable: list[str] | None = None) -> Any:
    if model in _NLP_CACHE:
        return _NLP_CACHE[model]
    try:
        import spacy
    except ImportError as e:
        raise ImportError("spaCy not installed. `pip install spacy && python -m spacy download en_core_web_sm`") from e
    try:
        nlp = spacy.load(model, disable=disable or [])
    except OSError as e:
        raise ImportError(
            f"spaCy model '{model}' not downloaded. Run: python -m spacy download {model}"
        ) from e
    _NLP_CACHE[model] = nlp
    return nlp


@register("linguistic", "spacy")
class SpacyAnalyzer(ILinguisticAnalyzer):
    name = "spacy"

    def __init__(self, model: str = "en_core_web_sm") -> None:
        self._nlp = _ensure_spacy(model)

    def analyze(self, sentence: str) -> Utterance:
        doc = self._nlp(sentence)
        tokens: list[Token] = []
        for t in doc:
            tokens.append(
                Token(
                    text=t.text,
                    lemma=t.lemma_,
                    pos=t.pos_,
                    tag=t.tag_,
                    dep=t.dep_,
                    ent_type=t.ent_type_,
                    is_punct=t.is_punct,
                    is_space=t.is_space,
                    idx=t.idx,
                )
            )
        return Utterance(text=sentence, raw_text=sentence, tokens=tokens)


_RE_TOKEN = re.compile(r"\w+|[^\w\s]")


@register("linguistic", "regex")
class RegexAnalyzer(ILinguisticAnalyzer):
    """Zero-dependency fallback: tokens only, no POS / NER / Dep."""

    name = "regex"

    def analyze(self, sentence: str) -> Utterance:
        tokens: list[Token] = []
        for m in _RE_TOKEN.finditer(sentence):
            txt = m.group(0)
            tokens.append(
                Token(
                    text=txt,
                    lemma=txt.lower(),
                    pos="PUNCT" if not txt[0].isalnum() else "X",
                    tag="",
                    is_punct=not txt[0].isalnum(),
                    idx=m.start(),
                )
            )
        return Utterance(text=sentence, raw_text=sentence, tokens=tokens)


def make_analyzer(name: str = "spacy", **kwargs: Any) -> ILinguisticAnalyzer:
    try:
        if name == "spacy":
            return SpacyAnalyzer(**kwargs)
    except ImportError:
        pass
    return RegexAnalyzer()
