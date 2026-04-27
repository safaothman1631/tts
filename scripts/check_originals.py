"""Distinctness check for the originals-only catalog (9 Qwen3 speakers)."""
from __future__ import annotations

import base64
import io
import sys
import types

# Stub webrtcvad (no Windows wheel for Python 3.13) before resemblyzer imports.
if "webrtcvad" not in sys.modules:
    _vad = types.ModuleType("webrtcvad")
    class _Vad:
        def __init__(self, mode: int = 0) -> None: ...
        def is_speech(self, *_a, **_kw) -> bool: return True
    _vad.Vad = _Vad  # type: ignore[attr-defined]
    sys.modules["webrtcvad"] = _vad

import numpy as np
import requests
import soundfile as sf
from resemblyzer import VoiceEncoder, preprocess_wav  # noqa: E402

IDS = [
    "qwen-aiden", "qwen-ryan",
    "qwen-vivian", "qwen-serena", "qwen-uncle-fu", "qwen-eric", "qwen-dylan",
    "qwen-ono-anna", "qwen-sohee",
]
TEXT = "Hello, this is a sample utterance to compare voice identity across the catalog."


def main() -> int:
    enc = VoiceEncoder("cpu")
    embs: dict[str, np.ndarray] = {}
    for cid in IDS:
        r = requests.post(
            "http://127.0.0.1:8765/v1/synthesize",
            json={"text": TEXT, "voice_character": cid, "format": "wav", "language": "en"},
            timeout=180,
        )
        r.raise_for_status()
        j = r.json()
        audio, _ = sf.read(io.BytesIO(base64.b64decode(j["audio_base64"])))
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        sr = int(j["sample_rate"])
        wav = preprocess_wav(audio.astype(np.float32), source_sr=sr)
        embs[cid] = enc.embed_utterance(wav)
        dur = float(j["duration_seconds"])
        print(f"{cid:<14} sr={sr}  dur={dur:.2f}s  voice={j.get('voice')}")

    keys = list(embs)
    print("\nCosine similarity matrix:")
    print("            " + "  ".join(k.replace("qwen-", "")[:8].ljust(8) for k in keys))
    for k1 in keys:
        row = [f"{float(np.dot(embs[k1], embs[k2])):.3f}".ljust(8) for k2 in keys]
        print(f"{k1.replace('qwen-', '')[:10].ljust(12)}" + "  ".join(row))

    mat = np.array([[float(np.dot(embs[a], embs[b])) for b in keys] for a in keys])
    upper = mat[np.triu_indices(len(keys), k=1)]
    print(f"\nmedian={np.median(upper):.3f}  max={upper.max():.3f}  min={upper.min():.3f}")
    threshold = 0.85
    bad = [(keys[i], keys[j], float(mat[i, j]))
           for i in range(len(keys)) for j in range(i + 1, len(keys))
           if mat[i, j] >= threshold]
    if bad:
        print(f"\nWARN: {len(bad)} pair(s) above {threshold} cosine:")
        for a, b, c in bad:
            print(f"  {a} vs {b}: {c:.3f}")
        return 1
    print(f"\nPASS: every pair is below {threshold} cosine.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
