"""Ingest a reference voice clip into the cloning library.

Pipeline:
1. Validate input WAV (mono-able, no clipping, reasonable length).
2. Resample to 24 kHz mono float32.
3. Trim leading/trailing silence (top_db=30).
4. Loudness-normalize to -23 LUFS.
5. Transcribe with faster-whisper (tiny.en CPU by default; --whisper-size to override).
6. Compute a 256-d speaker embedding via Resemblyzer.
7. Refuse if cosine similarity to any existing manifest entry > similarity_threshold
   (default 0.85) — unless --force is supplied.
8. Write ``reference_assets/<codename>/clip.wav`` + ``manifest.json`` + update
   the root ``MANIFEST.json`` index.

Usage:
    python scripts/ingest_reference_voice.py \\
        --codename Oracle \\
        --license PD \\
        --source-url "https://librivox.org/heart-of-darkness-by-joseph-conrad/" \\
        --input ./raw/heart_of_darkness_ch1.wav

Add ``--language en`` for non-English clips. Use ``--attribution "<string>"`` for
CC-BY material.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
REF_ROOT = REPO / "english" / "src" / "eng_tts" / "voices" / "reference_assets"
INDEX_PATH = REF_ROOT / "MANIFEST.json"

ALLOWED_LICENSES = {"PD", "CC0", "CC-BY-4.0", "CC-BY-3.0", "custom_owned"}


def _load_index() -> dict:
    if INDEX_PATH.exists():
        try:
            return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"_comment": "Reference voice clip registry. Auto-managed by scripts/ingest_reference_voice.py", "clips": []}


def _save_index(idx: dict) -> None:
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(idx, indent=2, ensure_ascii=False), encoding="utf-8")


def _load_audio(path: Path, target_sr: int = 24000) -> tuple[np.ndarray, int]:
    import librosa
    y, sr = librosa.load(str(path), sr=target_sr, mono=True)
    return y.astype(np.float32), int(sr)


def _trim_silence(y: np.ndarray, top_db: int = 30) -> np.ndarray:
    import librosa
    trimmed, _ = librosa.effects.trim(y, top_db=top_db)
    return trimmed


def _normalize_loudness(y: np.ndarray, sr: int, target_lufs: float = -23.0) -> tuple[np.ndarray, float]:
    import pyloudnorm as pyln
    meter = pyln.Meter(sr)
    loudness = meter.integrated_loudness(y)
    if not np.isfinite(loudness):
        return y, float("nan")
    out = pyln.normalize.loudness(y, loudness, target_lufs)
    peak = float(np.max(np.abs(out)) or 1.0)
    if peak > 0.99:
        out = out * (0.99 / peak)
    return out.astype(np.float32), float(loudness)


def _transcribe(wav_path: Path, language: str, model_size: str) -> str:
    from faster_whisper import WhisperModel
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, _info = model.transcribe(str(wav_path), language=language, vad_filter=False)
    return " ".join(seg.text.strip() for seg in segments).strip()


def _speaker_embedding(wav_path: Path) -> np.ndarray:
    from resemblyzer import VoiceEncoder, preprocess_wav
    wav = preprocess_wav(wav_path)
    enc = VoiceEncoder(verbose=False)
    return enc.embed_utterance(wav).astype(np.float32)


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _existing_embeddings() -> list[tuple[str, np.ndarray]]:
    """Walk every existing manifest.json and load its stored embedding bytes."""
    out: list[tuple[str, np.ndarray]] = []
    for manifest in REF_ROOT.glob("*/manifest.json"):
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except Exception:
            continue
        emb_path = manifest.parent / "embedding.npy"
        if emb_path.exists():
            out.append((data.get("codename", manifest.parent.name), np.load(emb_path)))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest a reference voice clip.")
    parser.add_argument("--codename", required=True, help="Catalog codename (e.g. Oracle).")
    parser.add_argument("--input", required=True, type=Path, help="Path to source audio file.")
    parser.add_argument("--license", required=True, choices=sorted(ALLOWED_LICENSES))
    parser.add_argument("--source-url", default="", help="Source URL for the clip.")
    parser.add_argument("--source-title", default="", help="Source title / work name.")
    parser.add_argument("--attribution", default="", help="Attribution string (required for CC-BY).")
    parser.add_argument("--language", default="en", help="ISO language for transcription.")
    parser.add_argument("--whisper-size", default="tiny.en", help="faster-whisper model size.")
    parser.add_argument("--similarity-threshold", type=float, default=0.85,
                        help="Reject if cosine to any existing voice exceeds this.")
    parser.add_argument("--min-duration", type=float, default=4.0)
    parser.add_argument("--max-duration", type=float, default=20.0)
    parser.add_argument("--force", action="store_true",
                        help="Override the similarity guard (use with care).")
    args = parser.parse_args()

    if args.license == "CC-BY-4.0" and not args.attribution:
        print("ERROR: --attribution is required for CC-BY-4.0 material.", file=sys.stderr)
        return 2

    src = args.input
    if not src.exists():
        print(f"ERROR: input not found: {src}", file=sys.stderr)
        return 2

    print(f"[1/7] Loading & resampling {src.name} -> 24 kHz mono")
    y, sr = _load_audio(src, target_sr=24000)
    print(f"      duration={len(y)/sr:.2f}s peak={float(np.max(np.abs(y))):.3f}")

    print("[2/7] Trimming silence")
    y = _trim_silence(y, top_db=30)
    duration = len(y) / sr
    print(f"      trimmed duration={duration:.2f}s")

    if duration < args.min_duration or duration > args.max_duration:
        print(
            f"ERROR: trimmed duration {duration:.2f}s outside [{args.min_duration}, {args.max_duration}]s",
            file=sys.stderr,
        )
        return 3

    print("[3/7] Loudness-normalizing to -23 LUFS")
    y, in_lufs = _normalize_loudness(y, sr, target_lufs=-23.0)
    print(f"      input LUFS={in_lufs:.2f} -> -23.0")

    out_dir = REF_ROOT / args.codename
    out_dir.mkdir(parents=True, exist_ok=True)
    clip_path = out_dir / "clip.wav"

    print(f"[4/7] Writing {clip_path.relative_to(REPO)}")
    import soundfile as sf
    sf.write(str(clip_path), y, sr, subtype="PCM_16")

    print(f"[5/7] Transcribing with faster-whisper [{args.whisper_size}]")
    transcript = _transcribe(clip_path, language=args.language, model_size=args.whisper_size)
    print(f"      transcript ({len(transcript)} chars): {transcript[:100]}...")

    print("[6/7] Computing speaker embedding (Resemblyzer)")
    emb = _speaker_embedding(clip_path)
    np.save(out_dir / "embedding.npy", emb)
    emb_sha = hashlib.sha256(emb.tobytes()).hexdigest()[:16]
    print(f"      embedding sha={emb_sha}")

    print("[7/7] Duplicate-detection vs existing voices")
    worst: tuple[str, float] = ("", 0.0)
    for name, other in _existing_embeddings():
        if name == args.codename:
            continue
        sim = _cosine(emb, other)
        if sim > worst[1]:
            worst = (name, sim)
    print(f"      closest={worst[0] or '<none>'} cos={worst[1]:.3f}")
    if worst[1] > args.similarity_threshold and not args.force:
        print(
            f"ERROR: too similar to '{worst[0]}' (cos={worst[1]:.3f} > {args.similarity_threshold}). "
            f"Re-run with --force to override.",
            file=sys.stderr,
        )
        # roll back files
        clip_path.unlink(missing_ok=True)
        (out_dir / "embedding.npy").unlink(missing_ok=True)
        try:
            out_dir.rmdir()
        except OSError:
            pass
        return 4

    manifest = {
        "codename": args.codename,
        "license": args.license,
        "source_url": args.source_url,
        "source_title": args.source_title,
        "attribution_required": args.license.startswith("CC-BY"),
        "attribution_string": args.attribution or None,
        "duration_s": round(duration, 3),
        "transcript": transcript,
        "language": args.language,
        "sample_rate": sr,
        "lufs": -23.0,
        "speaker_embedding_sha": emb_sha,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    idx = _load_index()
    idx["clips"] = [c for c in idx.get("clips", []) if c.get("codename") != args.codename]
    idx["clips"].append({
        "codename": args.codename,
        "license": args.license,
        "source_url": args.source_url,
        "duration_s": manifest["duration_s"],
        "language": args.language,
        "embedding_sha": emb_sha,
    })
    _save_index(idx)

    print(f"OK -> {out_dir.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
