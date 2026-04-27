# Architecture

`eng-tts` is a modular, plugin-driven, English-first text-to-speech engine.

```
text/SSML
   │
   ▼
SSML parser ──► Normalizer ──► Segmenter ──► Linguistic Analyzer
   │                                              │
   │                                              ▼
   │                              Homograph Disambiguator
   │                                              │
   │                                              ▼
   │                                            G2P
   │                                              │
   │                                              ▼
   │                                          Prosody
   │                                              │
   │                                              ▼
   │                                          Sentiment
   │                                              │
   │                                              ▼
   │                                       FrameBuilder
   │                                              │
   │                                              ▼
   └──────────────────────────────────► Acoustic backend (VITS / XTTS / StyleTTS2 / pyttsx3)
                                                  │
                                                  ▼
                                              Vocoder (passthrough or HiFi-GAN)
                                                  │
                                                  ▼
                                          Post-processing
                                          (loudness, denoise, resample)
                                                  │
                                                  ▼
                                              AudioChunk
```

## Key principles

- **Plugin registry**: Every stage is a class that subclasses an `IXxx`
  interface and is registered with `@register("category", "name")`. The
  pipeline composes them via `create("category", "name")`.
- **LinguisticFrame** is the contract between NLP and acoustic stages.
  Acoustic backends consume *only* a `LinguisticFrame`.
- **Lazy loading** with thread-safe locks for heavy ML models.
- **Tiers**: `fast` (VITS), `premium` (StyleTTS2), `clone` (XTTS-v2),
  `legacy` (pyttsx3) — selectable at runtime.
- **Optional dependencies**: install only what you need via extras
  (`[nlp]`, `[acoustic]`, `[api]`, `[ui]`, `[postproc]`, `[full]`).
