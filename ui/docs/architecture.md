# Architecture

```
┌──────────────────────┐  HTTP  ┌──────────────────────┐
│   Browser (React)    │◀─────▶│ Caddy reverse proxy  │
│  TanStack Query +    │  WS    │  /api/* → :8000      │
│  Zustand + WaveSurfer│       │  /ws/*  → :8000      │
└──────────────────────┘        └──────────┬───────────┘
                                           ▼
                                ┌──────────────────────┐
                                │   FastAPI eng-tts    │
                                │  Pipeline (9 stages) │
                                └──────────────────────┘
```

## Layers

1. **API layer** (`src/api/`)
   - `client.ts` — axios instance with token interceptor and normalized errors.
   - `endpoints.ts` — typed endpoint functions; every response is parsed by zod.
   - `stream.ts` — typed WebSocket helper for streaming synthesis.

2. **State layer** (`src/stores/` + TanStack Query)
   - `useSettingsStore` — persistent UI prefs (theme, locale, defaults).
   - `useStudioStore` — current text, voice, sliders, audio.
   - `useHistoryStore` — IndexedDB-backed list of recent generations.
   - `useUiStore` — transient flags (sidebar, palette).
   - **Server state lives in TanStack Query**, never duplicated in stores.

3. **Feature layer** (`src/features/<route>`)
   - Each route owns its UI; cross-cutting primitives live under
     `src/components/{ui,layout,audio,common}`.

4. **i18n layer** (`src/i18n/`)
   - `en` + `ckb` JSON catalogs.
   - `<DirectionSync>` toggles `dir="rtl"` for Sorani.

## Design tokens

HSL CSS variables in `src/styles/globals.css`:

- `--background`, `--foreground`, `--primary`, `--card`, `--border`, `--ring`, …
- Light + dark sets controlled by `.dark` class via `next-themes`.

## Build outputs

- `dist/` static assets (hashed JS / CSS / fonts).
- Multi-stage `Dockerfile` produces a Caddy image of < 50 MB.
