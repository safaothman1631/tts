"""Core data contracts shared between every NLP and acoustic stage."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Token:
    """A single linguistic token after spaCy analysis."""

    text: str
    lemma: str = ""
    pos: str = ""             # Universal POS
    tag: str = ""             # Fine-grained tag (e.g. NN, VBZ)
    dep: str = ""             # Dependency relation
    ent_type: str = ""        # NER label
    is_punct: bool = False
    is_space: bool = False
    idx: int = 0              # char offset in source
    # Phonetic content (filled by G2P)
    phonemes: list[str] = field(default_factory=list)   # ARPABET
    stress: list[int] = field(default_factory=list)
    syllables: list[list[str]] = field(default_factory=list)
    # Prosody (filled by prosody predictors)
    break_after: int = 0      # 0=none, 2=minor, 3=major, 4=sentence
    pitch: float = 0.0
    duration: float = 0.0
    energy: float = 0.0
    # SSML overrides
    ssml_attrs: dict[str, Any] = field(default_factory=dict)


@dataclass
class Phrase:
    """A prosodic phrase (sequence of tokens)."""

    tokens: list[Token] = field(default_factory=list)
    text: str = ""
    break_strength: int = 2

    @property
    def phonemes(self) -> list[str]:
        out: list[str] = []
        for t in self.tokens:
            out.extend(t.phonemes)
        return out


@dataclass
class Utterance:
    """One sentence after full NLP analysis."""

    text: str
    raw_text: str = ""
    tokens: list[Token] = field(default_factory=list)
    phrases: list[Phrase] = field(default_factory=list)
    sentiment: str = "neutral"
    sentiment_score: float = 0.0
    emotion: str = "neutral"
    language: str = "en-US"
    ssml_root: Any | None = None

    @property
    def phonemes(self) -> list[str]:
        out: list[str] = []
        for t in self.tokens:
            out.extend(t.phonemes)
        return out


@dataclass
class LinguisticFrame:
    """Final contract handed to the acoustic model.

    Acoustic backends consume ONLY this object. Anything they need
    (style/speaker/phonemes/prosody) must be present here.
    """

    phonemes: list[str] = field(default_factory=list)         # ARPABET
    phoneme_ids: list[int] = field(default_factory=list)      # backend-specific ids
    durations: Optional[list[float]] = None
    pitch_contour: Optional[list[float]] = None
    energy_contour: Optional[list[float]] = None
    word_boundaries: list[int] = field(default_factory=list)  # phoneme indices
    phrase_breaks: list[int] = field(default_factory=list)
    stress: list[int] = field(default_factory=list)
    text: str = ""                    # original (post-normalization) text
    speaker_id: Optional[str] = None
    speaker_embedding: Optional[Any] = None  # numpy array
    style_id: Optional[str] = None
    style_embedding: Optional[Any] = None
    language: str = "en-US"
    sample_rate: int = 22050
    speed: float = 1.0
    pitch_shift: float = 0.0
    energy_scale: float = 1.0
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class AudioChunk:
    """A piece of synthesized audio."""

    samples: Any                      # numpy.ndarray, float32 [-1,1]
    sample_rate: int
    text: str = ""
    is_final: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
