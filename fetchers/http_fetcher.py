import re
import mimetypes
import requests
from pathlib import Path
from urllib.parse import urlparse

def fetch_http_file(url: str, tmpdir: Path) -> Path:
    """
    Download a file via HTTP/HTTPS into tmpdir.
    Uses Content-Disposition and Content-Type to determine extension.
    """
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    # Try filename from Content-Disposition header
    cd = response.headers.get("Content-Disposition", "")
    filename_match = re.search(r'filename="([^"]+)"', cd)
    if filename_match:
        filename = filename_match.group(1)
    else:
        parsed = urlparse(url)
        filename = Path(parsed.path).name or "downloaded_file"

    # If filename has no extension, infer from MIME type
    if not Path(filename).suffix:
        mime = response.headers.get("Content-Type")
        ext = mimetypes.guess_extension(mime.split(";")[0].strip()) if mime else None
        if ext:
            filename += ext

    dest = tmpdir / filename
    dest.write_bytes(response.content)
    return dest
