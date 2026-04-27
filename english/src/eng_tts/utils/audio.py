"""Audio I/O and basic numeric utilities."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np


def to_float32(audio: np.ndarray) -> np.ndarray:
    """Coerce any audio array to float32 in [-1, 1]."""
    if audio.dtype == np.float32:
        return audio
    if np.issubdtype(audio.dtype, np.integer):
        max_v = float(np.iinfo(audio.dtype).max)
        return (audio.astype(np.float32) / max_v).clip(-1.0, 1.0)
    return audio.astype(np.float32)


def save_wav(path: str | Path, audio: np.ndarray, sample_rate: int) -> Path:
    import soundfile as sf

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), to_float32(audio), sample_rate, subtype="PCM_16")
    return path


def load_wav(path: str | Path) -> tuple[np.ndarray, int]:
    import soundfile as sf

    audio, sr = sf.read(str(path), always_2d=False)
    return to_float32(np.asarray(audio)), int(sr)


def resample(audio: np.ndarray, src_sr: int, dst_sr: int) -> np.ndarray:
    if src_sr == dst_sr:
        return audio
    try:
        import librosa  # type: ignore

        return librosa.resample(audio.astype(np.float32), orig_sr=src_sr, target_sr=dst_sr)
    except ImportError:  # pragma: no cover
        ratio = dst_sr / src_sr
        n = int(len(audio) * ratio)
        x_old = np.linspace(0.0, 1.0, len(audio), endpoint=False)
        x_new = np.linspace(0.0, 1.0, n, endpoint=False)
        return np.interp(x_new, x_old, audio).astype(np.float32)


def concat(chunks: list[np.ndarray], crossfade_samples: int = 0) -> np.ndarray:
    if not chunks:
        return np.zeros(0, dtype=np.float32)
    if crossfade_samples <= 0 or len(chunks) == 1:
        return np.concatenate(chunks).astype(np.float32)
    out = chunks[0].astype(np.float32)
    for nxt in chunks[1:]:
        n = min(crossfade_samples, len(out), len(nxt))
        if n == 0:
            out = np.concatenate([out, nxt.astype(np.float32)])
            continue
        fade_out = np.linspace(1.0, 0.0, n, dtype=np.float32)
        fade_in = np.linspace(0.0, 1.0, n, dtype=np.float32)
        head, tail = out[:-n], out[-n:] * fade_out + nxt[:n].astype(np.float32) * fade_in
        out = np.concatenate([head, tail, nxt[n:].astype(np.float32)])
    return out


def silence(seconds: float, sample_rate: int) -> np.ndarray:
    return np.zeros(int(seconds * sample_rate), dtype=np.float32)


def peak_normalize(audio: np.ndarray, peak_db: float = -1.0) -> np.ndarray:
    peak = float(np.max(np.abs(audio))) or 1.0
    target = 10 ** (peak_db / 20.0)
    return (audio * (target / peak)).astype(np.float32)
