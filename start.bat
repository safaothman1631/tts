@echo off
setlocal EnableDelayedExpansion

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
  echo ERROR: UI project not found at "%APP_DIR%".
  pause & exit /b 1
)

if not exist "%API_DIR%\src\eng_tts\api\rest.py" (
  echo ERROR: eng-tts API not found at "%API_DIR%".
  pause & exit /b 1
)

where pnpm >nul 2>nul
if errorlevel 1 (
  echo ERROR: pnpm not found. Install: npm install -g pnpm
  pause & exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python not found.
  pause & exit /b 1
)

if not exist "%APP_DIR%\node_modules\" (
  echo Installing UI dependencies...
  pnpm --dir "%APP_DIR%" install
  if errorlevel 1 ( echo Dependency install failed. & pause & exit /b 1 )
)

rem ── Backend ─────────────────────────────────────────────────────────────
curl -sf -o NUL --connect-timeout 2 --max-time 3 "%API_URL%/v1/health" >nul 2>nul
if errorlevel 1 (
  echo Starting backend API in new window...
  start "TTS Studio API" /D "%ROOT_DIR%" cmd /k call "%ROOT_DIR%start-api.bat"
  echo Waiting for backend to come up
  set "API_READY=0"
  for /L %%I in (1,1,120) do (
    if "!API_READY!"=="0" (
      curl -sf -o NUL --connect-timeout 1 --max-time 2 "%API_URL%/v1/health" >nul 2>nul
      if not errorlevel 1 (
        set "API_READY=1"
        echo  [OK] Backend ready ^(%%I s^)
      ) else (
        <nul set /p ".=."
        timeout /t 1 /nobreak >nul
      )
    )
  )
  if "!API_READY!"=="0" (
    echo.
    echo  Backend is still loading - models may be downloading.
    echo  UI will switch from Offline automatically when API is ready.
  )
) else (
  echo Backend already running: %API_URL%
)

rem ── Frontend ────────────────────────────────────────────────────────────
curl -sf -o NUL --connect-timeout 2 --max-time 3 "%UI_URL%" >nul 2>nul
if errorlevel 1 (
  echo Starting frontend UI in new window...
  start "TTS Studio UI" /D "%APP_DIR%" cmd /k "set VITE_API_URL=%API_URL%&& pnpm run dev -- --host 127.0.0.1 --port %UI_PORT%"
  echo Waiting for UI to be ready
  set "UI_READY=0"
  for /L %%I in (1,1,45) do (
    if "!UI_READY!"=="0" (
      curl -sf -o NUL --connect-timeout 1 --max-time 2 "%UI_URL%" >nul 2>nul
      if not errorlevel 1 (
        set "UI_READY=1"
        echo  [OK] UI ready ^(%%I s^)
      ) else (
        <nul set /p ".=."
        timeout /t 1 /nobreak >nul
      )
    )
  )
  if "!UI_READY!"=="0" (
    echo.
    echo  UI did not start in time. Check the TTS Studio UI window.
    pause & exit /b 1
  )
) else (
  echo Frontend already running: %UI_URL%
)

echo.
echo Opening browser...
start "" "%UI_URL%"

echo.
echo ========================================
echo   TTS Studio is running
echo   Frontend : %UI_URL%
echo   Backend  : %API_URL%
echo ========================================
echo.
echo Keep the API and UI windows open while using TTS Studio.
echo Press any key to close this launcher window.
pause >nul
exit /b 0
