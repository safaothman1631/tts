"""End-to-end synthesis benchmark."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

SAMPLE_TEXTS = [
    "The quick brown fox jumps over the lazy dog.",
    "Dr. Smith earned $1,250.50 on December 25th, 2024.",
    "Visit https://example.com to learn more about our products.",
    "She read the book; he read it too — but it was a different read.",
    "<speak>Hello <break time=\"300ms\"/> <emphasis level=\"strong\">world</emphasis>!</speak>",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", default="legacy", choices=["fast", "premium", "clone", "legacy"])
    ap.add_argument("--out", default="output/benchmark.json")
    ap.add_argument("--repeat", type=int, default=3)
    args = ap.parse_args()

    from eng_tts.config import get_settings
    from eng_tts.core.pipeline import TTSPipeline

    s = get_settings()
    s.acoustic_tier = args.tier  # type: ignore[assignment]
    pipe = TTSPipeline(settings=s)

    results: list[dict] = []
    for text in SAMPLE_TEXTS * args.repeat:
        t0 = time.perf_counter()
        chunk = pipe.synthesize(text)
        wall = time.perf_counter() - t0
        audio = float(len(chunk.samples) / chunk.sample_rate)
        results.append({
            "chars": len(text),
            "wall_seconds": wall,
            "audio_seconds": audio,
            "rtf": wall / max(audio, 1e-6),
        })

    summary = {
        "tier": args.tier,
        "n": len(results),
        "mean_rtf": sum(r["rtf"] for r in results) / len(results),
        "mean_wall": sum(r["wall_seconds"] for r in results) / len(results),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"summary": summary, "samples": results}, indent=2))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
