# 🗺️ Map Miner — Ultimate Lead Extraction Dashboard

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/products/docker-desktop)

**Map Miner** is a powerful, high-performance lead generation tool designed to extract business data from Google Maps at scale. Featuring a sleek, glassmorphic dashboard and advanced extraction logic, it's the premium solution for B2B lead mining.

---

## 🚀 Key Features

- **⚡ High-Accuracy Engine**: Stable searching logic for maximum regional accuracy
- **🛡️ Proxy Rotation**: Integrated support for HTTP/Socks proxies with "Strict Mode" protection
- **⚡ High-Speed Extraction**: Multithreaded scraping using Playwright
- **📱 PWA Supported**: Install the dashboard as a standalone app
- **🎨 Premium UI**: Modern dark mode interface with glassmorphic design
- **🐳 Docker**: Runs anywhere with zero setup

---

## 🛠️ Installation (Docker)

Best for **no setup required** - works on Windows, Mac, and Linux.

```bash
# Clone
git clone https://github.com/shayan-human/MAP-MINER.git
cd MAP-MINER

# First time build
docker-compose up --build
```

Then open **http://localhost:8000**

> ⚠️ **Requires**: [Docker Desktop](https://www.docker.com/products/docker-desktop) installed

---

## ⚡ Quick Start

**Every time you want to run Map Miner:**
```bash
docker-compose up
```

This 1 command will:
- ✅ Auto-update with latest code from GitHub
- ✅ Start the server at http://localhost:8000

---

## 💡 Tips & Flags

- **Rebuild after fixes** (if you get errors):
  ```bash
  docker-compose build --no-cache
  docker-compose up
  ```
- **Stop Container**:
  ```bash
  docker-compose down
  ```
- **View Logs**:
  ```bash
  docker-compose logs -f
  ```

---

## 🩹 Troubleshooting

### Browser/Chromium Errors
If you get errors like `libXfixes.so.3` or `Browser has been closed`:
```bash
docker-compose build --no-cache
docker-compose up
```

### Docker not working
- Make sure Docker Desktop is running
- On Windows, enable WSL2 in Docker Desktop settings

### Port 8000 in use
Change port in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"
```

### Container keeps restarting
Check logs:
```bash
docker-compose logs
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Built with ❤️ by [Shayan Alam](https://github.com/shayan-human)**
