@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "APP_DIR=%ROOT_DIR%ui"
set "API_DIR=%ROOT_DIR%english"
set "API_PORT=8765"
set "UI_PORT=5173"

if not exist "%APP_DIR%\package.json" (
  echo Could not find the UI project at "%APP_DIR%".
  pause
  exit /b 1
)

if not exist "%API_DIR%\src\eng_tts\api\rest.py" (
  echo Could not find the eng-tts API project at "%API_DIR%".
  pause
  exit /b 1
)

where pnpm >nul 2>nul
if errorlevel 1 (
  echo pnpm is required to start this app.
  echo Install it with: npm install -g pnpm
  pause
  exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
  echo Python is required to start the eng-tts API.
  pause
  exit /b 1
)

if not exist "%APP_DIR%\node_modules\" (
  echo Installing UI dependencies...
  pnpm --dir "%APP_DIR%" install
  if errorlevel 1 (
    echo Dependency install failed.
    pause
    exit /b 1
  )
)

set "VITE_API_URL=http://127.0.0.1:%API_PORT%"

powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-RestMethod -Uri 'http://127.0.0.1:%API_PORT%/v1/health' -TimeoutSec 2; if ($r.status -eq 'ok' -and $r.version) { exit 0 } } catch { exit 1 }" >nul 2>nul
if errorlevel 1 (
  echo Starting eng-tts API on http://127.0.0.1:%API_PORT% ...
  start "TTS Studio API" "%ROOT_DIR%start-api.bat"

  echo Waiting for API to become ready...
  for /L %%I in (1,1,30) do (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-RestMethod -Uri 'http://127.0.0.1:%API_PORT%/v1/health' -TimeoutSec 2; if ($r.status -eq 'ok' -and $r.version) { exit 0 } } catch { exit 1 }" >nul 2>nul
    if not errorlevel 1 goto api_ready
    timeout /t 1 /nobreak >nul
  )

  echo API did not become ready. Check the TTS Studio API window for details.
  pause
  exit /b 1
)

:api_ready
echo Starting TTS Studio on localhost...
pnpm --dir "%APP_DIR%" run dev -- --host 127.0.0.1 --port %UI_PORT% --open

if errorlevel 1 (
  echo Dev server stopped with an error.
  pause
)