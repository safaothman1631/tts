"""Pydantic schemas for the HTTP API."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Plain text or SSML to inspect")


class NlpToken(BaseModel):
    text: str
    type: str
    phonemes_arpabet: list[str] = Field(default_factory=list)
    phonemes_ipa: str | None = None
    stress: list[int] = Field(default_factory=list)


class NlpProsody(BaseModel):
    pitch_curve: list[float] = Field(default_factory=list)
    energy_curve: list[float] = Field(default_factory=list)
    duration_ms: float = 0.0


class AnalyzeResponse(BaseModel):
    tokens: list[NlpToken]
    prosody: NlpProsody | None = None
    ssml_ast: dict | None = None


class SynthesizeRequest(BaseModel):
    text: str = Field(..., description="Plain text or SSML")
    voice: Optional[str] = None
    tier: Optional[str] = Field(None, description="qwen3|piper|fast|premium|clone|legacy")
    speed: float = 1.0
    pitch_shift: float = 0.0
    volume: float = Field(1.0, ge=0.0, le=2.0)
    style_prompt: Optional[str] = None
    speaker_wav: Optional[str] = None
    format: str = Field("wav", description="wav|raw")
    ssml: bool = Field(False, description="Treat input text as SSML markup")
    language: Optional[str] = Field(None, description="Language hint (en|ckb|ar|tr|zh|ja|...)")
    qwen_speaker: Optional[str] = Field(None, description="Qwen3 named preset (e.g. Ryan, Aiden)")
    emotion: Optional[str] = Field(None, description="Emotion tag (neutral|happy|sad|angry|excited|calm)")
    voice_character: Optional[str] = Field(
        None,
        description="Global voice character id (overrides voice/qwen_speaker/style/language/emotion).",
    )


class SynthesizeResponse(BaseModel):
    sample_rate: int
    duration_seconds: float
    voice: Optional[str]
    cached: bool = False
    audio_base64: Optional[str] = None


class SynthesizeSegment(BaseModel):
    text: str = Field(..., min_length=1)
    voice: Optional[str] = None
    tier: Optional[str] = Field(None, description="qwen3|piper|fast|premium|clone|legacy")
    speed: float = 1.0
    pitch_shift: float = 0.0
    volume: float = Field(1.0, ge=0.0, le=2.0)
    style_prompt: Optional[str] = None
    pause_after_ms: int = Field(120, ge=0, le=5000)
    language: Optional[str] = None
    qwen_speaker: Optional[str] = None
    emotion: Optional[str] = None
    voice_character: Optional[str] = None


class SynthesizeSegmentsRequest(BaseModel):
    segments: list[SynthesizeSegment] = Field(..., min_length=1, max_length=64)
    format: str = Field("wav", description="wav")


class VoiceDescriptor(BaseModel):
    id: str
    name: str
    gender: str = "neutral"
    accent: str = ""
    backend: str = "piper"
    model: str = ""
    language: str = "en"
    description: str | None = None
    preview_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    custom: bool = False
    created_at: str | None = None
    supports_clone: bool = False
    supports_style_prompt: bool = False


class HealthResponse(BaseModel):
    status: str
    version: str
    device: str


class CapabilitiesResponse(BaseModel):
    languages: list[str]
    formats: list[str]
    tiers: list[str]
    controls: list[str]
    endpoints: list[str]
    voice_clone: bool
    streaming: bool
    custom_voice_persistence: bool
    qwen_speakers: list[str] = Field(default_factory=list)
    emotions: list[str] = Field(default_factory=list)
    style_presets: list[dict] = Field(default_factory=list)
    voice_characters_total: int = 0
