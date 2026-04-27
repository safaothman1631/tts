"""Bootstrap a starter pack of public-domain reference clips.

Reads a JSON config of {codename: {url, start, duration, ...}} entries,
downloads each source file, slices the requested window with ffmpeg,
and feeds it into ``scripts/ingest_reference_voice.py``.

Config format (see ``scripts/librivox_starter_pack.example.json``):

    {
      "clips": [
        {
          "codename": "Oracle",
          "url": "https://archive.org/download/.../file.mp3",
          "start": 12.0,
          "duration": 9.0,
          "license": "PD",
          "source_title": "Heart of Darkness, Ch.1 (LibriVox)",
          "source_url": "https://librivox.org/heart-of-darkness-by-joseph-conrad/",
          "language": "en"
        }
      ]
    }

Usage:
    python scripts/bootstrap_reference_pack.py --config scripts/librivox_starter_pack.json

Requires ``ffmpeg`` on PATH for slicing.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import requests

REPO = Path(__file__).resolve().parent.parent
INGEST = REPO / "scripts" / "ingest_reference_voice.py"


def _download(url: str, dest: Path) -> None:
    print(f"  download {url}")
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with dest.open("wb") as fh:
            for chunk in r.iter_content(chunk_size=1 << 16):
                fh.write(chunk)


def _slice(src: Path, dst: Path, start: float, duration: float) -> None:
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-ss", f"{start}", "-t", f"{duration}",
        "-i", str(src),
        "-ac", "1", "-ar", "24000",
        str(dst),
    ]
    subprocess.run(cmd, check=True)


def _ingest(clip: dict, wav: Path) -> int:
    cmd = [
        sys.executable, str(INGEST),
        "--codename", clip["codename"],
        "--input", str(wav),
        "--license", clip["license"],
        "--source-url", clip.get("source_url", ""),
        "--source-title", clip.get("source_title", ""),
        "--language", clip.get("language", "en"),
    ]
    if clip.get("attribution"):
        cmd += ["--attribution", clip["attribution"]]
    if clip.get("force"):
        cmd.append("--force")
    print("  $", " ".join(c if " " not in c else f'"{c}"' for c in cmd))
    return subprocess.call(cmd)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--only", default="", help="Comma-separated codename allow-list.")
    args = parser.parse_args()

    if not shutil.which("ffmpeg"):
        print("ERROR: ffmpeg not on PATH (needed to slice clips).", file=sys.stderr)
        return 2

    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    only = {s.strip() for s in args.only.split(",") if s.strip()}
    clips = cfg.get("clips", [])
    if only:
        clips = [c for c in clips if c["codename"] in only]
    print(f"[bootstrap] {len(clips)} clips to ingest from {args.config.name}")

    failures: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for i, clip in enumerate(clips, 1):
            cn = clip["codename"]
            print(f"\n--- [{i}/{len(clips)}] {cn} ---")
            try:
                ext = Path(urlparse(clip["url"]).path).suffix or ".bin"
                src = tmp / f"{cn}_src{ext}"
                _download(clip["url"], src)
                sliced = tmp / f"{cn}_slice.wav"
                _slice(src, sliced, float(clip["start"]), float(clip["duration"]))
                rc = _ingest(clip, sliced)
                if rc != 0:
                    failures.append(f"{cn} (ingest rc={rc})")
            except Exception as e:
                print(f"  ERR {cn}: {e}")
                failures.append(f"{cn} ({e})")

    print()
    print(f"Done. {len(clips)-len(failures)}/{len(clips)} succeeded.")
    if failures:
        print("Failures:")
        for f in failures:
            print(f"  - {f}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
