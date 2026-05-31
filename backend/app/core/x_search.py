"""X.com web-search scraper using Playwright.

This module is an optional dependency (playwright). It loads the X search page
with a headless browser, scrolls to load results, and extracts tweet URLs.
"""
from typing import List
from urllib.parse import quote_plus
import time
import threading
from datetime import datetime
import json

# Simple in-memory cache for fallback
_CACHE_LOCK = threading.Lock()
_CACHE: dict = {}  # key -> (timestamp, result_list)
CACHE_TTL = 300  # seconds

# Simple rate limiter: ensure at least MIN_INTERVAL seconds between Playwright navigations
_RATE_LOCK = threading.Lock()
_LAST_CALL = datetime.fromtimestamp(0)
MIN_INTERVAL = 0.5  # seconds

# Optional Redis client (if available and reachable)
_REDIS = None
try:
    import redis
    try:
        _REDIS = redis.Redis(host='127.0.0.1', port=6379, db=0, socket_connect_timeout=1)
        _REDIS.ping()
    except Exception:
        _REDIS = None
except Exception:
    _REDIS = None

def search_x(query: str, max_results: int = 50, headless: bool = True, timeout: int = 30) -> List[str]:
    """Search X (x.com) web search and return list of tweet URLs.

    Requires the `playwright` package and installed browsers.
    """
    key = f"search_x:{query}:{max_results}"
    now = time.time()
    # Try Redis first
    if _REDIS:
        try:
            raw = _REDIS.get(key)
            if raw:
                data = json.loads(raw)
                return list(data)
        except Exception:
            # fallback to in-memory
            pass
    with _CACHE_LOCK:
        entry = _CACHE.get(key)
        if entry and now - entry[0] < CACHE_TTL:
            return list(entry[1])

    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        raise RuntimeError("Playwright is not installed. Install with `pip install playwright` and run `playwright install`") from e

    urls = []
    q = quote_plus(query)
    search_url = f"https://x.com/search?q={q}&src=typed_query"

    # Rate limit Playwright navigations
    with _RATE_LOCK:
        global _LAST_CALL
        elapsed = (datetime.now() - _LAST_CALL).total_seconds()
        if elapsed < MIN_INTERVAL:
            time.sleep(MIN_INTERVAL - elapsed)
        _LAST_CALL = datetime.now()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto(search_url, timeout=timeout * 1000)

        # Collect links by scrolling until we have enough or timeout
        start = time.time()
        seen = set()
        while len(urls) < max_results and (time.time() - start) < timeout:
            # Find anchors with /status/
            anchors = page.query_selector_all('a')
            for a in anchors:
                try:
                    href = a.get_attribute('href') or ''
                except Exception:
                    href = ''
                if href and '/status/' in href:
                    if href.startswith('/'):
                        href = 'https://x.com' + href
                    if href not in seen:
                        seen.add(href)
                        urls.append(href)
                        if len(urls) >= max_results:
                            break
            if len(urls) >= max_results:
                break
            # scroll to bottom to load more
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(1)

        try:
            browser.close()
        except Exception:
            pass

    # store in cache (Redis preferred)
    try:
        if _REDIS:
            _REDIS.setex(key, CACHE_TTL, json.dumps(list(urls)))
            return urls
    except Exception:
        pass
    with _CACHE_LOCK:
        _CACHE[key] = (time.time(), list(urls))
    return urls


def get_cached_search(query: str, max_results: int = 50):
    key = f"search_x:{query}:{max_results}"
    now = time.time()
    with _CACHE_LOCK:
        entry = _CACHE.get(key)
        if entry and now - entry[0] < CACHE_TTL:
            return list(entry[1])
    return None


def search_user_timeline(username: str, max_results: int = 50, headless: bool = True, timeout: int = 30) -> List[str]:
    """Scrape a user's X timeline and return recent tweet URLs.

    This helps when queries include `from:username` and DDG misses recent tweets.
    """
    key = f"timeline:{username}:{max_results}"
    now = time.time()
    if _REDIS:
        try:
            raw = _REDIS.get(key)
            if raw:
                data = json.loads(raw)
                return list(data)
        except Exception:
            pass
    with _CACHE_LOCK:
        entry = _CACHE.get(key)
        if entry and now - entry[0] < CACHE_TTL:
            return list(entry[1])

    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        raise RuntimeError("Playwright is not installed. Install with `pip install playwright` and run `playwright install`") from e

    urls = []
    profile_url = f"https://x.com/{quote_plus(username)}"

    with _RATE_LOCK:
        global _LAST_CALL
        elapsed = (datetime.now() - _LAST_CALL).total_seconds()
        if elapsed < MIN_INTERVAL:
            time.sleep(MIN_INTERVAL - elapsed)
        _LAST_CALL = datetime.now()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto(profile_url, timeout=timeout * 1000)

        start = time.time()
        seen = set()
        while len(urls) < max_results and (time.time() - start) < timeout:
            anchors = page.query_selector_all('a')
            for a in anchors:
                try:
                    href = a.get_attribute('href') or ''
                except Exception:
                    href = ''
                if href and '/status/' in href and f'/{username}/status/' in href:
                    if href.startswith('/'):
                        href = 'https://x.com' + href
                    if href not in seen:
                        seen.add(href)
                        urls.append(href)
                        if len(urls) >= max_results:
                            break
            if len(urls) >= max_results:
                break
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(1)

        try:
            browser.close()
        except Exception:
            pass

    try:
        if _REDIS:
            _REDIS.setex(key, CACHE_TTL, json.dumps(list(urls)))
            return urls
    except Exception:
        pass
    with _CACHE_LOCK:
        _CACHE[key] = (time.time(), list(urls))
    return urls


def get_cached_timeline(username: str, max_results: int = 50):
    key = f"timeline:{username}:{max_results}"
    now = time.time()
    with _CACHE_LOCK:
        entry = _CACHE.get(key)
        if entry and now - entry[0] < CACHE_TTL:
            return list(entry[1])
    return None
