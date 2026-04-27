"""Vocoder placeholders.

Most modern acoustic models (VITS / XTTS / StyleTTS2) bundle their own
vocoder and emit waveform directly. We expose a passthrough vocoder here
so the pipeline contract is uniform.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from ..core.interfaces import IVocoder
from ..core.registry import register


@register("vocoder", "passthrough")
class PassthroughVocoder(IVocoder):
    """For end-to-end acoustic models that already emit waveform."""

    name = "passthrough"
    sample_rate = 22050

    def vocode(self, mel_or_wave: Any) -> np.ndarray:
        arr = np.asarray(mel_or_wave, dtype=np.float32)
        if arr.ndim > 1:
            arr = arr.mean(axis=0) if arr.shape[0] < arr.shape[1] else arr.mean(axis=1)
        return arr


@register("vocoder", "hifigan")
class HiFiGANVocoder(IVocoder):
    """HiFi-GAN wrapper. Lazy-loads from torch hub if available."""

    name = "hifigan"
    sample_rate = 22050

    def __init__(self, hub_repo: str = "bshall/hifigan", model: str = "hifigan_hubert_soft") -> None:
        self.hub_repo = hub_repo
        self.model_name = model
        self._model: Any = None

    def _load(self) -> Any:
        if self._model is not None:
            return self._model
        try:
            import torch  # type: ignore

            self._model = torch.hub.load(self.hub_repo, self.model_name).eval()
        except Exception:
            self._model = False
        return self._model

    def vocode(self, mel: Any) -> np.ndarray:
        m = self._load()
        if not m:
            return PassthroughVocoder().vocode(mel)
        try:
            import torch  # type: ignore

            mt = torch.as_tensor(mel).float().unsqueeze(0)
            with torch.no_grad():
                wav = m(mt).squeeze().cpu().numpy()
            return wav.astype(np.float32)
        except Exception:
            return PassthroughVocoder().vocode(mel)
