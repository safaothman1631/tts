import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture(scope="session")
def normalizer():
    from eng_tts.nlp.normalizer import RuleBasedNormalizer

    return RuleBasedNormalizer()


@pytest.fixture(scope="session")
def pipeline():
    from eng_tts.config import get_settings, reset_settings
    from eng_tts.core.pipeline import TTSPipeline, reset_default_pipeline

    reset_settings()
    reset_default_pipeline()
    s = get_settings()
    s.acoustic_tier = "legacy"
    s.enable_loudness_norm = False
    s.cache_audio = False
    return TTSPipeline(settings=s)
