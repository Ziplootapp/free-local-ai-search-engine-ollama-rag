@echo off
title ZipLoot AI Search Studio v2.0 - Auto-Installer
color 0B
echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║   ZipLoot AI Search Studio v2.0 - 1-Click Installer     ║
echo  ║   https://ziploot.app                                    ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

:: ─── Step 0: Check Python ───────────────────────────────────
echo [0/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ╔══════════════════════════════════════════════════════╗
    echo  ║  [ERROR] Python is NOT installed on this system.     ║
    echo  ║                                                      ║
    echo  ║  Please download and install Python 3.8+ from:       ║
    echo  ║  https://www.python.org/downloads/                   ║
    echo  ║                                                      ║
    echo  ║  IMPORTANT: Check "Add Python to PATH" during setup! ║
    echo  ╚══════════════════════════════════════════════════════╝
    echo.
    echo  Opening Python download page...
    start "" "https://www.python.org/downloads/"
    echo.
    echo  After installing Python, close this window and
    echo  double-click deploy_windows.bat again.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo  [OK] %PYVER% detected.
echo.

:: ─── Step 1: Create Virtual Environment ─────────────────────
echo [1/4] Setting up Python virtual environment...
if not exist "venv" (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo.
        echo  [ERROR] Failed to create virtual environment.
        echo  Try running: python -m pip install --upgrade pip virtualenv
        echo.
        pause
        exit /b 1
    )
    echo  [OK] Virtual environment created.
) else (
    echo  [OK] Virtual environment already exists.
)
call venv\Scripts\activate.bat
echo.

:: ─── Step 2: Install Dependencies ───────────────────────────
echo [2/4] Installing Python dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Failed to install dependencies.
    echo  Check your internet connection and try again.
    echo.
    pause
    exit /b 1
)
echo  [OK] All dependencies installed.
echo.

:: ─── Step 3: Check Ollama (Optional) ────────────────────────
echo [3/4] Checking for Ollama (optional local LLM)...
where ollama >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] Ollama detected! Enhanced AI answers enabled.
    echo  Tip: Run "ollama pull qwen2.5:7b" if you haven't already.
) else (
    echo  [INFO] Ollama not found - using built-in Smart Synthesizer.
    echo  [INFO] This is fine! Ollama is optional for enhanced AI answers.
    echo  [INFO] Install later from: https://ollama.com/download
)
echo.

:: ─── Step 4: Check Port & Launch ────────────────────────────
echo [4/4] Launching ZipLoot AI Search Studio...

netstat -an 2>nul | findstr ":8050 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo  [WARNING] Port 8050 is already in use!
    echo  Another instance may be running. Close it first, or
    echo  the server will fail to start.
    echo.
)

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║  ZipLoot AI Search Studio is starting...                 ║
echo  ║  Open your browser at: http://localhost:8050              ║
echo  ║  Press Ctrl+C to stop the server.                        ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

:: Open browser after 2 second delay (so server has time to start)
start /b cmd /c "timeout /t 2 /nobreak >nul & start "" http://localhost:8050"

python server.py

echo.
echo  [INFO] Server stopped.
pause
