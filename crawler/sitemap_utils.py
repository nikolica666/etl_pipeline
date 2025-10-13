from pathlib import Path
from typing import List, Set, Dict
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree as ET
import logging, gzip, requests

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def extract_urls_from_sitemap(source: str, timeout: int = 15) -> Dict[str, Set[str]]:
    """
    Extract URLs from a sitemap.xml or sitemap index.
    Supports both local files and remote URLs (.xml or .gz).

    Returns:
        dict:
            - "urls": Actual page URLs (<urlset>)
            - "sitemaps": Nested sitemap files (<sitemapindex>)
    """
    xml_content = None
    is_url = bool(urlparse(source).scheme in ("http", "https"))

    try:
        # --- Remote sitemap ---
        if is_url:
            resp = requests.get(source, timeout=timeout, headers={"User-Agent": "SitemapExtractor/1.0"})
            resp.raise_for_status()
            content = resp.content

            # Detect gzip
            is_gzipped = (
                resp.headers.get("Content-Encoding") == "gzip"
                or content[:2] == b"\x1f\x8b"
                or source.endswith(".gz")
            )

            if is_gzipped:
                try:
                    xml_content = gzip.decompress(content).decode("utf-8", errors="ignore")
                except Exception:
                    # fallback in case gzip header is wrong
                    xml_content = content.decode("utf-8", errors="ignore")
            else:
                xml_content = content.decode("utf-8", errors="ignore")

        # --- Local sitemap ---
        else:
            path = Path(source)
            if path.suffix == ".gz":
                with gzip.open(path, "rt", encoding="utf-8", errors="ignore") as f:
                    xml_content = f.read()
            else:
                xml_content = path.read_text(encoding="utf-8", errors="ignore")

    except Exception as e:
        logger.error(f"⚠️ Failed to load sitemap from {source}: {e}")
        return {"urls": set(), "sitemaps": set()}

    # --- Parse XML ---
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        logger.error(f"⚠️ Invalid XML in {source}: {e}")
        return {"urls": set(), "sitemaps": set()}

    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls, sitemaps = set(), set()

    for loc in root.findall(".//sm:url/sm:loc", ns):
        if loc.text:
            urls.add(loc.text.strip())

    for loc in root.findall(".//sm:sitemap/sm:loc", ns):
        if loc.text:
            sitemaps.add(loc.text.strip())

    return {"urls": urls, "sitemaps": sitemaps}


def collect_all_sitemap_urls(root_url: str, visited=None) -> set[str]:
    """
    Recursively collects all page URLs from a given sitemap (URL or file path).

    - Parses the sitemap via extract_urls_from_sitemap()
    - Recursively follows <sitemapindex> entries
    - Avoids revisiting already processed sitemaps
    """
    if visited is None:
        visited = set()
    if root_url in visited:
        return set()

    visited.add(root_url)
    logger.debug(f"added {root_url} to visited")

    data = extract_urls_from_sitemap(root_url)
    all_urls = set(data["urls"])

    for sm_url in data["sitemaps"]:
        all_urls |= collect_all_sitemap_urls(sm_url, visited)

    return all_urls


def discover_sitemaps(base_url: str, timeout: int = 10) -> List[str]:
    """
    Attempt to discover sitemap URLs for a given website.
    
    Checks:
      1. robots.txt for 'Sitemap:' entries
      2. Common default sitemap file paths
    """
    discovered = set()
    parsed = urlparse(base_url)
    root = f"{parsed.scheme}://{parsed.netloc}"

    # 1️⃣ Look for robots.txt entries
    robots_url = urljoin(root, "/robots.txt")
    try:
        resp = requests.get(robots_url, timeout=timeout, headers={"User-Agent": "SitemapDiscoverer/1.0"})
        if resp.status_code == 200:
            for line in resp.text.splitlines():
                if line.strip().lower().startswith("sitemap:"):
                    sitemap_url = line.split(":", 1)[1].strip()
                    if not sitemap_url.startswith("http"):
                        sitemap_url = urljoin(root, sitemap_url)
                    discovered.add(sitemap_url)
    except Exception:
        pass

    # 2️⃣ Try common sitemap URL patterns
    common_paths = [
        "/sitemap.xml",
        "/sitemap_index.xml",
        "/sitemap-index.xml",
        "/sitemap/sitemap.xml",
        "/sitemaps/sitemap-index.xml"
    ]

    for path in common_paths:
        candidate = urljoin(root, path)
        try:
            resp = requests.head(candidate, timeout=timeout, allow_redirects=True)
            if resp.status_code == 200 and "xml" in resp.headers.get("Content-Type", "").lower():
                discovered.add(candidate)
        except Exception:
            continue

    return sorted(discovered)
