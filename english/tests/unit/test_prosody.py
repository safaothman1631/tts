def test_breaks_for_punctuation():
    import eng_tts  # noqa: F401
    from eng_tts.core.frame import Token, Utterance
    from eng_tts.core.registry import create

    p = create("prosody", "rule_based")
    utt = Utterance(text="Hello, world.", tokens=[
        Token(text="Hello", pos="INTJ"),
        Token(text=",", pos="PUNCT", is_punct=True),
        Token(text="world", pos="NOUN"),
        Token(text=".", pos="PUNCT", is_punct=True),
    ])
    out = p.predict(utt)
    # First word should have a minor break after the comma
    assert out.tokens[0].break_after >= 2 or any(t.break_after >= 2 for t in out.tokens)


def test_durations_assigned():
    import eng_tts  # noqa: F401
    from eng_tts.core.frame import Token, Utterance
    from eng_tts.core.registry import create

    p = create("prosody", "rule_based")
    utt = Utterance(text="hello", tokens=[
        Token(text="hello", pos="INTJ", phonemes=["HH", "AH0", "L", "OW1"]),
    ])
    out = p.predict(utt)
    assert out.tokens[0].duration > 0
