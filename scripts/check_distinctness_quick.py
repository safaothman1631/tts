"""Quick distinctness sanity test: render 6 wildly different archetypes and
compute pairwise Resemblyzer cosine similarity. Exits 0 if max < 0.92.
"""
from __future__ import annotations
import json
import sys
import types
from pathlib import Path

# Stub webrtcvad (no Windows wheel for Python 3.13) before resemblyzer imports.
if "webrtcvad" not in sys.modules:
    _vad = types.ModuleType("webrtcvad")
    class _Vad:
        def __init__(self, mode: int = 0) -> None: ...
        def is_speech(self, *_a, **_kw) -> bool: return True
    _vad.Vad = _Vad
    sys.modules["webrtcvad"] = _vad

import numpy as np
import requests

OUT = Path("output/distinctness_check")
OUT.mkdir(parents=True, exist_ok=True)
TEXT = "The quick brown fox jumps over the lazy dog. I will tell you a story you have never heard before."
PICKS = [
    "arch-tycoon",        # Aiden  pitch -2
    "arch-pixie",         # Mia    pitch +5
    "arch-ogrerumble",    # Lucas  pitch -6
    "arch-spongeyellow",  # Liam   pitch +6
    "arch-faeriechime",   # Mia    pitch +7
    "arch-robotcore",     # Lucas  pitch  0  speed 0.92
]


def render(cid: str) -> Path:
    path = OUT / f"{cid}.wav"
    body = {"text": TEXT, "voice_character": cid, "format": "wav", "tier": "qwen3"}
    print(f"  rendering {cid} ...", flush=True)
    r = requests.post("http://127.0.0.1:8765/v1/synthesize.wav",
                      json=body, timeout=180)
    r.raise_for_status()
    path.write_bytes(r.content)
    return path


def main() -> int:
    paths = [render(c) for c in PICKS]
    from resemblyzer import VoiceEncoder, preprocess_wav
    enc = VoiceEncoder(verbose=False)
    embs = []
    for p in paths:
        wav = preprocess_wav(p)
        embs.append(enc.embed_utterance(wav).astype(np.float32))
    M = np.stack(embs)
    Mn = M / np.clip(np.linalg.norm(M, axis=1, keepdims=True), 1e-9, None)
    sim = Mn @ Mn.T
    n = len(PICKS)
    print("\nPairwise cosine similarity (lower = more distinct):")
    print("        " + "  ".join(p.replace("arch-", "")[:7].ljust(7) for p in PICKS))
    for i in range(n):
        row = "  ".join(f"{sim[i, j]:7.3f}" for j in range(n))
        print(f"  {PICKS[i].replace('arch-', '')[:7].ljust(7)} {row}")
    iu = np.triu_indices(n, k=1)
    pairs = sim[iu]
    print(f"\nmedian={np.median(pairs):.3f}  max={pairs.max():.3f}  min={pairs.min():.3f}")
    worst_idx = int(np.argmax(pairs))
    a, b = int(iu[0][worst_idx]), int(iu[1][worst_idx])
    print(f"worst pair: {PICKS[a]}  vs  {PICKS[b]}  cos={pairs.max():.3f}")
    report = {
        "voices": PICKS, "median": float(np.median(pairs)),
        "max": float(pairs.max()), "min": float(pairs.min()),
        "worst_pair": [PICKS[a], PICKS[b]],
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2))
    if pairs.max() > 0.92:
        print("\nFAIL: voices are still too similar in audio space.")
        return 1
    if np.median(pairs) > 0.55:
        print("\nWARN: median similarity is high; voices are weakly distinct.")
        return 0
    print("\nPASS: voices are clearly distinct.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
