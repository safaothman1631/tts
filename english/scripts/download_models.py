"""Pre-download model weights so the first run is offline-friendly."""
from __future__ import annotations

import sys


def main() -> int:
    print("[eng-tts] Downloading models...")

    # Coqui VITS
    try:
        from TTS.api import TTS  # type: ignore

        print("  - VITS (en/ljspeech) ...")
        TTS(model_name="tts_models/en/ljspeech/vits", progress_bar=True)
        print("  - XTTS-v2 (multilingual) ...")
        TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True)
    except Exception as e:
        print(f"  ! Coqui TTS unavailable: {e}")

    # spaCy model
    try:
        import spacy  # type: ignore

        if not spacy.util.is_package("en_core_web_sm"):
            print("  - spaCy en_core_web_sm ...")
            from spacy.cli import download as sp_download  # type: ignore

            sp_download("en_core_web_sm")
    except Exception as e:
        print(f"  ! spaCy model setup skipped: {e}")

    # NLTK CMUDict (fallback for g2p_en)
    try:
        import nltk  # type: ignore

        for pkg in ("cmudict", "averaged_perceptron_tagger"):
            try:
                nltk.download(pkg, quiet=True)
            except Exception:
                pass
    except Exception:
        pass

    print("[eng-tts] Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
