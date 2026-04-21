@echo off
setlocal

cd /d "%~dp0"

set "URL=http://127.0.0.1:8000/viewer.html"

where py >nul 2>&1
if not errorlevel 1 (
  set "PY=py -3"
) else (
  set "PY=python"
)

%PY% --version >nul 2>&1
if errorlevel 1 (
  echo Python 3.10+ is required but no Python interpreter was found.
  echo https://www.python.org/downloads/
  pause
  exit /b 1
)

%PY% -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 (
  echo Python 3.10+ is required.
  %PY% --version
  pause
  exit /b 1
)

echo Starting PET Viewer server...
start "PET Viewer Server" cmd /k %PY% server.py

echo Waiting for server...
powershell -NoProfile -Command "$deadline=(Get-Date).AddSeconds(15); while((Get-Date) -lt $deadline){ try { $r=Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/viewer.html'; if($r.StatusCode -eq 200){ exit 0 } } catch {}; Start-Sleep -Milliseconds 250 }; exit 1"
if errorlevel 1 (
  echo Server did not become ready at %URL%
  pause
  exit /b 1
)

echo Opening viewer...
start "" "%URL%"

echo.
echo PET Viewer started at:
echo   %URL%
echo.
echo Do not close the "PET Viewer Server" window while using the viewer.
endlocal
