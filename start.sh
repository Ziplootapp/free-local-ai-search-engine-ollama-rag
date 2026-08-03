#!/bin/bash
echo "═══════════════════════════════════════════════════════"
echo "  ZipLoot AI Search Studio v2.0 - Quick Start"
echo "  https://ziploot.app"
echo "═══════════════════════════════════════════════════════"
echo ""

if [ ! -d "venv" ]; then
    echo "[ERROR] Virtual environment not found!"
    echo "Please run ./deploy_linux.sh first for initial setup."
    exit 1
fi

source venv/bin/activate

echo "Starting server at http://localhost:8050 ..."
echo "Press Ctrl+C to stop."
echo ""

# Open browser after 2 second delay
(sleep 2 && if command -v xdg-open &> /dev/null; then xdg-open http://localhost:8050; elif command -v open &> /dev/null; then open http://localhost:8050; fi) &

python3 server.py
