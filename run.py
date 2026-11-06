"""Start the backend (uv + uvicorn) and the frontend (Next.js) together.

Usage: python run.py   (Ctrl+C stops both)
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
API_PORT = 8000
FRONTEND_PORT = 3000


def require(tool: str, hint: str) -> str:
    path = shutil.which(tool)
    if not path:
        sys.exit(f"'{tool}' was not found on PATH. {hint}")
    return path


def main() -> None:
    uv = require("uv", "Install it from https://docs.astral.sh/uv/")
    npm = require("npm", "Install Node.js 20+ from https://nodejs.org/")

    if not (FRONTEND / "node_modules").exists():
        print("Installing frontend dependencies...")
        subprocess.run([npm, "install"], cwd=FRONTEND, check=True)

    backend = subprocess.Popen(
        [uv, "run", "uvicorn", "wedplanner.api.main:app", "--reload", "--port", str(API_PORT)],
        cwd=BACKEND,
    )
    frontend = subprocess.Popen([npm, "run", "dev", "--", "--port", str(FRONTEND_PORT)], cwd=FRONTEND)

    print(f"Backend:  http://localhost:{API_PORT}  (API docs at /docs)")
    print(f"Frontend: http://localhost:{FRONTEND_PORT}")
    print("Press Ctrl+C to stop both.")

    processes = (backend, frontend)
    try:
        while all(process.poll() is None for process in processes):
            try:
                backend.wait(timeout=1)
            except subprocess.TimeoutExpired:
                pass
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
        for process in processes:
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()


if __name__ == "__main__":
    main()
