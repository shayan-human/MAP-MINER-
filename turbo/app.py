import asyncio
import argparse
import pandas as pd
import os
from turbo.search import scrape_gmaps
from turbo.enrich import enrich_business

async def main():
    parser = argparse.ArgumentParser(description="Turbo Lead Scraper")
    parser.add_argument("--niche", required=True, help="Business niche")
    parser.add_argument("--location", required=True, help="Target location")
    parser.add_argument("--depth", type=int, default=2, help="Search depth (scrolls)")
    parser.add_argument("--max-results", type=int, default=20, help="Maximum results to collect")
    parser.add_argument("--concurrency", type=int, default=5, help="Number of concurrent enrichment tasks")
    parser.add_argument("--output", default="leads.csv", help="Output file name")
    
    args = parser.parse_args()
    query = f"{args.niche} in {args.location}"
    
    print(f"\n--- Starting Turbo Lead Collection ---")
    print(f"Target: {query}")
    print(f"Max Results: {args.max_results} | Depth: {args.depth}\n")
    
    # 1. Scrape Google Maps
    businesses = await scrape_gmaps(query, depth=args.depth, max_results=args.max_results)
    
    if not businesses:
        print("No businesses found.")
        return

    # 2. Enrich with Emails (Parallel)
    print(f"\n--- Starting Enrichment for {len(businesses)} leads (Concurrency: {args.concurrency}) ---")
    
    semaphore = asyncio.Semaphore(args.concurrency)
    
    async def enriched_worker(biz):
        async with semaphore:
            if biz['website']:
                return await enrich_business(biz)
            return None

    tasks = [enriched_worker(biz) for biz in businesses]
    results = await asyncio.gather(*tasks)
    
    # Filter results and keep only those with emails
    enriched_leads = [r for r in results if r and r.get('emails')]

    # 3. Save to CSV
    if enriched_leads:
        df = pd.DataFrame(enriched_leads)
        # Deduplication
        df = df.drop_duplicates(subset=['name', 'website'])
        
        # Flatten emails for CSV
        df['emails'] = df['emails'].apply(lambda x: "; ".join(x) if isinstance(x, list) else x)
        
        # Ensure 'socials' exists even if empty
        if 'socials' not in df.columns:
            df['socials'] = ""
            
        # Reorder columns for better readability
        cols = ['name', 'emails', 'website', 'phone', 'address', 'socials', 'ip_address']
        # Filter columns that actually exist
        available_cols = [c for c in cols if c in df.columns]
        df = df[available_cols]
        
        df.to_csv(args.output, index=False)
        print(f"\n--- Mission Complete ---")
        print(f"Saved {len(enriched_leads)} high-accuracy leads to {args.output}")
    else:
        print("\nNo leads with valid emails found.")

if __name__ == "__main__":
    asyncio.run(main())
