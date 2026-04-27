def test_lead_noun_vs_verb():
    import eng_tts  # noqa: F401
    from eng_tts.core.frame import Token, Utterance
    from eng_tts.core.registry import create

    h = create("homograph", "rule_based")

    # Noun: "the lead pipe"
    noun = Utterance(text="the lead pipe", tokens=[
        Token(text="the", pos="DET"),
        Token(text="lead", pos="NOUN", tag="NN"),
        Token(text="pipe", pos="NOUN"),
    ])
    out = h.disambiguate(noun)
    assert out.tokens[1].phonemes  # set by override

    # Verb: "I will lead the team"
    verb = Utterance(text="I will lead the team", tokens=[
        Token(text="I", pos="PRON"),
        Token(text="will", pos="AUX"),
        Token(text="lead", pos="VERB", tag="VB"),
        Token(text="the", pos="DET"),
        Token(text="team", pos="NOUN"),
    ])
    out2 = h.disambiguate(verb)
    assert out2.tokens[2].phonemes
    # The two should differ
    assert out.tokens[1].phonemes != out2.tokens[2].phonemes
