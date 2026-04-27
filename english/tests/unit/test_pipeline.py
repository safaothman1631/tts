import importlib.util

import pytest

PYTTSX3_AVAILABLE = importlib.util.find_spec("pyttsx3") is not None
SOUNDFILE_AVAILABLE = importlib.util.find_spec("soundfile") is not None


@pytest.mark.skipif(
    not (PYTTSX3_AVAILABLE and SOUNDFILE_AVAILABLE),
    reason="pyttsx3 or soundfile not installed",
)
def test_end_to_end_legacy(pipeline, tmp_path):
    out = tmp_path / "hello.wav"
    chunk = pipeline.synthesize("Dr. Smith earned $1,250 today.", output_path=out)
    assert out.exists() and out.stat().st_size > 0
    assert chunk.sample_rate > 0
    assert chunk.metadata.get("duration_s", 0) > 0


def test_analyze_only(pipeline):
    utts = pipeline.analyze("Hello, world. How are you?")
    assert len(utts) >= 2
    assert all(u.tokens for u in utts)
