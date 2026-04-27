# NLP pipeline

| Stage | Default impl | Notes |
|-------|--------------|-------|
| SSML parser | `eng_tts.ssml.parser` | xml.etree-based, auto-wraps plain text |
| Normalizer | `RuleBasedNormalizer` | 18+ NSW categories: URL, email, phone, time, date, currency, %, year, decade, ordinal, fraction, decimal, range, math, comma-thousands, integer, Roman numerals, units, hashtag/mention, abbreviations, acronyms |
| Segmenter | `PySBDSegmenter` | Falls back to spaCy → regex |
| Analyzer | `SpacyAnalyzer(en_core_web_sm)` | Falls back to `RegexAnalyzer` |
| Homograph | `RuleBasedHomograph` | ~30 entries with POS-keyed pronunciations |
| G2P | `HybridG2P` | overrides → CMUDict → Neural (g2p-en LSTM) |
| Prosody | `RuleBasedProsody` | breaks (5-level) + pitch/duration contour |
| Sentiment | `LexiconSentiment` | optional `TransformerSentiment` |
| FrameBuilder | `DefaultFrameBuilder` | flattens to phonemes + boundaries |

All stages produce / consume **`Utterance`** objects; the FrameBuilder
finalises them into a **`LinguisticFrame`** for the acoustic model.
