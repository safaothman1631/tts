"""Structured logging via structlog."""
from __future__ import annotations

import logging
import sys
from typing import Any

try:
    import structlog
except ImportError:  # pragma: no cover
    structlog = None  # type: ignore[assignment]


_CONFIGURED = False


def setup_logging(level: str = "INFO") -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    log_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=log_level,
    )

    if structlog is not None:
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.dev.ConsoleRenderer(colors=True),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(log_level),
            logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
            cache_logger_on_first_use=True,
        )
    _CONFIGURED = True


def get_logger(name: str = "eng_tts") -> Any:
    if structlog is not None:
        return structlog.get_logger(name)
    return logging.getLogger(name)
