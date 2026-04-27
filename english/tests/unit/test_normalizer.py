from pathlib import Path

import pytest
import yaml

GOLDEN = Path(__file__).resolve().parents[1] / "golden" / "normalizer_cases.yaml"


def _load_cases():
    data = yaml.safe_load(GOLDEN.read_text(encoding="utf-8"))
    return data["cases"]


@pytest.mark.parametrize("case", _load_cases())
def test_normalizer_golden(normalizer, case):
    out = normalizer.normalize(case["in"]).lower()
    for needle in case["must_contain"]:
        assert needle.lower() in out, (
            f"Input: {case['in']!r}\nExpected substring: {needle!r}\nGot: {out!r}"
        )


def test_idempotent(normalizer):
    s = "Just plain text with no NSWs."
    assert normalizer.normalize(s).strip() == s


def test_unicode_quotes(normalizer):
    out = normalizer.normalize("\u201cHello\u201d he said.")
    assert "Hello" in out
