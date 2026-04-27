# Getting started

## Requirements

- Node.js ≥ 20
- pnpm ≥ 9 (`npm i -g pnpm`)
- The `eng-tts` FastAPI engine reachable at `http://localhost:8000`

## Install & run

```bash
cd ui
pnpm install
cp .env.example .env.local         # adjust if your engine is elsewhere
pnpm dev
```

Open <http://127.0.0.1:5173>. Vite proxies `/api/*` → `http://localhost:8000`,
so no CORS configuration is needed in the engine.

## First synthesis

1. Type something into the text editor on the **Studio** page.
2. Pick a voice from the right panel (defaults to engine default).
3. Press **Synthesize** (or `Ctrl+Enter`).
4. Audio appears in the player; `Download` saves it to disk.

## Keyboard shortcuts

| Action               | Shortcut         |
| -------------------- | ---------------- |
| Command palette      | `Ctrl/⌘ + K`     |
| Synthesize           | `Ctrl/⌘ + Enter` |
| Settings             | `Ctrl/⌘ + ,`     |
| Toggle theme         | `Ctrl/⌘ + Shift + L` |
