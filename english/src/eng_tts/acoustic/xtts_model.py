"""Coqui XTTS-v2 backend (voice cloning tier)."""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Any, Optional

import numpy as np

from ..core.exceptions import AcousticError
from ..core.frame import LinguisticFrame
from ..core.interfaces import IAcoustic
from ..core.registry import register
from ..utils.audio import resample
from ..utils.logging import get_logger

_log = get_logger(__name__)
_LOAD_LOCK = threading.Lock()


@register("acoustic", "xtts")
class XTTSAcoustic(IAcoustic):
    """XTTS-v2 multi-speaker, multi-lingual voice cloning."""

    name = "xtts"
    produces_waveform = True
    sample_rate = 24000

    def __init__(
        self,
        model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2",
        device: Optional[str] = None,
        speaker_wav: Optional[str | Path] = None,
        language: str = "en",
    ) -> None:
        self.model_name = model_name
        self.device = device or "cpu"
        self.default_speaker_wav = str(speaker_wav) if speaker_wav else None
        self.language = language
        self._tts: Any = None

    def _ensure_loaded(self) -> Any:
        if self._tts is not None:
            return self._tts
        with _LOAD_LOCK:
            if self._tts is not None:
                return self._tts
            try:
                from TTS.api import TTS  # type: ignore
            except ImportError as e:
                raise AcousticError(
                    "Coqui TTS not installed. `pip install eng-tts[acoustic]`"
                ) from e
            try:
                _log.info("loading_xtts", model=self.model_name, device=self.device)
                self._tts = TTS(model_name=self.model_name, progress_bar=False).to(self.device)
            except Exception as e:
                raise AcousticError(f"Failed to load XTTS: {e}") from e
        return self._tts

    def synthesize(self, frame: LinguisticFrame) -> np.ndarray:
        tts = self._ensure_loaded()
        text = frame.text
        if not text.strip():
            return np.zeros(0, dtype=np.float32)
        speaker_wav = frame.extra.get("speaker_wav") or self.default_speaker_wav
        if not speaker_wav:
            raise AcousticError("XTTS requires a speaker_wav reference (set in frame.extra or constructor).")
        try:
            wav = tts.tts(
                text=text,
                speaker_wav=speaker_wav,
                language=frame.language[:2] if frame.language else self.language,
            )
        except Exception as e:
            raise AcousticError(f"XTTS inference failed: {e}") from e
        audio = np.asarray(wav, dtype=np.float32)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        if frame.sample_rate and frame.sample_rate != self.sample_rate:
            audio = resample(audio, self.sample_rate, frame.sample_rate)
        return audio
