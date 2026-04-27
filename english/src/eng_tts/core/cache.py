"""Three-tier caching: in-memory LRU, on-disk persistent."""
from __future__ import annotations

import hashlib
import functools
from pathlib import Path
from typing import Any, Callable

try:
    import diskcache
except ImportError:  # pragma: no cover
    diskcache = None


def memoize(maxsize: int = 8192) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """LRU memoize decorator, hashable args only."""
    return functools.lru_cache(maxsize=maxsize)


class DiskCache:
    """Thin wrapper around diskcache.Cache. Falls back to no-op if unavailable."""

    def __init__(self, directory: str | Path, size_limit: int = 1 << 30) -> None:
        self.directory = Path(directory)
        self._cache: Any = None
        if diskcache is not None:
            self.directory.mkdir(parents=True, exist_ok=True)
            self._cache = diskcache.Cache(str(self.directory), size_limit=size_limit)

    def get(self, key: str, default: Any = None) -> Any:
        if self._cache is None:
            return default
        return self._cache.get(key, default=default)

    def set(self, key: str, value: Any, expire: float | None = None) -> None:
        if self._cache is None:
            return
        self._cache.set(key, value, expire=expire)

    def clear(self) -> None:
        if self._cache is not None:
            self._cache.clear()

    def __contains__(self, key: str) -> bool:
        return self._cache is not None and key in self._cache


def hash_key(*parts: Any) -> str:
    """Stable string key from any printable parts."""
    h = hashlib.sha256()
    for p in parts:
        h.update(repr(p).encode("utf-8"))
        h.update(b"|")
    return h.hexdigest()
