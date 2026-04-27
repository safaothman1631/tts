# Deployment

## Single-host Docker (recommended)

```bash
docker compose up -d --build
```

- UI listens on `:8080` (Caddy serving static files)
- Engine listens internally as `tts-engine:8000`
- Caddy proxies `/api/*` and `/ws/*` to the engine
- Single origin → no CORS, no token leakage between sub-domains

## Reverse proxy headers

`Caddyfile` sets:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security: max-age=31536000`
- `Permissions-Policy: microphone=(self)` — required for Voice Lab

## Environment variables

| Var               | Where used | Default               |
| ----------------- | ---------- | --------------------- |
| `VITE_API_URL`    | dev only   | `http://localhost:8000` |
| `API_UPSTREAM`    | Caddy      | `tts-engine:8000`     |

## Behind a TLS terminator (Cloudflare / Traefik)

Strip the global `Strict-Transport-Security` line and let the upstream
terminator inject it instead. Caddy itself can also do TLS — replace
`:80 {` with `your.domain {` and Caddy will provision a Let’s Encrypt cert.
