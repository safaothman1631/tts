"""Resampling post-processor."""
from __future__ import annotations

import numpy as np

from ..core.interfaces import IPostProcessor
from ..core.registry import register
from ..utils.audio import resample as _resample


@register("postproc", "resample")
class Resampler(IPostProcessor):
    name = "resample"

    def __init__(self, target_sr: int = 22050) -> None:
        self.target_sr = target_sr

    def process(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        if sample_rate == self.target_sr:
            return audio
        return _resample(audio, sample_rate, self.target_sr)
