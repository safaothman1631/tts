"""Piper TTS acoustic backend.

Lightweight, fully offline ONNX-based neural TTS. Runs on CPU.
Models are downloaded from rhasspy/piper-voices on Hugging Face into
``models/piper/`` and consumed via the ``piper-tts`` Python package.

Voice model file layout::

    <model_dir>/<voice_key>.onnx
    <model_dir>/<voice_key>.onnx.json

The default voice key is ``en_US-lessac-medium`` (~63 MB, 22.05 kHz).
"""
from __future__ import annotations

import os
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

DEFAULT_MODEL_DIR = Path(__file__).resolve().parents[4] / "models" / "piper"
DEFAULT_VOICE_KEY = "en_US-lessac-medium"


def _resolve_model_path(model_key: str, model_dir: Optional[Path] = None) -> Path:
    """Resolve <model_dir>/<key>.onnx, supporting absolute paths too."""
    p = Path(model_key)
    if p.suffix == ".onnx" and p.exists():
        return p
    base = Path(model_dir or os.environ.get("ENG_TTS_PIPER_DIR") or DEFAULT_MODEL_DIR)
    candidate = base / f"{model_key}.onnx"
    return candidate


def _onnx_cuda_available() -> bool:
    try:
        import onnxruntime as ort  # type: ignore
    except Exception:
        return False
    try:
        return "CUDAExecutionProvider" in ort.get_available_providers()
    except Exception:
        return False


@register("acoustic", "piper")
class PiperAcoustic(IAcoustic):
    """Piper ONNX neural TTS backend.

    Args:
        model_name: Voice key (e.g. ``en_US-lessac-medium``) or absolute
            path to a ``.onnx`` file. Defaults to ``en_US-lessac-medium``.
        model_dir: Directory holding ``<key>.onnx`` + ``<key>.onnx.json``.
            Defaults to ``<repo>/models/piper`` or ``ENG_TTS_PIPER_DIR``.
        device: ``"cpu"`` or ``"cuda"``. Piper uses ONNX Runtime; CUDA
            requires the ``onnxruntime-gpu`` wheel.
        speaker_id: Optional integer speaker id (multi-speaker voices only).
    """

    name = "piper"
    produces_waveform = True
    sample_rate = 22050

    def __init__(
        self,
        model_name: str = DEFAULT_VOICE_KEY,
        model_dir: Optional[str | Path] = None,
        device: Optional[str] = None,
        speaker_id: Optional[int] = None,
    ) -> None:
        self.model_name = model_name
        self.model_dir = Path(model_dir) if model_dir else None
        self.device = (device or "cpu").lower()
        self.speaker_id = speaker_id
        self._voice: Any = None

    # ---------------------------------------------------------------- internal

    def _ensure_loaded(self) -> Any:
        if self._voice is not None:
            return self._voice
        with _LOAD_LOCK:
            if self._voice is not None:
                return self._voice
            try:
                from piper import PiperVoice  # type: ignore
            except ImportError as e:
                raise AcousticError(
                    "piper-tts not installed. Run `pip install piper-tts`."
                ) from e

            model_path = _resolve_model_path(self.model_name, self.model_dir)
            if not model_path.exists():
                raise AcousticError(
                    f"Piper model not found at '{model_path}'. "
                    "Download with `python scripts/download_piper_models.py` "
                    "or set ENG_TTS_PIPER_DIR."
                )

            try:
                use_cuda = self.device == "cuda" and _onnx_cuda_available()
                if self.device == "cuda" and not use_cuda:
                    _log.info("piper_cuda_provider_unavailable using CPUExecutionProvider")
                _log.info(f"loading_piper model={model_path} device={'cuda' if use_cuda else 'cpu'}")
                self._voice = PiperVoice.load(
                    str(model_path),
                    use_cuda=use_cuda,
                )
                cfg = getattr(self._voice, "config", None)
                sr = getattr(cfg, "sample_rate", None) if cfg is not None else None
                if sr:
                    self.sample_rate = int(sr)
            except Exception as e:
                raise AcousticError(
                    f"Failed to load Piper voice '{model_path}': {e}"
                ) from e
        return self._voice

    # ---------------------------------------------------------------- public

    def synthesize(self, frame: LinguisticFrame) -> np.ndarray:
        voice = self._ensure_loaded()
        text = (frame.text or "").strip()
        if not text:
            return np.zeros(0, dtype=np.float32)

        syn_config = self._build_syn_config(frame, voice)

        try:
            chunks = list(voice.synthesize(text, syn_config=syn_config))
        except Exception as e:
            raise AcousticError(f"Piper inference failed: {e}") from e

        if not chunks:
            return np.zeros(0, dtype=np.float32)

        pcm = np.concatenate(
            [np.frombuffer(c.audio_int16_bytes, dtype=np.int16) for c in chunks]
        )
        sr = int(getattr(chunks[0], "sample_rate", self.sample_rate) or self.sample_rate)
        audio = pcm.astype(np.float32) / 32768.0

        target_sr = frame.sample_rate or sr
        if target_sr and target_sr != sr:
            audio = resample(audio, sr, target_sr)
            sr = target_sr

        # Pitch shifting is not natively supported by Piper; ignore silently
        # so callers don't break. Speed is applied via length_scale in config.
        return audio.astype(np.float32)

    def list_voices(self) -> list[str]:
        base = Path(self.model_dir or os.environ.get("ENG_TTS_PIPER_DIR") or DEFAULT_MODEL_DIR)
        if not base.exists():
            return []
        return sorted(p.stem.removesuffix(".onnx") if p.stem.endswith(".onnx") else p.stem
                      for p in base.glob("*.onnx"))

    # ---------------------------------------------------------------- helpers

    def _build_syn_config(self, frame: LinguisticFrame, voice: Any) -> Any:
        try:
            from piper.config import SynthesisConfig  # type: ignore
        except ImportError:
            return None

        speaker = self.speaker_id
        try:
            sid_str = frame.speaker_id
            if sid_str is not None:
                speaker = int(sid_str)
        except (TypeError, ValueError):
            pass

        # length_scale > 1 → slower; < 1 → faster. Piper uses inverse of speed.
        speed = float(frame.speed or 1.0)
        length_scale = 1.0 / speed if speed > 0 else 1.0

        kwargs: dict[str, Any] = {
            "length_scale": length_scale,
            "noise_scale": 0.667,
            "noise_w_scale": 0.8,
            "normalize_audio": True,
        }
        if speaker is not None:
            kwargs["speaker_id"] = speaker

        try:
            return SynthesisConfig(**kwargs)
        except TypeError:
            # Older piper versions had different field names; fall back to defaults.
            return None
