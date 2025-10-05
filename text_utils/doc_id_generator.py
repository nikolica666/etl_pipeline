import re
import os
import hashlib
import unicodedata

def sanitize_doc_id(doc_id: str) -> str:
    """
    Make a doc_id safe for use in filenames or URLs.

    - Removes or replaces characters unsafe for filesystems (:, /, \\, etc.)
    - Converts spaces to underscores
    - Normalizes Unicode (e.g., accents → plain letters)
    - Ensures only ASCII letters, digits, dashes, and underscores remain

    Args:
        doc_id (str): Original document ID.

    Returns:
        str: Sanitized, filesystem-safe document ID.
    """
    # Normalize Unicode (e.g., 'é' → 'e')
    doc_id = unicodedata.normalize("NFKD", doc_id).encode("ascii", "ignore").decode("ascii")

    # Replace spaces with underscores
    doc_id = doc_id.replace(" ", "_")

    # Replace all invalid characters with '_'
    doc_id = re.sub(r"[^A-Za-z0-9._-]", "_", doc_id)

    # Collapse multiple underscores/dots/dashes
    doc_id = re.sub(r"[_\-.]{2,}", "_", doc_id)

    return doc_id.strip("._-")

def make_doc_id(file_path: str) -> str:
    """
    Generate a semi-human-readable, unique doc_id that preserves the extension.
    """
    base = os.path.basename(file_path)
    ext = os.path.splitext(base)[1]
    name = os.path.splitext(base)[0]
    hash_part = hashlib.sha1(file_path.encode("utf-8")).hexdigest()[:8]
    return f"{name}_{hash_part}{ext}"

def make_sanitized_doc_id(file_path: str) -> str:
    return sanitize_doc_id(make_doc_id(file_path))