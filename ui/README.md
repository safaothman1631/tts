# TTS Studio — UI

A modern, accessible, fully self-hosted React UI for the
[`eng-tts`](../english) engine.

## Stack

- **React 19** + **TypeScript 5.6** (strict)
- **Vite 5** dev server with API proxy
- **Tailwind CSS 3.4** with HSL token design system, light + dark
- **shadcn/ui** primitives over **Radix UI**
- **TanStack Query 5** (server state) + **Zustand** (UI state)
- **Zod** schemas validate every API response
- **WaveSurfer.js 7** waveform player
- **i18next** with English + Kurdish (Sorani CKB) and full RTL
- **cmdk** command palette (⌘K)
- **next-themes** + reduce-motion + high-contrast modes
- **Vitest** + **@testing-library/react** unit tests
- **Playwright** E2E tests
- **Storybook 8** isolated component dev (configured via `pnpm storybook`)
- **Docker** + **Caddy** single-origin production deployment

## Routes

| Path           | Page                |
| -------------- | ------------------- |
| `/`            | Studio (text → audio, controls, player) |
| `/voices`      | Voice library (search, filters, grid)   |
| `/voice-lab`   | 5-step voice cloning wizard             |
| `/projects`    | Long-form project workspace             |
| `/analyzer`    | NLP analyzer (tokens, phonemes, prosody)|
| `/pipeline`    | Pipeline visualizer (9 stages)          |
| `/history`     | Local IndexedDB-backed generation log   |
| `/settings`    | General · Audio · API · Shortcuts · Adv |
| `/docs`        | Documentation index                     |
| `/about`       | App info                                |
| `*`            | 404                                     |

## Scripts

```bash
pnpm install
pnpm dev              # http://127.0.0.1:5173 (proxies /api → :8765)
pnpm build && pnpm preview
pnpm test             # vitest
pnpm test:e2e         # playwright
pnpm lint && pnpm typecheck
pnpm storybook
```

## Configuration

Create `.env.local`:

```env
VITE_API_URL=http://127.0.0.1:8765
VITE_DEFAULT_LOCALE=en
```

In production the UI talks to its own origin and Caddy proxies
`/api/*` and `/ws/*` to the engine — no CORS required.

## Production

```bash
docker compose up -d --build
# UI:        http://localhost:8080
# Engine:    proxied internally as tts-engine:8000
```

## Folder Structure

```
src/
├─ api/           # axios client, endpoints, WebSocket stream
├─ app/           # providers, router
├─ components/
│  ├─ audio/     # AudioPlayer (WaveSurfer)
│  ├─ common/    # ErrorBoundary
│  ├─ layout/    # AppShell · Sidebar · Topbar · CommandPalette
│  └─ ui/        # shadcn-style primitives (Button, Card, Slider, …)
├─ features/      # one folder per route (studio, voices, voice-lab, …)
├─ hooks/         # useGlobalShortcuts, useSynthesize, queries
├─ i18n/          # en/, ckb/, RTL detection
├─ lib/           # utils, config
├─ stores/        # zustand (settings, studio, history, ui)
├─ styles/        # globals.css (tokens, fonts, scrollbar)
├─ test/          # vitest setup + unit tests
└─ types/         # zod-derived API types
```

## Accessibility

- All interactives are keyboard-reachable, focus-ring respected.
- Reduce-motion + high-contrast switches honored.
- RTL via `dir="rtl"`; only logical CSS properties (`start`/`end`).
- Screen-reader labels on every icon-only button.

## License

MIT
