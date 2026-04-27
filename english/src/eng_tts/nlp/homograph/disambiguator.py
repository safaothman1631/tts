"""POS-based homograph disambiguator with neural fallback hook."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ...core.frame import Utterance
from ...core.interfaces import IHomographDisambiguator
from ...core.registry import register

_DICT_PATH = Path(__file__).with_name("dictionary.json")


def _load() -> dict[str, dict[str, str]]:
    with open(_DICT_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith("_")}


_HOMOGRAPHS = _load()


_POS_NORMALIZE = {
    "VERB": "VERB", "AUX": "VERB",
    "NOUN": "NOUN", "PROPN": "PROPN",
    "ADJ": "ADJ",
    "ADV": "ADV",
}


def _resolve_pron(word: str, pos: str, tag: str) -> str | None:
    entry = _HOMOGRAPHS.get(word.lower())
    if not entry:
        return None
    # Specific tag wins (VBD/VBN)
    if tag and tag in entry:
        return entry[tag]
    npos = _POS_NORMALIZE.get(pos, pos)
    if npos in entry:
        return entry[npos]
    return entry.get("*")


@register("homograph", "rule_based")
class RuleBasedHomograph(IHomographDisambiguator):
    name = "rule_based"

    def disambiguate(self, utt: Utterance) -> Utterance:
        for tok in utt.tokens:
            arpa = _resolve_pron(tok.text, tok.pos, tok.tag)
            if arpa:
                tok.phonemes = arpa.split()
                # Pre-compute stress
                tok.stress = [int(p[-1]) if p[-1].isdigit() else 0 for p in tok.phonemes]
        return utt


def is_homograph(word: str) -> bool:
    return word.lower() in _HOMOGRAPHS


def homograph_count() -> int:
    return len(_HOMOGRAPHS)
