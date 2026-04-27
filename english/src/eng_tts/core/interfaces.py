"""Abstract Base Classes for every pluggable component."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Iterator, Optional

from .frame import AudioChunk, LinguisticFrame, Utterance


class INormalizer(ABC):
    """Text Normalizer: NSW → spoken form."""

    name: str = "base"

    @abstractmethod
    def normalize(self, text: str) -> str: ...


class ISegmenter(ABC):
    """Sentence segmentation."""

    name: str = "base"

    @abstractmethod
    def segment(self, text: str) -> list[str]: ...


class ILinguisticAnalyzer(ABC):
    """POS / NER / Dep parsing → Utterance."""

    name: str = "base"

    @abstractmethod
    def analyze(self, sentence: str) -> Utterance: ...


class IHomographDisambiguator(ABC):
    name: str = "base"

    @abstractmethod
    def disambiguate(self, utt: Utterance) -> Utterance: ...


class IG2P(ABC):
    """Grapheme-to-Phoneme converter."""

    name: str = "base"

    @abstractmethod
    def word_to_phonemes(self, word: str, pos: str = "") -> list[str]: ...

    def annotate(self, utt: Utterance) -> Utterance:
        for tok in utt.tokens:
            if tok.is_punct or tok.is_space or not tok.text.strip():
                continue
            if not tok.phonemes:
                tok.phonemes = self.word_to_phonemes(tok.text, tok.pos)
        return utt


class IProsody(ABC):
    """Prosody predictor (breaks/pitch/duration/energy)."""

    name: str = "base"

    @abstractmethod
    def predict(self, utt: Utterance) -> Utterance: ...


class ISentiment(ABC):
    name: str = "base"

    @abstractmethod
    def score(self, utt: Utterance) -> Utterance: ...


class IFrameBuilder(ABC):
    name: str = "base"

    @abstractmethod
    def build(self, utt: Utterance, **overrides) -> LinguisticFrame: ...  # type: ignore[no-untyped-def]


class IAcoustic(ABC):
    """Acoustic model: LinguisticFrame → mel or waveform."""

    name: str = "base"
    produces_waveform: bool = False  # True for end-to-end (VITS, XTTS)
    sample_rate: int = 22050

    @abstractmethod
    def synthesize(self, frame: LinguisticFrame) -> "object": ...
    """Returns numpy.ndarray. Either mel-spectrogram or waveform."""

    def list_voices(self) -> list[str]:
        return []


class IVocoder(ABC):
    """Mel → waveform."""

    name: str = "base"
    sample_rate: int = 22050

    @abstractmethod
    def vocode(self, mel: "object") -> "object": ...


class IPostProcessor(ABC):
    name: str = "base"

    @abstractmethod
    def process(self, audio: "object", sample_rate: int) -> "object": ...


class IStreamer(ABC):
    """Streaming chunker for long-form audio."""

    name: str = "base"

    @abstractmethod
    def stream(
        self,
        utterances: Iterable[Utterance],
        synth_fn,  # Callable[[LinguisticFrame], np.ndarray]
        frame_builder: IFrameBuilder,
        **kwargs,  # type: ignore[no-untyped-def]
    ) -> Iterator[AudioChunk]: ...
