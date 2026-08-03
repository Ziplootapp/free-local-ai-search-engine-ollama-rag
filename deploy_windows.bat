@echo off
title ZipLoot AI Search Studio v2.0 - Auto-Installer
color 0B
echo.
echo ========================================================
echo   ZipLoot AI Search Studio v2.0 - 1-Click Installer
echo   Official Web App: https://ziploot.app
echo ========================================================
echo.

:: ─── Step 0: Check Python ───────────────────────────────────
echo [0/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ========================================================
    echo  [ERROR] Python is NOT installed on this system.
    echo.
    echo  Please download and install Python 3.8+ from:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: Check "Add Python to PATH" during setup!
    echo ========================================================
    echo.
    echo Opening Python download page...
    start "" "https://www.python.org/downloads/"
    echo.
    echo After installing Python, close this window and
    echo double-click deploy_windows.bat again.
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

:: ─── Step 3: Check & Auto-Install / Auto-Start Ollama ────────
echo [3/4] Checking for Ollama (Local AI Engine)...

set "OLLAMA_EXE="
where ollama >nul 2>&1
if %errorlevel% equ 0 set "OLLAMA_EXE=ollama"
if not defined OLLAMA_EXE (
    if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
        set "OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
        set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
    )
)

if not defined OLLAMA_EXE (
    echo  [INFO] Ollama is not installed on this PC.
    echo  [INFO] Starting 1-Click Auto-Download of Ollama for Windows...
    echo  [INFO] Downloading OllamaSetup.exe (Please wait 1-2 mins)...
    
    powershell -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; iwr -useb 'https://ollama.com/download/OllamaSetup.exe' -OutFile '$env:TEMP\OllamaSetup.exe'; Start-Process '$env:TEMP\OllamaSetup.exe' -ArgumentList '/silent' -Wait"
    
    if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
        set "OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
        set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
        echo  [OK] Ollama auto-installed successfully!
    ) else (
        echo  [INFO] Ollama download skipped or cancelled.
        echo  [INFO] ZipLoot will run using built-in Neural Synthesizer.
    )
) else (
    echo  [OK] Ollama binary detected.
)

:: Auto-Start Ollama Background Daemon if needed
if defined OLLAMA_EXE (
    netstat -an 2>nul | findstr ":11434 " | findstr "LISTENING" >nul 2>&1
    if %errorlevel% neq 0 (
        echo  [INFO] Starting Ollama background AI service...
        start /b "" "%OLLAMA_EXE%" serve >nul 2>&1
        timeout /t 3 /nobreak >nul
    )
    echo  [OK] Ollama AI Daemon active on port 11434!
)
echo.

:: ─── Step 4: Check Port & Launch ────────────────────────────
echo [4/4] Launching ZipLoot AI Search Studio...

netstat -an 2>nul | findstr ":8050 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo  [WARNING] Port 8050 is already in use!
    echo  Another ZipLoot instance may be running.
    echo.
)

echo.
echo ========================================================
echo   ZipLoot AI Search Studio is starting...
echo   Open your browser at: http://localhost:8050
echo   Official Portal: https://ziploot.app
echo   Press Ctrl+C in this window to stop the server.
echo ========================================================
echo.

:: Open browser after 2 second delay
start /b cmd /c "timeout /t 2 /nobreak >nul & start "" http://localhost:8050"

python server.py

echo.
echo [INFO] Server stopped.
pause
