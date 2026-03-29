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

# --- SYMLINK SETUP (Professional CLI) ---
echo "Installing global 'mapminer' command..."
chmod +x "$HOME/mapminer/mapminer"
chmod +x "$HOME/mapminer/run_map_miner.sh"

# Create symlink in /usr/local/bin (requires sudo)
if [ ! -L "/usr/local/bin/mapminer" ]; then
    echo "This step requires sudo to create a global shortcut in /usr/local/bin."
    sudo ln -sf "$HOME/mapminer/mapminer" /usr/local/bin/mapminer
    echo "✓ Global command 'mapminer' installed to /usr/local/bin"
else
    echo "✓ Global command 'mapminer' already exists."
fi


echo ""
echo "✅ DONE! Map Miner is now installed globally."
echo "🚀 You can now run the scraper from ANY folder by typing: mapminer"
