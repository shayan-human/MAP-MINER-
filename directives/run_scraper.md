# SOP: Running Map Miner

This directive outlines how to use the Map Miner in different modes.

## 1. Web UI Mode (Recommended)
Use this mode to interact with the scraper via a browser interface.

- **Start command:** `bash execution/start_web_gui.sh`
- **Access:** http://localhost:8080
- **Storage:** Results are stored in the `gmapsdata/` directory.

## 2. CLI Mode
Use this mode for automated or batch processing.

- **Command:** `python3 execution/run_cli_query.py --query "your search query"`
- **Options:**
    - `--email`: Enable email extraction (slower).
    - `--depth`: Number of result pages to scroll.

## 3. Data Management
- All temporary files should be placed in `.tmp/`.
- Final deliverables should be handled according to the specific task requirements.
