@echo off
title ZipLoot AI Search Studio v2.0
color 0B
echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║   ZipLoot AI Search Studio v2.0 - Quick Start            ║
echo  ║   https://ziploot.app                                    ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

if not exist "venv\Scripts\activate.bat" (
    echo  [ERROR] Virtual environment not found!
    echo  Please run deploy_windows.bat first for initial setup.
    echo.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo  Starting server at http://localhost:8050 ...
echo  Press Ctrl+C to stop.
echo.

start /b cmd /c "timeout /t 2 /nobreak >nul & start "" http://localhost:8050"

python server.py

echo.
echo  [INFO] Server stopped.
pause
