# Voice cloning

`eng-tts` supports zero-shot voice cloning via XTTS-v2.

## Quick start

```python
from eng_tts import TTSPipeline
from eng_tts.config import get_settings

s = get_settings()
s.acoustic_tier = "clone"
pipe = TTSPipeline(settings=s)

chunk = pipe.synthesize(
    "Hello, this is a cloned voice!",
    speaker_wav="path/to/reference.wav",   # 6–20s of clean speech
    output_path="cloned.wav",
)
```

CLI:

```bash
eng-tts say "Hello world" --tier clone --clone reference.wav --out cloned.wav
```

## Reference recording tips
- 6–20 seconds is enough; longer is *not* always better.
- Mono, 16–24 kHz, no music or background noise.
- One speaker only.
- Natural prosody — avoid monotone reading.

## Ethics
**You must have explicit consent** to clone someone's voice.
The maintainers do not condone deepfake misuse.
