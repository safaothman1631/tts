"""Pydantic-Settings based configuration."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global runtime configuration. Loaded from env vars, .env, defaults."""

    model_config = SettingsConfigDict(
        env_prefix="ENG_TTS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Paths
    cache_dir: Path = Field(default=Path("./.cache"))
    model_dir: Path = Field(default=Path("./models"))
    output_dir: Path = Field(default=Path("./output"))

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # Device
    device: Literal["auto", "cpu", "cuda"] = "auto"

    # Defaults
    default_voice: str = "piper_en_us_lessac_medium"
    acoustic_tier: Literal["fast", "premium", "clone", "legacy", "piper", "qwen3"] = "piper"
    sample_rate: int = 22050

    # Feature flags
    enable_nemo: bool = False
    enable_neural_g2p: bool = True
    enable_homograph_neural: bool = False
    enable_sentiment: bool = True
    enable_codeswitch: bool = False
    enable_loudness_norm: bool = True

    # Pipeline
    spacy_model: str = "en_core_web_sm"   # users can upgrade to en_core_web_trf
    sentence_segmenter: Literal["pysbd", "spacy", "regex"] = "pysbd"

    # Performance
    max_chunk_chars: int = 240
    cache_audio: bool = True

    def resolved_device(self) -> str:
        if self.device != "auto":
            return self.device
        try:
            import torch  # type: ignore

            if torch.cuda.is_available():
                return "cuda"
        except ImportError:
            pass
        return "cpu"

    def ensure_dirs(self) -> None:
        for d in (self.cache_dir, self.model_dir, self.output_dir):
            d.mkdir(parents=True, exist_ok=True)


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.ensure_dirs()
    return _settings


def reset_settings() -> None:
    """Test helper."""
    global _settings
    _settings = None
