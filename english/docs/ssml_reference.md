# SSML reference

Supported subset of W3C SSML 1.1 + custom extensions.

```xml
<speak>
  Hello <break time="500ms"/> world.
  <prosody rate="slow" pitch="+2st" volume="loud">Slow and loud</prosody>
  <emphasis level="strong">important</emphasis>
  <say-as interpret-as="date">2024-12-25</say-as>
  <say-as interpret-as="time">14:30</say-as>
  <say-as interpret-as="characters">FBI</say-as>
  <phoneme alphabet="ipa" ph="təˈmeɪtoʊ">tomato</phoneme>
  <sub alias="World Health Organization">WHO</sub>
  <voice name="en_uk_brit_m">A different voice</voice>
  <p>A paragraph.</p>
  <s>A sentence.</s>
</speak>
```

| Tag | Attributes | Meaning |
|-----|-----------|---------|
| `<break>` | `time` (ms/s) or `strength` (none/weak/medium/strong/x-strong) | Insert a pause |
| `<prosody>` | `rate`, `pitch`, `volume` | Modify acoustic params on children |
| `<emphasis>` | `level` (none/reduced/moderate/strong) | Lexical stress hint |
| `<say-as>` | `interpret-as` (digits/cardinal/date/time/characters/spell-out) | Force interpretation |
| `<phoneme>` | `alphabet` (ipa/arpabet), `ph` | Override G2P |
| `<sub>` | `alias` | Speak the alias instead of the body |
| `<voice>` | `name`, `gender`, `language` | Switch voice for sub-tree |
| `<p>`, `<s>` | – | Paragraph / sentence boundary |

Plain text is auto-wrapped in `<speak>` so callers don't need SSML.
