"""Build LinguisticFrame from Utterance."""
from __future__ import annotations

from typing import Any

from .frame import LinguisticFrame, Utterance
from .interfaces import IFrameBuilder
from .registry import register


@register("frame_builder", "default")
class DefaultFrameBuilder(IFrameBuilder):
    name = "default"

    def build(self, utt: Utterance, **overrides: Any) -> LinguisticFrame:
        phonemes: list[str] = []
        word_boundaries: list[int] = []
        phrase_breaks: list[int] = []
        stress: list[int] = []
        durations: list[float] = []
        idx = 0
        for tok in utt.tokens:
            if tok.is_punct or tok.is_space:
                continue
            for p in tok.phonemes:
                phonemes.append(p)
                stress.append(int(p[-1]) if p[-1].isdigit() else 0)
                idx += 1
            if tok.duration and tok.phonemes:
                # split tok.duration evenly
                per = tok.duration / max(1, len(tok.phonemes))
                durations.extend([per] * len(tok.phonemes))
            word_boundaries.append(idx)
            if tok.break_after >= 2:
                phrase_breaks.append(idx)

        return LinguisticFrame(
            phonemes=phonemes,
            phoneme_ids=[],
            durations=durations or None,
            word_boundaries=word_boundaries,
            phrase_breaks=phrase_breaks,
            stress=stress,
            text=utt.text,
            language=utt.language,
            **overrides,
        )
