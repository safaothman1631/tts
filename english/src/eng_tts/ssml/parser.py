"""Robust SSML parser.

Parses a subset of SSML 1.1 sufficient for high-quality TTS:
    <speak> <p> <s> <voice> <prosody> <break> <emphasis>
    <say-as> <phoneme> <sub> <lang> <mark> <audio>

Plain text input is auto-wrapped in <speak>.
Falls back to a stdlib XML parser if `lxml` is unavailable.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Any

from ..core.exceptions import SSMLError
from .ast import SSMLNode, SSMLText

_SUPPORTED = {
    "speak", "p", "s", "voice", "prosody", "break", "emphasis",
    "say-as", "phoneme", "sub", "lang", "mark", "audio", "w", "token",
}

_SSML_LIKE = re.compile(r"^\s*<\s*speak\b", re.IGNORECASE)


def is_ssml(text: str) -> bool:
    return bool(_SSML_LIKE.match(text))


def _strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1].lower() if "}" in tag else tag.lower()


def _convert(elem: Any) -> SSMLNode:
    node = SSMLNode(tag=_strip_ns(elem.tag), attrs={k: v for k, v in elem.attrib.items()})
    if elem.text:
        node.children.append(SSMLText(text=elem.text))
    for child in elem:
        node.children.append(_convert(child))
        if child.tail:
            node.children.append(SSMLText(text=child.tail))
    return node


def parse(text: str) -> SSMLNode:
    """Parse SSML or plain text into an SSMLNode tree rooted at <speak>."""
    if not is_ssml(text):
        # Auto-wrap plain text
        return SSMLNode(
            tag="speak",
            attrs={"version": "1.1", "xml:lang": "en-US"},
            children=[SSMLText(text=text)],
        )
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        raise SSMLError(f"Invalid SSML XML: {e}") from e
    node = _convert(root)
    if node.tag != "speak":
        raise SSMLError(f"Root element must be <speak>, got <{node.tag}>")
    return node


__all__ = ["parse", "is_ssml", "SSMLNode", "SSMLText"]
