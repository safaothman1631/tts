"""Discourse markers → pacing adjustments."""
from __future__ import annotations

from ..core.frame import Utterance

_DISCOURSE_BREAK = {
    "however", "moreover", "furthermore", "therefore", "consequently",
    "additionally", "nevertheless", "nonetheless", "meanwhile", "subsequently",
    "in conclusion", "in summary", "in fact", "in addition", "for example",
    "for instance", "on the other hand",
}


def annotate(utt: Utterance) -> Utterance:
    """If utterance starts with a discourse marker, mark pause after it."""
    text_lower = utt.text.lower().strip()
    for marker in sorted(_DISCOURSE_BREAK, key=len, reverse=True):
        if text_lower.startswith(marker):
            n_words = len(marker.split())
            for i, tok in enumerate(utt.tokens[:n_words + 2]):
                if tok.is_punct and tok.text == ",":
                    utt.tokens[i].break_after = max(utt.tokens[i].break_after, 2)
                    break
            break
    return utt
