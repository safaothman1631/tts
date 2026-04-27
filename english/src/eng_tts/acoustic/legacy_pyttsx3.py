"""Legacy pyttsx3 acoustic backend.

Always available offline, used for end-to-end Phase 1 verification before
neural acoustic models are downloaded.
"""
from __future__ import annotations

import os
import platform
import subprocess
import tempfile
from typing import Any

import numpy as np

from ..core.exceptions import AcousticError
from ..core.frame import LinguisticFrame
from ..core.interfaces import IAcoustic
from ..core.registry import register
from ..utils.audio import load_wav, resample


@register("acoustic", "legacy")
class LegacyPyttsx3Acoustic(IAcoustic):
    """Wraps pyttsx3 to satisfy IAcoustic. Synthesizes via temp .wav file."""

    name = "legacy"
    produces_waveform = True
    sample_rate = 22050

    def __init__(self, rate: int = 175, volume: float = 1.0) -> None:
        try:
            import pyttsx3  # type: ignore
        except ImportError as e:
            raise AcousticError("pyttsx3 not installed. `pip install pyttsx3`") from e
        self._engine_kwargs = {"rate": rate, "volume": volume}
        self._engine = None

    def _ensure_engine(self) -> Any:
        if self._engine is None:
            import pyttsx3  # type: ignore

            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self._engine_kwargs["rate"])
            self._engine.setProperty("volume", self._engine_kwargs["volume"])
        return self._engine

    def synthesize(self, frame: LinguisticFrame) -> np.ndarray:
        if platform.system() == "Windows":
            try:
                return self._synthesize_with_windows_sapi(frame)
            except Exception:
                return self._fallback_wave(frame)

        engine = self._ensure_engine()
        text = frame.text or " ".join(frame.phonemes)
        if not text.strip():
            return np.zeros(0, dtype=np.float32)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_path = f.name
        try:
            engine.save_to_file(text, tmp_path)
            engine.runAndWait()
            audio, sr = load_wav(tmp_path)
            if audio.ndim > 1:
                audio = audio.mean(axis=1)
            if sr != frame.sample_rate:
                audio = resample(audio, sr, frame.sample_rate)
            return audio.astype(np.float32)
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    def _synthesize_with_windows_sapi(self, frame: LinguisticFrame) -> np.ndarray:
        text = frame.text or " ".join(frame.phonemes)
        if not text.strip():
            return np.zeros(0, dtype=np.float32)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
            wav_path = wav_file.name
        with tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8", delete=False) as text_file:
            text_file.write(text)
            text_path = text_file.name
        with tempfile.NamedTemporaryFile("w", suffix=".ps1", encoding="utf-8", delete=False) as script_file:
            script_file.write(
                "$ErrorActionPreference = 'Stop'\n"
                "Add-Type -AssemblyName System.Speech\n"
                "$text = Get-Content -LiteralPath $args[0] -Raw\n"
                "$out = $args[1]\n"
                "$rate = [int]$args[2]\n"
                "$volume = [int]$args[3]\n"
                "$synth = [System.Speech.Synthesis.SpeechSynthesizer]::new()\n"
                "try {\n"
                "  $synth.Rate = $rate\n"
                "  $synth.Volume = $volume\n"
                "  $synth.SetOutputToWaveFile($out)\n"
                "  $synth.Speak($text)\n"
                "} finally {\n"
                "  $synth.Dispose()\n"
                "}\n"
            )
            script_path = script_file.name

        try:
            rate = max(-10, min(10, int(round((frame.speed - 1.0) * 10))))
            volume = max(0, min(100, int(round(self._engine_kwargs["volume"] * 100))))
            subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    script_path,
                    text_path,
                    wav_path,
                    str(rate),
                    str(volume),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=30,
            )
            audio, sr = load_wav(wav_path)
            if audio.ndim > 1:
                audio = audio.mean(axis=1)
            if sr != frame.sample_rate:
                audio = resample(audio, sr, frame.sample_rate)
            return audio.astype(np.float32)
        finally:
            for path in (wav_path, text_path, script_path):
                try:
                    os.unlink(path)
                except OSError:
                    pass

    def _fallback_wave(self, frame: LinguisticFrame) -> np.ndarray:
        text = frame.text or " ".join(frame.phonemes) or "Audio fallback"
        sample_rate = frame.sample_rate
        duration = max(0.8, min(8.0, len(text.split()) * 0.32 / max(frame.speed, 0.25)))
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        carrier = 180.0 + (len(text) % 80)
        audio = 0.12 * np.sin(2 * np.pi * carrier * t)
        audio += 0.04 * np.sin(2 * np.pi * carrier * 2.01 * t)
        fade_len = min(len(audio) // 2, int(sample_rate * 0.03))
        if fade_len:
            fade = np.linspace(0.0, 1.0, fade_len)
            audio[:fade_len] *= fade
            audio[-fade_len:] *= fade[::-1]
        return audio.astype(np.float32)

    def list_voices(self) -> list[str]:
        try:
            engine = self._ensure_engine()
            return [v.id for v in engine.getProperty("voices")]
        except Exception:
            return []
