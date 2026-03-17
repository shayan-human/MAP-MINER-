import os
import re
import asyncio
import uuid
import json
import datetime
import subprocess
from fastapi import FastAPI, Form, Request, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from turbo.search import scrape_gmaps
from turbo.utils import parse_proxies
from turbo.enrich import enrich_business
from turbo.db import LeadDB
import pandas as pd

REPO_URL = "https://github.com/shayan-human/MAP-MINER-TEMP.git"
LOCAL_VERSION_FILE = os.path.join(os.path.dirname(__file__), ".version")

def check_and_update():
    try:
        current_hash = subprocess.run(
            ["git", "rev-parse", "HEAD"], 
            capture_output=True, text=True, cwd=os.path.dirname(__file__)
        ).stdout.strip()
        
        stored_hash = ""
        if os.path.exists(LOCAL_VERSION_FILE):
            with open(LOCAL_VERSION_FILE, "r") as f:
                stored_hash = f.read().strip()
        
        if stored_hash != current_hash:
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                capture_output=True, text=True, cwd=os.path.dirname(__file__)
            )
            if result.returncode == 0:
                with open(LOCAL_VERSION_FILE, "w") as f:
                    f.write(current_hash)
                print(f"MAP-MINER: Updated to {current_hash[:8]}")
                return True
        return False
    except Exception:
        return False

check_and_update()

app = FastAPI(title="Map Miner Dashboard")

# Setup directories
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
HISTORY_FILE = os.path.join(OUTPUT_DIR, "history.json")
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize Database
db = LeadDB(os.path.join(OUTPUT_DIR, "leads.db"))

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# In-memory job status
jobs = {}

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

@app.post("/api/scrape")
async def start_scrape(
    background_tasks: BackgroundTasks,
    niche: str = Form(...),
    location: str = Form(...),
    max_results: int = Form(10),
    depth: int = Form(2),
    concurrency: int = Form(5),
    proxies: str = Form(None),
    email_limit: int = Form(0)
):
    job_id = str(uuid.uuid4())
    
    # Auto-scale depth based on max_results for better coverage
    # 50 results often need 4-5 scrolls to trigger dynamic loading reliably
    auto_depth = max(depth, (max_results // 5) + 1)
    
    jobs[job_id] = {
        "id": job_id,
        "niche": niche,
        "location": location,
        "status": "Starting...",
        "progress": 0,
        "total": 0,
        "file": None,
        "created_at": datetime.datetime.now().isoformat()
    }
    
    background_tasks.add_task(run_scrape_task, job_id, niche, location, max_results, auto_depth, concurrency, proxies, email_limit)
    return {"job_id": job_id}

async def run_scrape_task(job_id, niche, location, max_results, depth, concurrency, proxy_string, email_limit):
    query = f"{niche} in {location}"
    proxies_list = parse_proxies(proxy_string) if proxy_string else None
    
    # helper for CSV preparation
    def prepare_df(leads_list):
        if not leads_list:
            return pd.DataFrame(columns=['name', 'emails', 'website', 'phone', 'address', 'zip_code', 'socials', 'ip_address'])
        df = pd.DataFrame(leads_list)
        df = df.drop_duplicates(subset=['name'])
        if 'emails' in df.columns:
            df['emails'] = df['emails'].apply(lambda x: "; ".join(x) if isinstance(x, list) else (x or ""))
        else:
            df['emails'] = ""
        
        if 'zip_code' not in df.columns:
            df['zip_code'] = ""
            
        if 'socials' not in df.columns:
            df['socials'] = ""
        if 'ip_address' not in df.columns:
            df['ip_address'] = "N/A"
        
        cols = ['name', 'emails', 'website', 'phone', 'address', 'zip_code', 'socials', 'ip_address']
        available_cols = [c for c in cols if c in df.columns]
        return df[available_cols]

    try:
        # Get current IP
        current_ip = "Local"
        import httpx
        try:
            proxy_config = parse_proxies(proxy_string)[0] if proxy_string else None
            async with httpx.AsyncClient(proxy=proxy_config, timeout=5.0, verify=False) as client:
                ip_resp = await client.get("https://api.ipify.org", timeout=5.0)
                if ip_resp.status_code == 200:
                    current_ip = ip_resp.text.strip()
        except:
            pass

        jobs[job_id]["status"] = "Searching Google Maps..."
        businesses, fail_screenshot = await scrape_gmaps(query, depth=depth, max_results=max_results, proxy_string=proxy_string)
        
        if not businesses:
            jobs[job_id]["status"] = "No businesses found."
            jobs[job_id]["fail_screenshot"] = fail_screenshot
            return

        # Post-process results for ZIP and IP
        for biz in businesses:
            biz['ip_address'] = current_ip
            # Extract ZIP Code using regex
            if biz.get('address'):
                zip_match = re.search(r'\b\d{5}(?:-\d{4})?\b', biz['address'])
                biz['zip_code'] = zip_match.group(0) if zip_match else ""
            else:
                biz['zip_code'] = ""

        # 1. Track ALL found (before enrichment)
        total_found = len(businesses)
        unique_businesses = []
        duplicate_businesses = []
        
        for biz in businesses:
            if not db.is_duplicate(biz.get('name'), biz.get('phone'), biz.get('address')):
                unique_businesses.append(biz)
            else:
                duplicate_businesses.append(biz)
        
        duplicates_skipped = len(duplicate_businesses)
        unique_count = len(unique_businesses)
        
        jobs[job_id]["total_found"] = total_found
        jobs[job_id]["duplicates_skipped"] = duplicates_skipped
        jobs[job_id]["unique_found"] = unique_count
        
        if not unique_businesses:
            # Prepare and save duplicates file
            df_duplicates = prepare_df(duplicate_businesses)
            file_all = f"leads_all_{job_id[:8]}.csv"
            df_duplicates.to_csv(os.path.join(OUTPUT_DIR, file_all), index=False)

            jobs[job_id]["status"] = "Complete"
            jobs[job_id]["progress"] = 0
            jobs[job_id]["total"] = 0
            jobs[job_id]["result_count"] = 0
            jobs[job_id]["email_count"] = 0
            jobs[job_id]["file_all"] = file_all
            jobs[job_id]["results_unique"] = []
            jobs[job_id]["results_duplicates"] = df_duplicates.to_dict('records')
            
            # Save to history
            history = load_history()
            history.insert(0, {
                "id": job_id,
                "niche": niche,
                "location": location,
                "leads": 0,
                "total_found": total_found,
                "duplicates": duplicates_skipped,
                "emails": 0,
                "file": file_all, # Use all-leads file as primary
                "file_unique": None,
                "file_all": file_all,
                "created_at": jobs[job_id]["created_at"]
            })
            save_history(history)
            return

        semaphore = asyncio.Semaphore(concurrency)
        enriched_results = []
        progress_count = 0
        lock = asyncio.Lock()
        
        async def enriched_worker(biz):
            nonlocal progress_count
            async with semaphore:
                # Always try to enrich if website is present, even duplicates
                # This ensures we get the latest emails for every search.
                if biz.get('website'):
                    res = await enrich_business(biz, proxies=proxies_list, limit=email_limit)
                else:
                    res = biz
                    if 'emails' not in res: res['emails'] = []
                    if 'socials' not in res: res['socials'] = ""
                    res['ip_address'] = "N/A"
                
                enriched_results.append(res)
                
                async with lock:
                    progress_count += 1
                    jobs[job_id]["progress"] = progress_count
                    jobs[job_id]["status"] = f"Enriching... ({progress_count}/{total_found})"

        tasks = [enriched_worker(biz) for biz in businesses]
        print(f"  [Engine] Starting enrichment for {total_found} leads")
        await asyncio.gather(*tasks)
        
        # Save to DB (now handles updates/merges)
        db.add_leads(enriched_results)
        
        # Prepare DataFrames
        df_all = prepare_df(enriched_results)
        
        # Filter for unique ones (for the "unique" file)
        uniques_list = []
        for res in enriched_results:
            if not any(u.get('name') == res.get('name') and u.get('phone') == res.get('phone') for u in uniques_list):
                uniques_list.append(res)
        
        df_unique = prepare_df(uniques_list)
        
        # Save files
        file_unique = f"leads_unique_{job_id[:8]}.csv"
        file_all = f"leads_all_{job_id[:8]}.csv"
        
        df_unique.to_csv(os.path.join(OUTPUT_DIR, file_unique), index=False)
        df_all.to_csv(os.path.join(OUTPUT_DIR, file_all), index=False)
        
        leads_with_email = len(df_all[df_all['emails'].str.len() > 0]) if not df_all.empty else 0
        
        jobs[job_id]["status"] = "Complete"
        jobs[job_id]["file_unique"] = file_unique
        jobs[job_id]["file_all"] = file_all
        jobs[job_id]["result_count"] = len(df_all)
        jobs[job_id]["email_count"] = leads_with_email
        jobs[job_id]["results_unique"] = df_unique.to_dict('records')
        jobs[job_id]["results_duplicates"] = [] # Not really used in this logic now
        
        # Save to history
        history = load_history()
        history.insert(0, {
            "id": job_id,
            "niche": niche,
            "location": location,
            "leads": len(df_unique),
            "total_found": total_found,
            "duplicates": duplicates_skipped,
            "emails": leads_with_email,
            "file": file_unique, # Legacy compat
            "file_unique": file_unique,
            "file_all": file_all,
            "created_at": jobs[job_id]["created_at"]
        })
        save_history(history)
        
        # Add to Master DB
        db.add_leads(enriched_uniques)
            
    except Exception as e:
        import traceback
        print(f"Error in background task: {e}")
        traceback.print_exc()
        jobs[job_id]["status"] = f"Error: {str(e)}"

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    return jobs.get(job_id, {"error": "Job not found"})

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        return FileResponse(filepath, filename=filename, media_type='text/csv')
    return JSONResponse({"error": "File not found"}, status_code=404)

# === History API ===
@app.get("/api/history")
async def get_history():
    return load_history()

@app.delete("/api/history/{job_id}")
async def delete_history_item(job_id: str):
    history = load_history()
    # Find and remove the file
    for item in history:
        if item["id"] == job_id and item.get("file"):
            filepath = os.path.join(OUTPUT_DIR, item["file"])
            if os.path.exists(filepath):
                os.remove(filepath)
    history = [h for h in history if h["id"] != job_id]
    save_history(history)
    return {"status": "deleted"}

# === Datasets API ===
@app.get("/api/datasets")
async def get_datasets():
    datasets = []
    for f in os.listdir(OUTPUT_DIR):
        if f.endswith('.csv'):
            filepath = os.path.join(OUTPUT_DIR, f)
            stat = os.stat(filepath)
            # Count rows
            try:
                df = pd.read_csv(filepath)
                rows = len(df)
                cols = list(df.columns)
            except:
                rows = 0
                cols = []
            datasets.append({
                "filename": f,
                "size_bytes": stat.st_size,
                "rows": rows,
                "columns": cols,
                "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
    datasets.sort(key=lambda x: x["modified"], reverse=True)
    return datasets

@app.delete("/api/datasets/{filename}")
async def delete_dataset(filename: str):
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return {"status": "deleted"}
    return JSONResponse({"error": "File not found"}, status_code=404)

# === Proxies API (localStorage-based, but with a save endpoint) ===
@app.get("/api/proxies")
async def get_proxies():
    proxy_file = os.path.join(OUTPUT_DIR, "proxies.json")
    if os.path.exists(proxy_file):
        try:
            with open(proxy_file, 'r') as f:
                data = json.load(f)
                return data if "proxies" in data else {"proxies": []}
        except:
            return {"proxies": []}
    return {"proxies": []}

@app.post("/api/proxies")
async def save_proxies(request: Request):
    data = await request.json()
    proxy_file = os.path.join(OUTPUT_DIR, "proxies.json")
    with open(proxy_file, 'w') as f:
        json.dump(data, f, indent=2)
    return {"status": "saved"}

from pydantic import BaseModel
class ProxyTestRequest(BaseModel):
    proxy: str

@app.post("/api/test-proxy")
async def test_proxy(data: ProxyTestRequest):
    import httpx
    from turbo.utils import parse_proxies
    
    proxies = parse_proxies(data.proxy)
    if not proxies:
        return {"status": "error", "message": "No valid proxy provided"}
    
    # Test the first one
    proxy_url = proxies[0]

    try:
        # verify=False to avoid SSL issues with some proxies
        async with httpx.AsyncClient(proxy=proxy_url, timeout=12.0, verify=False) as client:
            # Check IP and connectivity
            response = await client.get("https://api.ipify.org", timeout=10.0)
            if response.status_code == 200:
                return {"status": "success", "ip": response.text.strip()}
            else:
                return {"status": "error", "message": f"Proxy returned status code {response.status_code}"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": f"{type(e).__name__}: {str(e)}"}

@app.post("/api/enrich-csv")
async def enrich_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    concurrency: int = Form(5),
    proxies: str = Form(None),
    email_limit: int = Form(0)
):
    """Upload a CSV with a 'website' column; enriches each row with scraped emails."""
    try:
        import io
        contents = await file.read()
        uploaded_df = pd.read_csv(io.BytesIO(contents))

        if uploaded_df.empty:
            return JSONResponse({"error": "Uploaded file is empty"}, status_code=400)

        if 'website' not in uploaded_df.columns:
            return JSONResponse({"error": "CSV must have a 'website' column"}, status_code=400)

        job_id = str(uuid.uuid4())
        jobs[job_id] = {
            "id": job_id,
            "type": "enrich",
            "status": "Starting enrichment...",
            "progress": 0,
            "total": len(uploaded_df),
            "file": None,
            "created_at": datetime.datetime.now().isoformat()
        }

        # Convert df rows to list of dicts
        rows = uploaded_df.to_dict('records')

        background_tasks.add_task(
            run_enrich_csv_task, job_id, rows, concurrency, proxies, email_limit
        )
        return {"job_id": job_id}
    except Exception as e:
        return JSONResponse({"error": f"Failed to process CSV: {str(e)}"}, status_code=400)


async def run_enrich_csv_task(job_id, rows, concurrency, proxy_string, email_limit):
    """Background task: enrich each row with email scraping."""
    try:
        proxies_list = parse_proxies(proxy_string) if proxy_string else None
        total = len(rows)
        semaphore = asyncio.Semaphore(concurrency)
        enriched_rows = []
        progress_count = 0
        lock = asyncio.Lock()

        async def worker(row):
            nonlocal progress_count
            async with semaphore:
                website = row.get('website')
                # Skip if not a string (handles NaN) or empty
                if isinstance(website, str) and website.strip():
                    res = await enrich_business(row, proxies=proxies_list, limit=email_limit)
                else:
                    res = row
                    if 'emails' not in res:
                        res['emails'] = []

                enriched_rows.append(res)

                async with lock:
                    progress_count += 1
                    jobs[job_id]["progress"] = progress_count
                    jobs[job_id]["status"] = f"Enriching... ({progress_count}/{total})"

        tasks = [worker(row) for row in rows]
        print(f"  [Enricher] Starting email enrichment for {total} leads")
        await asyncio.gather(*tasks)

        # Build output DataFrame
        df = pd.DataFrame(enriched_rows)
        if 'emails' in df.columns:
            df['emails'] = df['emails'].apply(
                lambda x: "; ".join(x) if isinstance(x, list) else (x or "")
            )
        else:
            df['emails'] = ""

        # Save output
        filename = f"enriched_{job_id[:8]}.csv"
        filepath = os.path.join(OUTPUT_DIR, filename)
        df.to_csv(filepath, index=False)

        leads_with_email = len(df[df['emails'].str.len() > 0]) if not df.empty else 0

        jobs[job_id]["status"] = "Complete"
        jobs[job_id]["file"] = filename
        jobs[job_id]["result_count"] = total
        jobs[job_id]["email_count"] = leads_with_email

        print(f"  [Enricher] Done! {leads_with_email}/{total} leads got emails → {filename}")

    except Exception as e:
        import traceback
        print(f"Error in enrich CSV task: {e}")
        traceback.print_exc()
        jobs[job_id]["status"] = f"Error: {str(e)}"


@app.post("/api/refine")
async def refine_leads(file: UploadFile = File(...)):
    try:
        # 1. Load the uploaded file
        contents = await file.read()
        import io
        uploaded_df = pd.read_csv(io.BytesIO(contents))
        
        if uploaded_df.empty:
            return {"status": "error", "message": "Uploaded file is empty"}
        
        initial_count = len(uploaded_df)
        
        # 2. Filter against Master DB
        def is_duplicate(row):
            return db.is_duplicate(row.get('name', ''), row.get('phone', ''), row.get('address', ''))

        # Apply filtering
        # We assume the uploaded CSV has at least a 'name' column
        if 'name' not in uploaded_df.columns:
            return {"status": "error", "message": "Uploaded CSV must have a 'name' column"}

        refined_df = uploaded_df[~uploaded_df.apply(is_duplicate, axis=1)]
        refined_count = len(refined_df)
        duplicates_removed = initial_count - refined_count
        
        # 4. Save the results
        job_id = str(uuid.uuid4())[:8]
        filename = f"refined_{job_id}.csv"
        filepath = os.path.join(OUTPUT_DIR, filename)
        refined_df.to_csv(filepath, index=False)
        
        return {
            "status": "success",
            "initial_count": initial_count,
            "refined_count": refined_count,
            "duplicates_removed": duplicates_removed,
            "file": filename
        }
    except Exception as e:
        return {"status": "error", "message": f"Refinement failed: {str(e)}"}

# Serve Frontend
@app.get("/")
async def read_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"error": "Frontend not built yet. Check turbo/static/"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
