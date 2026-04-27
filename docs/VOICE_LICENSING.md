# Voice licensing & cloning handbook

This guide explains how the TTS Studio voice catalog stays clean, distinct,
and legally safe.

## Why we don't ship Trump / SpongeBob / etc.

Cloning a recognizable real person or copyrighted character carries
serious risk under right-of-publicity statutes, the Lanham Act
(false-endorsement), and entertainment-industry copyright. Even shipping
"sounds like X" presets is enough to trigger takedowns or lawsuits.

Instead, the catalog uses **copyright-safe archetypes** — codenames like
`Tycoon`, `SpongeYellow`, `OgreRumble`, `Oracle` that *evoke* a familiar
voice family without naming or impersonating a specific person.

## The three voice tiers

| Tier             | Example                  | source_type        | Reference WAV needed? |
|------------------|--------------------------|--------------------|-----------------------|
| Synth-only       | "Wide Receiver"          | `qwen_named`       | No — Qwen3 named speaker + style prompt only. |
| Archetype slot   | `arch-tycoon` (Tycoon)   | `qwen_named` →     | Optional. Auto-promotes to `qwen_clone` when a clip is ingested. |
|                  |                          | `qwen_clone`       |                       |
| Cloned voice     | `arch-oracle` (post-PD)  | `qwen_clone`       | Yes — `<Codename>/clip.wav` from a PD/CC0/CC-BY source. |

## License vocabulary

| `license` value | Meaning                                              | Distribution rules |
|-----------------|------------------------------------------------------|--------------------|
| `synthetic_only`| No human reference; pure Qwen3 design                | Ship freely.       |
| `pending_clone` | Archetype awaiting a reference clip                  | Ship freely (uses fallback Qwen3 speaker). |
| `PD`            | Public domain (e.g. LibriVox US-PD recordings)       | Ship freely.       |
| `CC0`           | Public-domain dedication                             | Ship freely.       |
| `CC-BY-4.0`     | Creative Commons Attribution 4.0                     | **Must include attribution string** in distributable artefacts. |
| `custom_owned`  | You own the recording or have written permission     | Ship per your contract. |

## Ingesting a reference clip

```powershell
python scripts/ingest_reference_voice.py `
    --codename Oracle `
    --license PD `
    --source-url "https://librivox.org/heart-of-darkness-by-joseph-conrad/" `
    --source-title "Heart of Darkness, Ch.1 (LibriVox)" `
    --input ./raw/oracle_take.wav
```

The CLI will:

1. Resample to 24 kHz mono and trim silence.
2. Loudness-normalize to −23 LUFS.
3. Transcribe with faster-whisper (used as the cloning prompt).
4. Compute a Resemblyzer speaker embedding.
5. Refuse if cosine similarity to any existing voice exceeds **0.85**
   (override with `--force` if intentional).
6. Write `english/src/eng_tts/voices/reference_assets/<Codename>/clip.wav`
   plus a `manifest.json` and the speaker embedding.
7. Append the clip to the root `MANIFEST.json`.

## Bulk bootstrap from LibriVox / Internet Archive

Edit `scripts/librivox_starter_pack.example.json` with real PD URLs and run:

```powershell
python scripts/bootstrap_reference_pack.py --config scripts/librivox_starter_pack.json
```

This downloads each source file, slices the requested window with `ffmpeg`,
and feeds it through the ingest CLI. Requires `ffmpeg` on PATH.

## Acceptance gates

After ingesting clips, render probes and audit distinctness:

```powershell
# 1. Render the standard probe sentence with every voice
python scripts/render_voice_probes.py --tier qwen3

# 2. Open the HTML grid for human listening
start output/probes/index.html

# 3. Run the automatic distinctness audit
python scripts/audit_voice_distinctness.py
```

The audit fails if any pair of voices exceeds 0.92 cosine similarity, or
if the median pairwise similarity exceeds 0.55. Use `--strict` for the
tighter gates (0.85 / 0.45).

## Distribution checklist

Before publishing a build:

```powershell
python scripts/build_licenses_md.py        # regenerates LICENSES.md
```

`LICENSES.md` aggregates every CC-BY attribution string. Bundle it with
your release (e.g. as part of the installer or app-store listing) so
attribution duties are satisfied.

## Catalog conventions

* IDs of archetype slots are prefixed `arch-` (e.g. `arch-tycoon`).
* Reference paths use `<Codename>/clip.wav` (PascalCase folder).
* Each ingested clip gets `<Codename>/manifest.json` plus
  `<Codename>/embedding.npy` for fast duplicate detection.
* The catalog is the source of truth — the backend automatically detects
  whether a reference clip exists and switches `source_type` from
  `qwen_named` to `qwen_clone` per request.
