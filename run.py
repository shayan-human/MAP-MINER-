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
    """Install dependencies from requirements.txt if they have changed."""
    req_file = TURBO_DIR / "requirements.txt"
    marker_file = VENV_DIR / ".last_install"
    
    if not force and marker_file.exists():
        # Only skip if requirements haven't changed since last install
        if req_file.stat().st_mtime <= marker_file.stat().st_mtime:
            return

    print("Installing/Updating dependencies...")
    python = get_venv_python()
    try:
        subprocess.run([str(python), "-m", "pip", "install", "-r", str(req_file)], check=True)
        subprocess.run([str(python), "-m", "pip", "install", "playwright"], check=True)
        subprocess.run([str(python), "-m", "playwright", "install", "chromium"], check=True)
        
        # Mark successful installation
        marker_file.touch()
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
    
    # Ensure current directory is in PYTHONPATH for 'turbo' module discovery
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SCRIPT_DIR) + os.pathsep + env.get("PYTHONPATH", "")
    
    try:
        # Use subprocess instead of execv to maintain control and handle environment correctly
        subprocess.run([
            str(python), "-m", "uvicorn", 
            "turbo.server:app", 
            "--reload", 
            "--reload-dir", str(TURBO_DIR),
            "--port", "8000",
            "--host", "0.0.0.0"
        ], cwd=str(SCRIPT_DIR), env=env)
    except KeyboardInterrupt:
        print("\nStopping Map Miner...")
    except Exception as e:
        print(f"Error starting server: {e}")

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
            return False
        else:
            print("\nUpdates pulled successfully!")
            print(result.stdout.strip())
            return True
    except subprocess.TimeoutExpired:
        print("\nWarning: Update check timed out. Proceeding with current version.")
    except Exception as e:
        print(f"\nWarning: Could not check for updates ({e}). Proceeding with current version.")
    return False

def main():
    args = sys.argv[1:]
    do_setup = "--setup" in args
    
    if check_for_updates():
        print("Restarting script to apply updates...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    
    if not VENV_DIR.exists():
        create_venv()
        do_setup = True # Force install if venv is new
    
    if do_setup:
        install_deps(force=True)
        install_system_deps()
        
    run_server()

if __name__ == "__main__":
    main()
