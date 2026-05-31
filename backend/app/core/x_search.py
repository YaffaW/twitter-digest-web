"""X.com web-search scraper using Playwright.

This module is an optional dependency (playwright). It loads the X search page
with a headless browser, scrolls to load results, and extracts tweet URLs.
"""
from typing import List
from urllib.parse import quote_plus
import time

def search_x(query: str, max_results: int = 50, headless: bool = True, timeout: int = 30) -> List[str]:
    """Search X (x.com) web search and return list of tweet URLs.

    Requires the `playwright` package and installed browsers.
    """
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        raise RuntimeError("Playwright is not installed. Install with `pip install playwright` and run `playwright install`") from e

    urls = []
    q = quote_plus(query)
    search_url = f"https://x.com/search?q={q}&src=typed_query"

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

    return urls


def search_user_timeline(username: str, max_results: int = 50, headless: bool = True, timeout: int = 30) -> List[str]:
    """Scrape a user's X timeline and return recent tweet URLs.

    This helps when queries include `from:username` and DDG misses recent tweets.
    """
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        raise RuntimeError("Playwright is not installed. Install with `pip install playwright` and run `playwright install`") from e

    urls = []
    profile_url = f"https://x.com/{quote_plus(username)}"

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

    return urls
