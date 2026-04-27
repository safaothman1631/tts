"""Hybrid G2P: lexicon → user overrides → neural fallback."""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from ...core.interfaces import IG2P
from ...core.registry import register
from .lexicon import CMUDictG2P
from .neural import NeuralG2P


@register("g2p", "hybrid")
class HybridG2P(IG2P):
    name = "hybrid"

    def __init__(self, user_overrides: Optional[dict[str, str]] = None) -> None:
        self.lex = CMUDictG2P()
        self.neural = NeuralG2P()
        self.overrides: dict[str, list[str]] = {}
        if user_overrides:
            for w, arpa in user_overrides.items():
                self.overrides[w.lower()] = arpa.split()

    @lru_cache(maxsize=8192)
    def word_to_phonemes(self, word: str, pos: str = "") -> list[str]:
        wl = word.lower()
        if wl in self.overrides:
            return list(self.overrides[wl])
        out = self.lex.word_to_phonemes(word, pos)
        if out:
            return out
        return self.neural.word_to_phonemes(word, pos)

    def add_override(self, word: str, arpabet: str | list[str]) -> None:
        if isinstance(arpabet, str):
            phones = arpabet.split()
        else:
            phones = list(arpabet)
        self.overrides[word.lower()] = phones
        self.word_to_phonemes.cache_clear()
