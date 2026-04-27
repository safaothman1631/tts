"""Voice catalogue loader."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Optional

import yaml

from ..core.exceptions import VoiceNotFoundError


@dataclass
class Voice:
    id: str
    name: str
    gender: str = "neutral"
    accent: str = ""
    backend: str = "piper"
    model: str = ""
    speaker_id: Optional[str] = None
    language: str = "en"
    description: Optional[str] = None
    preview_url: Optional[str] = None
    tags: list[str] | None = None
    custom: bool = False
    speaker_wav: Optional[str] = None
    reference_text: Optional[str] = None
    created_at: Optional[str] = None


_BUILTIN_VOICES: dict[str, Voice] | None = None


def _load() -> dict[str, Voice]:
    path = Path(__file__).with_name("voices.yaml")
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {v["id"]: Voice(**v) for v in data.get("voices", [])}


def _custom_catalog_path() -> Path:
    from .settings import get_settings

    return get_settings().output_dir / "custom_voices" / "voices.json"


def _load_custom() -> dict[str, Voice]:
    path = _custom_catalog_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    voices = data.get("voices", []) if isinstance(data, dict) else []
    return {v["id"]: Voice(**v) for v in voices if isinstance(v, dict) and "id" in v}


def _write_custom(voices: dict[str, Voice]) -> None:
    path = _custom_catalog_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "voices": [
            {
                "id": voice.id,
                "name": voice.name,
                "gender": voice.gender,
                "accent": voice.accent,
                "backend": voice.backend,
                "model": voice.model,
                "speaker_id": voice.speaker_id,
                "language": voice.language,
                "description": voice.description,
                "preview_url": voice.preview_url,
                "tags": voice.tags or [],
                "custom": voice.custom,
                "speaker_wav": voice.speaker_wav,
                "reference_text": voice.reference_text,
                "created_at": voice.created_at,
            }
            for voice in voices.values()
        ]
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def all_voices() -> dict[str, Voice]:
    global _BUILTIN_VOICES
    if _BUILTIN_VOICES is None:
        _BUILTIN_VOICES = _load()
    voices = dict(_BUILTIN_VOICES)
    voices.update(_load_custom())
    return voices


def get_voice(voice_id: str) -> Voice:
    voices = all_voices()
    if voice_id not in voices:
        raise VoiceNotFoundError(
            f"Unknown voice '{voice_id}'. Available: {list(voices)}"
        )
    return voices[voice_id]


def save_custom_voice(voice: Voice) -> Voice:
    custom = _load_custom()
    custom[voice.id] = voice
    _write_custom(custom)
    return voice


def delete_custom_voice(voice_id: str) -> bool:
    custom = _load_custom()
    if voice_id not in custom:
        return False
    del custom[voice_id]
    _write_custom(custom)
    return True
