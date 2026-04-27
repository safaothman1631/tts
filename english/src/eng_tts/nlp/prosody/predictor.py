"""Composite prosody predictor."""
from __future__ import annotations

from ...core.frame import Utterance
from ...core.interfaces import IProsody
from ...core.registry import register
from . import breaks, contour


@register("prosody", "rule_based")
class RuleBasedProsody(IProsody):
    name = "rule_based"

    def predict(self, utt: Utterance) -> Utterance:
        utt = breaks.predict_breaks(utt)
        utt = contour.assign(utt)
        return utt
