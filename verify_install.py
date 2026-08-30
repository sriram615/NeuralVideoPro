"""
Fresh Machine Environment & Installation Verification Script for NEURALVIDEO.

Checks:
    1. Python version >= 3.9
    2. PyTorch & Acceleration (CUDA / MPS / CPU)
    3. Qdrant Client Vector DB Library
    4. FastAPI & Uvicorn Backend Stack
    5. ffmpeg System Binary
    6. Frontend Node.js Dependencies
    7. Workspace Folder Hierarchy
    8. Environment Variables / .env configuration
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# ANSI Color Codes for Clean CLI Output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

def print_check(label: str, status: bool, detail: str = "") -> None:
    symbol = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
    msg = f"  [{symbol}] {label:<35}"
    if detail:
        msg += f" -> {detail}"
    print(msg)

def verify_environment() -> bool:
    print("=" * 75)
    print("  NEURALVIDEO — ENVIRONMENT & DEPENDENCY VERIFICATION")
    print("=" * 75)

    all_passed = True

    # 1. Python Version
    py_ver = sys.version_info
    py_pass = py_ver.major == 3 and py_ver.minor >= 9
    print_check(
        "Python Version (>= 3.9)",
        py_pass,
        f"{py_ver.major}.{py_ver.minor}.{py_ver.micro}"
    )
    if not py_pass:
        all_passed = False

    # 2. PyTorch & Compute Acceleration
    torch_pass = False
    device_info = "Not installed"
    try:
        import torch
        torch_pass = True
        if torch.cuda.is_available():
            device_info = f"CUDA ({torch.cuda.get_device_name(0)})"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            device_info = "Apple Silicon MPS (Metal Performance Shaders)"
        else:
            device_info = "CPU Execution (Bounded)"
    except ImportError as err:
        device_info = f"Import error: {err}"

    print_check("PyTorch & Compute Device", torch_pass, device_info)
    if not torch_pass:
        all_passed = False

    # 3. Qdrant Client
    qdrant_pass = False
    qdrant_detail = ""
    try:
        import qdrant_client
        import importlib.metadata
        qdrant_pass = True
        try:
            ver = importlib.metadata.version("qdrant-client")
            qdrant_detail = f"v{ver}"
        except Exception:
            qdrant_detail = "Installed"
    except ImportError as err:
        qdrant_detail = f"Import error: {err}"

    print_check("Qdrant Vector Engine Client", qdrant_pass, qdrant_detail)
    if not qdrant_pass:
        all_passed = False

    # 4. FastAPI & Backend Server Stack
    fastapi_pass = False
    fastapi_detail = ""
    try:
        import fastapi
        import uvicorn
        import pydantic
        fastapi_pass = True
        fastapi_detail = f"FastAPI v{fastapi.__version__}, Uvicorn v{uvicorn.__version__}"
    except ImportError as err:
        fastapi_detail = f"Import error: {err}"

    print_check("FastAPI & Uvicorn Backend Stack", fastapi_pass, fastapi_detail)
    if not fastapi_pass:
        all_passed = False

    # 5. ffmpeg System Binary
    ffmpeg_bin = shutil.which("ffmpeg")
    ffmpeg_pass = ffmpeg_bin is not None
    ffmpeg_detail = ffmpeg_bin if ffmpeg_pass else "MISSING (Required for audio processing)"
    print_check("ffmpeg System Binary", ffmpeg_pass, ffmpeg_detail)
    if not ffmpeg_pass:
        print(f"      {YELLOW}Warning: Install ffmpeg via 'brew install ffmpeg' (macOS) or 'apt install ffmpeg' (Linux){RESET}")

    # 6. Frontend Node.js Dependencies
    root_dir = Path(__file__).resolve().parent
    frontend_dir = root_dir / "frontend"
    node_modules = frontend_dir / "node_modules"
    pkg_json = frontend_dir / "package.json"
    
    frontend_pass = pkg_json.exists() and node_modules.exists()
    frontend_detail = "node_modules present" if frontend_pass else ("package.json missing" if not pkg_json.exists() else "node_modules missing (Run 'npm install' in frontend/)")
    print_check("Frontend Dependencies (Next.js)", frontend_pass, frontend_detail)
    if not frontend_pass:
        all_passed = False

    # 7. Required Folder Hierarchy
    required_folders = [
        "backend",
        "frontend",
        "data",
        "docs",
        "reports",
        "scripts",
    ]
    missing_folders = [f for f in required_folders if not (root_dir / f).is_dir()]
    folder_pass = len(missing_folders) == 0
    folder_detail = "All 6 required top-level directories present" if folder_pass else f"Missing: {', '.join(missing_folders)}"
    print_check("Workspace Folder Structure", folder_pass, folder_detail)
    if not folder_pass:
        all_passed = False

    # 8. Environment Configuration
    env_file = root_dir / ".env"
    env_example = root_dir / ".env.example"
    env_pass = env_file.exists() or env_example.exists()
    env_detail = ".env present" if env_file.exists() else ".env.example present (.env recommended)"
    print_check("Environment Configuration (.env)", env_pass, env_detail)

    print("=" * 75)
    if all_passed:
        print(f"  {GREEN}SUCCESS: Environment is fully configured and ready for execution!{RESET}")
        print("=" * 75)
        return True
    else:
        print(f"  {RED}ERROR: Verification failed. Please resolve missing components above.{RESET}")
        print("=" * 75)
        return False

if __name__ == "__main__":
    success = verify_environment()
    sys.exit(0 if success else 1)
