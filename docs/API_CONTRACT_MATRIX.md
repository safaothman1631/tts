# API Contract Matrix (UI <-> Backend)

## Base
- UI dev origin: http://127.0.0.1:5173
- Vite proxy: /api -> http://127.0.0.1:8765 (rewrite strips /api)
- Source of truth for client mapping: ui/src/api/endpoints.ts

## Endpoint Matrix

| UI Function | UI Request Path | Backend Expectation | Response Contract | Fallback Class |
|---|---|---|---|---|
| getHealth | GET /api/v1/health | GET /v1/health | HealthSchema | B |
| capabilities | GET /api/v1/capabilities | GET /v1/capabilities | languages/formats/tiers/controls/endpoints | B |
| listVoices | GET /api/v1/voices | GET /v1/voices | Voice[] including built-in + custom voices | C |
| getVoice | GET /api/v1/voices/:id | GET /v1/voices/{id} | VoiceSchema | C |
| deleteVoice | DELETE /api/v1/voices/:id | DELETE /v1/voices/{id} | 204/200 | A |
| cloneVoice | POST /api/v1/voices/clone | POST /v1/voices/clone multipart(name, consent, audio, optional metadata) | VoiceSchema with custom=true/supports_clone=true | B |
| synthesize | POST /api/v1/synthesize.wav | POST /v1/synthesize.wav | WAV blob + meta headers | B |
| synthesize fallback | POST /api/v1/synthesize | POST /v1/synthesize | { audio_base64, sample_rate?, duration_seconds? } | B |
| synthesize segments | POST /api/v1/synthesize/segments.wav | POST /v1/synthesize/segments.wav | WAV blob composed from per-segment voice/prosody controls | B |
| synthesize segments fallback | POST /api/v1/synthesize/segments | POST /v1/synthesize/segments | { audio_base64, sample_rate, duration_seconds } | B |
| streamSynthesize | POST /api/v1/stream | POST /v1/stream | streamed single WAV blob | B |
| analyzeText | POST /api/v1/analyze | POST /v1/analyze | NlpAnalysisSchema | B |

## Contract Notes
- Voice clone is implemented on the backend and persists custom voice descriptors under the engine output directory.
- UI enables clone upload by default via VITE_ENABLE_VOICE_CLONE_ENDPOINT=true semantics, and keeps local fallback if endpoint/model capability is unavailable.
- UI attempts to convert recorded browser audio to WAV before upload; if conversion is unavailable, backend still stores the reference file and returns a custom voice descriptor.
- Synthesis with a custom voice resolves its stored speaker reference automatically through the backend voice catalog.
- Synthesis accepts `volume` and `style_prompt`; `volume` is applied by backend audio scaling and `style_prompt` is passed to capable models.
- Multi-segment synthesis accepts per-segment `text`, `voice`, `tier`, `speed`, `pitch_shift`, `volume`, `style_prompt`, and `pause_after_ms` for multi-voice/rhythm output.
- Synthesize endpoint tolerates 204/empty WAV by using JSON fallback endpoint.
- Health endpoint failure maps to `{ status: 'down' }` for resilient UI behavior.

## Change Rules
- Any backend contract change must update:
  - english/docs/api_reference.md
  - ui/src/types/api.ts
  - ui/src/api/endpoints.ts
  - this file (docs/API_CONTRACT_MATRIX.md)

## Verification Checklist
- [ ] Type schemas aligned (Zod)
- [ ] Endpoint paths aligned
- [ ] Status/error behavior aligned
- [ ] Fallback behavior documented
- [ ] E2E scenario exists for degraded mode
