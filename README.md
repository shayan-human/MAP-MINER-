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

### 1. Clone & Setup
```bash
git clone https://github.com/shayan-human/MAP-MINER.git
cd MAP-MINER
```

### 2. First-Time Installation
To install all necessary dependencies (including Playwright system drivers), run:
```bash
python3 run.py --setup
```
> [!NOTE]
> This step may require `sudo` privileges to install browser dependencies on Linux.

---

## 🏃 Quick Start

Once the setup is complete, you can launch the dashboard any time with a single command:

```bash
python3 run.py
```

The application will:
1. Check for updates automatically.
2. Verify your virtual environment.
3. Start the dashboard at **http://localhost:8000**

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Built with ❤️ by [Shayan Alam](https://github.com/shayan-human)**
