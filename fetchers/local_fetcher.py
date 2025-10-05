from pathlib import Path
import os

def fetch_local_file(path: str) -> Path:
    """Return the absolute Path to a local file."""
    abs_path = Path(os.path.abspath(path))
    if not abs_path.exists():
        raise FileNotFoundError(f"Local file not found: {abs_path}")
    return abs_path
