@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "APP_DIR=%ROOT_DIR%ui"
set "API_DIR=%ROOT_DIR%english"
set "API_PORT=8765"
set "UI_PORT=5173"
set "API_URL=http://127.0.0.1:%API_PORT%"
set "UI_URL=http://127.0.0.1:%UI_PORT%"

title TTS Studio Launcher
echo.
echo ========================================
echo   TTS Studio one-click launcher
echo ========================================
echo.

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

set "VITE_API_URL=%API_URL%"

call :check_api
if errorlevel 1 (
  echo Starting backend API: %API_URL%
  start "TTS Studio API" /D "%ROOT_DIR%" cmd /k call "%ROOT_DIR%start-api.bat"
) else (
  echo Backend API is already running: %API_URL%
)

call :check_ui
if errorlevel 1 (
  echo Starting frontend UI: %UI_URL%
  start "TTS Studio UI" /D "%APP_DIR%" cmd /k "set VITE_API_URL=%API_URL%&& pnpm run dev -- --host 127.0.0.1 --port %UI_PORT%"
) else (
  echo Frontend UI is already running: %UI_URL%
)

echo.
echo Waiting for the frontend to be ready...
for /L %%I in (1,1,45) do (
  call :check_ui
  if not errorlevel 1 goto ui_is_ready
  timeout /t 1 /nobreak >nul
)

echo.
echo The UI did not become ready in time. Check the TTS Studio UI window.
pause
exit /b 1

:ui_is_ready
echo Opening %UI_URL%
start "" "%UI_URL%"

echo.
echo Waiting for backend health...
for /L %%I in (1,1,90) do (
  call :check_api
  if not errorlevel 1 goto api_is_ready
  timeout /t 1 /nobreak >nul
)

echo Backend is still starting or downloading models.
echo You can use the UI now; it will switch from Offline when API is ready.
goto done

:api_is_ready
echo Backend API ready: %API_URL%

:done
echo.
echo Frontend: %UI_URL%
echo Backend:  %API_URL%
echo.
echo Keep the API and UI windows open while using TTS Studio.
echo Press any key to close this launcher window.
pause >nul
exit /b 0

:check_api
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-RestMethod -Uri '%API_URL%/v1/health' -TimeoutSec 2; if ($r.status -eq 'ok' -and $r.version) { exit 0 } } catch { exit 1 }" >nul 2>nul
exit /b %errorlevel%

:check_ui
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-WebRequest -Uri '%UI_URL%' -UseBasicParsing -TimeoutSec 2; if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 500) { exit 0 } } catch { exit 1 }" >nul 2>nul
exit /b %errorlevel%
