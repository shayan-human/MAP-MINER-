@echo off
echo Starting Map Miner...

:: Check if virtual environment exists
if not exist venv\ (
    echo Virtual environment not found. Please run install.bat first.
    pause
    exit /b
)

:: Start the Go backend server in a new minimized window
echo Starting core map-miner server...
start /MIN cmd /c "go run main.go -web"

:: Wait a few seconds for Go server to start
timeout /t 3 /nobreak >nul

:: Activate virtual environment and start Turbo Dashboard
echo Starting Turbo Dashboard...
call venv\Scripts\activate.bat
set PYTHONPATH=.
start http://localhost:8000
python turbo\server.py

pause
