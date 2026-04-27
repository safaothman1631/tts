"""Download Piper TTS voice models from rhasspy/piper-voices on Hugging Face.

Usage:
    python scripts/download_piper_models.py
    python scripts/download_piper_models.py en_US-lessac-medium en_GB-alan-medium

The default voice (``en_US-lessac-medium``) is ~63 MB and runs entirely on CPU.
Models are saved into ``<repo>/models/piper/`` (override with ENG_TTS_PIPER_DIR).
"""
from __future__ import annotations

import os
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIR = Path(os.environ.get("ENG_TTS_PIPER_DIR", REPO_ROOT / "models" / "piper"))
HF_BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main"

# voice_key → relative path on Hugging Face
VOICE_PATHS: dict[str, str] = {
    "en_US-lessac-medium": "en/en_US/lessac/medium",
    "en_US-amy-medium": "en/en_US/amy/medium",
    "en_US-ryan-medium": "en/en_US/ryan/medium",
    "en_GB-alan-medium": "en/en_GB/alan/medium",
}


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  ✓ {dest.name} (already present)")
        return
    print(f"  ↓ {url}")
    with urllib.request.urlopen(url) as r, open(dest, "wb") as f:
        total = int(r.headers.get("Content-Length", 0))
        chunk = 1 << 20
        downloaded = 0
        while True:
            block = r.read(chunk)
            if not block:
                break
            f.write(block)
            downloaded += len(block)
            if total:
                pct = downloaded * 100 // total
                print(f"\r    {downloaded // (1<<20)} / {total // (1<<20)} MB ({pct}%)",
                      end="", flush=True)
        print()


def fetch_voice(key: str, base_dir: Path) -> None:
    if key not in VOICE_PATHS:
        print(f"[piper] Unknown voice '{key}'. Known: {list(VOICE_PATHS)}")
        sys.exit(2)
    rel = VOICE_PATHS[key]
    print(f"[piper] Downloading {key}")
    download(f"{HF_BASE}/{rel}/{key}.onnx", base_dir / f"{key}.onnx")
    download(f"{HF_BASE}/{rel}/{key}.onnx.json", base_dir / f"{key}.onnx.json")


def main() -> int:
    voices = sys.argv[1:] or ["en_US-lessac-medium"]
    base_dir = DEFAULT_DIR
    print(f"[piper] Target directory: {base_dir}")
    for v in voices:
        fetch_voice(v, base_dir)
    print("[piper] Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
