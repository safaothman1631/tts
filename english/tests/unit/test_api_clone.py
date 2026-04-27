import importlib.util
import io

import numpy as np
import pytest

FASTAPI_AVAILABLE = importlib.util.find_spec("fastapi") is not None
SOUNDFILE_AVAILABLE = importlib.util.find_spec("soundfile") is not None


pytestmark = pytest.mark.skipif(
    not (FASTAPI_AVAILABLE and SOUNDFILE_AVAILABLE),
    reason="fastapi or soundfile not installed",
)


def _wav_bytes(duration_seconds: float = 1.1, amplitude: float = 0.2) -> bytes:
    import soundfile as sf

    sample_rate = 16_000
    t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds), endpoint=False)
    samples = (amplitude * np.sin(2 * np.pi * 220 * t)).astype(np.float32)
    buf = io.BytesIO()
    sf.write(buf, samples, sample_rate, format="WAV", subtype="PCM_16")
    return buf.getvalue()


@pytest.fixture()
def client(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    from eng_tts.api.rest import app
    from eng_tts.config import reset_settings
    from eng_tts.core.pipeline import reset_default_pipeline

    monkeypatch.setenv("ENG_TTS_OUTPUT_DIR", str(tmp_path / "output"))
    monkeypatch.setenv("ENG_TTS_CACHE_DIR", str(tmp_path / "cache"))
    reset_settings()
    reset_default_pipeline()
    return TestClient(app)


def test_clone_voice_requires_consent(client):
    response = client.post(
        "/v1/voices/clone",
        data={"name": "No Consent", "consent": "false"},
        files={"audio": ("sample.wav", _wav_bytes(), "audio/wav")},
    )

    assert response.status_code == 400
    assert "consent" in response.text.lower()


def test_clone_voice_rejects_silent_audio(client):
    response = client.post(
        "/v1/voices/clone",
        data={"name": "Silent", "consent": "true"},
        files={"audio": ("sample.wav", _wav_bytes(amplitude=0.0), "audio/wav")},
    )

    assert response.status_code == 400
    assert "silent" in response.text.lower()


def test_capabilities_reports_clone_and_controls(client):
    response = client.get("/v1/capabilities")

    assert response.status_code == 200
    data = response.json()
    assert data["voice_clone"] is True
    assert data["custom_voice_persistence"] is True
    assert "/v1/voices/clone" in data["endpoints"]
    assert "/v1/synthesize/segments" in data["endpoints"]
    assert "volume" in data["controls"]
    assert "style_prompt" in data["controls"]
    assert "pause_after_ms" in data["controls"]


def test_segment_synthesis_contract(client):
    response = client.post(
        "/v1/synthesize/segments",
        json={
            "segments": [
                {"text": "Hello from voice one.", "tier": "legacy", "speed": 1.0, "volume": 0.8},
                {"text": "And hello from voice two.", "tier": "legacy", "speed": 1.1, "pause_after_ms": 0},
            ],
            "format": "wav",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["sample_rate"] > 0
    assert data["duration_seconds"] > 0
    assert data["audio_base64"]


def test_segment_synthesis_wav_contract(client):
    response = client.post(
        "/v1/synthesize/segments.wav",
        json={"segments": [{"text": "Hello as wav.", "tier": "legacy"}]},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/wav")
    assert response.content[:4] == b"RIFF"


def test_stream_contract_returns_single_wav(client):
    response = client.post(
        "/v1/stream",
        json={"text": "Hello streaming.", "tier": "legacy"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/wav")
    assert response.content[:4] == b"RIFF"
    assert response.content[8:12] == b"WAVE"


def test_clone_voice_creates_custom_catalog_entry(client):
    response = client.post(
        "/v1/voices/clone",
        data={
            "name": "QA Clone",
            "description": "A test reference voice",
            "consent": "true",
            "language": "en",
            "gender": "neutral",
            "reference_text": "This is a reference sample.",
        },
        files={"audio": ("sample.wav", _wav_bytes(), "audio/wav")},
    )

    assert response.status_code == 200
    voice = response.json()
    assert voice["id"].startswith("custom-qa-clone-")
    assert voice["name"] == "QA Clone"
    assert voice["custom"] is True
    assert voice["supports_clone"] is True

    detail = client.get(f"/v1/voices/{voice['id']}")
    assert detail.status_code == 200
    assert detail.json()["id"] == voice["id"]

    voices = client.get("/v1/voices")
    assert voices.status_code == 200
    assert any(item["id"] == voice["id"] for item in voices.json())


def test_delete_custom_voice(client):
    created = client.post(
        "/v1/voices/clone",
        data={"name": "Delete Me", "consent": "true"},
        files={"audio": ("sample.wav", _wav_bytes(), "audio/wav")},
    ).json()

    deleted = client.delete(f"/v1/voices/{created['id']}")
    assert deleted.status_code == 200
    assert deleted.json() == {"deleted": True}

    missing = client.get(f"/v1/voices/{created['id']}")
    assert missing.status_code == 404
