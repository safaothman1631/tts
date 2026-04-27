# Changelog

## 0.1.0 — 2025

Initial public alpha. Full-stack rebuild from prototype.

### Added
- Plugin registry with `@register("category", "name")`.
- `LinguisticFrame` data contract between NLP and acoustic stages.
- Rule-based normalizer covering 18+ NSW categories.
- Sentence segmenter (pysbd / spaCy / regex fallback).
- spaCy-based linguistic analyzer with regex fallback.
- POS-aware homograph disambiguator (~30 entries).
- Hybrid G2P (overrides → CMUDict → neural g2p-en LSTM).
- ARPABET ↔ IPA bidirectional mapping with stress.
- Rule-based prosody (5-level breaks, pitch/duration contour).
- Sentiment analyzers (lexicon + transformer).
- SSML 1.1 subset parser/walker (`break`, `prosody`, `emphasis`,
  `say-as`, `phoneme`, `sub`, `voice`, `p`, `s`).
- Acoustic backends: `VitsAcoustic`, `XTTSAcoustic`,
  `StyleTTS2Acoustic` (alias), `LegacyPyttsx3Acoustic`.
- HiFi-GAN + passthrough vocoders.
- Post-processing: EBU R128 loudness, denoise, resample.
- Streaming chunker with crossfade.
- `TTSPipeline` orchestrator + `synthesize()` convenience.
- Typer CLI: `say`, `analyze`, `normalize`, `voices`, `plugins`,
  `benchmark`, `serve`, `ui`, `version`.
- FastAPI REST API + WebSocket streaming + Prometheus metrics.
- Gradio web UI.
- Multi-stage Dockerfile + docker-compose (api + Prometheus + Grafana).
- Pytest unit tests with YAML golden cases for the normalizer.
- Scripts: `download_models.py`, `benchmark.py`, `eval_g2p.py`.
- Docs: architecture, NLP pipeline, SSML reference, API reference,
  voice cloning, benchmarks.

### Preserved
- Original prototype moved unchanged into `legacy/`.
