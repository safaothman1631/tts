"""Acoustic distinctness audit for the voice catalog.

Reads every WAV in ``output/probes/`` (rendered by ``render_voice_probes.py``),
computes Resemblyzer 256-d speaker embeddings, builds a cosine similarity
matrix, and prints a report.

Acceptance gates (printed at end, exit code reflects pass/fail):
  - median pairwise similarity < 0.55  (lower = more distinct)
  - no pair similarity > 0.92          (any pair above is "near-duplicate")

Usage:
    python scripts/audit_voice_distinctness.py
    python scripts/audit_voice_distinctness.py --strict   # tighter gates
    python scripts/audit_voice_distinctness.py --top 30
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
PROBE_DIR = REPO / "output" / "probes"
REPORT_JSON = PROBE_DIR / "distinctness_report.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probes", type=Path, default=PROBE_DIR)
    parser.add_argument("--top", type=int, default=15, help="Print N closest pairs.")
    parser.add_argument("--strict", action="store_true",
                        help="Tighter acceptance gates (median < 0.45, max < 0.85).")
    args = parser.parse_args()

    wavs = sorted(args.probes.glob("*.wav"))
    if not wavs:
        print(f"ERROR: no probes found in {args.probes}. Run render_voice_probes.py first.", file=sys.stderr)
        return 2

    from resemblyzer import VoiceEncoder, preprocess_wav
    enc = VoiceEncoder(verbose=False)
    print(f"[embed] {len(wavs)} probes")
    embs: list[np.ndarray] = []
    ids: list[str] = []
    for i, w in enumerate(wavs, 1):
        try:
            wav = preprocess_wav(w)
            embs.append(enc.embed_utterance(wav).astype(np.float32))
            ids.append(w.stem)
            if i % 25 == 0:
                print(f"  {i}/{len(wavs)}")
        except Exception as e:
            print(f"  skip {w.name}: {e}")

    M = np.stack(embs)
    norms = np.linalg.norm(M, axis=1, keepdims=True)
    Mn = M / np.clip(norms, 1e-9, None)
    sim = Mn @ Mn.T  # cosine similarity matrix
    n = len(ids)

    iu = np.triu_indices(n, k=1)
    pair_sims = sim[iu]
    median = float(np.median(pair_sims))
    p90 = float(np.percentile(pair_sims, 90))
    mx = float(np.max(pair_sims))
    mn = float(np.min(pair_sims))

    # top-k worst (most similar) pairs
    order = np.argsort(-pair_sims)
    top_pairs = []
    for k in order[: args.top]:
        i, j = int(iu[0][k]), int(iu[1][k])
        top_pairs.append({"a": ids[i], "b": ids[j], "cos": float(pair_sims[k])})

    report = {
        "n_voices": n,
        "median_cos": median,
        "p90_cos": p90,
        "max_cos": mx,
        "min_cos": mn,
        "top_pairs": top_pairs,
    }
    PROBE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print()
    print("============== DISTINCTNESS AUDIT ==============")
    print(f"voices analysed : {n}")
    print(f"median cos sim  : {median:.3f}   (lower = more distinct)")
    print(f"p90    cos sim  : {p90:.3f}")
    print(f"max    cos sim  : {mx:.3f}")
    print(f"min    cos sim  : {mn:.3f}")
    print()
    print(f"Top {args.top} most-similar pairs (review for redundancy):")
    for p in top_pairs:
        print(f"  {p['cos']:.3f}   {p['a']:36s}  vs  {p['b']}")
    print()

    median_gate = 0.45 if args.strict else 0.55
    max_gate = 0.85 if args.strict else 0.92
    failures = []
    if median > median_gate:
        failures.append(f"median similarity {median:.3f} > gate {median_gate}")
    if mx > max_gate:
        failures.append(f"max similarity {mx:.3f} > gate {max_gate}  (pair: {top_pairs[0]['a']} / {top_pairs[0]['b']})")
    if failures:
        print("FAIL:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("PASS: catalog meets distinctness gates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
