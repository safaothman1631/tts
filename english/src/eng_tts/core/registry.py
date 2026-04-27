"""Decorator-based plugin registry.

Usage:
    @register("normalizer", "rule_based")
    class RuleBasedNormalizer(INormalizer): ...

    cls = get("normalizer", "rule_based")
"""
from __future__ import annotations

from typing import Any, Callable

_REGISTRY: dict[str, dict[str, type]] = {}


def register(category: str, name: str) -> Callable[[type], type]:
    def _wrap(cls: type) -> type:
        _REGISTRY.setdefault(category, {})[name] = cls
        return cls

    return _wrap


def get(category: str, name: str) -> type:
    try:
        return _REGISTRY[category][name]
    except KeyError as e:
        available = list(_REGISTRY.get(category, {}))
        raise KeyError(
            f"No plugin '{name}' registered under category '{category}'. "
            f"Available: {available}"
        ) from e


def list_plugins(category: str | None = None) -> dict[str, list[str]]:
    if category is not None:
        return {category: list(_REGISTRY.get(category, {}))}
    return {c: list(plugins) for c, plugins in _REGISTRY.items()}


def create(category: str, name: str, *args: Any, **kwargs: Any) -> Any:
    return get(category, name)(*args, **kwargs)
