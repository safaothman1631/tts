"""Typer-based CLI: `eng-tts say "..."`."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..config import get_settings
from ..core.pipeline import TTSPipeline
from ..core.registry import list_plugins
from ..version import __version__

app = typer.Typer(add_completion=False, help="eng-tts CLI — World-class English TTS")
console = Console()


def _pipeline() -> TTSPipeline:
    return TTSPipeline()


@app.command("version")
def version() -> None:
    """Print version."""
    console.print(f"eng-tts {__version__}")


@app.command("say")
def say(
    text: str = typer.Argument(..., help="Text or SSML to synthesize"),
    output: Path = typer.Option(Path("output/say.wav"), "--out", "-o", help="Output WAV path"),
    voice: Optional[str] = typer.Option(None, "--voice", "-v", help="Voice id"),
    tier: Optional[str] = typer.Option(None, "--tier", "-t", help="fast | premium | clone | legacy"),
    speed: float = typer.Option(1.0, "--speed", help="Speed multiplier"),
    speaker_wav: Optional[Path] = typer.Option(None, "--clone", help="Reference WAV for voice cloning"),
    play: bool = typer.Option(False, "--play", help="Try to play audio after synthesis"),
) -> None:
    """Synthesize text to a WAV file."""
    s = get_settings()
    if tier:
        s.acoustic_tier = tier  # type: ignore[assignment]
    pipe = TTSPipeline(settings=s)
    output.parent.mkdir(parents=True, exist_ok=True)
    chunk = pipe.synthesize(
        text=text,
        voice=voice,
        speed=speed,
        speaker_wav=speaker_wav,
        output_path=output,
    )
    console.print(
        f"[green]✓[/green] Wrote {output} "
        f"({chunk.metadata.get('duration_s', 0):.2f}s @ {chunk.sample_rate} Hz)"
    )
    if play:
        _play(output)


@app.command("analyze")
def analyze(text: str = typer.Argument(..., help="Text to analyze (no audio)")) -> None:
    """Run only the NLP front-end and print the result."""
    pipe = _pipeline()
    utts = pipe.analyze(text)
    for i, u in enumerate(utts, 1):
        console.rule(f"Sentence {i}")
        table = Table(show_header=True, header_style="bold")
        table.add_column("Token")
        table.add_column("POS")
        table.add_column("Phonemes")
        table.add_column("Brk")
        for t in u.tokens:
            table.add_row(
                t.text,
                t.pos,
                " ".join(t.phonemes) or "-",
                str(t.break_after),
            )
        console.print(table)
        console.print(f"sentiment={u.sentiment} score={u.sentiment_score:.2f}")


@app.command("normalize")
def normalize(text: str = typer.Argument(...)) -> None:
    """Show the normalized form of text (NSW expansion)."""
    from ..nlp.normalizer import RuleBasedNormalizer

    n = RuleBasedNormalizer()
    console.print(n.normalize(text))


@app.command("voices")
def voices() -> None:
    """List built-in voices."""
    pipe = _pipeline()
    table = Table(show_header=True, header_style="bold")
    for col in ("id", "name", "gender", "accent", "backend", "model"):
        table.add_column(col)
    for v in pipe.list_voices():
        table.add_row(v.id, v.name, v.gender, v.accent, v.backend, v.model)
    console.print(table)


@app.command("plugins")
def plugins() -> None:
    """List all registered plugin categories and names."""
    # Trigger registrations
    import importlib

    for mod in (
        "eng_tts.nlp.normalizer.rule_based",
        "eng_tts.nlp.segmentation",
        "eng_tts.nlp.linguistic",
        "eng_tts.nlp.homograph.disambiguator",
        "eng_tts.nlp.g2p.lexicon",
        "eng_tts.nlp.g2p.neural",
        "eng_tts.nlp.g2p.hybrid",
        "eng_tts.nlp.prosody.predictor",
        "eng_tts.nlp.sentiment",
        "eng_tts.acoustic.legacy_pyttsx3",
        "eng_tts.acoustic.vits_model",
        "eng_tts.acoustic.xtts_model",
        "eng_tts.acoustic.styletts2_model",
        "eng_tts.vocoder.hifigan",
        "eng_tts.postproc.loudness",
        "eng_tts.postproc.resample",
        "eng_tts.postproc.denoise",
        "eng_tts.streaming.chunker",
        "eng_tts.core.frame_builder",
    ):
        try:
            importlib.import_module(mod)
        except Exception as e:
            console.print(f"[yellow]skip {mod}: {e}[/yellow]")
    table = Table(show_header=True, header_style="bold")
    table.add_column("category")
    table.add_column("names")
    for cat, names in list_plugins().items():
        table.add_row(cat, ", ".join(names))
    console.print(table)


@app.command("benchmark")
def benchmark(
    sentences: int = typer.Option(20, "--n", help="Number of synthetic sentences"),
    output: Path = typer.Option(Path("output/benchmark.json"), "--out"),
) -> None:
    """Quick latency benchmark."""
    import json
    import time

    pipe = _pipeline()
    samples = [
        f"Sample {i}: The quick brown fox jumps over the lazy dog."
        for i in range(sentences)
    ]
    t0 = time.perf_counter()
    durations: list[float] = []
    for s in samples:
        c = pipe.synthesize(s, output_path=None)
        durations.append(c.metadata.get("duration_s", 0.0))
    elapsed = time.perf_counter() - t0
    total_audio = sum(durations)
    rtf = elapsed / max(total_audio, 1e-6)
    result = {
        "sentences": sentences,
        "wall_seconds": elapsed,
        "audio_seconds": total_audio,
        "real_time_factor": rtf,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2))
    console.print(result)


@app.command("serve")
def serve(
    host: str = typer.Option("127.0.0.1"),
    port: int = typer.Option(8000),
    reload: bool = typer.Option(False),
) -> None:
    """Start the FastAPI HTTP server."""
    try:
        import uvicorn  # type: ignore
    except ImportError:
        console.print("[red]Install API extras: pip install eng-tts[api][/red]")
        sys.exit(1)
    uvicorn.run("eng_tts.api.rest:app", host=host, port=port, reload=reload)


@app.command("ui")
def ui(host: str = typer.Option("127.0.0.1"), port: int = typer.Option(7860)) -> None:
    """Launch the Gradio web UI."""
    try:
        from ..ui.gradio_app import launch
    except ImportError:
        console.print("[red]Install UI extras: pip install eng-tts[ui][/red]")
        sys.exit(1)
    launch(host=host, port=port)


def _play(path: Path) -> None:
    import platform
    import subprocess

    sysname = platform.system()
    try:
        if sysname == "Windows":
            import winsound

            winsound.PlaySound(str(path), winsound.SND_FILENAME)
        elif sysname == "Darwin":
            subprocess.run(["afplay", str(path)], check=False)
        else:
            subprocess.run(["aplay", str(path)], check=False)
    except Exception:
        console.print(f"[yellow]Could not auto-play: {path}[/yellow]")


if __name__ == "__main__":
    app()
