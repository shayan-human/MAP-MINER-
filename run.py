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

LAST_INSTALL_FILE = SCRIPT_DIR / ".last_install"

def create_venv():
    print("Creating virtual environment...")
    venv.create(VENV_DIR, with_pip=True)
    
def get_venv_python():
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"

def install_deps(force=False):
    # Check if we need to install
    if not force and LAST_INSTALL_FILE.exists():
        if LAST_INSTALL_FILE.stat().st_mtime > REQUIREMENTS.stat().st_mtime:
            print("Dependencies already satisfied (skip). Use --setup to force reinstall.")
            return

    print("Installing/Updating dependencies...")
    python = get_venv_python()
    try:
        subprocess.run([str(python), "-m", "pip", "install", "-r", str(REQUIREMENTS)], check=True)
        subprocess.run([str(python), "-m", "pip", "install", "playwright"], check=True)
        subprocess.run([str(python), "-m", "playwright", "install", "chromium"], check=True)
        
        # Mark successful installation
        LAST_INSTALL_FILE.touch()
        print("Done! All dependencies are ready.")
    except Exception as e:
        print(f"Error during installation: {e}")
        sys.exit(1)

def install_system_deps():
    if sys.platform == "win32":
        print("System dependencies are handled automatically on Windows.")
        return

    print("Installing system dependencies for Playwright (requires sudo)...")
    python = get_venv_python()
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
    print("Checking for updates...", end="", flush=True)
    git_dir = SCRIPT_DIR / ".git"
    if not git_dir.exists():
        print(" (not a git repo)")
        return
        
    try:
        result = subprocess.run(
            ["git", "pull", "--ff-only"], 
            capture_output=True, text=True, cwd=SCRIPT_DIR, timeout=10
        )
        if "Already up to date" in result.stdout:
            print(" (up to date)")
        else:
            print("\nUpdates pulled successfully!")
            print(result.stdout.strip())
    except subprocess.TimeoutExpired:
        print("\nWarning: Update check timed out. Proceeding with current version.")
    except Exception as e:
        print(f"\nWarning: Could not check for updates ({e}). Proceeding with current version.")

def main():
    args = sys.argv[1:]
    do_setup = "--setup" in args
    
    check_for_updates()
    
    if not VENV_DIR.exists():
        create_venv()
        do_setup = True # Force install if venv is new
    
    if do_setup:
        install_deps(force=True)
        install_system_deps()
    else:
        install_deps(force=False)
        
    run_server()

if __name__ == "__main__":
    main()
