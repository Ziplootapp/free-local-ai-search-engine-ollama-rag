@echo off
title ZipLoot AI Search Studio v2.0 - Auto-Installer
color 0B
echo.
echo ========================================================
echo   ZipLoot AI Search Studio v2.0 - 1-Click Installer
echo   Official Web App: https://ziploot.app
echo ========================================================
echo.

REM --- Step 0: Check Python ---
echo [0/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 goto :MISSING_PYTHON

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo  [OK] %PYVER% detected.
echo.
goto :STEP_1

:MISSING_PYTHON
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

REM --- Step 1: Create Virtual Environment ---
:STEP_1
echo [1/4] Setting up Python virtual environment...
if exist "venv\Scripts\activate.bat" goto :VENV_EXISTS

python -m venv venv
if %errorlevel% neq 0 goto :VENV_ERROR
echo  [OK] Virtual environment created.
goto :ACTIVATE_VENV

:VENV_EXISTS
echo  [OK] Virtual environment already exists.

:ACTIVATE_VENV
call venv\Scripts\activate.bat
echo.
goto :STEP_2

:VENV_ERROR
echo.
echo  [ERROR] Failed to create virtual environment.
echo.
pause
exit /b 1

REM --- Step 2: Install Dependencies ---
:STEP_2
echo [2/4] Installing Python dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo  [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo  [OK] All dependencies installed.
echo.

REM --- Step 3: Check & Auto-Install Ollama ---
echo [3/4] Checking for Ollama (Local AI Engine)...

where ollama >nul 2>&1
if %errorlevel% equ 0 goto :OLLAMA_FOUND

if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
    set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
    goto :OLLAMA_FOUND
)

echo  [INFO] Ollama is not installed on this PC.
echo  [INFO] Starting 1-Click Auto-Download of Ollama for Windows...
echo  [INFO] Downloading OllamaSetup.exe (Please wait 1-2 mins)...

powershell -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; iwr -useb 'https://ollama.com/download/OllamaSetup.exe' -OutFile '$env:TEMP\OllamaSetup.exe'; Start-Process '$env:TEMP\OllamaSetup.exe' -ArgumentList '/silent' -Wait"

if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
    set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
    echo  [OK] Ollama auto-installed successfully!
    goto :OLLAMA_SERVICE
) else (
    echo  [INFO] Ollama download skipped or cancelled.
    echo  [INFO] ZipLoot will run using built-in Neural Synthesizer.
    goto :STEP_4
)

:OLLAMA_FOUND
echo  [OK] Ollama binary detected.

:OLLAMA_SERVICE
netstat -an 2>nul | findstr ":11434 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% neq 0 (
    echo  [INFO] Starting Ollama background AI service...
    if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
        start /b "" "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" serve >nul 2>&1
    ) else (
        start /b "" ollama serve >nul 2>&1
    )
    ping -n 3 127.0.0.1 >nul
)
echo  [OK] Ollama AI Daemon active on port 11434!
echo.

REM --- Step 4: Check Port & Launch ---
:STEP_4
echo [4/4] Launching ZipLoot AI Search Studio...

netstat -an 2>nul | findstr ":8050 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo  [WARNING] Port 8050 is already in use!
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

start /b cmd /c "ping -n 3 127.0.0.1 >nul & start "" http://localhost:8050"

python server.py

echo.
echo [INFO] Server stopped.
pause
