@echo off
REM ==============================================================================
REM NEURALVIDEO — Windows One-Command Setup Script
REM ==============================================================================
echo ======================================================================
echo   NEURALVIDEO HACKATHON 2026 — AUTOMATED ENVIRONMENT SETUP (WINDOWS)
echo ======================================================================

REM 1. Virtual Environment Setup
if not exist ".venv" (
    echo.
    echo [*] Creating Python virtual environment (.venv)...
    python -m venv .venv
) else (
    echo.
    echo [*] Virtual environment (.venv) already exists.
)

echo [*] Activating virtual environment...
call .venv\Scripts\activate.bat

REM 2. Upgrade pip & Install Python Dependencies
echo.
echo [*] Upgrading pip and installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM 3. Environment File Configuration
if not exist ".env" (
    echo.
    echo [*] Creating .env from .env.example...
    copy .env.example .env
)

REM 4. Frontend Node.js Dependencies
if exist "frontend" (
    echo.
    echo [*] Installing frontend dependencies (npm install)...
    cd frontend
    call npm install
    cd ..
)

REM 5. Execute Installation Verification
echo.
echo [*] Running installation verification suite...
python verify_install.py

echo.
echo ======================================================================
echo   SETUP COMPLETE ✓
echo ======================================================================
echo   To start the application:
echo     1. Activate Virtual Environment: .venv\Scripts\activate.bat
echo     2. Run FastAPI Backend Server:  cd backend ^&^& uvicorn api:app --reload
echo     3. Run Next.js Frontend Server: cd frontend ^&^& npm run dev
echo ======================================================================
pause
