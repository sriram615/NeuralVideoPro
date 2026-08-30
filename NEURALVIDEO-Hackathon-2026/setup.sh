#!/usr/bin/env bash
# ==============================================================================
# NEURALVIDEO — macOS / Linux One-Command Setup Script
# ==============================================================================
set -e

echo "======================================================================"
echo "  NEURALVIDEO HACKATHON 2026 — AUTOMATED ENVIRONMENT SETUP"
echo "======================================================================"

# 1. Virtual Environment Setup
if [ ! -d ".venv" ]; then
    echo "\n[*] Creating Python virtual environment (.venv)..."
    python3 -m venv .venv
else
    echo "\n[*] Virtual environment (.venv) already exists."
fi

echo "[*] Activating virtual environment..."
source .venv/bin/activate

# 2. Upgrade pip & Install Python Dependencies
echo "\n[*] Upgrading pip and installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Environment File Configuration
if [ ! -f ".env" ]; then
    echo "\n[*] Creating .env from .env.example..."
    cp .env.example .env
fi

# 4. Frontend Node.js Dependencies
if [ -d "frontend" ]; then
    echo "\n[*] Installing frontend dependencies (npm install)..."
    (cd frontend && npm install)
fi

# 5. Execute Installation Verification
echo "\n[*] Running installation verification suite..."
python verify_install.py

echo ""
echo "======================================================================"
echo "  SETUP COMPLETE ✓"
echo "======================================================================"
echo "  To start the application:"
echo "    1. Activate Virtual Environment: source .venv/bin/activate"
echo "    2. Run FastAPI Backend Server:  cd backend && uvicorn api:app --reload"
echo "    3. Run Next.js Frontend Server: cd frontend && npm run dev"
echo "======================================================================"
