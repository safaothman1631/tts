"""eng-tts — World-class English Text-to-Speech engine.

Public API:
    from eng_tts import TTSPipeline, synthesize
"""
from __future__ import annotations

from .core.frame import LinguisticFrame, Token, Phrase, Utterance
from .core.pipeline import TTSPipeline
from .core.exceptions import (
    EngTTSError,
    NormalizationError,
    G2PError,
    AcousticError,
    VocoderError,
    ConfigError,
)
from .version import __version__

# Eager-import subpackages so @register decorators populate the plugin registry
from . import nlp as _nlp  # noqa: F401
from . import acoustic as _acoustic  # noqa: F401
from . import vocoder as _vocoder  # noqa: F401
from . import postproc as _postproc  # noqa: F401
from . import streaming as _streaming  # noqa: F401

__all__ = [
    "TTSPipeline",
    "LinguisticFrame",
    "Token",
    "Phrase",
    "Utterance",
    "EngTTSError",
    "NormalizationError",
    "G2PError",
    "AcousticError",
    "VocoderError",
    "ConfigError",
    "synthesize",
    "__version__",
]


def synthesize(text: str, **kwargs):  # type: ignore[no-untyped-def]
    """Convenience one-shot synthesis. Lazily builds a default pipeline."""
    from .core.pipeline import get_default_pipeline

    return get_default_pipeline().synthesize(text, **kwargs)
