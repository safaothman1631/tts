# Voice Reference Assets

Drop short reference WAV clips here to enable **voice cloning** for any
character whose `reference_audio` field points to a filename in this
folder.

## Requirements
- **Format**: 16-bit PCM WAV, mono, 16-24 kHz
- **Length**: 8-15 seconds
- **Content**: clean speech, no background music or noise
- **License**: only public-domain (LibriVox), CC-0 (Mozilla Common Voice
  CC-0 subset), or recordings you own outright. **Never** drop celebrity
  audio you don't have rights to.

## Recommended sources

### Public Domain
- **LibriVox** (https://librivox.org/) — narrator voices, all PD
- **Project Gutenberg audio** — narrators, PD

### CC-0
- **Mozilla Common Voice** (CC-0 subset) — accent diversity
  (https://commonvoice.mozilla.org/)

## How a clip activates
1. Pick a character file in `eng_tts/config/voice_characters.py` and set
   its `reference="my_clip.wav"` and `reference_text="<exact transcript>"`
   keyword args.
2. Drop the WAV here as `my_clip.wav`.
3. Restart the backend — the catalog re-resolves on cold start. The
   character's `source_type` will switch from `qwen_named` to
   `qwen_clone` automatically.
4. If the file is missing, the character falls back to its `speaker_id`
   gracefully — no errors.

## Manifest
Track licenses in `MANIFEST.json` (one entry per WAV).
