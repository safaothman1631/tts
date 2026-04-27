"""CMUdict-backed lexicon G2P. Uses bundled g2p-en CMUdict if present."""
from __future__ import annotations

import re
from functools import lru_cache
from typing import Optional

from ...core.interfaces import IG2P
from ...core.registry import register

_CMUDICT: dict[str, list[list[str]]] | None = None


def _load_cmudict() -> dict[str, list[list[str]]]:
    """Try multiple sources to obtain CMUdict."""
    global _CMUDICT
    if _CMUDICT is not None:
        return _CMUDICT
    out: dict[str, list[list[str]]] = {}
    # Try g2p_en's bundled CMUdict
    try:
        from g2p_en import G2p  # type: ignore

        g = G2p()
        # g2p_en stores cmudict at g.cmu (dict word -> list of pron strings)
        for word, prons in g.cmu.items():
            if isinstance(prons, list):
                out[word.lower()] = [p if isinstance(p, list) else p.split() for p in prons]
    except Exception:
        pass
    # Try nltk.corpus.cmudict as backup
    if not out:
        try:
            from nltk.corpus import cmudict  # type: ignore

            for word, prons in cmudict.dict().items():
                out[word.lower()] = prons
        except Exception:
            pass
    _CMUDICT = out
    return out


@register("g2p", "cmudict")
class CMUDictG2P(IG2P):
    name = "cmudict"

    def __init__(self) -> None:
        self._dict = _load_cmudict()

    def has(self, word: str) -> bool:
        return word.lower() in self._dict

    @lru_cache(maxsize=8192)
    def word_to_phonemes(self, word: str, pos: str = "") -> list[str]:
        prons = self._dict.get(word.lower())
        if not prons:
            return []
        return list(prons[0])
