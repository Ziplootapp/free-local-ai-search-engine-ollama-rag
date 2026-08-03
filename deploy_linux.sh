#!/bin/bash
echo "═══════════════════════════════════════════════════════"
echo "  ZipLoot AI Search Studio v2.0 - 1-Click Installer"
echo "  https://ziploot.app"
echo "═══════════════════════════════════════════════════════"
echo ""

# ─── Step 0: Check Python ───────────────────────────────────
echo "[0/4] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo ""
    echo "  [ERROR] python3 is NOT installed."
    echo ""
    echo "  Install Python 3.8+ using your package manager:"
    echo "    Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "    Fedora/RHEL:   sudo dnf install python3 python3-pip"
    echo "    macOS:         brew install python3"
    echo "    Or download:   https://www.python.org/downloads/"
    echo ""
    exit 1
fi
echo "  [OK] $(python3 --version) detected."
echo ""

# ─── Step 1: Check python3-venv (Debian/Ubuntu) ─────────────
echo "[1/4] Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv 2>/dev/null
    if [ $? -ne 0 ]; then
        echo ""
        echo "  [ERROR] Failed to create virtual environment."
        echo "  On Ubuntu/Debian, you may need to install python3-venv:"
        echo "    sudo apt install python3-venv"
        echo ""
        exit 1
    fi
    echo "  [OK] Virtual environment created."
else
    echo "  [OK] Virtual environment already exists."
fi
source venv/bin/activate
echo ""

# ─── Step 2: Install Dependencies ───────────────────────────
echo "[2/4] Installing Python dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo ""
    echo "  [ERROR] Failed to install dependencies."
    echo "  Check your internet connection and try again."
    exit 1
fi
echo "  [OK] All dependencies installed."
echo ""

# ─── Step 3: Check Ollama (Optional) ────────────────────────
echo "[3/4] Checking for Ollama (optional local LLM)..."
if command -v ollama &> /dev/null; then
    echo "  [OK] Ollama detected! Enhanced AI answers enabled."
    echo "  Tip: Run 'ollama pull qwen2.5:7b' if you haven't already."
else
    echo "  [INFO] Ollama not found - using built-in Smart Synthesizer."
    echo "  [INFO] This is fine! Ollama is optional for enhanced AI answers."
    echo "  [INFO] Install later from: https://ollama.com/download"
fi
echo ""

# ─── Step 4: Launch Server ───────────────────────────────────
echo "[4/4] Launching ZipLoot AI Search Studio..."
echo ""
echo "═══════════════════════════════════════════════════════"
echo "  ZipLoot AI Search Studio is starting..."
echo "  Open your browser at: http://localhost:8050"
echo "  Press Ctrl+C to stop the server."
echo "═══════════════════════════════════════════════════════"
echo ""

# Open browser after 2 second delay
(sleep 2 && if command -v xdg-open &> /dev/null; then xdg-open http://localhost:8050; elif command -v open &> /dev/null; then open http://localhost:8050; fi) &

python3 server.py
