"""Lightweight VADER-style + transformer-based sentiment."""
from __future__ import annotations

import re

from ..core.frame import Utterance
from ..core.interfaces import ISentiment
from ..core.registry import register

_POS_WORDS = {
    "good", "great", "excellent", "amazing", "wonderful", "fantastic", "love",
    "happy", "joyful", "delighted", "pleased", "perfect", "best", "beautiful",
    "awesome", "nice", "fun", "win", "victory", "success", "brilliant",
}
_NEG_WORDS = {
    "bad", "terrible", "awful", "horrible", "hate", "sad", "angry", "upset",
    "broken", "fail", "failure", "loss", "ugly", "worst", "disappoint", "wrong",
    "cry", "pain", "hurt", "fear", "scared", "evil",
}
_INTENSIFIERS = {"very", "extremely", "really", "absolutely", "incredibly", "so"}
_NEGATIONS = {"not", "no", "never", "n't", "nothing", "nobody"}


@register("sentiment", "lexicon")
class LexiconSentiment(ISentiment):
    """Toy but effective: scaled count of positive/negative tokens."""

    name = "lexicon"

    def score(self, utt: Utterance) -> Utterance:
        tokens = [t.text.lower() for t in utt.tokens if not t.is_punct]
        pos = sum(1 for t in tokens if t in _POS_WORDS)
        neg = sum(1 for t in tokens if t in _NEG_WORDS)
        # Negation flip on adjacent
        flipped_neg, flipped_pos = 0, 0
        for i, w in enumerate(tokens):
            if w in _NEGATIONS and i + 1 < len(tokens):
                nxt = tokens[i + 1]
                if nxt in _POS_WORDS:
                    flipped_neg += 1
                elif nxt in _NEG_WORDS:
                    flipped_pos += 1
        total = max(1, pos + neg)
        score = (pos + flipped_pos - neg - flipped_neg) / total
        if score > 0.2:
            label = "positive"
        elif score < -0.2:
            label = "negative"
        else:
            label = "neutral"
        utt.sentiment = label
        utt.sentiment_score = float(score)
        utt.emotion = label
        return utt


@register("sentiment", "transformer")
class TransformerSentiment(ISentiment):
    """HuggingFace transformer model. Lazy-loaded; falls back to lexicon if unavailable."""

    name = "transformer"

    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest") -> None:
        self.model_name = model_name
        self._pipe = None
        self._fallback = LexiconSentiment()

    def _load(self) -> None:
        if self._pipe is not None:
            return
        try:
            from transformers import pipeline  # type: ignore

            self._pipe = pipeline("sentiment-analysis", model=self.model_name)
        except Exception:
            self._pipe = False  # type: ignore[assignment]

    def score(self, utt: Utterance) -> Utterance:
        self._load()
        if not self._pipe:
            return self._fallback.score(utt)
        try:
            res = self._pipe(utt.text[:512])[0]
            label = res["label"].lower()
            label_map = {"label_0": "negative", "label_1": "neutral", "label_2": "positive"}
            utt.sentiment = label_map.get(label, label)
            utt.sentiment_score = float(res["score"])
            utt.emotion = utt.sentiment
        except Exception:
            return self._fallback.score(utt)
        return utt
