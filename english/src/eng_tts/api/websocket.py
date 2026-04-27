"""WebSocket streaming endpoint."""
from __future__ import annotations

import io
import json

import soundfile as sf

from ..core.pipeline import get_default_pipeline

try:
    from fastapi import WebSocket, WebSocketDisconnect
except ImportError:  # pragma: no cover
    WebSocket = object  # type: ignore
    WebSocketDisconnect = Exception  # type: ignore


async def stream_endpoint(ws: "WebSocket") -> None:
    await ws.accept()
    pipe = get_default_pipeline()
    try:
        while True:
            payload = await ws.receive_text()
            try:
                req = json.loads(payload)
            except json.JSONDecodeError:
                await ws.send_text(json.dumps({"error": "invalid_json"}))
                continue
            text = req.get("text", "")
            voice = req.get("voice")
            for chunk in pipe.stream(text, voice=voice):
                buf = io.BytesIO()
                sf.write(buf, chunk.samples, chunk.sample_rate, format="WAV", subtype="PCM_16")
                await ws.send_bytes(buf.getvalue())
            await ws.send_text(json.dumps({"event": "end"}))
    except WebSocketDisconnect:
        return
