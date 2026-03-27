# MAP-MINER

**By Shayan Alam** | A powerful Google Maps scraper with web dashboard

![Dashboard](docs/dashboard.png)

---

## Quick Install (One Command)

### Linux/macOS
```bash
curl -sL https://raw.githubusercontent.com/shayan-human/MAP-MINER/main/install.sh | bash
```

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/shayan-human/MAP-MINER/main/install.ps1 | iex
```

### Manual Install
```bash
git clone https://github.com/shayan-human/MAP-MINER.git
cd MAP-MINER
./mapminer install
```

### Global Install (optional)
```bash
# Run with --global to use 'mapminer' from anywhere
curl -sL https://raw.githubusercontent.com/shayan-human/MAP-MINER/main/install.sh | bash -s -- --global
```

---

## Quick Start

```bash
# First time: Install dependencies
./mapminer install

# Start the server (auto-updates on each run)
./mapminer
```

Then open **http://localhost:8000** in your browser.

## CLI Commands

| Command | Description |
|---------|-------------|
| `./mapminer` | Start server (auto-updates first) |
| `./mapminer install` | Install dependencies |
| `./mapminer update` | Pull latest updates |

---

## Auto-Update

MAP-MINER automatically checks for updates on every run. When you push new features to GitHub, users will be notified:

```
🔄 Updated to latest version: v1.2.0
```

No manual updates needed!

---

## Features

- 🌐 **Web Dashboard** - Beautiful UI for managing scrapes
- 🔍 **Google Maps Scraping** - Extract business data at scale
- 📧 **Email Enrichment** - Find business emails
- 📊 **Export to CSV** - Multiple output formats
- ⚡ **Async Performance** - Fast concurrent scraping
- 🔄 **Auto-Update** - Always stay up to date

---

## Configuration

| Option | Description |
|--------|-------------|
| `niche` | Business type (e.g., "plumber", "restaurant") |
| `location` | City or region (e.g., "New York", "California") |
| `max_results` | Maximum results to scrape |
| `depth` | Search depth for better coverage |
| `concurrency` | Parallel browser instances |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/scrape` | POST | Start a new scrape job |
| `/api/jobs` | GET | List all jobs |
| `/api/jobs/{id}` | GET | Get job status |
| `/api/export/{job_id}` | GET | Download results |

---

## License

MIT License - © 2026 Shayan Alam

---

## GitHub

https://github.com/shayan-human/MAP-MINER
