import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
]

def get_random_ua():
    return random.choice(USER_AGENTS)

def parse_proxies(proxy_string):
    """
    Parses a comma-separated string of proxies.
    Supports formats:
    - http://user:pass@host:port
    - host:port
    - host:port:user:pass
    - user:pass:host:port
    """
    if not proxy_string:
        return []
    
    # Handle both comma and newline separators
    proxy_string = proxy_string.replace("\n", ",").replace("\r", ",")
    raw_proxies = [p.strip() for p in proxy_string.split(",") if p.strip()]
    parsed = []
    
    for p in raw_proxies:
        if "://" in p:
            parsed.append(p)
            continue
            
        # Handle colon-separated formats only if no protocol is present
        parts = p.split(":")
        if len(parts) == 4:
            # user:pass:host:port
            if parts[3].isdigit():
                p = f"http://{parts[0]}:{parts[1]}@{parts[2]}:{parts[3]}"
            # host:port:user:pass
            elif parts[1].isdigit():
                p = f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
            else:
                p = "http://" + p
        else:
            p = "http://" + p
            
        parsed.append(p)
    return parsed

class ProxyManager:
    def __init__(self, proxies):
        self.proxies = [p for p in proxies if self._is_valid(p)]
        self.index = 0

    def _is_valid(self, proxy_url):
        """Basic validation for proxy URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(proxy_url)
            return all([parsed.scheme, parsed.hostname])
        except:
            return False

    def get_next(self):
        if not self.proxies:
            return None
        proxy = self.proxies[self.index]
        self.index = (self.index + 1) % len(self.proxies)
        return proxy

    def get_playwright_proxy(self):
        """Returns proxy in format suitable for Playwright browser context."""
        proxy_url = self.get_next()
        if not proxy_url:
            return None
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(proxy_url)
            # Playwright expects 'server' as 'host:port' or 'scheme://host:port'
            port = parsed.port if parsed.port else (80 if parsed.scheme == 'http' else 443)
            pw_proxy = {"server": f"{parsed.scheme}://{parsed.hostname}:{port}"}
            
            if parsed.username:
                pw_proxy["username"] = parsed.username
            if parsed.password:
                pw_proxy["password"] = parsed.password
            return pw_proxy
        except Exception as e:
            print(f"Error parsing proxy for Playwright: {e}")
            return None
