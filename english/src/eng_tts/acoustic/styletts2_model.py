"""StyleTTS2 placeholder backend.

The actual StyleTTS2 implementation requires fairly heavy dependencies
(`styletts2-inference` or community forks). To keep installs small we
keep this as a soft alias to VITS until users install the optional extras.
Replace with a real StyleTTS2 wrapper when available.
"""
from __future__ import annotations

from ..core.registry import register
from .vits_model import VitsAcoustic


@register("acoustic", "styletts2")
class StyleTTS2Acoustic(VitsAcoustic):
    """Soft alias for now — uses VITS until the full StyleTTS2 wrapper is wired."""

    name = "styletts2"
