import tempfile
import shutil
from pathlib import Path
from urllib.parse import urlparse

from .local_fetcher import fetch_local_file
from .http_fetcher import fetch_http_file
from .ftp_fetcher import fetch_ftp_file

FETCHERS = {
    "": fetch_local_file,
    "file": fetch_local_file,
    "http": fetch_http_file,
    "https": fetch_http_file,
    "ftp": fetch_ftp_file
}


def fetch_file(source: str, keep: bool = False):
    """
    Unified fetcher — detects the protocol and downloads or copies the file.

    Args:
        source (str): Local or remote path/URL.
        keep (bool): If True, downloaded temp files are kept for inspection.

    Returns:
        tuple[Path, Callable]: (local_path, cleanup_callback)
            - local_path: Path to the fetched local file
            - cleanup_callback(): safely deletes temp files when called
    """
    parsed = urlparse(source)
    scheme = parsed.scheme.lower()

    # --- Local file: no tempdir involved ---
    if scheme in ("", "file"):
        path = fetch_local_file(source)
        return path, (lambda: None)  # no cleanup needed

    # --- Remote file: create controlled tempdir ---
    tmpdir = Path(tempfile.mkdtemp(prefix="rag_fetch_"))
    try:
        if scheme not in FETCHERS:
            raise ValueError(f"Unsupported protocol: {scheme}")

        fetcher = FETCHERS[scheme]
        local_path = fetcher(source, tmpdir)

        def cleanup():
            if not keep and tmpdir.exists():
                shutil.rmtree(tmpdir, ignore_errors=True)

        return local_path, cleanup

    except Exception:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise