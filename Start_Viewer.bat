@echo off
setlocal

REM Go to this folder
cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
  echo Python is not found. Please install Python 3 and try again.
  echo https://www.python.org/downloads/
  pause
  exit /b 1
)

REM Start server in a new window
start "PET Viewer Server" cmd /k python server.py

REM Give server a moment
timeout /t 1 >nul

REM Open browser
start "" http://127.0.0.1:8000/viewer.html

echo Viewer started. Do not close the "PET Viewer Server" window while using the viewer.
endlocal