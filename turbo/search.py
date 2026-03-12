import asyncio
import random
import json
import os
import datetime
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from turbo.utils import parse_proxies

async def handle_consent(page):
    """Aggressive consent handler for Google/Maps."""
    consent_selectors = [
        'button[aria-label*="Accept all"]', 'button[aria-label*="Agree"]',
        'button:has-text("Accept all")', 'button:has-text("I agree")',
        'button:has-text("Allow all")', 'button:has-text("Accept")',
        'button:has-text("Admirer")', # Some regional variants
        'div[role="dialog"] button:has-text("Accept all")',
        '.qc-cmp2-summary-buttons button:nth-child(2)',
        'div[aria-modal="true"] button:has-text("Accept all")',
        '#introAgreeButton',
    ]
    # Check for CAPTCHA first
    is_captcha = await page.evaluate('() => document.body.innerText.includes("detecting unusual traffic") || document.querySelector("#captcha-form")')
    if is_captcha:
        print("  [V2.1] [WARNING] Google detected unusual traffic (CAPTCHA).")
        return

    for selector in consent_selectors:
        try:
            btn = await page.wait_for_selector(selector, timeout=2000)
            if btn:
                print(f"  [V2.1] Clicking consent: {selector}")
                await btn.click()
                await asyncio.sleep(1.0)
                # Check if dialog closed
                if not await page.is_visible(selector):
                    break
        except: pass

async def extract_details(context, lead, idx, total, results_list, lock):
    """Worker to extract details for a single business in a new tab."""
    page = await context.new_page()
    page.set_default_timeout(60000)
    
    # Block heavy resources
    await page.route("**/*.{png,jpg,jpeg,svg,webp,gif,css,woff,woff2,ttf,pdf}", lambda route: route.abort())
    
    try:
        await asyncio.sleep(random.uniform(0.1, 0.5))
        await page.goto(lead['link'], wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(0.5)
        
        details = await page.evaluate('''() => {
            const clean = (text) => text ? text.replace(/[^\x20-\x7E]/g, '').trim() : "";
            const name = document.querySelector('h1')?.innerText || "";
            
            // Try multiple selectors for website
            let website_el = document.querySelector('a[data-item-id="authority"]');
            if (!website_el) website_el = document.querySelector('a[aria-label*="Website"]');
            if (!website_el) website_el = document.querySelector('a[data-tooltip*="Open website"]');
            
            const phone_el = document.querySelector('button[data-tooltip="Copy phone number"]');
            const address_el = document.querySelector('button[data-item-id="address"]');
            const rating_el = document.querySelector('span[role="img"]');
            
            return {
                name: name,
                website: website_el ? website_el.href : "",
                phone: clean(phone_el ? phone_el.innerText : ""),
                address: clean(address_el ? address_el.innerText : ""),
                rating: rating_el ? rating_el.getAttribute('aria-label') || "" : ""
            };
        }''')
        
        if details['name']:
            async with lock:
                results_list.append(details)
                print(f"  [{len(results_list)}/{total}] Extracted: {details['name']}")
    except Exception as e:
        async with lock:
            results_list.append({
                'name': lead['name'],
                'website': '', 'phone': '', 'address': '', 'rating': ''
            })
            print(f"  [!] Extraction failed for: {lead['name']}")
    finally:
        await page.close()

async def scrape_gmaps(query, depth=2, max_results=50, proxy_string=None, is_subsearch=False):
    """
    [ENGINE-V2.0] High-Robustness Maps Scraper
    """
    from turbo.utils import get_random_ua, ProxyManager
    
    print(f"\n[ENGINE-V2.0] STARTING SEARCH: {query}")
    print(f"[ENGINE-V2.0] Target: {max_results} leads, Depth: {depth}")

    pm = ProxyManager(parse_proxies(proxy_string)) if proxy_string else None
    
    async with async_playwright() as p:
        proxy_config = pm.get_playwright_proxy() if pm else None
        
        try:
            print("  [V2] Launching browser...")
            browser = await p.chromium.launch(headless=True, proxy=proxy_config)
            print("  [V2] Browser initialized.")
        except Exception as e:
            if proxy_config:
                print(f"  [!] Proxy failed: {e}. Falling back to LOCAL IP...")
                browser = await p.chromium.launch(headless=True)
            else:
                raise e

        # Fixed modern UA for stability
        modern_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        context = await browser.new_context(user_agent=modern_ua, viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        page.set_default_timeout(60000)
        
        # Block heavy assets
        await page.route("**/*.{png,jpg,jpeg,svg,webp,gif,css,woff,woff2,ttf,pdf}", lambda route: route.abort())
        
        print("  [V2] Applying stealth...")
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        # [V2.1] Nuclear Interactive Search
        # We visit the base maps URL first to set the session/locale, 
        # then type the query to avoid regional redirects.
        base_url = "https://www.google.com/maps?hl=en"
        print(f"  [V2.1] Navigating to: {base_url}")
        
        try:
            await page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
            await handle_consent(page)
            
            # 2. Type the query
            print(f"  [V2.1] Typing query: {query}")
            search_box = None
            search_selectors = ['input#searchboxinput', 'input[name="q"]', 'input[aria-label*="Search"]']
            for selector in search_selectors:
                try:
                    search_box = await page.wait_for_selector(selector, timeout=5000)
                    if search_box: break
                except: pass
            
            if not search_box:
                raise Exception("Search box not found via interactive method")
                
            await search_box.click()
            await search_box.fill(query)
            await asyncio.sleep(0.5)
            await page.keyboard.press("Enter")
            
            # Fallback: Click the search button if Enter didn't work
            try:
                search_btn = await page.wait_for_selector('button#searchbox-searchbutton', timeout=2000)
                if search_btn:
                    await search_btn.click()
            except: pass
            
            print("  [V2.1] Search submitted. Waiting for results...")
            await asyncio.sleep(5.0)
            
            # Verify if we actually moved from the home page
            if page.url == base_url:
                print("  [V2.1] [WARNING] Still on base URL. Retrying with direct URL...")
                raise Exception("Search failed to trigger")
                
        except Exception as e:
            print(f"  [!] Interactive search failed/timed out: {e}. Trying URL method...")
            clean_query = " ".join(query.split()).replace(' ', '+')
            # Append hl=en and force English to avoid local redirects
            url = f"https://www.google.com/maps/search/{clean_query}?hl=en"
            await page.goto(url, wait_until="domcontentloaded")
            await handle_consent(page)
            await asyncio.sleep(5.0)

        # 2. Results Extraction Link Search (Permissive)
        print("  [V2] Waiting for leads to appear...")
        try:
            # Wait for content or place links
            await page.wait_for_selector('a[href*="/maps/place/"]', timeout=20000)
        except:
            print("  [!] Primary selector timed out. Checking body content...")
            # If no results container, maybe it's a "No results" page
            no_results = await page.evaluate('() => document.body.innerText.includes("Google Maps can\'t find") || document.body.innerText.includes("No results found")')
            if no_results:
                print(f"  [!] Google confirmed: No results found for '{query}'")
                await browser.close()
                return [], None
            
            print("  [!] Results might be lazy-loaded. Forcing 3x Nuclear Scrolls...")
            for _ in range(3):
                await page.mouse.wheel(0, 1500)
                await asyncio.sleep(2.0)


        # Harvest Place Links with Nuclear Scrolling
        print(f"  [V2] Harvesting business links (Target: {max_results})...")
        card_data = []
        last_count = 0
        scroll_attempts = 0
        max_scrolls = max(depth * 3, (max_results // 2) + 5) # Increased scroll attempts
        
        # Identification of results container (The "Feed")
        feed_selector = 'div[role="feed"], div[aria-label*="Results for"]'
        
        while len(card_data) < max_results and scroll_attempts < max_scrolls:
            # 1. Direct Element Scrolling (The "Nuclear" way)
            await page.evaluate(f'''(sel) => {{
                const el = document.querySelector(sel);
                if (el) {{
                    el.scrollBy(0, 1500);
                }} else {{
                    window.scrollBy(0, 1500);
                }}
            }}''', feed_selector)
            
            await asyncio.sleep(1.5)
            
            # 2. Harvest currently visible links
            current_cards = await page.evaluate(r'''() => {
                const results = [];
                const links = Array.from(document.querySelectorAll('a[href*="/maps/place/"]'));
                links.forEach(a => {
                    const name = a.getAttribute('aria-label') || a.innerText || "";
                    if (name && a.href && !results.find(r => r.link === a.href)) {
                        results.push({ name, link: a.href });
                    }
                });
                return results;
            }''')
            
            # 3. Update master card_data
            for card in current_cards:
                if not any(c['link'] == card['link'] for c in card_data):
                    card_data.append(card)
            
            print(f"  [V2] Scroll {scroll_attempts+1}/{max_scrolls}: Found {len(card_data)} leads...")
            
            # 4. End-of-results detection
            if len(card_data) == last_count:
                # If stuck, try a bigger scroll
                await page.mouse.wheel(0, 3000)
                await asyncio.sleep(2.0)
                
                # Check for "You've reached the end" or similar text
                end_check = await page.evaluate('''() => 
                    document.body.innerText.includes("You've reached the end") || 
                    document.body.innerText.includes("No more results")
                ''')
                if end_check:
                    print("  [V2] Google confirms: End of results reached.")
                    break
                    
                # If no new cards after retry, we might be truly done
                if len(card_data) == last_count and scroll_attempts > 5:
                    print("  [V2] No new leads appearing. Finishing harvest.")
                    break
            
            last_count = len(card_data)
            scroll_attempts += 1

        if not card_data:
            print("  [!] Stage 2 harvest failed. Taking emergency screenshot...")
            os.makedirs("outputs", exist_ok=True)
            spath = f"outputs/fail_{datetime.datetime.now().strftime('%H%M%S')}.png"
            await page.screenshot(path=spath)
            print(f"  [V2] Screenshot saved to: {spath}")
            await browser.close()
            return [], spath

        print(f"  [V2] Found {len(card_data)} total candidates. Extracting top {max_results}...")
        
        # Parallel extraction
        final_results = []
        lock = asyncio.Lock()
        batch_size = 5
        
        for i in range(0, min(len(card_data), max_results), batch_size):
            batch = card_data[i:i+batch_size]
            tasks = [extract_details(context, lead, i+j, max_results, final_results, lock) for j, lead in enumerate(batch)]
            await asyncio.gather(*tasks)
            await asyncio.sleep(0.5)
            
        print(f"[ENGINE-V2.0] COMPLETED. Found {len(final_results)} leads.")
        await browser.close()
        return final_results, None

if __name__ == "__main__":
    # Test
    asyncio.run(scrape_gmaps("Car detailing Miami", depth=1, max_results=5))
