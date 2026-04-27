"""Speaker embedding utilities for voice cloning."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ...utils.logging import get_logger

_log = get_logger(__name__)


class SpeakerEmbedder:
    """Lightweight wrapper around an embedding extractor (lazy)."""

    def __init__(self, model: str = "speechbrain/spkrec-xvect-voxceleb") -> None:
        self.model_name = model
        self._enc: Any = None

    def _load(self) -> Any:
        if self._enc is not None:
            return self._enc
        try:
            from speechbrain.inference import EncoderClassifier  # type: ignore

            self._enc = EncoderClassifier.from_hparams(source=self.model_name)
        except Exception as e:
            _log.warning("speaker_embed_unavailable", error=str(e))
            self._enc = False
        return self._enc

    def embed(self, audio_path: str | Path) -> list[float] | None:
        enc = self._load()
        if not enc:
            return None
        try:
            import torchaudio  # type: ignore

            wav, _ = torchaudio.load(str(audio_path))
            emb = enc.encode_batch(wav).squeeze().cpu().tolist()
            return emb
        except Exception:
            return None
