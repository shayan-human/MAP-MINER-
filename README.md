# MAP-MINER

**Google Maps Scraper with Web Dashboard**

---

## Quick Start (All OS)

```bash
# Clone & Run
git clone https://github.com/shayan-human/MAP-MINER.git
cd MAP-MINER

# Run (auto-creates venv & installs deps)
python3 run.py
```

Then open **http://localhost:8000**

---

## Manual Install

```bash
git clone https://github.com/shayan-human/MAP-MINER.git
cd MAP-MINER

# Create venv
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install deps
pip install -r turbo/requirements.txt
pip install playwright
python3 -m playwright install chromium

# Run
python3 run.py
```

---

## Alternative: Shell Script (Linux/Mac only)

```bash
chmod +x mapminer
./mapminer
```

---

## License

MIT - © 2026 Shayan Alam
