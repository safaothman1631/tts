@echo off
setlocal

set "API_DIR=%~dp0english"

if not exist "%API_DIR%\src\eng_tts\api\rest.py" (
  echo Could not find the eng-tts API project at "%API_DIR%".
  pause
  exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
  echo Python is required to start the eng-tts API.
  pause
  exit /b 1
)

cd /d "%API_DIR%"
set "PYTHONPATH=%API_DIR%\src"
if "%ENG_TTS_ACOUSTIC_TIER%"=="" set "ENG_TTS_ACOUSTIC_TIER=piper"
if "%ENG_TTS_DEFAULT_VOICE%"=="" set "ENG_TTS_DEFAULT_VOICE=piper_en_us_lessac_medium"
set "ENG_TTS_PIPER_DIR=%~dp0models\piper"
if "%ENG_TTS_QWEN3_MODEL%"=="" set "ENG_TTS_QWEN3_MODEL=Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"
if "%ENG_TTS_QWEN3_CACHE_DIR%"=="" set "ENG_TTS_QWEN3_CACHE_DIR=%~dp0models\qwen3"

if /I "%ENG_TTS_ACOUSTIC_TIER%"=="qwen3" (
  if not exist "%ENG_TTS_QWEN3_CACHE_DIR%" (
    echo [eng-tts] Qwen3 model cache not found, attempting download...
    python "%~dp0scripts\download_qwen3_tts.py" "%ENG_TTS_QWEN3_MODEL%"
    if errorlevel 1 (
      echo [eng-tts] Qwen3 download failed; falling back to Piper backend.
      set "ENG_TTS_ACOUSTIC_TIER=piper"
      set "ENG_TTS_DEFAULT_VOICE=piper_en_us_lessac_medium"
    )
  )
)

if /I "%ENG_TTS_ACOUSTIC_TIER%"=="piper" (
  if not exist "%ENG_TTS_PIPER_DIR%\en_US-lessac-medium.onnx" (
    echo [eng-tts] Piper model missing, downloading en_US-lessac-medium...
    python "%~dp0scripts\download_piper_models.py"
    if errorlevel 1 (
      echo [eng-tts] Piper model download failed; falling back to legacy SAPI backend.
      set "ENG_TTS_ACOUSTIC_TIER=legacy"
      set "ENG_TTS_DEFAULT_VOICE=legacy_pyttsx3"
    )
  )
)

python -m uvicorn eng_tts.api.rest:app --host 127.0.0.1 --port 8765

if errorlevel 1 (
  echo eng-tts API stopped with an error.
  pause
)