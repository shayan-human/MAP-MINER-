#!/bin/bash
set -e

# Auto-clone if not exists
if [ ! -d "$HOME/mapminer" ]; then
    echo "Cloning MAP-MINER..."
    git clone https://github.com/shayan-human/MAP-MINER.git ~/mapminer
fi

cd ~/mapminer

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Install dependencies
source venv/bin/activate
pip install -r turbo/requirements.txt
pip install playwright
python -m playwright install chromium

echo ""
echo "✅ DONE! Run: cd ~/mapminer && ./mapminer"
