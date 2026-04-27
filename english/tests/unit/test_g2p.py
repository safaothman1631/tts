def test_cmudict_lookup():
    import eng_tts  # noqa: F401  (trigger registry)
    from eng_tts.core.frame import Token, Utterance
    from eng_tts.core.registry import create
    from eng_tts.nlp.g2p.lexicon import _load_cmudict

    if not _load_cmudict():
        import pytest

        pytest.skip("CMUDict (g2p_en/nltk) not installed")
    g = create("g2p", "cmudict")
    utt = Utterance(text="hello world", tokens=[Token(text="hello"), Token(text="world")])
    out = g.annotate(utt)
    assert any(t.phonemes for t in out.tokens), "Expected phonemes for at least one token"


def test_hybrid_with_override():
    import eng_tts  # noqa: F401
    from eng_tts.core.frame import Token, Utterance
    from eng_tts.core.registry import create

    g = create("g2p", "hybrid")
    g.add_override("foobarbaz", ["F", "UW1"])
    utt = Utterance(text="foobarbaz", tokens=[Token(text="foobarbaz")])
    out = g.annotate(utt)
    assert out.tokens[0].phonemes == ["F", "UW1"]


def test_arpabet_to_ipa():
    from eng_tts.nlp.g2p import arpabet_to_ipa, ipa_to_arpabet

    ipa = arpabet_to_ipa(["HH", "AH0", "L", "OW1"])
    assert "h" in ipa
    back = ipa_to_arpabet(ipa)
    assert isinstance(back, list)
