def test_parse_basic():
    from eng_tts.ssml import is_ssml, parse, walk

    txt = '<speak>Hello <break time="200ms"/> world.</speak>'
    assert is_ssml(txt)
    root = parse(txt)
    spans = list(walk(root))
    assert len(spans) >= 2
    assert any(s.is_break for s in spans)


def test_prosody_inheritance():
    from eng_tts.ssml import parse, walk

    txt = '<speak><prosody rate="slow"><emphasis level="strong">Hi</emphasis></prosody></speak>'
    root = parse(txt)
    spans = [s for s in walk(root) if s.text]
    assert spans
    assert spans[0].rate == "slow"
    assert spans[0].emphasis == "strong"


def test_plain_text_wrapped():
    from eng_tts.ssml import is_ssml, parse, walk

    s = "Just a plain sentence."
    assert not is_ssml(s)
    root = parse(s)
    spans = [x for x in walk(root) if x.text]
    assert spans[0].text.strip() == s
