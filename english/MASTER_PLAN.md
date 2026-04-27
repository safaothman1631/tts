# 🎙️ MASTER PLAN — English TTS World-Class Rebuild

> **ئامانج:** گۆڕینی بەشی `english/` لە سیستەمێکی سادەی pyttsx3+gTTS بۆ سیستەمێکی **state-of-the-art** لە ئاستی ElevenLabs / OpenAI TTS / Google WaveNet.
>
> **فەلسەفە:** *NLP-first*. ٧٠٪ـی کوالێتی TTS لەسەر front-end ـی NLP بەستراوە، نەک acoustic model. بۆیە Phase 1 = NLP بنیاتنانی تەواو.
>
> **دۆخی ئێستا (baseline):** monolithic، ٦ stage NLP زۆر سادە، textblob+num2words+pyttsx3. **G2P نییە، Phonemes نییە، Prosody model نییە، Neural acoustic نییە.** ئەمە دەستپێکێکە، نەک بنکە.

---

## 📑 ناوەڕۆک
1. ڤیژن و فەلسەفە
2. Architecture Overview
3. NLP Pipeline تەواو (12 stage)
4. Acoustic Model & Vocoder
5. Code Architecture & File Structure
6. Quality, Evaluation & Benchmarks
7. Performance & Optimization
8. Deployment
9. Roadmap — 6 Phases
10. Dependencies & Tooling
11. Risk Assessment
12. Success Metrics
13. Concrete Next Steps — Phase 1

---

## 1. ڤیژن و فەلسەفە

### Vision
> *"A production-grade, fully open-source English TTS engine where every stage of the pipeline — from raw text to waveform — is independently testable, replaceable, and benchmark-comparable to commercial systems."*

### Core Principles
| # | Principle | Meaning |
|---|-----------|---------|
| 1 | Modular by default | هەر stage یەک interface هەیە، دەگۆڕێت بەبێ تێکدانی بەشی تر |
| 2 | NLP > Acoustic | کوالێتی phoneme + prosody گرنگترە لە کوالێتی vocoder |
| 3 | Linguistic correctness first | "150" نابێت ببێت "one five zero" — context-aware (year? currency? phone?) |
| 4 | Reproducibility | هەموو model+config+seed لۆگ دەکرێت |
| 5 | Streaming-first | API دەبێت chunk-by-chunk audio بنێرێت |
| 6 | Offline-capable | core pipeline بەبێ ئینتەرنێت |
| 7 | Production observability | logging, metrics, tracing لە ڕۆژی ١ ـەوە |

### "World-Class" بە concrete
- **MOS ≥ 4.3** (near-human)
- **WER ≤ 2%** (Whisper-large-v3 ASR re-transcription)
- **RTF ≤ 0.1** CPU، ≤ 0.02 GPU
- **Phoneme accuracy ≥ 98%** (CMUdict held-out)
- **Homograph disambig ≥ 95%**
- **Time-to-first-audio ≤ 200ms** (streaming)

---

## 2. Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│            CLIENT (REST · WebSocket · CLI · SDK · Web UI)      │
└──────────────────────────────┬─────────────────────────────────┘
                               │ text + voice_id + params
                               ▼
┌────────────────────────────────────────────────────────────────┐
│          ORCHESTRATOR (TTSPipeline)                            │
│   caching · batching · streaming · error recovery              │
└──────┬──────────────────────────────────────────────────┬──────┘
       │                                                  │
       ▼                                                  ▼
┌──────────────────────────┐         ┌──────────────────────────┐
│  FRONT-END (NLP)         │         │  BACK-END (ACOUSTIC)     │
│  1. SSML parser          │         │  8. Acoustic model       │
│  2. Text Normalizer      │         │     (VITS/StyleTTS2/XTTS)│
│  3. Sentence Segmenter   │   ──►   │     → mel-spectrogram    │
│  4. Tokenize+POS+NER+dep │         │                          │
│  5. Homograph Disambig.  │         │  9. Vocoder              │
│  6. G2P (CMU + Neural)   │         │     (HiFi-GAN/BigVGAN)   │
│  7. Prosody Predictor    │         │     → waveform 22/24kHz  │
│  → LinguisticFrame       │         │ 10. Post-proc (loudness, │
│                          │         │     denoise, resample)   │
└──────────────────────────┘         └──────────────────────────┘
```

**Data contract** (single source of truth between front-end ↔ back-end):

```python
@dataclass
class LinguisticFrame:
    phonemes: list[str]            # ARPABET or IPA
    durations: list[float] | None
    pitch_contour: list[float] | None
    energy_contour: list[float] | None
    word_boundaries: list[int]
    phrase_breaks: list[int]       # B2/B3 indices
    stress: list[int]              # 0/1/2 per vowel
    speaker_id: str | None
    style_id: str | None
    language: str = "en-US"
```

> هەر acoustic backendێک کە plug ببێت، تەنها ئەم contract ـە قبوڵ دەکات.

---

## 3. NLP Pipeline تەواو — ١٢ Stage

### Stage 1 — SSML & Input Parser
- Parse: `<speak>`, `<voice>`, `<prosody>`, `<break>`, `<emphasis>`, `<say-as interpret-as="date|currency|telephone|spell-out">`, `<phoneme alphabet="ipa" ph="">`, `<sub>`, `<lang>`
- Plain text → implicit `<speak>` wrap
- Output: AST → walker یeیلد دەکات text spans + attributes
- **Lib:** `lxml` + custom AST

### Stage 2 — Text Normalizer (TN) — ئەمە یەکەم گرنگییە
هەموو "non-standard words" (NSW) → "spoken form".

| Category | Input | Output |
|----------|-------|--------|
| Cardinal | `42` | forty-two |
| Ordinal | `3rd`, `21st` | third, twenty-first |
| Year | `1999`, `2024` | nineteen ninety-nine, twenty twenty-four |
| Decade | `1990s`, `'90s` | nineteen nineties |
| Decimal | `3.14` | three point one four |
| Fraction | `1/2`, `3/4` | one half, three quarters |
| Currency | `$1,250.50`, `€10`, `£5.99` | one thousand two hundred fifty dollars and fifty cents |
| Percent | `25%` | twenty-five percent |
| Phone | `+1-555-123-4567` | plus one, five five five, … |
| Time | `3:30 PM`, `14:00` | three thirty p m, fourteen hundred |
| Date | `12/25/2024`, `Dec 25` | December twenty-fifth twenty twenty-four |
| Range | `10-20` | ten to twenty |
| Math | `2+2=4`, `5×3` | two plus two equals four |
| Units | `5 kg`, `25°C`, `10 km/h` | five kilograms, twenty-five degrees celsius |
| URL | `https://github.com` | h t t p s colon slash slash github dot com |
| Email | `a@b.com` | a at b dot com |
| Hashtag | `#AI` | hashtag A I |
| Acronym | `NASA` vs `FBI` | "nasa" (word) vs "f b i" (spell) — lexicon-driven |
| Abbreviation | `Dr.`, `St.`, `Mt.` | context-aware (`St.` = Saint vs Street) |
| Roman | `Henry VIII` | the eighth |
| Symbols | `&`, `@`, `*` | context-aware |
| Unicode | smart quotes, em-dash, NBSP | normalize |
| Emoji | `❤️` | red heart (configurable) |

**Strategy:**
- Layer 1: **Rule-based** (regex + `num2words` + `inflect` + lexicons) — fast, deterministic
- Layer 2: **Neural fallback** (T5/ByT5 fine-tuned on Google TN dataset) — rare cases
- **Highly recommended lib:** `nemo_text_processing` (NVIDIA, WFST-based, production-grade)

### Stage 3 — Sentence Segmentation
- **`pySBD`** or **spaCy `en_core_web_trf`** — far better than NLTK on edge cases
- Handle: quotations, parentheticals, ellipses, mid-sentence abbrevs, list items
- Preserve original char offsets (SSML alignment)

### Stage 4 — Tokenize + POS + NER + Dependency
- **spaCy `en_core_web_trf`** (transformer SOTA)
- Outputs: POS (homograph + prosody)، NER (PERSON/ORG/MONEY/DATE → say-as routing)، dependency parse (phrase breaks)، lemmas (lexicon lookup)

### Stage 5 — Homograph Disambiguation
کلاسیکیترین کێشە: *lead* (LEED metal) vs *lead* (LIID guide)، *read* (RIID/RED)، *bass* (BAES/BEYS)، *tear/wind/bow/close/desert/minute/object/present/record/refuse*…

**Approach:**
1. Curated list (~150 homographs + pronunciations)
2. POS-based rule (covers ~80%)
3. Fine-tuned **DistilBERT** classifier (5-word context) for ambiguous
4. **Dataset:** Wikipedia Homograph Dataset (Google) — pre-labeled

### Stage 6 — G2P (Grapheme-to-Phoneme)
**Hybrid سێ-ئاستە:**

```
word
  ├─► Lexicon lookup (CMUdict ~134k)        → hit? return
  ├─► User custom overrides                  → hit? return
  └─► Neural fallback (DeepPhonemizer)       → generate
```

- **Format:** ARPABET internal، IPA on demand
- **Libs:** `g2p-en` (quick start) → `phonemizer` (espeak-ng) → **DeepPhonemizer** (best neural)
- OOV handling: confidence score، below threshold → log
- Multi-pronunciation: choose by POS، then frequency

### Stage 7 — Lexical Stress & Syllabification
- ARPABET vowels carry stress (0/1/2) — free from CMUdict
- OOV → multi-task neural model
- Syllabification: maximum onset principle + sonority hierarchy (پێویستە بۆ duration)
- Lib: `syllapy` or rule-based

### Stage 8 — Prosody Prediction
**ئەمە جیاوازی "natural" و "robotic" دروست دەکات.**

Sub-tasks:
1. **Phrase break** (B0 word / B2 minor / B3 major / B4 sentence) — BiLSTM+CRF on POS+punct OR fine-tuned BERT token classifier (LibriTTS-aligned)
2. **Pitch (F0)** per phoneme
3. **Duration** per phoneme
4. **Energy** per phoneme

> ئەگەر end-to-end VITS بەکاربهێنرێت → prosody implicit. بەڵام بۆ explicit control، FastSpeech2-style variance adaptors وەک standalone module.

### Stage 9 — Punctuation-aware Intonation
- `.` → falling pitch + 400ms break
- `?` → rising (yes/no) or falling (wh-) + 350ms
- `!` → high peak + emphasis + 350ms
- `,` → slight rise + 150ms
- `;` `:` → 250ms
- `—` → 200ms
- `...` → 500ms + trailing pitch
- `"…"` → optional voice modulation

### Stage 10 — Discourse & Sentiment
- Replace TextBlob (toy) with **`cardiffnlp/twitter-roberta-base-sentiment-latest`**
- Emotion: 7-class Ekman via **`j-hartmann/emotion-english-distilroberta-base`**
- Discourse markers ("however", "moreover", "in conclusion") → adjust pacing
- Map → style embedding (if multi-style acoustic)

### Stage 11 — Code-Switching Detection
- Detect non-English spans inline (*"Let's go to the café"*، *"the Schadenfreude was real"*)
- `fasttext lid.176` per token-window
- Route foreign words → native G2P (if available) OR English-accented approximation
- **Future:** seamless integration with Kurdish module بۆ true bilingual sentences

### Stage 12 — LinguisticFrame Builder
هەموو dataـەکانی سەرەوە package دەکات بۆ `LinguisticFrame` (وەک §2)، ئامادە بۆ acoustic.

---

## 4. Acoustic Model & Vocoder

### Model Selection Matrix

| Model | Quality | Speed | Voice Clone | Stream | Multi-spk | Verdict |
|-------|---------|-------|-------------|--------|-----------|---------|
| **VITS / VITS2** | ⭐⭐⭐⭐ | Fast | Limited | Yes | Yes | ✅ **Default** — best balance |
| **StyleTTS 2** | ⭐⭐⭐⭐⭐ | Med | Excellent | Yes | Yes | ✅ **Premium** — SOTA quality |
| **XTTS-v2** (Coqui) | ⭐⭐⭐⭐ | Med | ⭐⭐⭐⭐⭐ (6s) | Yes | Yes | ✅ **Voice cloning** |
| **FastSpeech2 + HiFi-GAN** | ⭐⭐⭐ | V.Fast | No | Yes | Yes | Reliable baseline |
| Tacotron 2 | ⭐⭐⭐ | Slow | No | No | Limited | ❌ Legacy |
| Bark (Suno) | ⭐⭐⭐⭐ | Slow | Yes | No | Yes | Niche (FX/music) |
| Tortoise | ⭐⭐⭐⭐⭐ | V.Slow | Yes | No | Yes | ❌ Too slow |
| Parler-TTS | ⭐⭐⭐⭐ | Med | Description | Partial | Yes | 🆕 Promising، Apache-2.0 |

**Decision:** ship **3 tiers** behind unified interface:
- `tier="fast"` → VITS
- `tier="premium"` → StyleTTS 2
- `tier="clone"` → XTTS-v2

### Vocoder
- **HiFi-GAN v3** — default (22.05 kHz)
- **BigVGAN** (NVIDIA) — premium (44.1 kHz, near-perfect)
- **WaveRNN** — only for extreme low-resource

### Voice Library
- 4 built-in voices fine-tuned on LibriTTS / VCTK (2 male، 2 female، neutral US)
- Voice cloning via XTTS-v2 (6–30s reference → speaker embedding cached)
- Custom fine-tuning recipe in `docs/finetune.md` (30 min audio → personal voice)

### Style / Emotion Control
- Global Style Tokens (GST) on top of VITS
- Reference audio conditioning
- Prompt-based (Parler-TTS style)

### Streaming
- Chunk by sentence/phrase break
- Overlap-add 50ms crossfade
- Time-to-first-audio < 200ms

---

## 5. Code Architecture & File Structure

```
english/
├── pyproject.toml                  # ← replaces requirements.txt
├── README.md
├── MASTER_PLAN.md
├── CHANGELOG.md
├── LICENSE
├── .env.example
├── Dockerfile
├── docker-compose.yml
│
├── src/
│   └── eng_tts/
│       ├── __init__.py
│       ├── version.py
│       │
│       ├── config/
│       │   ├── settings.py         # Pydantic Settings
│       │   ├── defaults.yaml
│       │   └── voices.yaml
│       │
│       ├── core/
│       │   ├── pipeline.py         # TTSPipeline orchestrator
│       │   ├── frame.py            # LinguisticFrame
│       │   ├── interfaces.py       # ABCs
│       │   ├── registry.py         # plugin registry
│       │   ├── cache.py            # LRU + disk
│       │   └── exceptions.py
│       │
│       ├── ssml/
│       │   ├── parser.py
│       │   ├── ast.py
│       │   └── walker.py
│       │
│       ├── nlp/
│       │   ├── normalizer/
│       │   │   ├── base.py
│       │   │   ├── rule_based.py
│       │   │   ├── nemo_wfst.py
│       │   │   ├── neural.py       # T5/ByT5 fallback
│       │   │   └── lexicons/
│       │   │       ├── abbreviations.json
│       │   │       ├── acronyms.json
│       │   │       ├── units.json
│       │   │       └── currencies.json
│       │   ├── segmentation.py
│       │   ├── linguistic.py       # spaCy POS/NER/dep
│       │   ├── homograph/
│       │   │   ├── disambiguator.py
│       │   │   ├── dictionary.json
│       │   │   └── classifier.py
│       │   ├── g2p/
│       │   │   ├── base.py
│       │   │   ├── lexicon.py      # CMUdict
│       │   │   ├── neural.py
│       │   │   ├── hybrid.py
│       │   │   ├── arpabet_ipa.py
│       │   │   └── data/cmudict.txt
│       │   ├── prosody/
│       │   │   ├── breaks.py
│       │   │   ├── pitch.py
│       │   │   ├── duration.py
│       │   │   ├── energy.py
│       │   │   └── stress.py
│       │   ├── syllabify.py
│       │   ├── sentiment.py
│       │   ├── discourse.py
│       │   └── codeswitch.py
│       │
│       ├── acoustic/
│       │   ├── base.py
│       │   ├── vits_model.py
│       │   ├── styletts2_model.py
│       │   ├── xtts_model.py
│       │   ├── fastspeech2_model.py
│       │   └── speakers/embeddings.py
│       │
│       ├── vocoder/
│       │   ├── base.py
│       │   ├── hifigan.py
│       │   └── bigvgan.py
│       │
│       ├── postproc/
│       │   ├── denoise.py
│       │   ├── loudness.py         # EBU R128
│       │   └── resample.py
│       │
│       ├── streaming/
│       │   ├── chunker.py
│       │   └── crossfade.py
│       │
│       ├── api/
│       │   ├── rest.py             # FastAPI
│       │   ├── websocket.py
│       │   ├── schemas.py          # Pydantic
│       │   └── auth.py
│       │
│       ├── cli/main.py             # Typer CLI
│       ├── ui/gradio_app.py
│       └── utils/
│           ├── logging.py          # structlog
│           ├── metrics.py          # prometheus
│           ├── audio.py
│           └── download.py
│
├── models/                         # gitignored checkpoints
├── data/{lexicons,test_sets,benchmarks}/
├── scripts/
│   ├── download_models.py
│   ├── benchmark.py
│   ├── eval_g2p.py
│   ├── eval_mos.py
│   └── train_homograph.py
│
├── tests/
│   ├── unit/{test_normalizer,test_g2p,test_homograph,test_prosody,test_pipeline}.py
│   ├── integration/{test_api,test_streaming}.py
│   ├── golden/normalizer_cases.yaml   # snapshot tests
│   └── conftest.py
│
├── notebooks/
├── docs/{architecture,nlp_pipeline,ssml_reference,api_reference,voice_cloning,finetune,benchmarks}.md
│
└── legacy/                         # ← move current files here
    ├── bilingual_tts.py
    ├── english_tts.py
    ├── tts_engine.py
    ├── tts_pipeline.py
    ├── nlp_processor.py
    ├── config.py
    ├── main.py
    ├── demo_bilingual.py
    ├── example_usage.py
    └── quick_test.py
```

### Key Architectural Decisions
1. **Plugin / Registry** — هەر component لە registry تۆمار، switching backend = یەک سەتر config
2. **Pydantic Settings** — config لە env vars / YAML / `.env` (نەک constants)
3. **`pyproject.toml`** — extras: `[fast]`, `[premium]`, `[clone]`, `[gpu]`, `[api]`, `[ui]`, `[full]`
4. **Async-first** — `async def synthesize(...)` core، sync wrapper لەسەر
5. **Strict typing** — `mypy --strict` بۆ هەموو public API
6. **Caching سێ ئاست:** L1 (in-mem LRU بۆ G2P per-word) → L2 (disk بۆ phoneme sequences per-sentence hash) → L3 (disk بۆ audio per-input+voice+params hash)
7. **Observability:** `structlog` + OpenTelemetry traces + Prometheus metrics لە ڕۆژی ١

---

## 6. Quality, Evaluation & Benchmarks

| Suite | What | Tooling |
|-------|------|---------|
| Normalizer golden | 500+ in→out pairs | pytest + YAML |
| G2P accuracy | PER vs CMUdict held-out + LibriSpeech words | custom |
| Homograph | Wikipedia Homograph eval | custom |
| Prosody alignment | breaks vs LibriTTS-R gold | F1 |
| Acoustic objective | MCD، F0 RMSE، WER (Whisper-large-v3) | `whisper`, `pymcd` |
| Acoustic subjective | MOS via Toloka/Prolific or internal panel | rating UI |
| A/B harness | side-by-side blind voting | Gradio |
| Latency / RTF | first-chunk + total | locust |

**Datasets:** LJSpeech، LibriTTS / LibriTTS-R، VCTK، Blizzard Challenge، **custom edge-case suite** (tongue twisters، code-switched، heavy abbrev، long URLs).

**CI:** every PR → unit tests + 50-utt regression suite (objective only). Weekly → full benchmark + MOS panel. Auto-published to `docs/benchmarks.md`.

---

## 7. Performance & Optimization

| Metric | CPU 1-thread | GPU (RTX 3060) |
|--------|-------------|----------------|
| RTF (VITS) | ≤ 0.3 | ≤ 0.02 |
| RTF (StyleTTS2) | ≤ 0.5 | ≤ 0.05 |
| Time-to-first-audio | ≤ 400ms | ≤ 150ms |
| Memory loaded | ≤ 1.5 GB | ≤ 3 GB VRAM |

**Optimization stack:** ONNX export + ONNX Runtime (CUDA/CoreML/DirectML/CPU) → Quantization (INT8 G2P+prosody، FP16 acoustic+vocoder) → `torch.compile` alternative path → dynamic batcher (20ms window) → KV cache (XTTS) → mixed precision → CPU OMP_NUM_THREADS tuning، AVX2/AVX-512 → mobile-ready (CoreML + TFLite stretch).

---

## 8. Deployment

### REST API (FastAPI)
```
POST /v1/synthesize             # full audio
POST /v1/synthesize/stream      # SSE / chunked
WS   /v1/stream                 # bidirectional
GET  /v1/voices
POST /v1/voices/clone           # upload reference → voice_id
GET  /v1/health
GET  /metrics                   # Prometheus
```

**Containerization:** multi-stage Dockerfile (CUDA + CPU-only variants). `docker-compose` بۆ local dev (api + redis + prometheus + grafana).

**Distribution:** PyPI (`pip install eng-tts`) · GHCR/Docker Hub · Hugging Face Space (Gradio) · HF model cards per voice · optional PyInstaller binary.

**Production:** rate limiting per API key، JWT/API-key auth، PII-safe logs، model hot-reload، graceful shutdown، liveness vs readiness healthchecks.

---

## 9. Roadmap — 6 Phases

### 🥇 Phase 1 — Foundation NLP (priority #1)
**Effort: XL · longest phase**

Deliverables: legacy موڤ بۆ `legacy/` · `pyproject.toml` + `src/eng_tts/` skeleton · `LinguisticFrame` + ABCs · SSML parser (full subset §3.1) · Text normalizer (هەموو ١٨ category + 500+ golden tests) · pySBD segmentation · spaCy linguistic · Logging+config+cache infra · CLI · Wrap legacy pyttsx3 وەک temporary `Acoustic` plugin بۆ end-to-end کارکردن.

**Exit:** normalizer 95%+ golden، test coverage 80%+ NLP، new pipeline ≥ legacy quality on 20 samples.

### 🥈 Phase 2 — G2P + Prosody (Effort: L)
CMUdict loader · Hybrid G2P (lookup + DeepPhonemizer) · Homograph disambiguator (rules + DistilBERT) · Stress + syllabification · Phrase break predictor · Pitch/duration/energy predictors · ARPABET↔IPA · benchmark script.

**Exit:** PER ≥ 98%، homograph ≥ 95%.

### 🥉 Phase 3 — Acoustic Integration (Effort: XL)
Coqui TTS (or direct PyTorch) → VITS · StyleTTS 2 · HiFi-GAN · speaker embedding · streaming chunker + crossfade · replace pyttsx3 backend · Gradio A/B demo.

**Exit:** MOS ≥ 4.0 panel، RTF ≤ 0.3 CPU.

### Phase 4 — Voice Quality & Cloning (Effort: L)
XTTS-v2 cloning · BigVGAN · style/emotion conditioning · EBU R128 loudness · denoise · fine-tuning recipe + docs · 4 polished built-in voices.

**Exit:** clone from 6s → MOS ≥ 3.8.

### Phase 5 — API + Deployment (Effort: M)
FastAPI REST + WebSocket · streaming · auth + rate-limit · Docker (CPU+CUDA) · Gradio public demo · ONNX exports + INT8/FP16 · Prometheus + Grafana · PyPI alpha.

**Exit:** TTFA ≤ 200ms streaming، 100 concurrent users single-GPU.

### Phase 6 — Polish & Benchmark (Effort: M)
Full benchmark suite + public results · MOS panel · mkdocs-material site · examples + tutorials · v1.0.0 release · comparison report vs ElevenLabs/OpenAI/Coqui.

**Exit:** هەموو KPIـەکانی §1 وەرگیراون.

---

## 10. Dependencies & Tooling

### Runtime — Core
```
python = ">=3.10,<3.13"

# NLP
spacy ^3.7  · spacy-transformers · pysbd · regex · inflect · num2words
nemo-text-processing      # WFST normalization
phonemizer                # espeak-ng wrapper
g2p-en · deep-phonemizer · syllapy

# ML
torch >=2.1 · transformers >=4.40 · onnxruntime · onnxruntime-gpu (extra)
sentencepiece · accelerate

# TTS
TTS                       # Coqui (VITS, XTTS-v2)
# styletts2 via fork

# Audio
librosa · soundfile · pyloudnorm · noisereduce (optional)

# Lang ID
fasttext-wheel

# Infra
pydantic ^2.5 · pydantic-settings · structlog · typer
fastapi · uvicorn[standard] · websockets · gradio
prometheus-client · opentelemetry-api · opentelemetry-sdk
redis (optional cache)
```

### Dev
```
pytest · pytest-asyncio · pytest-cov · hypothesis (property-based)
mypy · ruff · black · pre-commit · mkdocs-material · locust
```

### Extras
- `[clone]` → XTTS-v2
- `[premium]` → StyleTTS2 + BigVGAN
- `[gpu]` → onnxruntime-gpu، torch+CUDA
- `[api]` → FastAPI stack
- `[ui]` → Gradio
- `[full]` → هەموو

---

## 11. Risk Assessment

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| 1 | XTTS-v2 license (Coqui Public — non-commercial) | High | High | VITS وەک commercial-safe default; explore Parler-TTS (Apache-2.0) |
| 2 | `nemo_text_processing` heavy deps | Med | Med | Optional; pure-Python fallback |
| 3 | espeak-ng binary required | Med | Low | Document install; DeepPhonemizer-only path |
| 4 | GPU not available | High | Low | Optimize CPU; ONNX INT8 |
| 5 | Voice cloning misuse (deepfake/fraud) | Med | High | Audio watermarking; ToS; consent file requirement |
| 6 | XTTS long-form drift (>250 chars) | High | Med | Mandatory sentence chunking; speaker embedding reuse |
| 7 | Memory pressure (3 acoustic models) | Med | Med | Lazy load; LRU model cache |
| 8 | Benchmark dataset staleness | Low | Low | Maintain custom evolving suite |
| 9 | Scope creep (every NLP feature) | High | High | Strict phase gates; ship Phase 1 narrow but solid |
| 10 | Coqui TTS upstream breaking changes | Med | Med | Pin versions; abstraction absorbs |
| 11 | PII in logs | Med | High | Configurable redaction |
| 12 | Model download size (gigs) | High | Low | Tiered downloads; resume; mirrors |

---

## 12. Success Metrics

### Technical KPIs
| KPI | Baseline (legacy) | Target (v1.0) |
|-----|------------------|---------------|
| MOS | ~2.8 (pyttsx3) | **≥ 4.3** |
| WER on synth (Whisper-large-v3) | ~15% | **≤ 2%** |
| Phoneme accuracy | n/a | **≥ 98%** |
| Homograph accuracy | n/a | **≥ 95%** |
| Phrase break F1 | n/a | **≥ 0.85** |
| Normalizer golden | n/a | **≥ 99%** |
| RTF VITS CPU 1-thread | ~0.5 | **≤ 0.3** |
| RTF VITS GPU | n/a | **≤ 0.02** |
| TTFA (stream) | n/a | **≤ 200ms GPU** |
| Test coverage | ~0% | **≥ 85%** |
| Type coverage (mypy strict) | 0% | **≥ 95%** |

### Qualitative
- ✅ First-time dev: `pip install` → speech in **< 60 seconds**
- ✅ Audio of *"Dr. Smith earned $1,250.50 on 12/25/2024 — that's a 25% raise!"* indistinguishable from human
- ✅ Blind A/B vs ElevenLabs Turbo: ≥ 35% preference (ambitious بەڵام دەکرێت بۆ VITS+ tier)
- ✅ Documentation rated "excellent" by 5 external reviewers
- ✅ Featured in ≥ 1 open-source TTS comparison post

---

## 13. Concrete Next Steps — Phase 1

### Step 1 — Repo cleanup & scaffolding
- [ ] Move all current `english/*.py` → `legacy/` (keep working as reference)
- [ ] Add `pyproject.toml` (Poetry/hatch) with extras
- [ ] Create `src/eng_tts/` skeleton (هەموو subdirsـی §5 + empty `__init__.py`)
- [ ] `pre-commit` (ruff + black + mypy)
- [ ] `pytest` + coverage + GitHub Actions CI
- [ ] `.env.example` + Pydantic Settings
- [ ] `structlog` setup
- [ ] `docs/architecture.md` (one-pager from §2 + §5)

### Step 2 — Core abstractions
- [ ] `LinguisticFrame` dataclass
- [ ] `core/interfaces.py`: `INormalizer`, `ISegmenter`, `IG2P`, `IProsody`, `IAcoustic`, `IVocoder`
- [ ] `core/registry.py` (decorator-based plugin)
- [ ] `core/cache.py` (LRU + diskcache)
- [ ] `core/exceptions.py` (typed)
- [ ] `core/pipeline.py` skeleton
- [ ] Unit tests for above

### Step 3 — SSML parser
- [ ] AST nodes (`ssml/ast.py`)
- [ ] `ssml/parser.py` (subset §3.1)
- [ ] `ssml/walker.py` (yield text spans + attrs)
- [ ] 30+ unit tests with real SSML
- [ ] Plain-text auto-wrap

### Step 4 — Text normalizer (the big one)
- [ ] Lexicons (`abbreviations.json`, `acronyms.json`, `units.json`, `currencies.json`)
- [ ] `RuleBasedNormalizer` بۆ هەموو ١٨ category §3.2
- [ ] **Golden suite** `tests/golden/normalizer_cases.yaml` (500+ cases per category)
- [ ] `nemo_text_processing` integration (feature flag)
- [ ] `hypothesis` property tests بۆ number ranges
- [ ] Benchmark on 10k Wikipedia sentences (no crashes، < 5ms/sentence avg)

### Step 5 — Linguistic analyzer
- [ ] spaCy lazy loader (`en_core_web_trf`)
- [ ] Sentence segmenter (`pysbd` first، spaCy fallback)
- [ ] Tokens + POS + NER + dep wrapper → typed `Token` objects
- [ ] Edge-case tests (quotes، abbrevs mid-sentence، lists)

### Step 6 — Pipeline glue + temporary backend
- [ ] Wire stages: SSML → normalize → segment → linguistic → (G2P stub) → temporary acoustic
- [ ] Wrap legacy pyttsx3 وەک `LegacyAcousticPlugin` → end-to-end audio کاردەکات
- [ ] Typer CLI: `eng-tts say "Hello"`, `eng-tts say --ssml file.xml`, `eng-tts list-voices`, `eng-tts benchmark`
- [ ] Integration test on 20 reference inputs

### Step 7 — Documentation
- [ ] `README.md` rewrite (quickstart + diagram + status badges)
- [ ] `docs/nlp_pipeline.md` (per-stage + examples)
- [ ] `docs/ssml_reference.md`
- [ ] 3 Jupyter notebooks (explore_normalizer، ssml_demo، pipeline_walkthrough)

### Phase 1 Exit Criteria (gate بۆ Phase 2)
- [ ] All 7 steps complete
- [ ] CI green
- [ ] Coverage ≥ 80% on `nlp/`, `ssml/`, `core/`
- [ ] Demo input *"Dr. Smith earned $1,250.50 on 12/25/2024 — visit https://example.com or call +1-555-0100."* → هەموو NSWـیشتانی وەکو پێویست دەخوێنرێت (audio هێشتا legacy-quality، ئیشکالی نییە)
- [ ] Architecture review: کەسێکی تر `docs/architecture.md` دەخوێنێتەوە و دەتوانێت لە کۆددا گەڕانەوە بکات

---

## 📊 ئاماری کۆتایی

| بەش | ژمارە |
|-----|-------|
| Phases | **6** |
| NLP Stages | **12** |
| Acoustic tiers | **3** (fast / premium / clone) |
| API endpoints | **7** |
| File modules | **~50** |
| Lexicons | **4+** |
| Test categories | **3** (unit / integration / golden) |
| Risks tracked | **12** |
| KPIs | **11 quantitative + 5 qualitative** |
| Phase 1 sub-tasks | **~50 across 7 steps** |

---

> **یەکەم کاری دوای ئەم پلانە:** Step 1 §13 — cleanup + scaffolding. **هیچ کۆد** پێش ئەوەی package skeleton + CI سەتاپ نەکرابێت.
>
> **یاسای زێڕین:** هەر فیچەرێک کە لە golden test suite ـی Phase 1 تێپەڕ نەبێت → **نابێت بچێتە Phase 2**. کوالێتی لەسەر سپێد.
