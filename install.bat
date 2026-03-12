@echo off
echo Installing Map Miner Dependencies...

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.10 or higher.
    pause
    exit /b
)

:: Create virtual environment if it doesn't exist
if not exist venv\ (
    echo Creating Python virtual environment...
    python -m venv venv
)

:: Activate background virtual environment to install packages
call venv\Scripts\activate.bat

:: Install requirements
echo Installing Python requirements...
pip install --quiet -r turbo\requirements.txt

:: Install playwright browser
echo Installing Playwright chromium...
playwright install chromium

echo Installation complete! You can now double click run_map_miner.bat
pause
