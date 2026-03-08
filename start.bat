 @echo off
setlocal
cd /d "%~dp0"

echo.
echo ========================================
echo   CipherX Pro - Startup Launcher
echo ========================================
echo.

:: Check for virtual environment folder
if exist "venv\Scripts\python.exe" (
    echo [INFO] Using virtual environment (venv)
    set PY=venv\Scripts\python.exe
) else (
    echo [INFO] Using system Python
    set PY=python
)

:: Test if Python is actually available
%PY% --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python or set it in your PATH.
    pause
    exit /b 1
)

:: Try to run with START_HERE.py (Safe ASCII version)
if exist "START_HERE.py" (
    echo Launching with safe startup script...
    "%PY%" START_HERE.py
) else (
    echo [ERROR] START_HERE.py not found in the current directory!
    pause
    exit /b 1
)

echo.
echo Launch sequence complete.
echo.
pause
