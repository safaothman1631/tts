"""Phrase break prediction (B0/B2/B3/B4)."""
from __future__ import annotations

from ...core.frame import Phrase, Token, Utterance

# Punctuation → break strength
_PUNCT_BREAK = {
    ".": (4, 400),
    "!": (4, 350),
    "?": (4, 350),
    ";": (3, 250),
    ":": (3, 250),
    ",": (2, 150),
    "—": (2, 200),
    "-": (2, 100),
    "...": (3, 500),
    "…": (3, 500),
}

# POS that often precede a phrase break
_BREAK_AFTER_POS = {"CCONJ", "SCONJ"}


def predict_breaks(utt: Utterance) -> Utterance:
    """Annotate Token.break_after based on punctuation and POS heuristics."""
    for i, tok in enumerate(utt.tokens):
        if tok.is_punct:
            strength, _ = _PUNCT_BREAK.get(tok.text, (0, 0))
            if strength and i > 0:
                utt.tokens[i - 1].break_after = max(utt.tokens[i - 1].break_after, strength)
        elif tok.pos in _BREAK_AFTER_POS:
            tok.break_after = max(tok.break_after, 2)

    # Last non-punct token gets sentence break
    for tok in reversed(utt.tokens):
        if not tok.is_punct:
            tok.break_after = max(tok.break_after, 4)
            break

    # Build phrases
    phrases: list[Phrase] = []
    cur: list[Token] = []
    for tok in utt.tokens:
        cur.append(tok)
        if tok.break_after >= 2:
            phrases.append(Phrase(tokens=cur, text=" ".join(t.text for t in cur), break_strength=tok.break_after))
            cur = []
    if cur:
        phrases.append(Phrase(tokens=cur, text=" ".join(t.text for t in cur), break_strength=4))
    utt.phrases = phrases
    return utt


def break_to_silence_ms(strength: int) -> int:
    return {0: 0, 2: 150, 3: 300, 4: 400}.get(strength, 0)
