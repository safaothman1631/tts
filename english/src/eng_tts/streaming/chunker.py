"""Sentence/phrase chunker for streaming synthesis with crossfade."""
from __future__ import annotations

from typing import Callable, Iterable, Iterator

import numpy as np

from ..core.frame import AudioChunk, LinguisticFrame, Utterance
from ..core.interfaces import IFrameBuilder, IStreamer
from ..core.registry import register
from ..utils.audio import concat as audio_concat
from ..utils.audio import silence


@register("streamer", "default")
class DefaultStreamer(IStreamer):
    name = "default"

    def __init__(self, crossfade_ms: int = 30, sample_rate: int = 22050) -> None:
        self.crossfade_ms = crossfade_ms
        self.sample_rate = sample_rate

    def stream(
        self,
        utterances: Iterable[Utterance],
        synth_fn: Callable[[LinguisticFrame], np.ndarray],
        frame_builder: IFrameBuilder,
        **kwargs,
    ) -> Iterator[AudioChunk]:
        utts = list(utterances)
        for i, utt in enumerate(utts):
            frame = frame_builder.build(utt, sample_rate=self.sample_rate, **kwargs)
            audio = synth_fn(frame)
            if audio.size == 0:
                continue
            yield AudioChunk(
                samples=audio,
                sample_rate=self.sample_rate,
                text=utt.text,
                is_final=(i == len(utts) - 1),
                metadata={"index": i, "of": len(utts)},
            )

    def collect(
        self,
        utterances: Iterable[Utterance],
        synth_fn: Callable[[LinguisticFrame], np.ndarray],
        frame_builder: IFrameBuilder,
        inter_pause_ms: int = 100,
        **kwargs,
    ) -> np.ndarray:
        chunks: list[np.ndarray] = []
        pause = silence(inter_pause_ms / 1000.0, self.sample_rate)
        for ch in self.stream(utterances, synth_fn, frame_builder, **kwargs):
            if chunks:
                chunks.append(pause)
            chunks.append(ch.samples)
        cf = int(self.sample_rate * self.crossfade_ms / 1000)
        return audio_concat(chunks, crossfade_samples=cf) if chunks else np.zeros(0, dtype=np.float32)
