# eng-tts — World-class English Text-to-Speech

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/status-alpha-orange)](#)

`eng-tts` is a modular, plugin-driven, English-first TTS engine that
combines a research-grade NLP front-end with state-of-the-art neural
acoustic backends (VITS, XTTS-v2, StyleTTS2) and a fast offline fallback
(pyttsx3).

```text
┌──────────┐  ┌────────────┐  ┌──────────┐  ┌──────────────┐  ┌────────────┐
│ SSML/text│→ │ Normalizer │→ │  G2P     │→ │ Acoustic     │→ │ Loudness/  │ → wav
│          │  │ + segment  │  │ + Prosody│  │ (VITS/XTTS…) │  │ resample   │
└──────────┘  └────────────┘  └──────────┘  └──────────────┘  └────────────┘
```

## Highlights

- **18+ NSW categories**: URL, email, phone, time, date, currency, %,
  year, decade, ordinal, fraction, decimal, range, math, units…
- **Hybrid G2P**: user overrides → CMUDict → neural LSTM (g2p-en)
- **30+ homographs** with POS-aware disambiguation
- **Rule-based prosody** (5-level breaks, pitch & duration contour)
- **SSML 1.1** subset (`<break>`, `<prosody>`, `<emphasis>`,
  `<say-as>`, `<phoneme>`, `<sub>`, `<voice>`, `<p>`, `<s>`)
- **4 acoustic tiers**: `fast` (VITS) · `premium` (StyleTTS2) ·
  `clone` (XTTS-v2 voice cloning) · `legacy` (pyttsx3 — works offline,
  no GPU)
- **Plugin registry** — swap any stage with one decorator
- **CLI**, **REST API**, **WebSocket streaming**, **Gradio UI**
- **EBU R128 loudness normalization**
- **Diskcache** for repeated synthesis

## Install

```bash
# Minimal (legacy backend, NLP only)
pip install -e .

# Full feature set
pip install -e ".[full]"

# Pick what you need
pip install -e ".[nlp,acoustic,api]"
```

System packages: `espeak-ng`, `libsndfile1`, `ffmpeg`. On Windows the
legacy backend uses SAPI5 — no extra system deps needed.

Then download models (one-time, optional):

```bash
python scripts/download_models.py
```

## Quickstart

### Python API

```python
from eng_tts import synthesize

chunk = synthesize(
    "Dr. Smith earned $1,250.50 on 12/25/2024.",
    voice="en_us_neutral_f",
    output_path="hello.wav",
)
print(chunk.metadata)
```

### CLI

```bash
eng-tts say "Hello, world!" --out hello.wav
eng-tts say "<speak>Hi <break time='400ms'/> world.</speak>" --tier fast
eng-tts say "I am cloning a voice." --tier clone --clone ref.wav -o cloned.wav
eng-tts analyze "Dr. Smith earned $1,250 today."
eng-tts normalize "She got 95% on 12/25/2024."
eng-tts voices
eng-tts plugins
eng-tts benchmark --n 10
eng-tts serve --port 8000
eng-tts ui --port 7860
```

### HTTP API

```bash
curl -X POST http://127.0.0.1:8000/v1/synthesize.wav \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello world","voice":"en_us_neutral_f"}' \
  --output hello.wav
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full diagram.

## Configuration

All settings can be overridden via environment variables with the
`ENG_TTS_` prefix or a `.env` file. See `.env.example`.

| Var | Default | Meaning |
|-----|---------|---------|
| `ENG_TTS_ACOUSTIC_TIER` | `fast` | `fast` / `premium` / `clone` / `legacy` |
| `ENG_TTS_DEVICE` | `auto` | `auto` / `cpu` / `cuda` |
| `ENG_TTS_SAMPLE_RATE` | `22050` | Output sample rate |
| `ENG_TTS_DEFAULT_VOICE` | `en_us_neutral_f` | Default voice id |
| `ENG_TTS_LOG_LEVEL` | `INFO` | `DEBUG`/`INFO`/`WARNING`/`ERROR` |
| `ENG_TTS_API_TOKEN` | – | Bearer token for HTTP API auth |

## Docker

```bash
docker compose up --build
```

Brings up:
- `api` on `:8000`
- `prometheus` on `:9090`
- `grafana` on `:3000` (admin / admin)

## Testing

```bash
pip install -e ".[dev]"
pytest -q
```

Includes a YAML golden test set with 25+ in→out cases for the normalizer.

## Project status

Phase | Topic | Status
------|-------|-------
1 | Scaffolding & NLP front-end | ✅
2 | G2P, homograph, prosody | ✅
3 | Acoustic backends (VITS / XTTS / StyleTTS2 / legacy) | ✅
4 | API / CLI / UI | ✅
5 | Docker & deployment | ✅
6 | Docs, benchmarks, evals | ✅

See `MASTER_PLAN.md` for the original blueprint.

## Legacy

The original prototype lives under `legacy/` — preserved verbatim for
reference and migration.

## License

MIT.
# TTS + NLP Pipeline

A text-to-speech system that actually understands what it's reading before speaking it. Built with Python.

Instead of just dumping raw text into a speech engine, the text goes through several NLP stages first — abbreviation expansion, number conversion, sentiment detection, etc. The result is more natural-sounding speech.

## What it does

- Normalizes text before speaking (expands "Dr." to "Doctor", "$150,000" to "one hundred fifty thousand dollars", etc.)
- Detects the sentiment of the text and adjusts voice speed/volume accordingly
- Extracts entities (noun phrases) from input
- Supports two TTS backends: pyttsx3 (offline) and gTTS (Google, needs internet)
- Can save audio to files with metadata
- Works from command line or interactively

## How it works

The whole thing is a pipeline. Text goes in, gets processed through NLP, then gets spoken.

```
User Input → main.py → tts_pipeline.py → nlp_processor.py (6 stages) → tts_engine.py → Audio
```

More specifically:

1. **Language detection** — uses `langdetect` to figure out what language the input is
2. **Text normalization** — expands abbreviations, converts numbers to words, replaces symbols like `&` → `and`
3. **Sentence segmentation** — NLTK's `sent_tokenize` splits text into sentences (handles edge cases like "Dr." properly)
4. **Sentiment analysis** — TextBlob gives a polarity score, which gets mapped to happy/sad/angry/neutral
5. **Entity extraction** — pulls out noun phrases
6. **Pause insertion** — adds natural pauses after punctuation

The sentiment maps to voice settings:

- happy → faster speech (170 WPM), full volume
- sad → slower (130 WPM), quieter
- angry → fastest (180 WPM), loud
- neutral → default (150 WPM)

## Project structure

```
english/
├── main.py              - entry point, CLI args + interactive mode
├── tts_pipeline.py      - connects NLP processing to TTS engine
├── nlp_processor.py     - all the NLP stuff (6 processing stages)
├── tts_engine.py        - wraps pyttsx3 and gTTS
├── config.py            - all settings in one place
├── english_tts.py       - standalone English TTS (simpler interface)
├── bilingual_tts.py     - multi-language support
├── example_usage.py     - usage examples
├── quick_test.py        - quick test script
├── requirements.txt     - dependencies
└── output/              - generated audio + metadata goes here
```

## Setup

```powershell
cd c:\Users\SAFA\tts\english
pip install -r requirements.txt
```

Dependencies: `nltk`, `pyttsx3`, `gTTS`, `textblob`, `langdetect`, `num2words`, `inflect`

NLTK data gets downloaded automatically on first run.

You need Python 3.8+ and speakers/headphones. Internet only needed if you want to use the Google TTS engine.

## Usage

### From Python

```python
from tts_pipeline import TTSPipeline

pipeline = TTSPipeline()

# just speak
pipeline.process_and_speak("Hello, how are you today?")

# save to file
pipeline.process_and_save("Welcome to our system.", output_filename="welcome")
# creates output/welcome.mp3 and output/welcome_metadata.json

# batch processing
texts = ["Good morning!", "The weather is nice.", "See you later."]
pipeline.batch_process(texts, output_prefix="batch")
```

### Number handling

The NLP processor handles a bunch of number formats automatically:

```python
pipeline.process_and_speak("Dr. Smith earned $150,000 in 2023.")
# speaks: "Doctor Smith earned one hundred fifty thousand dollars in twenty twenty-three"

pipeline.process_and_speak("Sales increased by 25% in Q3.")
# speaks: "Sales increased by twenty-five percent in Q three"

pipeline.process_and_speak("She finished 1st in the 3rd race.")
# speaks: "She finished first in the third race"
```

It detects currencies, percentages, years (1900-2099), and ordinals.

### Simpler interface

If you don't need the full NLP pipeline:

```python
from english_tts import say, say_offline

say("Hello!", "hello.mp3")           # Google TTS
say_offline("Works without wifi!")    # pyttsx3
```

### Command line

```powershell
python main.py "Hello World"
python main.py "Hello" --save --output hello
python main.py --file story.txt
python main.py --engine gtts
python main.py --no-emotion
python main.py --voices
python main.py          # interactive mode
```

## Architecture details

### config.py

Central place for all settings. Every other module reads from here.

```python
TTS_ENGINE = "pyttsx3"
VOICE_RATE = 150
VOICE_VOLUME = 0.9
VOICE_GENDER = "female"

ABBREVIATIONS = {
    "Dr.": "Doctor",
    "Mr.": "Mister",
    "Mrs.": "Misses",
    "Prof.": "Professor",
    "e.g.": "for example",
    "i.e.": "that is",
    # ...
}

EMOTION_SETTINGS = {
    "happy":  {"rate": 170, "volume": 1.0, "pitch": 1.2},
    "sad":    {"rate": 130, "volume": 0.7, "pitch": 0.8},
    "angry":  {"rate": 180, "volume": 1.0, "pitch": 1.3},
    "neutral":{"rate": 150, "volume": 0.9, "pitch": 1.0},
}
```

Having one config file means I don't have magic numbers scattered everywhere. Want to change the speech rate? One place to edit.

### nlp_processor.py

This is where most of the complexity lives. The `NLPProcessor` class has a `process_text()` method that runs all 6 stages and returns the cleaned text plus a metadata dict.

The number conversion was probably the trickiest part. I had to handle several cases separately:

- `$150,000` → currency (uses `num2words` with `to='currency'`)
- `25%` → percentage (num2words + " percent")
- `2023` → year (num2words with `to='year'`)
- `3rd` → ordinal (num2words with `to='ordinal'`)
- `42` → regular (num2words straight)

Each one uses a regex to detect the pattern and a lambda to do the conversion.

Sentiment analysis uses TextBlob's polarity score:
- Above 0.3 → happy
- Below -0.3 → sad
- In between → neutral

### tts_engine.py

Wraps two backends behind the same interface.

pyttsx3 is offline, instant, supports emotion (rate/volume adjustment), outputs .wav files. Uses whatever voices Windows has installed (usually Microsoft David and Zira).

gTTS needs internet, has a small delay (1-3 seconds), sounds more natural, outputs .mp3 files. No emotion control though since you can't adjust Google's voice parameters.

### tts_pipeline.py

The glue. Creates an `NLPProcessor` and a `TTSEngine`, then provides methods like `process_and_speak()` that run the NLP pipeline and feed the result to the TTS engine.

Also handles saving metadata as JSON alongside audio files — useful for debugging or reviewing what the NLP picked up.

## Troubleshooting

**No audio?** Check your system volume and audio device.

**ModuleNotFoundError?** Run `pip install -r requirements.txt`.

**NLTK data error?** Run `python -c "import nltk; nltk.download('punkt')"`.

**pyttsx3 has no voice?** Check Windows Settings → Time & Language → Speech.

**gTTS timing out?** No internet. Use `--engine pyttsx3` instead.

**Wrong emotion detected?** Sentiment analysis isn't perfect. Use `--no-emotion` to disable it.

## Dependencies

- **nltk** — tokenization, sentence splitting
- **pyttsx3** — offline TTS (Windows SAPI)
- **gTTS** — Google Text-to-Speech
- **textblob** — sentiment analysis, noun phrase extraction
- **langdetect** — language detection
- **num2words** — converting numbers to words
- **inflect** — text inflection
