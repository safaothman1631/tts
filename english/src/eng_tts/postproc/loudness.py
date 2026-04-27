"""EBU R128-style loudness normalization (ITU-R BS.1770)."""
from __future__ import annotations

import numpy as np

from ..core.interfaces import IPostProcessor
from ..core.registry import register


@register("postproc", "loudness")
class LoudnessNormalizer(IPostProcessor):
    name = "loudness"

    def __init__(self, target_lufs: float = -16.0) -> None:
        self.target_lufs = target_lufs

    def process(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        try:
            import pyloudnorm as pyln  # type: ignore

            meter = pyln.Meter(sample_rate)
            audio = audio.astype(np.float32, copy=False)
            if audio.size == 0:
                return audio
            try:
                loudness = meter.integrated_loudness(audio)
            except Exception:
                return _peak_normalize(audio, peak_db=-1.0)
            if not np.isfinite(loudness):
                return _peak_normalize(audio, peak_db=-1.0)
            normalized = pyln.normalize.loudness(audio, loudness, self.target_lufs)
            return _safe_clip(normalized.astype(np.float32))
        except ImportError:
            return _peak_normalize(audio, peak_db=-1.0)


def _peak_normalize(audio: np.ndarray, peak_db: float = -1.0) -> np.ndarray:
    if audio.size == 0:
        return audio
    peak = float(np.max(np.abs(audio))) or 1.0
    target = 10 ** (peak_db / 20.0)
    return _safe_clip((audio * (target / peak)).astype(np.float32))


def _safe_clip(audio: np.ndarray) -> np.ndarray:
    return np.clip(audio, -1.0, 1.0).astype(np.float32)
