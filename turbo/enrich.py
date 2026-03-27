import asyncio
import httpx
import re
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
]

def get_random_ua():
    return random.choice(USER_AGENTS)


def _deobfuscate_text(text):
    """Replace common email obfuscation patterns before regex extraction."""
    # Replace [at] (at) {at} variations (bracketed only — safe)
    text = re.sub(r'\s*[\[\(\{]\s*at\s*[\]\)\}]\s*', '@', text, flags=re.IGNORECASE)
    # Replace [dot] (dot) {dot} variations (bracketed only — safe)
    text = re.sub(r'\s*[\[\(\{]\s*dot\s*[\]\)\}]\s*', '.', text, flags=re.IGNORECASE)
    return text


# Junk patterns to filter out
_JUNK_PATTERNS = [
    'example@', '@example.', 'your@email', 'info@example',
    'team@latofonts', 'filler@godaddy', 'impallari@gmail',
    'sentry', 'wixpress', 'noreply', 'no-reply', '@domain.com',
    '@sentry.', '@wix.', 'webpack', 'cloudflare', '@test.',
    'username@', 'user@', 'email@email', 'name@', 'sample@',
]

_EXCLUDED_EXTS = (
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp',
    '.pdf', '.zip', '.css', '.js', '.woff', '.woff2',
    '.ttf', '.eot', '.ico', '.mp4', '.mp3',
)


async def extract_emails_from_text(text):
    """Extract emails from text, handling obfuscated patterns."""
    # First deobfuscate
    text = _deobfuscate_text(text)

    email_pattern = r'[a-zA-Z0-9._%+\-]+@(?![a-zA-Z0-9.\-]*\.(?:png|jpg|jpeg|gif|svg|webp|pdf|zip|gz|tar|mp4|mp3|exe|dll|bin|iso|css|js|woff|woff2|ttf|eot|ico))[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
    found = re.findall(email_pattern, text)

    cleaned = []
    for e in found:
        e_low = e.lower().strip('.')
        if any(e_low.endswith(ext) for ext in _EXCLUDED_EXTS):
            continue
        if any(junk in e_low for junk in _JUNK_PATTERNS):
            continue
        # Skip if domain part is too short or suspicious
        parts = e_low.split('@')
        if len(parts) != 2:
            continue
        domain = parts[1]
        if '.' not in domain or len(domain) < 4:
            continue
        cleaned.append(e_low)

    return list(set(cleaned))


async def extract_mailto_emails(html):
    """Extract emails from mailto: links — the most reliable source."""
    soup = BeautifulSoup(html, 'html.parser')
    emails = set()
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if href.lower().startswith('mailto:'):
            # Extract email after mailto: and before any ?subject= etc
            raw = href[7:].split('?')[0].strip()
            if raw and '@' in raw:
                emails.add(raw.lower())
    return list(emails)


async def extract_emails_from_attributes(html):
    """Extract emails from HTML attributes like data-email, data-cfemail, title, content meta tags."""
    soup = BeautifulSoup(html, 'html.parser')
    emails = set()

    # Check common attributes that contain emails
    email_attrs = ['data-email', 'data-mail', 'data-contact', 'title', 'aria-label']
    for attr in email_attrs:
        for tag in soup.find_all(attrs={attr: True}):
            val = tag[attr]
            found = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', val)
            emails.update(e.lower() for e in found)

    # Check meta tags (og:email, contact:email, etc.)
    for meta in soup.find_all('meta', attrs={'content': True}):
        content = meta.get('content', '')
        if '@' in content:
            found = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', content)
            emails.update(e.lower() for e in found)

    return list(emails)


async def get_page_content(client, url):
    try:
        response = await client.get(url, timeout=15.0, follow_redirects=True)
        if response.status_code == 200:
            return response.text
    except Exception:
        pass
    return None


async def find_contact_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    contact_links = set()
    social_links = set()

    noise_keywords = ['privacy', 'terms', 'legal', 'policy', 'tos', 'disclaimer', 'cookies', 'login', 'signup', 'cart', 'checkout']
    contact_keywords = ['contact', 'about', 'team', 'staff', 'reach', 'info', 'support', 'connect', 'get-in-touch', 'enquiry', 'inquiry']
    social_platforms = ['facebook.com', 'instagram.com', 'linkedin.com', 'twitter.com', 'x.com', 'youtube.com', 'tiktok.com']

    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text().lower().strip()
        href_low = href.lower()

        # Skip mailto/tel/javascript
        if href_low.startswith(('mailto:', 'tel:', 'javascript:', '#')):
            continue

        # Check for social media
        if any(platform in href_low for platform in social_platforms):
            social_links.add(href)
            continue

        # Skip noisy links
        if any(nk in href_low or nk in text for nk in noise_keywords):
            continue

        # Check if the link text or href contains contact keywords
        if any(kw in text for kw in contact_keywords) or any(kw in href_low for kw in contact_keywords):
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                contact_links.add(full_url)

    return list(contact_links), list(social_links)


# Common contact page paths to try as fallback
COMMON_CONTACT_PATHS = [
    '/contact', '/contact-us', '/contactus',
    '/about', '/about-us', '/aboutus',
    '/team', '/our-team',
    '/support', '/help',
    '/get-in-touch',
]


async def _extract_all_emails_from_html(html):
    """Run all email extraction methods on a single HTML page."""
    emails = set()

    # Method 1: Regex on visible text
    text_emails = await extract_emails_from_text(html)
    emails.update(text_emails)

    # Method 2: mailto: links (most reliable)
    mailto_emails = await extract_mailto_emails(html)
    emails.update(mailto_emails)

    # Method 3: HTML attributes
    attr_emails = await extract_emails_from_attributes(html)
    emails.update(attr_emails)

    return emails


async def enrich_business(business_data, proxies=None, limit=0, strict_mode=False):
    """
    Takes business data with a website and tries to find emails.
    Now uses multiple extraction methods and ALWAYS checks contact pages.
    :param limit: If > 0, stops after finding this many unique emails.
    :param strict_mode: If True, fails without proxy to protect user IP.
    """
    website = business_data.get('website')
    # Check if empty or NaN (pandas reads empty cells as float NaN)
    if not website or not isinstance(website, str):
        if 'emails' not in business_data:
            business_data['emails'] = []
        if strict_mode:
            business_data['ip_address'] = "BLOCKED - No website"
        return business_data

    # Ensure website has protocol
    if not website.startswith(('http://', 'https://')):
        website = 'https://' + website

    emails = set()
    socials = set()

    def is_limit_reached():
        return limit > 0 and len(emails) >= limit

    # Random delay for stealth
    await asyncio.sleep(random.uniform(0.3, 1.5))

    # Setup proxy
    proxy = None
    if proxies:
        proxy = random.choice(proxies)
    
    # Strict Mode Check - Must have proxy
    if strict_mode and not proxy:
        raise Exception("❌ STRICT MODE: No proxy available. Stopping to protect your IP. Provide a proxy or disable strict mode.")

    async with httpx.AsyncClient(
        headers={"User-Agent": get_random_ua()},
        verify=False,
        follow_redirects=True,
        proxy=proxy,
        timeout=18.0
    ) as client:
        # Detect IP (proxy confirmation)
        try:
            ip_resp = await client.get("https://api.ipify.org", timeout=5.0)
            business_data['ip_address'] = ip_resp.text.strip() if ip_resp.status_code == 200 else "unknown"
        except Exception:
            business_data['ip_address'] = "unknown"

        # === 1. Check Home Page ===
        html = await get_page_content(client, website)
        if html:
            home_emails = await _extract_all_emails_from_html(html)
            emails.update(home_emails)
            
            if is_limit_reached():
                # Trim to limit if we overshot on homepage
                final_emails = list(emails)[:limit] if limit > 0 else list(emails)
                business_data['emails'] = final_emails
                business_data['socials'] = "" # Might miss socials if we exit too early, but usually found on homepage
                # Try to get socials from home page before returning
                _, social_links = await find_contact_links(html, website)
                business_data['socials'] = "; ".join(list(social_links))
                return business_data

            # === 2. Find contact/about links from navigation ===
            contact_links, social_links = await find_contact_links(html, website)
            socials.update(social_links)

            # === 3. ALWAYS check contact/about subpages (not just when 0 emails) ===
            pages_to_check = list(set(contact_links))
            random.shuffle(pages_to_check)

            # Check up to 5 contact-related links found in navigation
            for link in pages_to_check[:5]:
                if is_limit_reached(): break
                await asyncio.sleep(random.uniform(0.5, 1.5))
                sub_html = await get_page_content(client, link)
                if sub_html:
                    sub_emails = await _extract_all_emails_from_html(sub_html)
                    emails.update(sub_emails)

        # === 4. Try common fallback paths if we still have few/no contact links ===
        if not is_limit_reached():
            base_domain = f"{urlparse(website).scheme}://{urlparse(website).netloc}"
            tried_urls = set(contact_links) if html else set()

            # Always try common paths to catch emails we might have missed
            fallback_paths = COMMON_CONTACT_PATHS.copy()
            random.shuffle(fallback_paths)

            for path in fallback_paths[:4]:
                if is_limit_reached(): break
                fallback_url = base_domain + path
                if fallback_url in tried_urls:
                    continue
                tried_urls.add(fallback_url)

                await asyncio.sleep(random.uniform(0.5, 1.5))
                fb_html = await get_page_content(client, fallback_url)
                if fb_html:
                    fb_emails = await _extract_all_emails_from_html(fb_html)
                    emails.update(fb_emails)
                    # If we found emails from a fallback, that's enough
                    if fb_emails:
                        break

    # Final filtering — remove any junk that slipped through
    clean_emails = []
    for e in emails:
        e_low = e.lower().strip('.')
        if any(junk in e_low for junk in _JUNK_PATTERNS):
            continue
        if any(e_low.endswith(ext) for ext in _EXCLUDED_EXTS):
            continue
        clean_emails.append(e_low)

    final_emails = list(set(clean_emails))
    if limit > 0:
        final_emails = final_emails[:limit]

    business_data['emails'] = final_emails
    business_data['socials'] = "; ".join(list(socials))
    return business_data


if __name__ == "__main__":
    # Test enrichment
    test_data = {
        "name": "Test Business",
        "website": "https://www.google.com"
    }
    result = asyncio.run(enrich_business(test_data))
    print(result)
