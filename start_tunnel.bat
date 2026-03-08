@echo off
setlocal
cd /d "%~dp0"

echo.
echo ========================================
echo   🔐 CipherX Pro - Cloud Tunnel Launcher
echo ========================================
echo.

:: Check for virtual environment
if exist "venv\Scripts\python.exe" (
    echo [INFO] Using virtual environment...
    set PY=venv\Scripts\python.exe
) else (
    echo [INFO] Using system Python...
    set PY=python
)

echo Closing old tunnel sessions (if any)...
taskkill /F /IM ngrok.exe /T >nul 2>&1
taskkill /F /IM ngrok-asgi.exe /T >nul 2>&1
timeout /t 1 /nobreak >nul

echo Starting CipherX with tunnel...
%PY% run.py --tunnel

echo.
echo Tunnel stopped.
echo.
pause
