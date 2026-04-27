"""Naive language ID for code-switch detection."""
from __future__ import annotations

import re
from typing import Iterable

from ..core.frame import Utterance
from ..core.registry import register

# Crude script-based detection
_LATIN_RE = re.compile(r"[A-Za-z]")
_CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
_ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F]")
_CJK_RE = re.compile(r"[\u4E00-\u9FFF]")
_HANGUL_RE = re.compile(r"[\uAC00-\uD7AF]")
_HIRAGANA_RE = re.compile(r"[\u3040-\u309F\u30A0-\u30FF]")
_DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")


def detect_script(text: str) -> str:
    if not text:
        return "und"
    counts = {
        "latin": len(_LATIN_RE.findall(text)),
        "cyrillic": len(_CYRILLIC_RE.findall(text)),
        "arabic": len(_ARABIC_RE.findall(text)),
        "cjk": len(_CJK_RE.findall(text)),
        "hangul": len(_HANGUL_RE.findall(text)),
        "japanese": len(_HIRAGANA_RE.findall(text)),
        "devanagari": len(_DEVANAGARI_RE.findall(text)),
    }
    best = max(counts, key=counts.get)
    return best if counts[best] > 0 else "und"


@register("codeswitch", "script")
class ScriptCodeSwitch:
    """Mark tokens whose script is non-latin as foreign."""

    name = "script"

    def detect(self, utt: Utterance) -> Utterance:
        for tok in utt.tokens:
            script = detect_script(tok.text)
            if script not in {"latin", "und"}:
                tok.ssml_attrs["foreign_script"] = script
        return utt
