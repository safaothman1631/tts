# UI MASTER PLAN — TTS Studio
### پلانی گەورەی تەواو بۆ یوئای ریاکت لە لۆکاڵ هۆست

> **نوسەر:** شادۆ مێشک (orchestrator)
> **بەروار:** 2026-04
> **ئەرک:** UI ی شاز و مۆدێرنترین بۆ پڕۆژەی TTS (ئینگلیزی + کوردی)
> **مەنسوب:** local-host فێرستە ئەنجامبدرێت، بێ هیچ vendor lock-in.
> **زمانی پڕۆژە:** TypeScript + React 19
> **زمانی UI:** ئینگلیزی + کوردی (RTL)

---

## 0. خۆلاسە
ئامانج: درووست‌کردنی **TTS Studio** — وێب ئەپلیکەیشنێکی پرۆفیشناڵ کە لەسەر سێرڤەری
لۆکاڵ کاردەکات و بەستراوەتە بە `eng-tts` REST API. هەروەها مۆدیولی کوردیشی هەیە.
دەبێت هاوشێوەی ElevenLabs / Play.ht / Murf بێت لە کوالیتی، بەڵام هەمووی offline.

ئەو UI-ە لە ٣ بەشی سەرەکی پێکدێت:
1. **Studio** — TTS playground (text → audio)
2. **Voice Lab** — voice cloning, library, recording
3. **Projects** — long-form audio (audiobook / podcast)

---

## 1. تێکنۆلۆجی ستاک (Tech Stack)

### Core
| چەند | کاتی هەڵبژاردن |
|---|---|
| **Vite 5** | dev server خێرا، HMR شازە، outputی بچووک |
| **React 19** | concurrent rendering, server components ready |
| **TypeScript 5.5** strict mode | type safety تەواو |
| **React Router v7** (data routes) | routing + loaders + actions |

### State & Data
| چەند | کاتی هەڵبژاردن |
|---|---|
| **TanStack Query v5** | server state, caching, retries, optimistic updates |
| **Zustand** | client-side UI state (theme, sidebar, audio player) |
| **Immer** | immutable updates ئاسان |
| **TanStack Form** | type-safe forms |
| **Zod** | schema validation (API + forms) |

### UI / Design System
| چەند | کاتی هەڵبژاردن |
|---|---|
| **Tailwind CSS v4** | utility-first، خێرا، theme-able |
| **shadcn/ui** | unstyled, copy-paste components |
| **Radix UI** primitives | accessible (a11y باش) |
| **Lucide React** | icon set مۆدێرن |
| **Framer Motion** | animations سپۆکی |
| **Sonner** | toast notifications شاز |
| **next-themes** | dark / light / system |
| **cmdk** | command palette (⌘K) |
| **vaul** | mobile drawer |
| **react-resizable-panels** | layout panels |

### Audio
| چەند | کاتی هەڵبژاردن |
|---|---|
| **WaveSurfer.js v7** | waveform visualizer + regions |
| **howler.js** | audio playback cross-browser |
| **lamejs** | client-side MP3 encode |
| **MediaRecorder API** | voice recording (clone) |
| **Web Audio API** | real-time effects |

### Editor & Misc
| چەند | کاتی هەڵبژاردن |
|---|---|
| **TipTap v2** (ProseMirror) | rich-text + SSML editor |
| **Monaco Editor** | SSML / config code editor |
| **react-markdown** + remark-gfm | render docs |
| **react-hotkeys-hook** | keyboard shortcuts |
| **dnd-kit** | drag & drop |
| **react-virtuoso** | virtual lists (long history) |

### Charts & Viz
| چەند | کاتی هەڵبژاردن |
|---|---|
| **Recharts** | dashboard charts |
| **react-flow** | pipeline visualizer |

### i18n
| چەند | کاتی هەڵبژاردن |
|---|---|
| **i18next** + **react-i18next** | translations |
| **i18next-browser-languagedetector** | auto language detect |
| Kurdish RTL via `dir="rtl"` + `tailwindcss-rtl` plugin |

### Testing
| چەند | کاتی هەڵبژاردن |
|---|---|
| **Vitest** | unit tests |
| **React Testing Library** | component tests |
| **MSW** (Mock Service Worker) | mock API |
| **Playwright** | E2E tests |
| **Storybook 8** | component documentation |
| **Chromatic** (optional) | visual regression |

### Quality
| چەند | کاتی هەڵبژاردن |
|---|---|
| **ESLint** flat config + `@typescript-eslint` | linting |
| **Prettier** + `prettier-plugin-tailwindcss` | formatting |
| **Husky** + **lint-staged** | git hooks |
| **commitlint** + **conventional commits** | commit hygiene |
| **Lighthouse CI** | perf budget |

### Build / Deploy
| چەند | کاتی هەڵبژاردن |
|---|---|
| **pnpm** | package manager (خێرا، disk-efficient) |
| **Turborepo** (optional) | اگر monorepo بکەین |
| **Docker** multi-stage | local-host container |
| **Caddy** یان **nginx** | reverse proxy + HTTPS |

---

## 2. ئارکیتێکتی گشتی

```
┌────────────────────────────────────────────────────┐
│                   Browser (UI)                      │
│  React 19 · TypeScript · Tailwind · shadcn/ui      │
└─────────────┬──────────────────────────┬───────────┘
              │ HTTP/REST                │ WebSocket
              │ (TanStack Query)         │ (streaming)
              ▼                          ▼
┌────────────────────────────────────────────────────┐
│           FastAPI backend (eng-tts)                │
│   /v1/synthesize  /v1/voices  /v1/stream  ...      │
└─────────────┬──────────────────────────────────────┘
              │
              ▼
       eng_tts package (NLP → Acoustic → Audio)
```

دوو سێرڤەر کاردەکەن:
- **Backend:** `uvicorn eng_tts.api.rest:app` لەسەر `:8000`
- **Frontend:** `vite dev` لەسەر `:5173` بە proxy بۆ `:8000`

لە production: یەک container، nginx Caddy serve دەکات frontend-ی build کراو
و proxy دەکات `/api/*` بۆ FastAPI.

---

## 3. پێکهاتەی فۆڵدەرەکان

```
ui/
├── README.md
├── package.json
├── pnpm-lock.yaml
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── tailwind.config.ts
├── postcss.config.js
├── eslint.config.js
├── prettier.config.js
├── components.json              # shadcn config
├── .env.example                 # VITE_API_URL=http://localhost:8000
├── index.html
├── public/
│   ├── favicon.svg
│   ├── logo.svg
│   └── locales/                 # i18n loaded at runtime
│       ├── en/common.json
│       └── ckb/common.json
├── src/
│   ├── main.tsx                 # React entry
│   ├── App.tsx                  # Router + providers
│   ├── router.tsx               # route table
│   ├── env.ts                   # validated env (zod)
│   │
│   ├── api/                     # API client layer
│   │   ├── client.ts            # axios/fetch wrapper
│   │   ├── schemas.ts           # zod schemas matching FastAPI
│   │   ├── tts.ts               # synthesize/stream
│   │   ├── voices.ts            # voice CRUD
│   │   ├── projects.ts          # long-form
│   │   ├── ws.ts                # websocket helper
│   │   └── queries/             # TanStack Query hooks
│   │       ├── use-voices.ts
│   │       ├── use-synthesize.ts
│   │       └── use-health.ts
│   │
│   ├── components/
│   │   ├── ui/                  # shadcn primitives (button, dialog, ...)
│   │   ├── layout/
│   │   │   ├── app-shell.tsx
│   │   │   ├── sidebar.tsx
│   │   │   ├── topbar.tsx
│   │   │   ├── command-palette.tsx
│   │   │   └── theme-toggle.tsx
│   │   ├── audio/
│   │   │   ├── waveform-player.tsx       # WaveSurfer wrapper
│   │   │   ├── audio-controls.tsx        # play/pause/scrub
│   │   │   ├── audio-recorder.tsx        # MediaRecorder
│   │   │   ├── audio-export-menu.tsx     # WAV / MP3 / FLAC
│   │   │   └── ab-compare.tsx            # A/B tier comparison
│   │   ├── editor/
│   │   │   ├── ssml-editor.tsx           # Monaco
│   │   │   ├── rich-text-editor.tsx      # TipTap
│   │   │   └── ssml-toolbar.tsx          # break / prosody / voice
│   │   ├── voices/
│   │   │   ├── voice-card.tsx
│   │   │   ├── voice-grid.tsx
│   │   │   ├── voice-filter.tsx
│   │   │   └── voice-preview-button.tsx
│   │   ├── pipeline/
│   │   │   ├── pipeline-graph.tsx        # react-flow visualizer
│   │   │   └── stage-inspector.tsx       # NLP stage inspector
│   │   └── common/
│   │       ├── empty-state.tsx
│   │       ├── error-boundary.tsx
│   │       ├── loading-skeleton.tsx
│   │       └── icon.tsx
│   │
│   ├── features/                # vertical slices
│   │   ├── studio/
│   │   │   ├── studio-page.tsx
│   │   │   ├── studio-form.tsx
│   │   │   ├── studio-history.tsx
│   │   │   └── store.ts          # zustand slice
│   │   ├── voice-lab/
│   │   │   ├── voice-lab-page.tsx
│   │   │   ├── clone-wizard.tsx
│   │   │   ├── recording-step.tsx
│   │   │   └── upload-step.tsx
│   │   ├── projects/
│   │   │   ├── projects-list.tsx
│   │   │   ├── project-detail.tsx
│   │   │   ├── chapter-list.tsx
│   │   │   └── render-queue.tsx
│   │   ├── analyzer/
│   │   │   ├── analyzer-page.tsx
│   │   │   ├── token-table.tsx
│   │   │   ├── phoneme-view.tsx
│   │   │   └── prosody-chart.tsx
│   │   ├── settings/
│   │   │   ├── settings-page.tsx
│   │   │   ├── general-settings.tsx
│   │   │   ├── audio-settings.tsx
│   │   │   ├── api-settings.tsx
│   │   │   └── shortcuts.tsx
│   │   ├── docs/
│   │   │   ├── docs-page.tsx
│   │   │   └── markdown-viewer.tsx
│   │   └── about/
│   │       └── about-page.tsx
│   │
│   ├── hooks/
│   │   ├── use-debounce.ts
│   │   ├── use-clipboard.ts
│   │   ├── use-media-recorder.ts
│   │   ├── use-keyboard-shortcuts.ts
│   │   ├── use-audio-blob.ts
│   │   └── use-local-storage.ts
│   │
│   ├── lib/
│   │   ├── utils.ts             # cn(), formatters
│   │   ├── audio.ts             # blob → wav, encode mp3
│   │   ├── ssml.ts              # SSML helpers
│   │   ├── format.ts            # duration, bytes
│   │   └── analytics.ts         # opt-in only
│   │
│   ├── stores/                  # zustand global stores
│   │   ├── theme-store.ts
│   │   ├── player-store.ts
│   │   ├── settings-store.ts
│   │   └── history-store.ts
│   │
│   ├── styles/
│   │   ├── globals.css          # tailwind base + tokens
│   │   └── themes.css           # light / dark / brand
│   │
│   ├── i18n/
│   │   ├── index.ts             # i18next init
│   │   └── resources/
│   │       ├── en.ts
│   │       └── ckb.ts
│   │
│   ├── types/
│   │   ├── api.ts
│   │   ├── voice.ts
│   │   └── project.ts
│   │
│   └── test/
│       ├── setup.ts             # vitest setup
│       └── mocks/
│           ├── handlers.ts      # MSW
│           └── server.ts
│
├── tests/
│   └── e2e/
│       ├── studio.spec.ts
│       ├── clone.spec.ts
│       └── settings.spec.ts
│
├── .storybook/
│   ├── main.ts
│   └── preview.ts
│
└── docs/
    ├── architecture.md
    ├── component-library.md
    ├── state-management.md
    ├── i18n.md
    ├── theming.md
    ├── shortcuts.md
    ├── api-integration.md
    └── deployment.md
```

---

## 4. لاپەڕە / ڕووتەکان (Pages / Routes)

| Route | بەش | پێشەکی |
|---|---|---|
| `/` | **Studio** | TTS playground |
| `/voices` | **Voice Library** | لیستی هەموو دەنگەکان |
| `/voices/:id` | **Voice Detail** | preview, samples, metadata |
| `/voice-lab` | **Voice Lab** | clone wizard |
| `/voice-lab/record` | **Recorder** | record reference voice |
| `/projects` | **Projects** | long-form list |
| `/projects/new` | wizard | new project |
| `/projects/:id` | **Project Detail** | chapters, render queue |
| `/projects/:id/edit` | **Editor** | TipTap chapter editor |
| `/analyzer` | **NLP Analyzer** | tokens, phonemes, prosody |
| `/pipeline` | **Pipeline Viz** | react-flow graph |
| `/history` | **History** | virtual list of past renders |
| `/docs` | **Docs Browser** | render markdown docs |
| `/docs/:slug` | doc | individual doc |
| `/settings` | **Settings** | tabs (general/audio/api/shortcuts) |
| `/settings/about` | **About** | version, system info |
| `*` | NotFound | 404 |

### Layout
- **Sidebar** هەمیشە (collapsible) لە دەستچەپ (LTR) یان دەستڕاست (RTL)
- **Topbar:** logo, command palette trigger (⌘K), language switcher, theme toggle, health pill (server status)
- **Main:** route outlet
- **Bottom audio dock** (سته‌هتسین): persistent player کە نمایش بکات گوێگرتن لە هەر کوێیەک

---

## 5. فیچەرە تەواوەکان (Feature Inventory)

### 5.1 Studio (TTS playground)
- Text input بە TipTap (یان simple textarea toggle)
- Toggle: **Plain Text ↔ SSML** (Monaco editor)
- SSML toolbar: insert `<break>`, `<prosody>`, `<emphasis>`, `<phoneme>`, `<voice>`, `<say-as>`
- Voice selector (search + filter by gender/accent/backend)
- Tier selector: `fast` / `premium` / `clone` / `legacy`
- Sliders: speed (0.5–2.0), pitch shift (-12 to +12 st), volume
- "Synthesize" button → progress bar + estimated time
- **Streaming mode** toggle — renders sentence-by-sentence using `/v1/stream` WebSocket
- **WaveSurfer player** with regions (each sentence highlighted)
- Click on text token → seek to that audio position (sync via word boundaries)
- Export: WAV, MP3 (lamejs), FLAC, JSON metadata
- Copy-to-clipboard audio URL
- "Save to history" / auto-save last 50
- Character counter + estimated audio duration
- **A/B compare** — render same text with 2 tiers, switch between them
- Keyboard shortcuts: ⌘Enter render, Space play/pause

### 5.2 Voice Library
- Grid / list toggle
- Filters: gender, accent (US/UK), backend (vits/xtts/legacy), tier
- Search bar (fuse.js fuzzy)
- Voice card: name, gender icon, accent flag, sample wave preview, hover-to-play
- "Set as default" button
- Sort: name, recently used, popularity
- Detail page: long sample, metadata, used-in projects

### 5.3 Voice Lab (Cloning)
Wizard ٥ ستێپ:
1. **Intro** — ethics consent checkbox (پرسی ئەخلاقی)
2. **Source** — record live (MediaRecorder) یان upload
3. **Trim & Preview** — WaveSurfer region selection (6–20s)
4. **Name & Save** — voice name, language hint, gender
5. **Test** — synthesize a test sentence using the new voice
- Recordings saved to backend `/v1/voices/clone` (multipart upload)
- Live waveform during recording
- Noise level meter + clipping warning
- Auto-detect silence and trim

### 5.4 Projects (long-form)
- Project = audiobook, podcast, lecture
- Create wizard: name, language, default voice, output format
- **Chapter list** with drag reorder (dnd-kit)
- Each chapter = TipTap document
- "Render all" → batch job, progress via WebSocket
- Render queue shows: queued, running, done, failed
- Per-chapter: voice override, tier override
- Export: single concatenated WAV/MP3 یان zip of chapters
- Project metadata: cover image, author, description
- Auto-save every 5s

### 5.5 NLP Analyzer
سایدبار شیکاری بۆ توێژینەوە و debug:
- Input text → "Analyze" button
- Tabs:
  - **Tokens** — table: text, lemma, POS, tag, dep, NER, breaks
  - **Phonemes** — ARPABET + IPA side by side
  - **Prosody** — line chart (Recharts) of F0 + duration per token
  - **SSML AST** — JSON tree view (react-json-view)
  - **Sentiment** — score + label
- Hover token → highlight in audio waveform

### 5.6 Pipeline Visualizer
- react-flow node graph showing: Normalizer → Segmenter → Analyzer → Homograph → G2P → Prosody → Acoustic → Vocoder → PostProc
- Click node → inspector panel: implementation name, config, last-run input/output sample
- Live updating during synthesis

### 5.7 History
- Virtual list (react-virtuoso) of last N renders
- Each entry: timestamp, voice, text snippet, duration, audio mini-player, "re-render" / delete
- Stored in IndexedDB (idb-keyval) + audio blob persistence
- Export entire history as zip
- Filter by voice / date range

### 5.8 Settings
Tabs:
- **General:** language (en/ckb), theme, accent color, font size, animations toggle
- **Audio:** default sample rate, default tier, default voice, loudness target (LUFS), output format
- **API:** API base URL, bearer token (stored in IndexedDB encrypted), timeout, retry count
- **Shortcuts:** customizable keybindings (use-hotkeys)
- **Cache:** clear audio cache, clear history, storage usage bar
- **Advanced:** dev tools toggle, log level, send anonymous usage (default off)

### 5.9 Docs Browser
- Sidebar: list of docs from `english/docs/*.md`
- Render with react-markdown + remark-gfm + rehype-highlight
- Search across docs (lunr.js or flexsearch)
- Edit-on-github link (optional)

### 5.10 Command Palette (⌘K)
- Powered by `cmdk`
- Quick navigation, "synthesize current text", "clone voice", "open settings", "toggle theme", search docs

### 5.11 Notifications & Status
- **Sonner** toasts for success/error
- **Server health pill** in topbar — green/yellow/red, click for details
- Long jobs → toast with progress
- Offline detection → banner

### 5.12 Onboarding
- First-launch tour (using `driver.js` یان custom)
- 5 steps: studio → voices → cloning → projects → settings
- Skippable, replay-able from About

### 5.13 Theming
- Light / Dark / System (next-themes)
- 6 accent colors: blue (default), violet, emerald, rose, orange, slate
- Tailwind v4 `@theme` tokens
- Glass morphism cards (optional)
- Smooth transitions (Framer Motion `LayoutGroup`)

### 5.14 Accessibility (a11y)
- All interactive elements ARIA-labeled
- Focus rings (keyboard navigation تەواو)
- `prefers-reduced-motion` ڕێز دەگیرێت
- Color contrast WCAG AA minimum
- Screen reader labels on audio controls
- Skip-to-main link

### 5.15 Performance
- Code splitting per route (React.lazy + Suspense)
- Image lazy-loading
- Audio chunks streamed not buffered
- IndexedDB for offline asset cache
- Service worker (Workbox) for offline shell
- Lighthouse target: 95+ on all categories

### 5.16 Internationalization (i18n)
- زمانەکان: English, کوردی (Sorani CKB)
- RTL support: HTML `dir` toggled، Tailwind `rtl:` variants
- Number, date formats locale-aware (Intl API)
- Switch lang from topbar — instantly applies
- All strings extracted to `locales/{lang}/common.json`

### 5.17 Security
- API token stored in IndexedDB encrypted with WebCrypto
- CSP header set in vite preview / nginx
- No external CDN by default (everything self-hosted)
- Strict CORS rules for FastAPI
- Sanitize markdown render (DOMPurify)

### 5.18 PWA (optional Phase 2)
- Installable, offline-capable shell
- "Add to home screen" prompt
- Background sync for queued renders

---

## 6. State Management Strategy

```
┌─────────────────────────────────────────────┐
│           Server state                      │
│  TanStack Query  (voices, health, render)   │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│           Client UI state                   │
│  Zustand slices:                            │
│   - theme-store                             │
│   - player-store    (current playing audio) │
│   - settings-store  (persisted localStorage)│
│   - history-store   (IndexedDB backed)      │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│           Form state                        │
│  TanStack Form + zod                        │
└─────────────────────────────────────────────┘
```

ڕێگانوێنی: **Server state → TanStack Query**، **UI state → Zustand**، **Form → TanStack Form**.
هیچ Redux نییە — overkill.

---

## 7. API بەرکارهاتن

Schemas (zod) دەرکراون لە `api/schemas.ts` کە یەک بە یەک match دەکەن لەگەڵ
FastAPI Pydantic schemas. هیچ drift ڕوو نادات چونکە سکریپتێکی بچوک
(`scripts/sync-schemas.ts`) ـیان OpenAPI ـی FastAPI fetch دەکات و TypeScript
types generate دەکات بە `openapi-typescript`.

```ts
// api/tts.ts
export const synthesize = async (req: SynthesizeRequest): Promise<SynthesizeResponse> => {
  const res = await client.post('/v1/synthesize', req);
  return SynthesizeResponseSchema.parse(res.data);
};
```

WebSocket helper بۆ streaming:
```ts
export function openStream(text: string, voice?: string): AsyncIterable<Blob> { ... }
```

---

## 8. Design System

### Tokens (Tailwind v4 `@theme`)
```css
@theme {
  --color-bg: 0 0% 100%;
  --color-fg: 240 10% 4%;
  --color-primary: 220 90% 56%;
  --color-accent: 270 95% 65%;
  --radius-md: 0.75rem;
  --font-sans: 'Inter Variable', 'NotoNaskhArabicVariable', sans-serif;
}
```

### Typography
- **Latin:** Inter Variable
- **Arabic/Kurdish:** Noto Naskh Arabic Variable
- Font sizes: 12 / 14 / 16 / 18 / 24 / 32 / 48
- Line height tokens: tight / normal / relaxed

### Spacing scale: 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64

### Component variants (cva)
- Buttons: primary / secondary / ghost / destructive / outline · sizes sm/md/lg/icon
- Cards: default / elevated / glass / outline
- Inputs: default / error / success states

### Motion
- Page transitions: 200ms easeOut
- Dialogs: spring (Framer Motion)
- Skeletons shimmer
- Audio waveform smooth scrubbing

---

## 9. Storybook

ـ هەر componentێک (شاد) Story هەیە
- Categories: `Atoms / Molecules / Organisms / Pages`
- A11y addon, controls, viewport (mobile/tablet/desktop)
- MSW addon بۆ mock API
- Dark/light theme toggle
- Auto-deployed بۆ `:6006` لۆکاڵ

---

## 10. Testing Strategy

### Unit (Vitest)
- helpers, utils, hooks
- coverage target: 80%

### Component (RTL + Vitest)
- هەر `features/**` ـی سەرەکی testی هەیە
- snapshot-free — interaction tests

### Integration (RTL + MSW)
- پەیجی Studio: type → render → audio appears

### E2E (Playwright)
- 5 critical flows:
  1. Synthesize plain text
  2. Switch voice + tier
  3. Clone voice (mocked recording)
  4. Create project + render chapter
  5. Change settings + persist after reload

### Visual (Storybook + Chromatic — optional)

### Performance
- Lighthouse CI in pipeline
- Bundle size budget: < 250KB gzipped initial

---

## 11. Deployment (Local Host)

### Option A — Dev mode
```bash
pnpm dev          # vite :5173 with proxy to :8000
```

### Option B — Docker compose (recommended)
`docker-compose.yml` دوو سێرڤیس:
- `api` — eng-tts FastAPI container (موجود)
- `ui` — multi-stage: build vite → serve via Caddy on `:80`

Caddyfile:
```
:80 {
  root * /usr/share/caddy
  try_files {path} /index.html
  file_server
  reverse_proxy /api/* api:8000
}
```

ـئنجامگیری: `http://localhost` تەنها — UI و API لەسەر یەک origin.

### Option C — Standalone Tauri (Phase 2 optional)
Wrap بۆ desktop app cross-platform.

---

## 12. Documentation

هەموو فایلێک بنیادکراو لە `ui/docs/`:

| فایل | پێویستی |
|---|---|
| `README.md` | quick start، scripts، structure |
| `docs/architecture.md` | overall + diagram |
| `docs/component-library.md` | atoms/organisms catalogue |
| `docs/state-management.md` | zustand + tanstack patterns |
| `docs/i18n.md` | how to add new locale, RTL rules |
| `docs/theming.md` | tokens, accent colors, dark mode |
| `docs/shortcuts.md` | keyboard map |
| `docs/api-integration.md` | schema sync, error handling |
| `docs/audio.md` | wavesurfer setup, encoding |
| `docs/deployment.md` | Docker, Caddy, env vars |
| `docs/testing.md` | unit/e2e/storybook |
| `docs/contributing.md` | branching, commits, PR |
| `docs/roadmap.md` | phases و چی دێت |
| Storybook itself = component docs |

پلوس JSDoc لەسەر هەموو exportی public.

---

## 13. Phases

### **Phase 0 — Bootstrap** (ڕۆژێک)
- pnpm + vite + ts + tailwind + shadcn + eslint + prettier + husky
- folder skeleton + basic providers (theme, router, query, i18n)
- API client + zod schemas (fetch from FastAPI OpenAPI)
- AppShell layout + sidebar + topbar + theme toggle + ⌘K palette
- Health endpoint pill — proves wire-up works
- Storybook init

### **Phase 1 — Studio MVP**
- Studio page: textarea → voice select → tier → speed → synthesize → audio
- WaveSurfer player + basic export (WAV)
- TanStack Query mutation
- Toast notifications
- History (in-memory, last 20)
- 10 unit tests + 1 E2E test
- i18n English baseline

### **Phase 2 — Voice Library**
- `/voices` page with grid + filter + search + preview-on-hover
- Voice detail page
- "Set as default" via settings store
- shadcn dialog for "About this voice"

### **Phase 3 — SSML Editor + Analyzer**
- Monaco SSML editor with custom language definition (highlights, autocomplete)
- SSML toolbar (insert tags)
- `/analyzer` page: tokens table + phoneme view + prosody chart
- Pipeline visualizer (react-flow) — read-only

### **Phase 4 — Voice Lab (cloning)**
- Wizard component (5 steps)
- MediaRecorder hook + waveform live preview
- Upload alternative
- POST /v1/voices/clone (multipart)
- Test step

### **Phase 5 — Projects (long-form)**
- Projects list + create wizard
- TipTap chapter editor
- Drag-reorder chapters (dnd-kit)
- Batch render queue (WebSocket progress)
- Export concatenated audio
- IndexedDB project persistence

### **Phase 6 — Polish**
- Full Kurdish (CKB) translations + RTL
- 6 accent colors + glass theme
- All keyboard shortcuts wired
- Onboarding tour
- Empty states & error boundaries
- Lighthouse pass (≥95)
- Service worker offline shell

### **Phase 7 — Docs & deployment**
- All `ui/docs/*.md` written
- Storybook deployed
- Multi-stage Dockerfile + docker-compose update
- Caddy config
- Playwright suite green in CI
- Release v1.0.0

---

## 14. Roadmap (Future)

- v1.1 — User accounts (multi-user local)
- v1.2 — Audio editing timeline (cuts, fades, layers)
- v1.3 — Real-time collaboration (yjs)
- v1.4 — Tauri desktop build
- v1.5 — Mobile companion (Expo)
- v2.0 — Plugin system (custom acoustic backends loadable from UI)

---

## 15. Acceptance Criteria (هەنگاوی کۆتایی)

- [ ] `pnpm dev` کار دەکات و UI بە API بەستراوە
- [ ] هەموو ٧+ پەیجی سەرەکی هەن و ناوبژیون
- [ ] Synthesize → audio plays لە <2s بۆ ١٠ ووشە
- [ ] Voice cloning کار دەکات end-to-end
- [ ] Project بە ٥+ chapter دەتوانرێت render بکرێت
- [ ] Dark/light + 6 accent colors کاردەکەن
- [ ] کوردی + ئینگلیزی + RTL تەواو
- [ ] Lighthouse ≥ 95 لە هەموو categoriesدا
- [ ] Storybook ڕووخسارەکان نمایش دەکات
- [ ] Playwright E2E ئەنجام دەدات هەموو ٥ flow ـی سەرەکی
- [ ] Docker compose یەک command up دەکات
- [ ] هەموو docs فایلەکان نوسراون

---

## 16. تێبینی کۆتایی (شادۆ مێشک)

- **هەرگیز** vendor-lock نەکە — هەموو شت self-hosted، هیچ Auth0 / Vercel / Firebase
- **هەرگیز** وەرگرتنی emoji لە کۆد یان UI نییە مەگەر داوا بکرێت
- **شیر بە** اسلوبی Karpathy: think → simplest → minimal diff → verify
- **ڕیزە** لە RTL — هیچ مارجن یان padding `left/right` بەکار نەهێنرێت، تەنها `start/end`
- **پسێکۆلۆجی** بەکارهێنەر — کاتی چاوەڕێ کردنی synth، نمایشی progress + ESL
- **Privacy first** — هیچ telemetry بێ ڕێگەپێدان

> **تۆ ئامادەی، ئێستا تۆ شادۆ پلانساز چاو بکەرە بۆ ئەنجامدان.**

