"""TTSPipeline orchestrator: end-to-end text → audio.

Pipeline stages:
    SSML → normalize → segment → analyze → homograph → G2P → prosody
    → sentiment → frame → acoustic → vocoder → postproc → audio
"""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Any, Iterable, Iterator, Optional

import numpy as np

from ..config import Settings, get_settings
from ..config.voices import Voice, all_voices, get_voice
from ..ssml import is_ssml, parse as parse_ssml, walk as walk_ssml
from ..ssml.walker import to_plain_text as ssml_text
from ..utils.audio import save_wav, silence
from ..utils.logging import get_logger, setup_logging
from .cache import DiskCache, hash_key
from .exceptions import EngTTSError, AcousticError
from .frame import AudioChunk, LinguisticFrame, Utterance
from .frame_builder import DefaultFrameBuilder
from .interfaces import (
    IAcoustic,
    IFrameBuilder,
    IG2P,
    IHomographDisambiguator,
    ILinguisticAnalyzer,
    INormalizer,
    IPostProcessor,
    IProsody,
    ISegmenter,
    ISentiment,
    IStreamer,
    IVocoder,
)
from .registry import create, get

_log = get_logger(__name__)
_DEFAULT_LOCK = threading.Lock()
_DEFAULT_PIPELINE: Optional["TTSPipeline"] = None
_ACOUSTIC_CACHE: dict[tuple[Any, ...], IAcoustic] = {}
_ACOUSTIC_CACHE_LOCK = threading.Lock()


def _cached_acoustic(backend: str, **kwargs: Any) -> IAcoustic:
    """Return a process-wide cached acoustic backend instance.

    Avoids re-instantiating the same backend (and reloading the underlying
    model) for every synthesis request. Falls back to creating a fresh
    instance only when the cache key has not been seen before.
    """
    key = (backend, tuple(sorted((k, v) for k, v in kwargs.items() if v is not None)))
    cached = _ACOUSTIC_CACHE.get(key)
    if cached is not None:
        return cached
    with _ACOUSTIC_CACHE_LOCK:
        cached = _ACOUSTIC_CACHE.get(key)
        if cached is not None:
            return cached
        instance = create("acoustic", backend, **kwargs)
        _ACOUSTIC_CACHE[key] = instance
        return instance


_FRAME_BUILDER_OVERRIDE_KEYS = frozenset(
    {
        "pitch_contour",
        "energy_contour",
        "speaker_id",
        "speaker_embedding",
        "style_id",
        "style_embedding",
        "sample_rate",
        "speed",
        "pitch_shift",
        "energy_scale",
        "extra",
    }
)


class TTSPipeline:
    """End-to-end English TTS pipeline."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        normalizer: Optional[INormalizer] = None,
        segmenter: Optional[ISegmenter] = None,
        analyzer: Optional[ILinguisticAnalyzer] = None,
        homograph: Optional[IHomographDisambiguator] = None,
        g2p: Optional[IG2P] = None,
        prosody: Optional[IProsody] = None,
        sentiment: Optional[ISentiment] = None,
        frame_builder: Optional[IFrameBuilder] = None,
        acoustic: Optional[IAcoustic] = None,
        vocoder: Optional[IVocoder] = None,
        postproc: Optional[list[IPostProcessor]] = None,
        streamer: Optional[IStreamer] = None,
    ) -> None:
        self.settings = settings or get_settings()
        setup_logging(self.settings.log_level)
        # Lazy init via factories
        self._normalizer = normalizer
        self._segmenter = segmenter
        self._analyzer = analyzer
        self._homograph = homograph
        self._g2p = g2p
        self._prosody = prosody
        self._sentiment = sentiment
        self._frame_builder = frame_builder
        self._acoustic = acoustic
        self._vocoder = vocoder
        self._postproc = postproc
        self._streamer = streamer
        self._audio_cache = DiskCache(self.settings.cache_dir / "audio") if self.settings.cache_audio else None

    # ─── Lazy component accessors ──────────────────────────────────────

    @property
    def normalizer(self) -> INormalizer:
        if self._normalizer is None:
            self._normalizer = create("normalizer", "rule_based")
        return self._normalizer

    @property
    def segmenter(self) -> ISegmenter:
        if self._segmenter is None:
            from ..nlp.segmentation import make_segmenter

            self._segmenter = make_segmenter(self.settings.sentence_segmenter)
        return self._segmenter

    @property
    def analyzer(self) -> ILinguisticAnalyzer:
        if self._analyzer is None:
            from ..nlp.linguistic import make_analyzer

            self._analyzer = make_analyzer("spacy", model=self.settings.spacy_model)
        return self._analyzer

    @property
    def homograph(self) -> IHomographDisambiguator:
        if self._homograph is None:
            self._homograph = create("homograph", "rule_based")
        return self._homograph

    @property
    def g2p(self) -> IG2P:
        if self._g2p is None:
            self._g2p = create("g2p", "hybrid")
        return self._g2p

    @property
    def prosody(self) -> IProsody:
        if self._prosody is None:
            self._prosody = create("prosody", "rule_based")
        return self._prosody

    @property
    def sentiment(self) -> ISentiment:
        if self._sentiment is None:
            self._sentiment = create("sentiment", "lexicon")
        return self._sentiment

    @property
    def frame_builder(self) -> IFrameBuilder:
        if self._frame_builder is None:
            self._frame_builder = DefaultFrameBuilder()
        return self._frame_builder

    @property
    def acoustic(self) -> IAcoustic:
        if self._acoustic is None:
            self._acoustic = self._build_acoustic(self.settings.acoustic_tier)
        return self._acoustic

    @property
    def vocoder(self) -> IVocoder:
        if self._vocoder is None:
            self._vocoder = create("vocoder", "passthrough")
        return self._vocoder

    @property
    def postproc(self) -> list[IPostProcessor]:
        if self._postproc is None:
            chain: list[IPostProcessor] = []
            if self.settings.enable_loudness_norm:
                chain.append(create("postproc", "loudness"))
            self._postproc = chain
        return self._postproc

    @property
    def streamer(self) -> IStreamer:
        if self._streamer is None:
            from ..streaming.chunker import DefaultStreamer

            self._streamer = DefaultStreamer(sample_rate=self.settings.sample_rate)
        return self._streamer

    # ─── Acoustic factory ──────────────────────────────────────────────

    def _build_acoustic(self, tier: str) -> IAcoustic:
        device = self.settings.resolved_device()
        try:
            if tier == "qwen3":
                return _cached_acoustic("qwen3", device=device)
            if tier == "piper":
                return _cached_acoustic("piper", device=device)
            if tier == "fast":
                return _cached_acoustic("vits", device=device)
            if tier == "premium":
                return _cached_acoustic("styletts2", device=device)
            if tier == "clone":
                return _cached_acoustic("xtts", device=device)
        except Exception as e:
            _log.warning("acoustic_load_fallback", tier=tier, error=str(e))
        # Try Piper (lightweight, offline) before falling all the way back to SAPI.
        if tier != "piper" and tier != "legacy":
            try:
                return _cached_acoustic("piper", device=device)
            except Exception as e:
                _log.warning("piper_load_fallback", error=str(e))
        # Final fallback to legacy SAPI
        return _cached_acoustic("legacy")

    # ─── Public API ────────────────────────────────────────────────────

    def set_acoustic_tier(self, tier: str | None) -> None:
        if not tier or tier == self.settings.acoustic_tier:
            return
        self.settings.acoustic_tier = tier  # type: ignore[assignment]
        self._acoustic = None

    def _frame_builder_overrides(self, overrides: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in overrides.items() if k in _FRAME_BUILDER_OVERRIDE_KEYS and v is not None}

    def analyze(self, text: str) -> list[Utterance]:
        """Run text through all NLP stages and return Utterance list."""
        if is_ssml(text):
            root = parse_ssml(text)
            spans = list(walk_ssml(root))
            text_only = " ".join(s.text for s in spans if s.text and not s.is_break)
            ssml_root = root
        else:
            text_only = text
            ssml_root = None

        normalized = self.normalizer.normalize(text_only)
        sentences = self.segmenter.segment(normalized)
        utterances: list[Utterance] = []
        for sent in sentences:
            utt = self.analyzer.analyze(sent)
            utt.ssml_root = ssml_root
            utt = self.homograph.disambiguate(utt)
            utt = self.g2p.annotate(utt)
            utt = self.prosody.predict(utt)
            if self.settings.enable_sentiment:
                try:
                    utt = self.sentiment.score(utt)
                except Exception:
                    pass
            utterances.append(utt)
        return utterances

    def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        pitch_shift: float = 0.0,
        volume: float = 1.0,
        speaker_wav: Optional[str | Path] = None,
        output_path: Optional[str | Path] = None,
        **frame_overrides: Any,
    ) -> AudioChunk:
        """One-shot synthesis. Returns the full audio chunk; optionally writes WAV."""
        voice_id = voice or self.settings.default_voice
        try:
            v = get_voice(voice_id) if voice_id in all_voices() else None
        except Exception:
            v = None

        if v and v.speaker_wav and speaker_wav is None:
            speaker_wav = v.speaker_wav

        if self._audio_cache is not None:
            cache_key = hash_key(text, voice_id, speed, pitch_shift, volume, str(speaker_wav or ""), frame_overrides)
            cached = self._audio_cache.get(cache_key)
            if cached is not None:
                samples, sr = cached
                return AudioChunk(
                    samples=np.asarray(samples, dtype=np.float32),
                    sample_rate=int(sr),
                    text=text,
                    metadata={"cached": True, "voice": voice_id},
                )
        else:
            cache_key = None

        utterances = self.analyze(text)
        if not utterances:
            return AudioChunk(samples=np.zeros(0, dtype=np.float32), sample_rate=self.settings.sample_rate, text=text)

        # If caller forced a qwen_speaker (i.e. voice_character), bypass the
        # voice's bound backend and use the configured acoustic so 150
        # characters don't all collapse to the default voice's Piper model.
        force_default_acoustic = bool(frame_overrides.get("qwen_speaker"))
        if force_default_acoustic:
            acoustic = self.acoustic
        else:
            acoustic = self._select_acoustic_for_voice(v) if (v and self.settings.acoustic_tier != "legacy") else self.acoustic
        sample_rate = self.settings.sample_rate

        def synth_fn(frame: LinguisticFrame) -> np.ndarray:
            frame.sample_rate = sample_rate
            frame.speed = speed
            frame.pitch_shift = pitch_shift
            frame.energy_scale = volume
            if v:
                frame.speaker_id = v.speaker_id
            if speaker_wav:
                frame.extra["speaker_wav"] = str(speaker_wav)
            if v and v.reference_text:
                frame.extra["speaker_text"] = v.reference_text
            if frame_overrides.get("style_prompt"):
                frame.extra["voice_prompt"] = str(frame_overrides["style_prompt"])
            if frame_overrides.get("qwen_speaker"):
                frame.extra["qwen_speaker"] = str(frame_overrides["qwen_speaker"])
            if frame_overrides.get("emotion"):
                emo = str(frame_overrides["emotion"]).strip()
                if emo:
                    frame.emotion = emo
                    frame.extra["emotion"] = emo
            if frame_overrides.get("language"):
                frame.language = str(frame_overrides["language"])
            try:
                wave = acoustic.synthesize(frame)
            except AcousticError as e:
                _log.warning("acoustic_failed_falling_back_to_legacy: %s", str(e))
                wave = create("acoustic", "legacy").synthesize(frame)
            if not getattr(acoustic, "produces_waveform", True):
                wave = self.vocoder.vocode(wave)
            return wave

        audio = self.streamer.collect(
            utterances, synth_fn, self.frame_builder,
            speaker_id=(v.speaker_id if v else None),
            **self._frame_builder_overrides(frame_overrides),
        )

        for pp in self.postproc:
            audio = pp.process(audio, sample_rate)

        if volume != 1.0:
            audio = np.clip(audio * max(0.0, min(2.0, volume)), -1.0, 1.0)

        if cache_key is not None:
            self._audio_cache.set(cache_key, (audio.tolist(), sample_rate))

        chunk = AudioChunk(
            samples=audio,
            sample_rate=sample_rate,
            text=text,
            metadata={"voice": voice_id, "duration_s": float(len(audio) / sample_rate)},
        )
        if output_path is not None:
            save_wav(output_path, audio, sample_rate)
            chunk.metadata["output_path"] = str(output_path)
        return chunk

    def stream(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        volume: float = 1.0,
        speaker_wav: Optional[str | Path] = None,
        **frame_overrides: Any,
    ) -> Iterator[AudioChunk]:
        """Yield audio sentence by sentence."""
        voice_id = voice or self.settings.default_voice
        v = get_voice(voice_id) if voice_id in all_voices() else None
        if v and v.speaker_wav and speaker_wav is None:
            speaker_wav = v.speaker_wav
        utterances = self.analyze(text)
        force_default_acoustic = bool(frame_overrides.get("qwen_speaker"))
        if force_default_acoustic:
            acoustic = self.acoustic
        else:
            acoustic = self._select_acoustic_for_voice(v) if (v and self.settings.acoustic_tier != "legacy") else self.acoustic
        sample_rate = self.settings.sample_rate

        def synth_fn(frame: LinguisticFrame) -> np.ndarray:
            frame.sample_rate = sample_rate
            frame.speed = speed
            frame.pitch_shift = float(frame_overrides.get("pitch_shift") or 0.0)
            frame.energy_scale = volume
            if v:
                frame.speaker_id = v.speaker_id
            if speaker_wav:
                frame.extra["speaker_wav"] = str(speaker_wav)
            if v and v.reference_text:
                frame.extra["speaker_text"] = v.reference_text
            if frame_overrides.get("style_prompt"):
                frame.extra["voice_prompt"] = str(frame_overrides["style_prompt"])
            if frame_overrides.get("qwen_speaker"):
                frame.extra["qwen_speaker"] = str(frame_overrides["qwen_speaker"])
            if frame_overrides.get("emotion"):
                emo = str(frame_overrides["emotion"]).strip()
                if emo:
                    frame.emotion = emo
                    frame.extra["emotion"] = emo
            if frame_overrides.get("language"):
                frame.language = str(frame_overrides["language"])
            try:
                wave = acoustic.synthesize(frame)
            except AcousticError:
                wave = create("acoustic", "legacy").synthesize(frame)
            if not getattr(acoustic, "produces_waveform", True):
                wave = self.vocoder.vocode(wave)
            for pp in self.postproc:
                wave = pp.process(wave, sample_rate)
            if volume != 1.0:
                wave = np.clip(wave * max(0.0, min(2.0, volume)), -1.0, 1.0)
            return wave

        yield from self.streamer.stream(
            utterances, synth_fn, self.frame_builder, **self._frame_builder_overrides(frame_overrides)
        )

    # ─── Voice selection ───────────────────────────────────────────────

    def _select_acoustic_for_voice(self, voice: Voice) -> IAcoustic:
        backend = voice.backend
        device = self.settings.resolved_device()
        try:
            if backend == "qwen3":
                return _cached_acoustic("qwen3", model_name=voice.model, device=device)
            if backend == "piper":
                return _cached_acoustic(
                    "piper",
                    model_name=voice.model,
                    device=device,
                    speaker_id=int(voice.speaker_id) if voice.speaker_id else None,
                )
            if backend == "vits":
                return _cached_acoustic("vits", model_name=voice.model, device=device)
            if backend == "xtts":
                return _cached_acoustic("xtts", model_name=voice.model, device=device)
            if backend == "styletts2":
                return _cached_acoustic("styletts2", model_name=voice.model, device=device)
            if backend == "legacy":
                return _cached_acoustic("legacy")
        except Exception as e:
            _log.warning("voice_acoustic_load_fallback", voice=voice.id, error=str(e))
        # Try Piper as a graceful neural fallback before SAPI.
        try:
            return _cached_acoustic("piper", device=device)
        except Exception:
            return _cached_acoustic("legacy")

    def list_voices(self) -> list[Voice]:
        return list(all_voices().values())


def get_default_pipeline() -> TTSPipeline:
    global _DEFAULT_PIPELINE
    with _DEFAULT_LOCK:
        if _DEFAULT_PIPELINE is None:
            _DEFAULT_PIPELINE = TTSPipeline()
        return _DEFAULT_PIPELINE


def reset_default_pipeline() -> None:
    global _DEFAULT_PIPELINE
    _DEFAULT_PIPELINE = None
    with _ACOUSTIC_CACHE_LOCK:
        _ACOUSTIC_CACHE.clear()


def warmup(text: str = "Warm up.", tier: Optional[str] = None) -> None:
    """Pre-load default pipeline + acoustic backend with a tiny synth call.

    Reduces first-request latency for end users by paying the model load cost
    eagerly at process startup instead of inside the first request.
    """
    pipe = get_default_pipeline()
    if tier:
        pipe.set_acoustic_tier(tier)
    try:
        pipe.synthesize(text)
    except Exception as exc:  # noqa: BLE001 - warmup is best-effort
        _log.warning("warmup_failed", error=str(exc))
