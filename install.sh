#!/bin/bash
echo "Installing Map Miner Dependencies..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null
then
    echo "Python 3 is not installed. Please install Python 3.10 or higher."
    exit
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements quietly
echo "Installing Python requirements..."
pip install --quiet -r turbo/requirements.txt

# Install Playwright browser
echo "Installing Playwright chromium..."
playwright install chromium

echo "Installation complete! You can now run the app with ./run_map_miner.sh"
