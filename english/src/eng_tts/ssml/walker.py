"""Walk an SSML AST yielding flat SSMLSpan objects with inherited attributes."""
from __future__ import annotations

from typing import Any, Iterator

from .ast import SSMLNode, SSMLSpan, SSMLText


def _parse_break_time(s: str) -> int:
    s = s.strip().lower()
    if s.endswith("ms"):
        try:
            return int(float(s[:-2]))
        except ValueError:
            return 0
    if s.endswith("s"):
        try:
            return int(float(s[:-1]) * 1000)
        except ValueError:
            return 0
    if s in {"none", "x-weak"}:
        return 0
    if s == "weak":
        return 100
    if s == "medium":
        return 250
    if s == "strong":
        return 500
    if s == "x-strong":
        return 800
    return 0


def walk(root: SSMLNode) -> Iterator[SSMLSpan]:
    """Yield SSMLSpan in document order. Inherited attrs are merged downward."""
    yield from _walk(root, parent_attrs={})


def _make_text_span(text: str, attrs: dict[str, Any]) -> SSMLSpan:
    return SSMLSpan(
        text=text,
        attrs=dict(attrs),
        voice=str(attrs.get("voice", "")),
        lang=str(attrs.get("lang", "")),
        emphasis=str(attrs.get("emphasis", "")),
        rate=str(attrs.get("rate", "")),
        pitch=str(attrs.get("pitch", "")),
        volume=str(attrs.get("volume", "")),
        say_as=str(attrs.get("say_as", "")),
    )


def _walk(node: SSMLNode | SSMLText, parent_attrs: dict[str, Any]) -> Iterator[SSMLSpan]:
    if isinstance(node, SSMLText):
        if node.text and node.text.strip():
            yield _make_text_span(node.text, parent_attrs)
        return

    attrs = dict(parent_attrs)

    if node.tag == "voice":
        attrs["voice"] = node.attrs.get("name", attrs.get("voice", ""))
    elif node.tag == "lang":
        attrs["lang"] = node.attrs.get("xml:lang", node.attrs.get("lang", attrs.get("lang", "")))
    elif node.tag == "prosody":
        for k in ("rate", "pitch", "volume"):
            if k in node.attrs:
                attrs[k] = node.attrs[k]
    elif node.tag == "emphasis":
        attrs["emphasis"] = node.attrs.get("level", "moderate")
    elif node.tag == "break":
        time_attr = node.attrs.get("time") or node.attrs.get("strength", "medium")
        yield SSMLSpan(text="", attrs=dict(parent_attrs), is_break=True, break_ms=_parse_break_time(time_attr))
        return
    elif node.tag == "say-as":
        attrs["say_as"] = node.attrs.get("interpret-as", "")
    elif node.tag == "phoneme":
        # Yield exactly one span carrying the phoneme override
        text_content = "".join(c.text for c in node.children if isinstance(c, SSMLText))
        yield SSMLSpan(
            text=text_content,
            attrs=dict(attrs),
            phoneme=node.attrs.get("ph", ""),
            phoneme_alphabet=node.attrs.get("alphabet", "ipa"),
        )
        return
    elif node.tag == "sub":
        # Replace text content with alias
        alias = node.attrs.get("alias", "")
        yield SSMLSpan(text=alias, attrs=dict(attrs), sub=alias)
        return
    elif node.tag == "p":
        # Add paragraph break before
        yield SSMLSpan(text="", attrs=dict(attrs), is_break=True, break_ms=400)
    elif node.tag == "s":
        # Sentence break
        yield SSMLSpan(text="", attrs=dict(attrs), is_break=True, break_ms=200)

    for child in node.children:
        yield from _walk(child, attrs)


def to_plain_text(root: SSMLNode) -> str:
    """Concatenate all text spans (lossy — for pre-normalization preview)."""
    return " ".join(s.text for s in walk(root) if s.text)


__all__ = ["walk", "to_plain_text"]
