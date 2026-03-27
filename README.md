# MAP-MINER

**Google Maps Scraper with Web Dashboard**

---

## Install & Run (Linux/Mac)

```bash
# 1. Install (one time) - auto-clones repo
curl -sL https://raw.githubusercontent.com/shayan-human/MAP-MINER/main/install.sh | bash

# 2. Run
cd ~/mapminer && ./mapminer
```

Then open **http://localhost:8000**

---

## Manual Install

```bash
git clone https://github.com/shayan-human/MAP-MINER.git ~/mapminer
cd ~/mapminer
python3 -m venv venv
source venv/bin/activate
pip install -r turbo/requirements.txt
pip install playwright
python -m playwright install chromium
./mapminer
```

---

## Windows

```powershell
git clone https://github.com/shayan-human/MAP-MINER.git
cd MAP-MINER
python -m venv venv
venv\Scripts\activate
pip install -r turbo\requirements.txt
pip install playwright
python -m playwright install chromium
cd turbo
python -m uvicorn server:app --reload --port 8000
```

---

## License

MIT - © 2026 Shayan Alam
