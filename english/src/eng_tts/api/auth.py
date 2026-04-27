"""Optional bearer-token auth helpers."""
from __future__ import annotations

import os
from typing import Optional

try:
    from fastapi import Header, HTTPException
except ImportError:  # pragma: no cover
    def Header(*_a, **_k):  # type: ignore
        return None
    HTTPException = Exception  # type: ignore


def require_token(authorization: Optional[str] = Header(None)) -> None:
    expected = os.environ.get("ENG_TTS_API_TOKEN")
    if not expected:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if token != expected:
        raise HTTPException(status_code=401, detail="invalid token")
