import asyncio
import os
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from turbo.utils import get_random_ua

async def diagnostic():
    query = "real estate in kolkata"
    clean_query = query.replace(' ', '+')
    url = f"https://www.google.com/maps/search/{clean_query}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent=get_random_ua())
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        print(f"Navigating to {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(5)
        
        await page.screenshot(path="maps_diagnostic.png")
        print("Screenshot saved to maps_diagnostic.png")
        
        # Check for feed
        feed = await page.query_selector('div[role="feed"]')
        print(f"Feed found: {feed is not None}")
        
        # Check for businesses
        links = await page.evaluate(r'Array.from(document.querySelectorAll("a[href*=\"/maps/place/\"]")).map(a => a.getAttribute("aria-label"))')
        print(f"Leads found ({len(links)}): {links[:5]}")
        
        # Check for city links
        city_links = await page.evaluate(r'''() => {
            const suggestions = Array.from(document.querySelectorAll('button[aria-label*="Search in"], a[href*="/maps/search/"]'));
            return suggestions.map(el => ({
                text: el.innerText,
                label: el.getAttribute('aria-label'),
                tag: el.tagName
            }));
        }''')
        print(f"Potential city suggestions: {json.dumps(city_links[:10], indent=2)}")
        
        await browser.close()

if __name__ == "__main__":
    import json
    asyncio.run(diagnostic())
