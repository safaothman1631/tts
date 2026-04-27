"""Coqui-TTS VITS acoustic backend (default 'fast' tier).

Lazy-loads the model on first synthesis. Uses Coqui's bundled vocoder; emits
a waveform directly.
"""
from __future__ import annotations

import io
import threading
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


@register("acoustic", "vits")
class VitsAcoustic(IAcoustic):
    name = "vits"
    produces_waveform = True
    sample_rate = 22050

    def __init__(
        self,
        model_name: str = "tts_models/en/ljspeech/vits",
        device: Optional[str] = None,
        use_speaker: Optional[str] = None,
    ) -> None:
        self.model_name = model_name
        self.device = device
        self.use_speaker = use_speaker
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
                _log.info("loading_vits", model=self.model_name, device=self.device)
                self._tts = TTS(model_name=self.model_name, progress_bar=False).to(
                    self.device or "cpu"
                )
                # Coqui exposes sample_rate via synthesizer.output_sample_rate
                sr = getattr(self._tts.synthesizer, "output_sample_rate", None)
                if sr:
                    self.sample_rate = int(sr)
            except Exception as e:
                raise AcousticError(f"Failed to load VITS model '{self.model_name}': {e}") from e
        return self._tts

    def synthesize(self, frame: LinguisticFrame) -> np.ndarray:
        tts = self._ensure_loaded()
        text = frame.text
        if not text.strip():
            return np.zeros(0, dtype=np.float32)
        kwargs: dict[str, Any] = {"text": text}
        speaker = frame.speaker_id or self.use_speaker
        if speaker and tts.is_multi_speaker:
            kwargs["speaker"] = speaker
        try:
            wav = tts.tts(**kwargs)
        except Exception as e:
            raise AcousticError(f"VITS inference failed: {e}") from e
        audio = np.asarray(wav, dtype=np.float32)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        if frame.sample_rate and frame.sample_rate != self.sample_rate:
            audio = resample(audio, self.sample_rate, frame.sample_rate)
        if frame.speed and frame.speed != 1.0:
            audio = _time_stretch(audio, frame.sample_rate, frame.speed)
        return audio

    def list_voices(self) -> list[str]:
        try:
            tts = self._ensure_loaded()
            return list(getattr(tts, "speakers", None) or [])
        except Exception:
            return []


def _time_stretch(audio: np.ndarray, sr: int, speed: float) -> np.ndarray:
    if speed <= 0:
        return audio
    try:
        import librosa  # type: ignore

        return librosa.effects.time_stretch(audio, rate=speed)
    except Exception:
        return audio
