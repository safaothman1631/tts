"""Neural G2P fallback for OOV words.

Wraps `g2p-en` (LSTM model trained on CMUdict). If unavailable, falls back
to a deterministic letter-spelling approximation.
"""
from __future__ import annotations

from functools import lru_cache

from ...core.interfaces import IG2P
from ...core.registry import register

_LETTER_ARPA = {
    "a": ["EY1"], "b": ["B IY1"], "c": ["S IY1"], "d": ["D IY1"], "e": ["IY1"],
    "f": ["EH1 F"], "g": ["JH IY1"], "h": ["EY1 CH"], "i": ["AY1"], "j": ["JH EY1"],
    "k": ["K EY1"], "l": ["EH1 L"], "m": ["EH1 M"], "n": ["EH1 N"], "o": ["OW1"],
    "p": ["P IY1"], "q": ["K Y UW1"], "r": ["AA1 R"], "s": ["EH1 S"], "t": ["T IY1"],
    "u": ["Y UW1"], "v": ["V IY1"], "w": ["D AH1 B AH0 L Y UW0"], "x": ["EH1 K S"],
    "y": ["W AY1"], "z": ["Z IY1"],
}


@register("g2p", "neural")
class NeuralG2P(IG2P):
    name = "neural"

    def __init__(self) -> None:
        self._g2p = None
        try:
            from g2p_en import G2p  # type: ignore

            self._g2p = G2p()
        except Exception:
            self._g2p = None

    @lru_cache(maxsize=4096)
    def word_to_phonemes(self, word: str, pos: str = "") -> list[str]:
        if self._g2p is not None:
            try:
                phones = self._g2p(word)
                # filter out non-phoneme tokens (spaces, punct)
                return [p for p in phones if p and p[0].isalpha()]
            except Exception:
                pass
        return self._spell_fallback(word)

    @staticmethod
    def _spell_fallback(word: str) -> list[str]:
        out: list[str] = []
        for ch in word.lower():
            if ch in _LETTER_ARPA:
                out.extend(_LETTER_ARPA[ch][0].split())
        return out
