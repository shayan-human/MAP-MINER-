# 🗺️ Map Miner — Ultimate Lead Extraction Dashboard

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PWA Ready](https://img.shields.io/badge/PWA-Ready-green.svg)](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)

**Map Miner** is a powerful, high-performance lead generation tool designed to extract business data from Google Maps at scale. Featuring a sleek, glassmorphic dashboard and advanced extraction logic, it's the premium solution for B2B lead mining.

![Dashboard Preview](assets/dashboard_preview.png)
*Professional, glassmorphic dashboard for managing extractions.*

---

## 🚀 Key Features

- **⚡ High-Accuracy Engine**: Reverted to our most stable searching logic for maximum regional accuracy (Commit `30178f6`).
- **🛡️ Proxy Rotation**: Integrated support for HTTP/Socks proxies with "Strict Mode" protection.
- **⚡ High-Speed Extraction**: Multithreaded scraping using Playwright.
- **📱 PWA Supported**: Install the dashboard as a standalone app on your desktop or mobile.
- **🎨 Premium UI**: Modern dark mode interface with real-time statistics and glassmorphic design.
- **🔄 Auto-Updates**: Stays up-to-date with the latest features automatically using a secure hash-check system.

---

## 🛠️ Installation & Setup

### Linux/Mac (Professional Installation)
This sets up the **global command** (`mapminer`), creates the virtual environment, and installs all system drivers automatically.

> ⚠️ **IMPORTANT**: Clone to `~/mapminer` folder (NOT `~/MAP-MINER`) for the global command to work.

```bash
cd ~
sudo rm /usr/local/bin/mapminer
rm -rf mapminer
git clone https://github.com/shayan-human/MAP-MINER.git mapminer
cd mapminer && bash install.sh
```
> [!NOTE]
> This step requires `sudo` privileges to create the global shortcut (`mapminer`) and install browser dependencies.

After installation, run from **ANY** folder:
```bash
mapminer
```

---

### Windows (Quick Start)

#### Installation
```bash
git clone https://github.com/shayan-human/MAP-MINER.git
cd MAP-MINER
```

#### Run
```bash
python run.py
```

Then open http://localhost:8000

---

### Docker (All Platforms)

Best for **no setup required** - works on Windows, Mac, and Linux with Docker.

#### Installation & Run
```bash
git clone https://github.com/shayan-human/MAP-MINER.git
cd MAP-MINER
docker-compose up --build
```

Then open http://localhost:8000

> ⚠️ **Requires**: [Docker Desktop](https://www.docker.com/products/docker-desktop) installed

### 💡 Tips & Flags
- **Force Re-Setup** (Linux/Mac):
  ```bash
  mapminer --setup
  ```
- **Force Re-Setup** (Windows):
  ```bash
  python run.py --setup
  ```
- **Skip Updates** (Linux/Mac):
  ```bash
  mapminer --no-update
  ```
- **Skip Updates** (Windows):
  ```bash
  python run.py --no-update
  ```

---

## 🩹 Troubleshooting

### Broken mapminer Command
If you see error like `can't open file '/usr/local/bin/run.py'`, fix by removing old folder and reinstalling:

```bash
cd ~
sudo rm /usr/local/bin/mapminer
rm -rf mapminer
git clone https://github.com/shayan-human/MAP-MINER.git mapminer
cd mapminer && bash install.sh
```

Then use `mapminer` from anywhere.

### Infinite Update Loop
If you ever find yourself in an infinite update loop (common after a `force push` to the main repository), run this cure:

```bash
cd ~/mapminer
git fetch origin
git reset --hard origin/main
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Built with ❤️ by [Shayan Alam](https://github.com/shayan-human)**
