# Benchmarks

Run:

```bash
python scripts/benchmark.py --tier fast
python scripts/eval_g2p.py --n 500
```

Reported metrics:

- **RTF (Real-Time Factor)** = wall-clock seconds / audio seconds.
  Lower is better; <1.0 means faster than real-time.
- **PER (Phoneme Error Rate)** for the G2P stack vs CMUDict gold.

Indicative numbers on a Ryzen 7 / CPU-only:

| Tier | Backend | Model | RTF (CPU) | RTF (GPU) |
|------|---------|-------|-----------|-----------|
| fast | VITS | ljspeech | ~0.6 | ~0.05 |
| premium | StyleTTS2 | * | ~1.5 | ~0.10 |
| clone | XTTS-v2 | xtts_v2 | ~3.0 | ~0.20 |
| legacy | pyttsx3 | SAPI/eSpeak | ~0.05 | – |

(Actual numbers depend on hardware, text length, and model warm-up.)
