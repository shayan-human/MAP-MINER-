# 🗺️ Map Miner — Ultimate Lead Extraction Dashboard

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PWA Ready](https://img.shields.io/badge/PWA-Ready-green.svg)](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)

**Map Miner** is a powerful, high-performance lead generation tool designed to extract business data from Google Maps at scale. Featuring a sleek, glassmorphic dashboard and advanced extraction logic, it's the premium solution for B2B lead mining.

![Dashboard Preview](assets/dashboard_preview.png)
*Professional, glassmorphic dashboard for managing extractions.*

---

## 🚀 Key Features

- **⚡ High-Speed Extraction**: Multithreaded scraping using Playwright.
- **🛡️ Proxy Rotation**: Integrated support for HTTP/Socks proxies with "Strict Mode" protection.
- **📱 PWA Supported**: Install the dashboard as a standalone app on your desktop or mobile.
- **🎨 Premium UI**: Modern dark mode interface with real-time statistics and glassmorphic design.
- **🔄 Auto-Updates**: Stays up-to-date with the latest features automatically on every launch.
- **📊 Data Management**: Export leads to CSV/Excel, track history, and manage datasets.

---

## 🛠️ Installation & Setup

### 1. Simple Installation (Recommended)
This is the professional way to install Map Miner. It sets up the **global command**, creates the virtual environment, and installs all system drivers automatically.

```bash
git clone https://github.com/shayan-human/MAP-MINER.git ~/mapminer
cd ~/mapminer && bash install.sh
```
> [!NOTE]
> This step requires `sudo` privileges to create the global shortcut and install browser dependencies.

---

## 🏃 Quick Start

Once the installer is finished, you can launch the dashboard from **ANY** terminal window and **ANY** folder by just typing:

```bash
mapminer
```

### Advanced Usage
- **Force Re-Setup**: If you ever need to refresh your dependencies or fix an installation, run:
  ```bash
  mapminer --setup
  ```
- **Auto-Updates**: Every time you launch with `mapminer`, the tool automatically checks for new code on GitHub. If updates are found, it pulls them and restarts itself instantly!

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Built with ❤️ by [Shayan Alam](https://github.com/shayan-human)**
