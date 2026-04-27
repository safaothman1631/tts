"""Optional spectral noise reduction."""
from __future__ import annotations

import numpy as np

from ..core.interfaces import IPostProcessor
from ..core.registry import register


@register("postproc", "denoise")
class Denoiser(IPostProcessor):
    name = "denoise"

    def __init__(self, prop_decrease: float = 0.6) -> None:
        self.prop_decrease = prop_decrease

    def process(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        try:
            import noisereduce as nr  # type: ignore

            return nr.reduce_noise(
                y=audio, sr=sample_rate, prop_decrease=self.prop_decrease
            ).astype(np.float32)
        except ImportError:
            return audio
