"""Gradio web UI."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from ..core.pipeline import TTSPipeline


def _build_pipeline(tier: str) -> TTSPipeline:
    from ..config import get_settings

    s = get_settings()
    s.acoustic_tier = tier  # type: ignore[assignment]
    return TTSPipeline(settings=s)


def synthesize_gr(text: str, voice: str, tier: str, speed: float, speaker_wav: Optional[str]):
    pipe = _build_pipeline(tier)
    chunk = pipe.synthesize(
        text=text, voice=voice or None, speed=speed, speaker_wav=speaker_wav or None
    )
    return (chunk.sample_rate, chunk.samples)


def launch(host: str = "127.0.0.1", port: int = 7860) -> None:
    try:
        import gradio as gr  # type: ignore
    except ImportError as e:
        raise ImportError("Install UI extras: pip install eng-tts[ui]") from e

    pipe = TTSPipeline()
    voice_choices = [v.id for v in pipe.list_voices()]

    with gr.Blocks(title="eng-tts") as demo:
        gr.Markdown("# eng-tts — World-class English TTS")
        with gr.Row():
            with gr.Column():
                txt = gr.Textbox(label="Text or SSML", lines=6)
                voice = gr.Dropdown(voice_choices, value=voice_choices[0] if voice_choices else None, label="Voice")
                tier = gr.Dropdown(["fast", "premium", "clone", "legacy"], value="fast", label="Tier")
                speed = gr.Slider(0.5, 2.0, value=1.0, step=0.05, label="Speed")
                speaker_wav = gr.Audio(type="filepath", label="Reference voice (clone tier)")
                btn = gr.Button("Synthesize", variant="primary")
            with gr.Column():
                audio = gr.Audio(label="Output")
        btn.click(synthesize_gr, [txt, voice, tier, speed, speaker_wav], audio)

    demo.queue().launch(server_name=host, server_port=port)


if __name__ == "__main__":
    launch()
