"""Qwen 3 TTS acoustic backend.

Uses the official ``qwen-tts`` runtime for Qwen3-TTS models.

Environment variables:
- ENG_TTS_QWEN3_MODEL: HF repo id (default: Qwen/Qwen3-TTS-12Hz-0.6B-Base)
- ENG_TTS_QWEN3_CACHE_DIR: local cache/output dir for model files
- HF_TOKEN / HUGGING_FACE_HUB_TOKEN: token for gated/private models
"""
from __future__ import annotations

import os
from pathlib import Path
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

DEFAULT_QWEN3_MODEL = "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"

# ─── Emotion → rich tone instruction ─────────────────────────────────
# These short prose descriptions are appended to the base style prompt so
# Qwen3 actually shapes pitch / energy / breathiness / pacing differently.
EMOTION_INSTRUCTIONS: dict[str, str] = {
    "neutral": "Speak in a balanced, neutral tone with even pacing and unhurried clarity.",
    "happy": (
        "Speak with a bright, smiling, energetic tone. Lift the pitch slightly upward at "
        "phrase ends, lengthen vowels on emphasis, and let a hint of laughter colour the voice."
    ),
    "sad": (
        "Speak with a soft, melancholy tone. Slow the pacing, soften consonants, drop the pitch "
        "gently at phrase ends and let breath linger between words."
    ),
    "angry": (
        "Speak with a sharp, intense, controlled anger. Strengthen consonants, push energy "
        "forward, slightly tighten the throat, and bite into stressed syllables."
    ),
    "excited": (
        "Speak with high-energy excitement. Quicken the pacing, raise the pitch, sharpen the "
        "emphasis on key words, and let breath bursts punctuate the most thrilling phrases."
    ),
    "calm": (
        "Speak with a calm, soothing, grounded presence. Slow the pacing significantly, soften "
        "the attack on every word, lower the pitch slightly and let warm breath flow through."
    ),
    "serious": (
        "Speak with a serious, authoritative, weighty tone. Lower the pitch, slow the cadence, "
        "firm up the consonants and let pauses carry gravity."
    ),
    "friendly": (
        "Speak with a warm, friendly, conversational tone. Smile through the voice, keep pacing "
        "easy, lift inflections naturally and sound genuinely engaged with the listener."
    ),
    "whisper": (
        "Speak in an intimate close-mic whisper. Use only breath, suppress voiced phonation, "
        "keep pacing slow and gentle, and shape consonants very softly."
    ),
    "confident": (
        "Speak with assured confidence. Project from the chest, keep the pitch steady, place "
        "firm emphasis on key claims and end phrases with conviction."
    ),
    "sarcastic": (
        "Speak with dry sarcasm. Stretch key vowels, dip the pitch on punchlines, and let a "
        "knowing half-smile colour the delivery."
    ),
    "romantic": (
        "Speak with a soft romantic tenderness. Slow the pacing, lower the pitch a touch, "
        "breathe gently through phrases and warm every vowel."
    ),
}

# Style preset id → expanded instruction prose. Mirrors api.rest.STYLE_PRESETS.
STYLE_INSTRUCTIONS: dict[str, str] = {
    "narration": "A clear, natural narration voice with steady pacing and balanced warmth.",
    "news": "A confident newscaster tone with crisp articulation, brisk pacing and impartial delivery.",
    "audiobook": "A warm, expressive long-form audiobook voice with nuanced emphasis and unhurried pacing.",
    "conversational": "A friendly, casual conversational voice with natural smile and easy rhythm.",
    "podcast": "A relaxed, engaging podcast host voice with light personality and conversational warmth.",
    "announce": "An energetic announcement voice with strong projection and clear emphasis.",
    "calm": "A slow, soothing voice with low resonance, long warm vowels and meditative pacing.",
    "cinematic": "A deep cinematic trailer voice with dramatic intensity, ominous pacing and powerful pauses.",
    "customer": "A polite, empathetic customer support voice with helpful warmth and reassuring pacing.",
    "asmr": "An intimate ASMR whisper with delicate articulation and very soft sibilants.",
    "sportscaster": "An energetic sportscaster with rapid play-by-play cadence and crowd-aware projection.",
    "luxury": "A refined luxury-brand voiceover with elegant slow pacing and understated confidence.",
}


def _resolve_style_prompt(raw: str | None) -> str | None:
    """If the user passes a known preset id (e.g. ``cinematic``) expand it to the
    full descriptive prose. Otherwise return the raw prompt unchanged."""
    if not raw:
        return None
    key = raw.strip().lower()
    return STYLE_INSTRUCTIONS.get(key, raw)


@register("acoustic", "qwen3")
class Qwen3Acoustic(IAcoustic):
    name = "qwen3"
    produces_waveform = True
    sample_rate = 24000

    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
    ) -> None:
        self.model_name = model_name or os.environ.get("ENG_TTS_QWEN3_MODEL") or DEFAULT_QWEN3_MODEL
        self.device = (device or "cpu").lower()
        self._model: Any = None

    def _ensure_loaded(self) -> Any:
        if self._model is not None:
            return self._model

        with _LOAD_LOCK:
            if self._model is not None:
                return self._model

            try:
                import torch  # type: ignore
                from qwen_tts import Qwen3TTSModel  # type: ignore
            except ImportError as e:
                raise AcousticError("qwen-tts not installed. Install `eng-tts[qwen3]`.") from e

            cache_dir = os.environ.get("ENG_TTS_QWEN3_CACHE_DIR")
            token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")

            kwargs: dict[str, Any] = {}
            if self.device == "cuda":
                kwargs["device_map"] = "cuda:0"
                kwargs["dtype"] = torch.bfloat16
            else:
                kwargs["device_map"] = "cpu"
                kwargs["dtype"] = torch.float32

            if cache_dir:
                kwargs["cache_dir"] = cache_dir
            if token:
                kwargs["token"] = token

            try:
                model_ref = _resolve_qwen3_model_ref(self.model_name)
                _log.info(f"loading_qwen3 model={model_ref} device={self.device}")
                self._model = Qwen3TTSModel.from_pretrained(model_ref, **kwargs)
            except Exception as e:
                raise AcousticError(f"Failed to load Qwen3 TTS model '{self.model_name}': {e}") from e

        return self._model

    def _resolve_speaker(self, model: Any, requested: str) -> str:
        """Strict speaker resolution: return the requested name if (and only
        if) the loaded model genuinely supports it. No aliasing, no fallback
        to a different speaker - the catalog is required to use real names
        from ``model.get_supported_speakers()``.
        """
        try:
            supported = sorted(set(model.get_supported_speakers() or []))
        except Exception:  # noqa: BLE001
            supported = []
        key = (requested or "").strip().lower()
        if supported and key not in supported:
            raise AcousticError(
                f"Unknown Qwen3 speaker '{requested}'. "
                f"Supported by this model: {supported}"
            )
        return key

    def synthesize(self, frame: LinguisticFrame) -> np.ndarray:
        model = self._ensure_loaded()
        text = (frame.text or "").strip()
        if not text:
            return np.zeros(0, dtype=np.float32)

        language = _map_language(frame.language)

        try:
            ref_audio = frame.extra.get("speaker_wav") if frame.extra else None
            ref_text = frame.extra.get("speaker_text") if frame.extra else None
            if ref_audio:
                wavs, sr = model.generate_voice_clone(
                    text=text,
                    language=language,
                    ref_audio=ref_audio,
                    ref_text=ref_text,
                    non_streaming_mode=True,
                )
            else:
                raw_speaker = (
                    frame.extra.get("qwen_speaker")
                    if frame.extra and isinstance(frame.extra.get("qwen_speaker"), str)
                    else (frame.speaker_id or "Ryan")
                )
                raw_prompt = (
                    frame.extra.get("voice_prompt")
                    if frame.extra and isinstance(frame.extra.get("voice_prompt"), str)
                    else None
                )
                speaker = self._resolve_speaker(model, raw_speaker)
                base_instruct = _resolve_style_prompt(raw_prompt) or \
                    "A clear, neutral, natural speaking voice."
                emotion = (
                    frame.extra.get("emotion")
                    if frame.extra and isinstance(frame.extra.get("emotion"), str)
                    else (frame.emotion if getattr(frame, "emotion", None) else None)
                )
                emo_key = (emotion or "").strip().lower()
                if emo_key and emo_key != "neutral":
                    detail = EMOTION_INSTRUCTIONS.get(emo_key, f"Speak with a clearly {emotion} tone.")
                    instruct = f"{base_instruct} {detail}"
                else:
                    instruct = base_instruct
                wavs, sr = model.generate_custom_voice(
                    text=text,
                    speaker=speaker,
                    instruct=instruct,
                    language=language,
                    non_streaming_mode=True,
                )
        except Exception as e:
            raise AcousticError(f"Qwen3 inference failed: {e}") from e

        if not wavs:
            return np.zeros(0, dtype=np.float32)

        audio = np.asarray(wavs[0], dtype=np.float32)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)

        target_sr = frame.sample_rate or int(sr or self.sample_rate)
        if target_sr and target_sr != sr:
            audio = resample(audio, int(sr), target_sr)

        # NOTE: no post-synth pitch/time DSP. Every voice exposed by this
        # backend must be a true Qwen3 original - identity is owned by the
        # speaker id, not by librosa effects.
        return audio.astype(np.float32)


def _map_language(tag: str | None) -> str:
    if not tag:
        return "English"

    t = tag.lower()
    # Pass through canonical Qwen3 language names directly.
    canonical = {
        "english", "chinese", "japanese", "korean", "german", "french",
        "russian", "portuguese", "spanish", "italian",
    }
    if t in canonical:
        return t.capitalize()
    if t.startswith("en"):
        return "English"
    if t.startswith("zh"):
        return "Chinese"
    if t.startswith("ja"):
        return "Japanese"
    if t.startswith("ko"):
        return "Korean"
    if t.startswith("de"):
        return "German"
    if t.startswith("fr"):
        return "French"
    if t.startswith("ru"):
        return "Russian"
    if t.startswith("pt"):
        return "Portuguese"
    if t.startswith("es"):
        return "Spanish"
    if t.startswith("it"):
        return "Italian"
    # Languages without first-class Qwen3 phoneme support: route via English
    # (the underlying TTS will still pronounce romanised text reasonably).
    return "English"


def _resolve_qwen3_model_ref(model_name: str) -> str:
    # If the model name is already a local path, use it directly.
    maybe_path = Path(model_name)
    if maybe_path.exists():
        return str(maybe_path)

    # Try local mirror produced by snapshot download scripts.
    if "/" in model_name:
        cache_root = os.environ.get("ENG_TTS_QWEN3_CACHE_DIR")
        roots: list[Path] = []
        if cache_root:
            roots.append(Path(cache_root))
        roots.append(Path.cwd() / "models" / "qwen3")

        repo_dir_name = model_name.replace("/", "--")
        for root in roots:
            candidate = root / repo_dir_name
            if (candidate / "model.safetensors").exists():
                return str(candidate)

    return model_name
