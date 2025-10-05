from urllib.parse import urlparse
from pathlib import Path

try:
    from ftplib import FTP
except ImportError:
    FTP = None

def fetch_ftp_file(url: str, tmpdir: Path) -> Path:
    """Download a file from an FTP server."""
    if not FTP:
        raise RuntimeError("ftplib not available for FTP support.")
    parsed = urlparse(url)
    host = parsed.hostname
    user = parsed.username or "anonymous"
    passwd = parsed.password or ""
    dest = tmpdir / Path(parsed.path).name
    with FTP(host) as ftp:
        ftp.login(user, passwd)
        with open(dest, "wb") as f:
            ftp.retrbinary(f"RETR " + parsed.path, f.write)
    return dest
