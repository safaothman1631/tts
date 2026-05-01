# TTS — Bilingual Text-to-Speech Workspace

This repository contains two clearly separated text-to-speech projects:

```
tts/
├── english/   ← world-class English TTS engine (eng-tts package)
└── kurdish/   ← Kurdish TTS apps, training scripts, datasets, docs
```

## One-Click Local Start

On Windows, double-click [start.bat](start.bat) from the project root. It starts
the eng-tts API on `http://127.0.0.1:8765`, starts the React UI on
`http://127.0.0.1:5173`, reuses either service if it is already running, and
opens the UI in your browser.

Keep the API and UI terminal windows open while using TTS Studio.

## English — `english/`

A modular, plugin-driven, production-grade English TTS engine.

- Source: [english/src/eng_tts/](english/src/eng_tts/)
- Plan: [english/MASTER_PLAN.md](english/MASTER_PLAN.md)
- Docs: [english/README.md](english/README.md), [english/docs/](english/docs/)
- Legacy prototype preserved in [english/legacy/](english/legacy/)

Quick start:

```bash
cd english
pip install -e ".[full]"
eng-tts say "Hello world" --out hello.wav
```

## Kurdish — `kurdish/`

Standalone Kurdish TTS apps and training pipeline.

```
kurdish/
├── apps/       ← Runnable Kurdish TTS apps (kurdish_app.py, ...)
├── training/   ← Training & test scripts (train_kurdish_*.py, ...)
├── tools/      ← Voice recorder, phonetic readers, fixes
├── docs/       ← Guides, quickstart, voice guide (Kurdish)
└── data/       ← Datasets, recordings, trained models
```

See [kurdish/docs/README_Kurdish.md](kurdish/docs/README_Kurdish.md) and
[kurdish/docs/START_HERE_Kurdish.txt](kurdish/docs/START_HERE_Kurdish.txt).

## Cross-Project Planning and Governance

- 90-day master plan (Sorani): [MASTER_PLAN_90D_SORANI.md](MASTER_PLAN_90D_SORANI.md)
- Governance baseline: [docs/GOVERNANCE_BASELINE.md](docs/GOVERNANCE_BASELINE.md)
- Ownership matrix: [docs/OWNERSHIP_MATRIX.md](docs/OWNERSHIP_MATRIX.md)
- Release checklist: [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md)
- Fallback policy: [docs/FALLBACK_POLICY.md](docs/FALLBACK_POLICY.md)
