from bs4 import BeautifulSoup
from pathlib import Path
from typing import List

def extract_html(file_path: str, mode: str = "naive") -> str:
    """
    Extract readable text from an HTML file.

    Modes:
        - "naive": Basic HTML text extraction (flattened).
        - "smart": Preserves headings, tables, and hyperlinks, but still returns plain text.
    """
    if mode == "smart":
        return _extract_html_smart(file_path)
    return _extract_html_naive(file_path)


# ---------------------------------------------------------------------
# 🧩 Naive mode — quick and flat
# ---------------------------------------------------------------------
def _extract_html_naive(file_path: str) -> str:
    """Extract plain readable text from HTML. Removes scripts/styles and flattens structure."""
    html = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "iframe", "footer", "nav", "header", "form"]):
        tag.decompose()

    text = soup.get_text(" ", strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


# ---------------------------------------------------------------------
# 🧠 Smart mode — semantically aware but still plain text
# ---------------------------------------------------------------------
def _extract_html_smart(file_path: str) -> str:
    """
    Extract semantically structured text from HTML for RAG / LLM use.

    - Keeps headings, paragraphs, lists, tables, and hyperlinks.
    - Returns a single string for compatibility with other extractors.
    """
    html = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    # Remove noise
    for tag in soup(["script", "style", "noscript", "iframe", "footer", "nav", "header", "form", "meta"]):
        tag.decompose()

    lines: List[str] = []

    def extract_links(element):
        for a in element.find_all("a", href=True):
            link_text = a.get_text(" ", strip=True)
            href = a["href"].strip()
            a.replace_with(f"{link_text} (URL: {href})")

    def extract_table(table):
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"])]
            if cells:
                rows.append(" | ".join(cells))
        return "\n".join(rows)

    for element in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "table"]):
        if element.name == "table":
            table_text = extract_table(element)
            if table_text:
                lines.append(table_text)
            continue

        extract_links(element)
        text = element.get_text(" ", strip=True)
        if not text:
            continue

        if element.name.startswith("h"):
            lines.append(f"\n{text.upper()}\n")
        else:
            lines.append(text)

    text = "\n".join(line.strip() for line in lines if line.strip())
    return text.strip()