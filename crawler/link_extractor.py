from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def extract_links_from_html(base_url: str, html: str, domain_limit: str | None = None) -> set[str]:
    """
    Extract and normalize all unique hyperlinks (<a href>) from an HTML page.

    Args:
        base_url (str): The page URL (used to resolve relative links).
        html (str): The HTML content of the page.
        domain_limit (str, optional): If provided, restricts results to URLs
                                      ending with this domain (e.g. "index.hr").

    Returns:
        set[str]: A set of absolute, normalized URLs.
    """
    soup = BeautifulSoup(html, "html.parser")
    urls = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue

        absolute = urljoin(base_url, href)
        parsed = urlparse(absolute)
        normalized = parsed._replace(fragment="").geturl()

        if domain_limit and parsed.netloc and not parsed.netloc.endswith(domain_limit):
            continue

        urls.add(normalized)

    return urls
