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

:: ─── Step 3: Check / Auto-Install Ollama ─────────────────────
echo [3/4] Checking for Ollama (Local AI Engine)...
where ollama >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] Ollama detected! Enhanced AI answers enabled.
) else (
    if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
        set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
        echo  [OK] Ollama detected at LocalAppData!
    ) else (
        echo  [INFO] Ollama not found. Starting 1-Click Auto-Installer...
        echo  [INFO] Downloading Ollama for Windows...
        powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile '$env:TEMP\OllamaSetup.exe'; Start-Process '$env:TEMP\OllamaSetup.exe' -ArgumentList '/silent' -Wait" >nul 2>&1
        if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
            set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
            echo  [OK] Ollama auto-installed successfully!
        ) else (
            echo  [INFO] Ollama installation skipped - using built-in ZipLoot Smart Synthesizer.
            echo  [INFO] ZipLoot works 100%% out-of-the-box using built-in Neural Synthesizer.
        )
    )
)
echo.

:: ─── Step 4: Check Port & Launch ────────────────────────────
echo [4/4] Launching ZipLoot AI Search Studio...

netstat -an 2>nul | findstr ":8050 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo  [WARNING] Port 8050 is already in use!
    echo  Another instance may be running. Close it first if needed.
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
