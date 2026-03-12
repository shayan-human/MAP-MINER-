import subprocess
import os
import argparse
import sys

def run_scraper(query, email=False, depth=1):
    tmp_input = ".tmp/queries.txt"
    results_file = ".tmp/results.csv"
    
    os.makedirs(".tmp", exist_ok=True)
    
    with open(tmp_input, "w") as f:
        f.write(query)
    
    # Ensure results file exists for volume mounting
    if not os.path.exists(results_file):
        with open(results_file, "w") as f:
            pass
            
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{os.getcwd()}/{tmp_input}:/queries.txt",
        "-v", f"{os.getcwd()}/{results_file}:/results.csv",
        "google-maps-scraper",
        "-input", "/queries.txt",
        "-results", "/results.csv",
        "-depth", str(depth),
        "-exit-on-inactivity", "1m"
    ]
    
    if email:
        cmd.append("-email")
        
    print(f"Running scraper for query: {query}")
    try:
        subprocess.run(cmd, check=True)
        print(f"Scraping complete. Results saved to {results_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error running scraper: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Google Maps Scraper CLI")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--email", action="store_true", help="Extract emails")
    parser.add_argument("--depth", type=int, default=1, help="Max scroll depth")
    
    args = parser.parse_args()
    run_scraper(args.query, args.email, args.depth)
