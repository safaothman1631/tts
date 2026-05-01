"""FastAPI REST surface for eng-tts."""
from __future__ import annotations

import base64
from datetime import datetime, timezone
import io
import re
import time
from typing import Iterator
from uuid import uuid4

from ..config import get_settings
from ..config.voices import Voice, delete_custom_voice, get_voice, save_custom_voice
from ..config.voice_characters import (
    all_characters,
    character_to_dict,
    filter_characters,
    get_character,
    list_categories,
    list_personas,
)
from ..core.pipeline import get_default_pipeline, warmup as pipeline_warmup
from ..nlp.g2p.arpabet_ipa import arpabet_to_ipa
from ..utils.audio import silence
from ..version import __version__
from .schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    CapabilitiesResponse,
    HealthResponse,
    NlpProsody,
    NlpToken,
    SynthesizeSegmentsRequest,
    SynthesizeRequest,
    SynthesizeResponse,
    VoiceDescriptor,
)

try:
    from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import StreamingResponse
except ImportError as e:  # pragma: no cover
    raise ImportError("Install API extras: pip install eng-tts[api]") from e

import numpy as np
import soundfile as sf

app = FastAPI(title="eng-tts", version=__version__)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:4173",
        "http://localhost:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Built-in Qwen3 named speaker presets and Studio style suggestions. Keep the
# speaker list in lockstep with the originals-only character catalog so the UI
# never exposes aliases or unsupported speakers.
QWEN3_SPEAKERS: list[str] = [c.speaker_id for c in all_characters()]
EMOTIONS: list[str] = [
    "neutral", "happy", "sad", "angry", "excited", "calm",
    "serious", "friendly", "whisper", "confident", "sarcastic", "romantic",
]
STYLE_PRESETS: list[dict[str, str]] = [
    {"id": "narration", "label": "Narration",
     "prompt": "A clear, natural narration voice with steady pacing, balanced warmth, neutral pitch and confident articulation."},
    {"id": "news", "label": "Newscaster",
     "prompt": "A confident newscaster tone with crisp articulation, brisk pacing, controlled breathing and impartial delivery."},
    {"id": "audiobook", "label": "Audiobook",
     "prompt": "A warm, expressive long-form audiobook voice with nuanced emphasis on emotional beats and unhurried pacing."},
    {"id": "conversational", "label": "Conversational",
     "prompt": "A friendly casual conversational voice with natural smile, easy rhythm and engaged warmth."},
    {"id": "podcast", "label": "Podcast host",
     "prompt": "A relaxed engaging podcast host with light personality, conversational warmth and easy back-and-forth energy."},
    {"id": "announce", "label": "Announcer",
     "prompt": "An energetic announcement voice with strong projection, clear emphasis and crisp consonants."},
    {"id": "calm", "label": "Calm meditation",
     "prompt": "A slow, soothing voice with low resonance, long warm vowels, gentle breath and meditative pacing."},
    {"id": "cinematic", "label": "Cinematic trailer",
     "prompt": "A deep cinematic trailer voice with dramatic intensity, rich low-end resonance and powerful pauses between phrases."},
    {"id": "customer", "label": "Customer support",
     "prompt": "A polite empathetic customer support agent with helpful warmth, calm professionalism and reassuring pacing."},
    {"id": "asmr", "label": "ASMR whisper",
     "prompt": "An intimate close-mic ASMR whisper with delicate articulation, soft sibilants and unhurried gentle pacing."},
    {"id": "sportscaster", "label": "Sportscaster",
     "prompt": "An energetic sportscaster with rapid play-by-play cadence, rising excitement and crowd-aware projection."},
    {"id": "luxury", "label": "Luxury brand",
     "prompt": "A refined luxury-brand voiceover with elegant slow pacing, premium polished diction and understated confidence."},
]


@app.on_event("startup")
def _on_startup() -> None:
    """Pre-load the default acoustic backend so the first user request is fast."""
    try:
        pipeline_warmup()
    except Exception:  # noqa: BLE001 - best effort
        pass


def _apply_character(req_kwargs: dict[str, object], character_id: str | None) -> dict[str, object]:
    """Resolve a global voice character into concrete synth kwargs.

    Character fields *fill in* missing user-supplied options but never
    overwrite an explicit value the caller already provided.
    """
    if not character_id:
        return req_kwargs
    character = get_character(character_id)
    if not character:
        return req_kwargs
    # Force qwen3 tier for character voices regardless of what the UI sent.
    req_kwargs["tier"] = "qwen3"
    # Clear the legacy `voice` field so the pipeline does not route this
    # request through that voice's bound backend (e.g. Piper) and instead
    # uses the configured Qwen3 acoustic with the per-character speaker
    # below. Without this, every character collapses to the default voice.
    req_kwargs["voice"] = None
    if not req_kwargs.get("qwen_speaker"):
        req_kwargs["qwen_speaker"] = character.speaker_id
    if not req_kwargs.get("style_prompt"):
        req_kwargs["style_prompt"] = character.style_prompt
    if not req_kwargs.get("language"):
        req_kwargs["language"] = character.qwen_language
    if not req_kwargs.get("emotion"):
        req_kwargs["emotion"] = character.default_emotion

    # Apply per-character pitch / speed offsets for real timbre distinctness
    # so two characters that share a base speaker still sound clearly
    # different. Caller-supplied values win; offsets compose on top of the
    # neutral defaults (1.0 speed, 0.0 pitch semitones).
    if character.pitch_offset and req_kwargs.get("pitch_shift") in (None, 0, 0.0):
        req_kwargs["pitch_shift"] = float(character.pitch_offset)
    if character.speed_offset and req_kwargs.get("speed") in (None, 1, 1.0):
        req_kwargs["speed"] = max(0.5, min(2.0, 1.0 + float(character.speed_offset)))

    # Wire up voice cloning if a reference clip is registered.
    if character.reference_audio:
        req_kwargs.setdefault("speaker_wav", character.reference_audio)
        if character.reference_text and not req_kwargs.get("speaker_text"):
            req_kwargs["speaker_text"] = character.reference_text

    return req_kwargs


def _voice_descriptor(v: Voice) -> VoiceDescriptor:
    return VoiceDescriptor(
        id=v.id,
        name=v.name,
        gender=v.gender,
        accent=v.accent,
        backend=v.backend,
        model=v.model,
        language=v.language,
        description=v.description,
        preview_url=v.preview_url,
        tags=v.tags or [],
        custom=v.custom,
        created_at=v.created_at,
        supports_clone=bool(v.speaker_wav),
        supports_style_prompt=v.backend == "qwen3",
    )


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return cleaned[:48] or "voice"


def _extension_for_upload(audio: UploadFile) -> str:
    content_type = (audio.content_type or "").lower()
    name = (audio.filename or "").lower()
    if "wav" in content_type or name.endswith(".wav"):
        return ".wav"
    if "webm" in content_type or name.endswith(".webm"):
        return ".webm"
    if "mpeg" in content_type or name.endswith(".mp3"):
        return ".mp3"
    if name.endswith(".ogg") or "ogg" in content_type:
        return ".ogg"
    return ".bin"


def _validate_audio_bytes(data: bytes, extension: str = ".bin") -> None:
    if not data:
        raise HTTPException(status_code=400, detail="Audio sample is empty.")
    max_bytes = 50 * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(status_code=413, detail="Audio sample is too large (max 50 MB).")
    if extension in {".webm", ".bin"}:
        return

    try:
        samples, sample_rate = sf.read(io.BytesIO(data), dtype="float32", always_2d=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Audio sample could not be decoded.") from e

    if sample_rate <= 0 or samples.size == 0:
        raise HTTPException(status_code=400, detail="Audio sample has no readable audio frames.")

    duration_seconds = samples.shape[0] / sample_rate
    if duration_seconds < 1.0:
        raise HTTPException(status_code=400, detail="Audio sample is too short for voice cloning (minimum 1 second).")
    if duration_seconds > 120.0:
        raise HTTPException(status_code=400, detail="Audio sample is too long for voice cloning (maximum 120 seconds).")

    absolute = np.abs(samples)
    peak = float(np.max(absolute))
    rms = float(np.sqrt(np.mean(np.square(samples))))
    if peak < 0.005 or rms < 0.001:
        raise HTTPException(status_code=400, detail="Audio sample is too silent for voice cloning.")

    clipped_ratio = float(np.mean(absolute >= 0.999))
    if clipped_ratio > 0.01:
        raise HTTPException(status_code=400, detail="Audio sample appears clipped; record again with lower input gain.")


@app.get("/v1/health", response_model=HealthResponse)
def health() -> HealthResponse:
    s = get_settings()
    return HealthResponse(status="ok", version=__version__, device=s.resolved_device())


@app.get("/v1/capabilities", response_model=CapabilitiesResponse)
def capabilities() -> CapabilitiesResponse:
    return CapabilitiesResponse(
        languages=["en", "ckb", "ar", "tr", "zh", "ja", "ko", "de", "fr", "es", "it", "pt", "ru"],
        formats=["wav"],
        tiers=["piper", "qwen3", "fast", "premium", "clone", "legacy"],
        controls=[
            "voice", "speed", "pitch_shift", "volume", "style_prompt",
            "pause_after_ms", "ssml", "language", "qwen_speaker", "emotion",
            "voice_character",
        ],
        endpoints=[
            "/v1/health",
            "/v1/capabilities",
            "/v1/voices",
            "/v1/voices/{voice_id}",
            "/v1/voices/clone",
            "/v1/voice-characters",
            "/v1/voice-characters/{character_id}",
            "/v1/personas",
            "/v1/voice-categories",
            "/v1/analyze",
            "/v1/synthesize",
            "/v1/synthesize.wav",
            "/v1/synthesize/segments",
            "/v1/synthesize/segments.wav",
            "/v1/stream",
            "/v1/warmup",
            "/metrics",
        ],
        voice_clone=True,
        streaming=True,
        custom_voice_persistence=True,
        qwen_speakers=QWEN3_SPEAKERS,
        emotions=EMOTIONS,
        style_presets=STYLE_PRESETS,
        voice_characters_total=len(all_characters()),
    )


@app.post("/v1/warmup")
def warmup_endpoint(tier: str | None = None) -> dict[str, object]:
    """Force a warmup of the default pipeline (or a specific tier)."""
    started = time.time()
    try:
        pipeline_warmup(tier=tier)
        return {"ok": True, "tier": tier, "elapsed_ms": int((time.time() - started) * 1000)}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Warmup failed: {exc}") from exc


@app.get("/v1/voices", response_model=list[VoiceDescriptor])
def voices() -> list[VoiceDescriptor]:
    pipe = get_default_pipeline()
    return [_voice_descriptor(v) for v in pipe.list_voices()]


@app.get("/v1/voice-characters")
def voice_characters(
    language: str | None = None,
    gender: str | None = None,
    persona: str | None = None,
    category: str | None = None,
    accent: str | None = None,
    age_range: str | None = None,
    q: str | None = None,
    limit: int = 200,
    offset: int = 0,
) -> dict[str, object]:
    """List the global voice character catalog with optional filtering."""
    matches = filter_characters(
        language=language, gender=gender, persona=persona,
        category=category, accent=accent, age_range=age_range, query=q,
    )
    total = len(matches)
    page = matches[max(0, offset): max(0, offset) + max(1, min(limit, 1000))]
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": [character_to_dict(c) for c in page],
    }


@app.get("/v1/voice-characters/{character_id}")
def voice_character_detail(character_id: str) -> dict[str, object]:
    c = get_character(character_id)
    if not c:
        raise HTTPException(status_code=404, detail=f"Voice character not found: {character_id}")
    return character_to_dict(c)


@app.get("/v1/personas")
def voice_personas() -> list[dict]:
    return list_personas()


@app.get("/v1/voice-categories")
def voice_categories() -> list[dict]:
    return list_categories()


@app.post("/v1/voices/clone", response_model=VoiceDescriptor)
async def clone_voice(
    name: str = Form(...),
    consent: bool = Form(...),
    audio: UploadFile = File(...),
    description: str | None = Form(None),
    language: str = Form("en"),
    gender: str = Form("neutral"),
    reference_text: str | None = Form(None),
) -> VoiceDescriptor:
    if not consent:
        raise HTTPException(status_code=400, detail="Voice cloning requires explicit consent.")

    data = await audio.read()
    extension = _extension_for_upload(audio)
    _validate_audio_bytes(data, extension)

    settings = get_settings()
    voice_id = f"custom-{_slug(name)}-{uuid4().hex[:8]}"
    voice_dir = settings.output_dir / "custom_voices" / voice_id
    voice_dir.mkdir(parents=True, exist_ok=True)
    sample_path = voice_dir / f"reference{extension}"
    sample_path.write_bytes(data)

    voice = save_custom_voice(
        Voice(
            id=voice_id,
            name=name.strip() or "Custom Voice",
            gender=gender or "neutral",
            accent="custom",
            backend="qwen3",
            model="Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
            language=language or "en",
            description=description,
            tags=["custom", "cloned"],
            custom=True,
            speaker_wav=str(sample_path),
            reference_text=reference_text,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
    )
    return _voice_descriptor(voice)


@app.get("/v1/voices/{voice_id}", response_model=VoiceDescriptor)
def get_voice_descriptor(voice_id: str) -> VoiceDescriptor:
    try:
        return _voice_descriptor(get_voice(voice_id))
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Voice not found: {voice_id}") from e


@app.delete("/v1/voices/{voice_id}")
def delete_voice_descriptor(voice_id: str) -> dict[str, bool]:
    if not delete_custom_voice(voice_id):
        raise HTTPException(status_code=404, detail=f"Custom voice not found: {voice_id}")
    return {"deleted": True}


@app.post("/v1/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    pipe = get_default_pipeline()
    try:
        utterances = pipe.analyze(req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    tokens: list[NlpToken] = []
    pitch_curve: list[float] = []
    energy_curve: list[float] = []
    duration_ms = 0.0

    for utterance in utterances:
        for token in utterance.tokens:
            if token.is_space:
                continue
            token_type = "punct" if token.is_punct else (token.pos.lower() or "word")
            tokens.append(
                NlpToken(
                    text=token.text,
                    type=token_type,
                    phonemes_arpabet=token.phonemes,
                    phonemes_ipa=arpabet_to_ipa(token.phonemes) if token.phonemes else None,
                    stress=token.stress,
                )
            )
            if token.pitch:
                pitch_curve.append(float(token.pitch))
            if token.energy:
                energy_curve.append(float(token.energy))
            if token.duration:
                duration_ms += float(token.duration) * 1000

    return AnalyzeResponse(
        tokens=tokens,
        prosody=NlpProsody(
            pitch_curve=pitch_curve,
            energy_curve=energy_curve,
            duration_ms=duration_ms,
        ),
    )


@app.post("/v1/synthesize", response_model=SynthesizeResponse)
def synthesize(req: SynthesizeRequest) -> SynthesizeResponse:
    pipe = get_default_pipeline()
    kwargs: dict[str, object] = {
        "text": req.text, "voice": req.voice, "speed": req.speed,
        "pitch_shift": req.pitch_shift, "volume": req.volume,
        "speaker_wav": req.speaker_wav, "style_prompt": req.style_prompt,
        "language": req.language, "qwen_speaker": req.qwen_speaker,
        "emotion": req.emotion, "tier": req.tier,
    }
    kwargs = _apply_character(kwargs, req.voice_character)
    pipe.set_acoustic_tier(kwargs.pop("tier", None))
    try:
        chunk = pipe.synthesize(**{k: v for k, v in kwargs.items() if k != "text"}, text=kwargs["text"])  # type: ignore[arg-type]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    audio_b64 = None
    if req.format == "wav":
        buf = io.BytesIO()
        sf.write(buf, chunk.samples, chunk.sample_rate, format="WAV", subtype="PCM_16")
        audio_b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    return SynthesizeResponse(
        sample_rate=chunk.sample_rate,
        duration_seconds=float(len(chunk.samples) / chunk.sample_rate),
        voice=chunk.metadata.get("voice"),
        cached=bool(chunk.metadata.get("cached")),
        audio_base64=audio_b64,
    )


@app.post("/v1/synthesize.wav")
def synthesize_wav(req: SynthesizeRequest) -> Response:
    pipe = get_default_pipeline()
    kwargs: dict[str, object] = {
        "text": req.text, "voice": req.voice, "speed": req.speed,
        "pitch_shift": req.pitch_shift, "volume": req.volume,
        "speaker_wav": req.speaker_wav, "style_prompt": req.style_prompt,
        "language": req.language, "qwen_speaker": req.qwen_speaker,
        "emotion": req.emotion, "tier": req.tier,
    }
    kwargs = _apply_character(kwargs, req.voice_character)
    pipe.set_acoustic_tier(kwargs.pop("tier", None))
    try:
        chunk = pipe.synthesize(**{k: v for k, v in kwargs.items() if k != "text"}, text=kwargs["text"])  # type: ignore[arg-type]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    duration_seconds = float(len(chunk.samples) / chunk.sample_rate) if chunk.sample_rate else 0.0
    buf = io.BytesIO()
    sf.write(buf, chunk.samples, chunk.sample_rate, format="WAV", subtype="PCM_16")
    return Response(
        content=buf.getvalue(),
        media_type="audio/wav",
        headers={
            "X-Sample-Rate": str(chunk.sample_rate),
            "X-Duration-Seconds": f"{duration_seconds:.6f}",
        },
    )


def _synthesize_segments(req: SynthesizeSegmentsRequest) -> tuple[np.ndarray, int, list[dict[str, object]]]:
    pipe = get_default_pipeline()
    chunks: list[np.ndarray] = []
    metadata: list[dict[str, object]] = []
    sample_rate = pipe.settings.sample_rate

    for index, segment in enumerate(req.segments):
        kwargs: dict[str, object] = {
            "text": segment.text, "voice": segment.voice, "speed": segment.speed,
            "pitch_shift": segment.pitch_shift, "volume": segment.volume,
            "style_prompt": segment.style_prompt, "language": segment.language,
            "qwen_speaker": segment.qwen_speaker, "emotion": segment.emotion,
            "tier": segment.tier,
        }
        kwargs = _apply_character(kwargs, segment.voice_character)
        pipe.set_acoustic_tier(kwargs.pop("tier", None))
        chunk = pipe.synthesize(**{k: v for k, v in kwargs.items() if k != "text"}, text=kwargs["text"])  # type: ignore[arg-type]
        sample_rate = chunk.sample_rate
        if chunk.samples.size:
            chunks.append(chunk.samples.astype(np.float32))
        if index < len(req.segments) - 1 and segment.pause_after_ms:
            chunks.append(silence(segment.pause_after_ms / 1000.0, sample_rate))
        metadata.append(
            {
                "index": index,
                "voice": segment.voice,
                "duration_seconds": float(len(chunk.samples) / chunk.sample_rate) if chunk.sample_rate else 0.0,
            }
        )

    if not chunks:
        return np.zeros(0, dtype=np.float32), sample_rate, metadata
    return np.concatenate(chunks).astype(np.float32), sample_rate, metadata


@app.post("/v1/synthesize/segments", response_model=SynthesizeResponse)
def synthesize_segments(req: SynthesizeSegmentsRequest) -> SynthesizeResponse:
    try:
        audio, sample_rate, metadata = _synthesize_segments(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    buf = io.BytesIO()
    sf.write(buf, audio, sample_rate, format="WAV", subtype="PCM_16")
    return SynthesizeResponse(
        sample_rate=sample_rate,
        duration_seconds=float(len(audio) / sample_rate) if sample_rate else 0.0,
        voice=None,
        cached=False,
        audio_base64=base64.b64encode(buf.getvalue()).decode("ascii"),
    )


@app.post("/v1/synthesize/segments.wav")
def synthesize_segments_wav(req: SynthesizeSegmentsRequest) -> Response:
    try:
        audio, sample_rate, metadata = _synthesize_segments(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    duration_seconds = float(len(audio) / sample_rate) if sample_rate else 0.0
    buf = io.BytesIO()
    sf.write(buf, audio, sample_rate, format="WAV", subtype="PCM_16")
    return Response(
        content=buf.getvalue(),
        media_type="audio/wav",
        headers={
            "X-Sample-Rate": str(sample_rate),
            "X-Duration-Seconds": f"{duration_seconds:.6f}",
            "X-Segments": str(len(metadata)),
        },
    )


@app.post("/v1/stream")
def stream(req: SynthesizeRequest) -> StreamingResponse:
    pipe = get_default_pipeline()
    kwargs: dict[str, object] = {
        "text": req.text, "voice": req.voice, "speed": req.speed,
        "pitch_shift": req.pitch_shift, "volume": req.volume,
        "speaker_wav": req.speaker_wav, "style_prompt": req.style_prompt,
        "language": req.language, "qwen_speaker": req.qwen_speaker,
        "emotion": req.emotion, "tier": req.tier,
    }
    kwargs = _apply_character(kwargs, req.voice_character)
    pipe.set_acoustic_tier(kwargs.pop("tier", None))

    try:
        chunk = pipe.synthesize(**{k: v for k, v in kwargs.items() if k != "text"}, text=kwargs["text"])  # type: ignore[arg-type]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    buf = io.BytesIO()
    sf.write(buf, chunk.samples, chunk.sample_rate, format="WAV", subtype="PCM_16")
    payload = buf.getvalue()

    def gen() -> Iterator[bytes]:
        step = 32 * 1024
        for offset in range(0, len(payload), step):
            yield payload[offset:offset + step]

    return StreamingResponse(
        gen(),
        media_type="audio/wav",
        headers={
            "Content-Length": str(len(payload)),
            "X-Sample-Rate": str(chunk.sample_rate),
            "X-Duration-Seconds": f"{(len(chunk.samples) / chunk.sample_rate):.6f}" if chunk.sample_rate else "0",
        },
    )


@app.get("/metrics")
def metrics() -> Response:
    try:
        from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    except ImportError:
        return Response(content=b"# prometheus_client not installed\n", media_type="text/plain")
