# syntax=docker/dockerfile:1.6
# Multi-stage CPU image for eng-tts.

# ───── Builder ─────
FROM python:3.11-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl ca-certificates espeak-ng libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src

RUN pip install --upgrade pip && \
    pip install ".[nlp,acoustic,api,postproc]"

# Pre-fetch English spaCy model
RUN python -m spacy download en_core_web_sm || true

# ───── Runtime ─────
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    ENG_TTS_LOG_LEVEL=INFO \
    ENG_TTS_DEVICE=cpu \
    ENG_TTS_ACOUSTIC_TIER=fast

RUN apt-get update && apt-get install -y --no-install-recommends \
    espeak-ng libsndfile1 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# copy the prebuilt environment
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app
COPY src ./src
COPY pyproject.toml README.md ./

RUN pip install --no-deps -e .

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/v1/health').read()" || exit 1

CMD ["uvicorn", "eng_tts.api.rest:app", "--host", "0.0.0.0", "--port", "8000"]
