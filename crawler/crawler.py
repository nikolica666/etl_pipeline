import time
import logging
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional, Iterable

import requests
from requests.adapters import HTTPAdapter, Retry

from crawler.sitemap_utils import discover_sitemaps, collect_all_sitemap_urls
from crawler.link_extractor import extract_links_from_html
from extractors.html_extractor import extract_html

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# -----------------------------------------------------------
# 🕸️ Create a resilient requests session
# -----------------------------------------------------------
def make_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": "CrawlerBot/1.0 (+https://example.com)"})
    return session


# -----------------------------------------------------------
# 🌐 Fetch a single page safely
# -----------------------------------------------------------
def fetch_html(url: str, session: Optional[requests.Session] = None, timeout: int = 10) -> Optional[str]:
    session = session or make_session()
    try:
        resp = session.get(url, timeout=timeout)
        resp.raise_for_status()
        if "html" not in resp.headers.get("Content-Type", "").lower():
            return None
        return resp.text
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None


# -----------------------------------------------------------
# 🧩 Crawl one domain
# -----------------------------------------------------------
def crawl_domain(base_url: str, output_dir: str = "data", limit: Optional[int] = None, delay: float = 1.0) -> None:
    """
    Crawl a domain using sitemap discovery, fetch pages, and extract text.

    Args:
        base_url: e.g. "https://www.index.hr"
        output_dir: where to save text files
        limit: optional number of pages to limit crawling
        delay: seconds to wait between requests
    """
    session = make_session()
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    parsed = urlparse(base_url)
    domain = parsed.netloc.replace("www.", "")

    logger.info(f"🌍 Discovering sitemaps for {domain} ...")
    sitemap_urls = discover_sitemaps(base_url)
    if not sitemap_urls:
        logger.warning(f"No sitemaps found for {domain}.")
        return

    logger.info(f"Found {len(sitemap_urls)} sitemap(s). Collecting page URLs...")
    all_urls = set()
    for sitemap_url in sitemap_urls:
        urls = collect_all_sitemap_urls(sitemap_url)
        logger.info(f"  {sitemap_url} → {len(urls)} URLs")
        all_urls |= urls

    if not all_urls:
        logger.warning(f"No page URLs found in sitemaps for {domain}.")
        return

    logger.info(f"Total unique URLs: {len(all_urls)}")

    for i, url in enumerate(sorted(all_urls)):
        if limit and i >= limit:
            break

        html = fetch_html(url, session=session)
        if not html:
            continue

        # Save extracted readable text
        temp_path = Path(output_dir) / f"{domain}_{i:04d}.txt"
        try:
            text = extract_html_from_string(html)
        except Exception:
            # fallback to path-based extraction if saved locally
            temp_html = temp_path.with_suffix(".html")
            temp_html.write_text(html, encoding="utf-8", errors="ignore")
            text = extract_html(str(temp_html))
            temp_html.unlink(missing_ok=True)

        temp_path.write_text(text, encoding="utf-8")
        logger.info(f"[{i+1}/{len(all_urls)}] Saved {temp_path.name}")

        # Optional: extract additional links for exploration
        internal_links = extract_links_from_html(url, html, domain_limit=domain)
        logger.debug(f"Found {len(internal_links)} internal links")

        time.sleep(delay)  # be polite
        

# -----------------------------------------------------------
# Helper: Extract from raw HTML string (for convenience)
# -----------------------------------------------------------
from bs4 import BeautifulSoup
from io import StringIO

def extract_html_from_string(html: str, mode: str = "smart") -> str:
    """
    Like extract_html(), but accepts raw HTML string directly.
    """
    tmp_path = Path("_temp_extract.html")
    tmp_path.write_text(html, encoding="utf-8", errors="ignore")
    text = extract_html(str(tmp_path), mode=mode)
    tmp_path.unlink(missing_ok=True)
    return text
