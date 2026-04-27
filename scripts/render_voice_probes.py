"""Render a probe sentence with every voice character and emit an HTML grid.

Useful for human A/B listening to verify the catalog is audibly distinct.
Outputs:
    output/probes/<character_id>.wav
    output/probes/index.html

Usage:
    python scripts/render_voice_probes.py --tier qwen3
    python scripts/render_voice_probes.py --filter arch- --limit 50
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from html import escape
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "output" / "probes"
PROBE_TEXT = (
    "The quick brown fox jumps over the lazy dog. "
    "I will tell you a story you have never heard before, where every voice "
    "stands clearly apart from the next."
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="http://127.0.0.1:8765")
    parser.add_argument("--tier", default="qwen3")
    parser.add_argument("--filter", default="", help="Only ids containing this substring.")
    parser.add_argument("--limit", type=int, default=0, help="0 = no limit.")
    parser.add_argument("--text", default=PROBE_TEXT)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)

    print(f"[fetch] catalog from {args.api}/v1/voice-characters")
    resp = requests.get(f"{args.api}/v1/voice-characters", params={"limit": 1000}, timeout=15)
    resp.raise_for_status()
    items = resp.json()["items"]
    if args.filter:
        items = [c for c in items if args.filter in c["id"]]
    if args.limit:
        items = items[: args.limit]
    print(f"[fetch] {len(items)} characters to render")

    rendered = []
    for i, c in enumerate(items, 1):
        wav_path = OUT / f"{c['id']}.wav"
        if args.skip_existing and wav_path.exists() and wav_path.stat().st_size > 1000:
            print(f"  [{i:3d}/{len(items)}] skip {c['id']} (cached)")
            rendered.append(c)
            continue
        body = {
            "text": args.text,
            "voice_character": c["id"],
            "format": "wav",
            "tier": args.tier,
        }
        t0 = time.time()
        try:
            r = requests.post(
                f"{args.api}/v1/synthesize.wav",
                json=body,
                timeout=args.timeout,
                headers={"Content-Type": "application/json"},
            )
            if r.status_code != 200:
                print(f"  [{i:3d}/{len(items)}] FAIL {c['id']} -> HTTP {r.status_code}")
                continue
            wav_path.write_bytes(r.content)
            print(f"  [{i:3d}/{len(items)}] OK   {c['id']:36s}  {len(r.content)//1024} KB  {time.time()-t0:.1f}s")
            rendered.append(c)
        except Exception as e:
            print(f"  [{i:3d}/{len(items)}] ERR  {c['id']} -> {e}")

    # ---- emit index.html
    src_badge = {
        "qwen_named": ("synth-only", "#9ca3af"),
        "qwen_clone": ("cloned", "#10b981"),
        "piper":      ("piper",     "#6366f1"),
    }
    html = ['<!doctype html><html><head><meta charset="utf-8">',
            '<title>Voice character probes</title>',
            '<style>',
            'body{font-family:ui-sans-serif,system-ui;background:#0b0b10;color:#e7e7ec;margin:24px}',
            'h1{font-size:20px;margin:0 0 16px}',
            '.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px}',
            '.card{background:#16161e;border:1px solid #25252f;border-radius:10px;padding:14px}',
            '.name{font-weight:600;font-size:14px;margin-bottom:2px}',
            '.tag{font-size:11px;color:#a8a8b3;margin-bottom:8px}',
            '.badge{display:inline-block;font-size:10px;padding:2px 6px;border-radius:4px;color:#fff;margin-right:4px}',
            'audio{width:100%;margin-top:8px}',
            '.q{margin:8px 0 12px;padding:10px;background:#13131a;border-radius:8px;font-size:13px;color:#c8c8d2}',
            '.row{display:flex;gap:6px;flex-wrap:wrap;font-size:11px;color:#888}',
            '</style></head><body>',
            f'<h1>Voice character probes ({len(rendered)} voices)</h1>',
            f'<div class="q">{escape(args.text)}</div>',
            '<div class="grid">']
    for c in rendered:
        label, color = src_badge.get(c.get("source_type", ""), ("", "#666"))
        html.append('<div class="card">')
        html.append(f'<div class="name">{escape(c["name"])}</div>')
        html.append(f'<div class="tag">{escape(c.get("tagline", "") or c.get("description", "")[:60])}</div>')
        html.append(f'<span class="badge" style="background:{color}">{label}</span>')
        html.append(f'<span class="badge" style="background:#374151">{escape(c["category"])}</span>')
        html.append(f'<span class="badge" style="background:#374151">{escape(c["accent"])}</span>')
        html.append(f'<span class="badge" style="background:#374151">{escape(c["gender"])}</span>')
        html.append(f'<audio controls preload="none" src="{escape(c["id"])}.wav"></audio>')
        html.append(f'<div class="row">id: {escape(c["id"])}  ·  speaker: {escape(c["speaker_id"])}  ·  pitch: {c.get("pitch_offset", 0)}  ·  speed: {c.get("speed_offset", 0)}</div>')
        html.append('</div>')
    html.append('</div></body></html>')
    (OUT / "index.html").write_text("\n".join(html), encoding="utf-8")

    print(f"\nDone. Open: {OUT / 'index.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
