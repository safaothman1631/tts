"""Download Qwen3 TTS model snapshots from Hugging Face.

Usage:
    python scripts/download_qwen3_tts.py
    python scripts/download_qwen3_tts.py Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice

Environment:
- HF_TOKEN / HUGGING_FACE_HUB_TOKEN: token for gated/private access
- ENG_TTS_QWEN3_CACHE_DIR: local cache/output dir (default: ./models/qwen3)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

DEFAULT_MODEL = "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"


def main() -> int:
    model_id = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL
    out_dir = Path(os.environ.get("ENG_TTS_QWEN3_CACHE_DIR", "./models/qwen3")).resolve()
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")

    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("[qwen3] missing dependency: huggingface-hub. Install eng-tts[qwen3].")
        return 2

    print(f"[qwen3] downloading model: {model_id}")
    print(f"[qwen3] target dir: {out_dir}")

    try:
        path = snapshot_download(
            repo_id=model_id,
            local_dir=str(out_dir / model_id.replace('/', '--')),
            local_dir_use_symlinks=False,
            token=token,
        )
    except Exception as e:
        print(f"[qwen3] download failed: {e}")
        print("[qwen3] If model access is restricted, set HF_TOKEN and retry.")
        return 1

    print(f"[qwen3] done: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
