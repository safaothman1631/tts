"""Typed exception hierarchy."""
from __future__ import annotations


class EngTTSError(Exception):
    """Base exception for all eng-tts errors."""


class ConfigError(EngTTSError):
    """Configuration / settings error."""


class NormalizationError(EngTTSError):
    """Text normalization failed."""


class SegmentationError(EngTTSError):
    """Sentence segmentation failed."""


class LinguisticError(EngTTSError):
    """POS / NER / dependency parsing failed."""


class HomographError(EngTTSError):
    """Homograph disambiguation failed."""


class G2PError(EngTTSError):
    """Grapheme-to-phoneme conversion failed."""


class ProsodyError(EngTTSError):
    """Prosody prediction failed."""


class AcousticError(EngTTSError):
    """Acoustic model inference failed."""


class VocoderError(EngTTSError):
    """Vocoder inference failed."""


class SSMLError(EngTTSError):
    """SSML parsing failed."""


class VoiceNotFoundError(EngTTSError):
    """Requested voice id is unknown."""
