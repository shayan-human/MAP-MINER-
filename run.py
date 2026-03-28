#!/usr/bin/env python3
import os
import sys
import subprocess
import venv
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
TURBO_DIR = SCRIPT_DIR / "turbo"
VENV_DIR = SCRIPT_DIR / "venv"
REQUIREMENTS = TURBO_DIR / "requirements.txt"

def create_venv():
    print("Creating virtual environment...")
    venv.create(VENV_DIR, with_pip=True)
    
def get_venv_python():
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"

def get_venv_activate():
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "activate.bat"
    return VENV_DIR / "bin" / "activate"

def install_deps():
    print("Installing dependencies...")
    python = get_venv_python()
    subprocess.run([str(python), "-m", "pip", "install", "-r", str(REQUIREMENTS)], check=True)
    subprocess.run([str(python), "-m", "pip", "install", "playwright"], check=True)
    subprocess.run([str(python), "-m", "playwright", "install", "chromium"], check=True)
    # Add system dependencies for playwright on Linux
    if sys.platform != "win32":
        print("Installing system dependencies for Playwright...")
        try:
            subprocess.run([str(python), "-m", "playwright", "install-deps", "chromium"], check=True)
        except Exception as e:
            print(f"Warning: Could not install system dependencies: {e}. You may need to run 'sudo playwright install-deps' manually.")

def run_server():
    print("\nStarting server at http://localhost:8000\n")
    python = get_venv_python()
    os.execv(str(python), [str(python), "-m", "uvicorn", "turbo.server:app", "--reload", "--port", "8000"])

def check_for_updates():
    """Attempt to pull the latest changes from Git before running."""
    print("Checking for updates...")
    git_dir = SCRIPT_DIR / ".git"
    if not git_dir.exists():
        return
        
    try:
        # We use git fetch followed by git pull --ff-only to be safe
        # timeout=10 to prevent hanging on network issues
        subprocess.run(
            ["git", "pull", "--ff-only"], 
            capture_output=True, text=True, cwd=SCRIPT_DIR, timeout=10
        )
        print("Done! Application is up to date.")
    except subprocess.TimeoutExpired:
        print("Warning: Update check timed out. Proceeding with current version.")
    except Exception as e:
        print(f"Warning: Could not check for updates ({e}). Proceeding with current version.")

def main():
    check_for_updates()
    if not VENV_DIR.exists():
        create_venv()
    
    install_deps()
    run_server()

if __name__ == "__main__":
    main()
