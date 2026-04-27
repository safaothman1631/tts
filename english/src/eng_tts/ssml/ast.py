"""SSML AST node definitions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SSMLNode:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list["SSMLNode | SSMLText"] = field(default_factory=list)


@dataclass
class SSMLText:
    text: str


@dataclass
class SSMLSpan:
    """Output of the walker: a flat span of text plus inherited attributes."""

    text: str
    attrs: dict[str, Any] = field(default_factory=dict)
    is_break: bool = False
    break_ms: int = 0
    say_as: str = ""        # date, currency, telephone, spell-out, characters
    phoneme: str = ""       # explicit phoneme override
    phoneme_alphabet: str = "ipa"
    sub: str = ""           # substitution text
    voice: str = ""
    lang: str = ""
    emphasis: str = ""      # strong | moderate | reduced | none
    rate: str = ""          # x-slow | slow | medium | fast | x-fast | %
    pitch: str = ""         # x-low | low | medium | high | x-high | st/Hz
    volume: str = ""        # silent | x-soft | soft | medium | loud | x-loud | dB
