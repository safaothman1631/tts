"""Core building blocks: pipeline, frame, interfaces, registry, cache."""
from .cache import DiskCache, hash_key, memoize
from .exceptions import (
    AcousticError,
    ConfigError,
    EngTTSError,
    G2PError,
    NormalizationError,
    SegmentationError,
    SSMLError,
    VoiceNotFoundError,
)
from .frame import AudioChunk, LinguisticFrame, Phrase, Token, Utterance
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
from .registry import create, get, list_plugins, register

__all__ = [
    # data
    "AudioChunk",
    "LinguisticFrame",
    "Phrase",
    "Token",
    "Utterance",
    "DefaultFrameBuilder",
    # interfaces
    "IAcoustic",
    "IFrameBuilder",
    "IG2P",
    "IHomographDisambiguator",
    "ILinguisticAnalyzer",
    "INormalizer",
    "IPostProcessor",
    "IProsody",
    "ISegmenter",
    "ISentiment",
    "IStreamer",
    "IVocoder",
    # registry
    "register",
    "get",
    "create",
    "list_plugins",
    # cache
    "DiskCache",
    "hash_key",
    "memoize",
    # exceptions
    "EngTTSError",
    "ConfigError",
    "NormalizationError",
    "SegmentationError",
    "SSMLError",
    "G2PError",
    "AcousticError",
    "VoiceNotFoundError",
]
