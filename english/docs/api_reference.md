# HTTP API reference

Start the server:

```bash
eng-tts serve --host 0.0.0.0 --port 8000
# or
uvicorn eng_tts.api.rest:app --host 0.0.0.0 --port 8000
```

## Endpoints

### `GET /v1/health`
```json
{ "status": "ok", "version": "0.1.0", "device": "cpu" }
```

### `GET /v1/capabilities`
Returns supported languages, formats, tiers, controls, endpoints, and feature
availability such as `voice_clone`, `streaming`, and custom voice persistence.

### `GET /v1/voices`
Returns the list of voices known to the engine.

### `GET /v1/voices/{voice_id}`
Returns one built-in or custom voice descriptor.

### `DELETE /v1/voices/{voice_id}`
Deletes a custom voice descriptor. Built-in voices are not deleted through this endpoint.

### `POST /v1/voices/clone`
Creates a custom voice descriptor from a consented reference recording.

Multipart fields:
- `name` (required)
- `consent` (required, must be true)
- `audio` (required file; WAV preferred)
- `description` (optional)
- `language` (optional, default `en`)
- `gender` (optional, default `neutral`)
- `reference_text` (optional)

Response: a `VoiceDescriptor` with `custom=true` and `supports_clone=true`.
The stored reference audio is automatically used as `speaker_wav` when that
custom voice is selected for synthesis.

Decodable uploads are validated for practical clone quality: 1-120 seconds,
non-silent signal, and no heavy clipping.

### `POST /v1/synthesize`
Body:
```json
{
  "text": "Hello world.",
  "voice": "en_us_neutral_f",
  "tier": "fast",
  "speed": 1.0,
  "pitch_shift": 0.0,
  "volume": 1.0,
  "style_prompt": "A clear, natural narration voice.",
  "speaker_wav": null,
  "format": "wav"
}
```
Response: JSON with base64-encoded WAV.

### `POST /v1/synthesize.wav`
Same request body as above; returns raw `audio/wav` bytes.

### `POST /v1/synthesize/segments`
Creates one WAV from multiple text segments, each with its own voice/prosody
controls. Returns JSON with base64 WAV audio.

Body:
```json
{
  "segments": [
    {
      "text": "Narrator line.",
      "voice": "piper_en_us_lessac_medium",
      "tier": "piper",
      "speed": 1.0,
      "pitch_shift": 0.0,
      "volume": 1.0,
      "style_prompt": "Natural narration.",
      "pause_after_ms": 120
    }
  ],
  "format": "wav"
}
```

### `POST /v1/synthesize/segments.wav`
Same request body as `/v1/synthesize/segments`; returns raw `audio/wav` bytes
with segment count and duration headers.

### `POST /v1/stream`
Same request body as `/v1/synthesize`; returns one valid `audio/wav` response
as streamed chunks with duration/sample-rate headers.

### `GET /metrics`
Prometheus exposition format.

### Auth
Set `ENG_TTS_API_TOKEN=<token>` to enable bearer-token auth on
write endpoints (use the helper in `eng_tts.api.auth`).

## UI Integration Notes (TTS Studio)

- UI runtime maps `/api/*` to backend `/v1/*` via Vite proxy.
- Typical local UI proxy target is `http://127.0.0.1:8765` (wrapper service),
  while engine examples above may run directly on `:8000`.
- UI contract mapping is documented in `docs/API_CONTRACT_MATRIX.md`.

### Contract Expectations used by UI
- `GET /v1/voices` may be either:
  - `{ "voices": [...] }`, or
  - direct array `[...]`
- `POST /v1/synthesize.wav` should return WAV bytes. If empty/204, UI may
  fall back to `POST /v1/synthesize` expecting `audio_base64`.
- `volume` is applied server-side as final audio gain. `style_prompt` is passed
  to capable acoustic backends such as Qwen-style custom voice models.
- `POST /v1/voices/clone` is implemented for custom voice descriptors. UI still
  keeps local fallback behavior for older/degraded deployments.
