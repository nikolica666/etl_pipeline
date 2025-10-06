import os
import hashlib
import logging
from text_utils.embedding_generator import EmbeddingGenerator
from extractors import extract_file
from text_utils.cleaning import clean_text
from text_utils.chunking import chunk_text
from text_utils.doc_id_generator import make_sanitized_doc_id
from loaders.local_loader import save_chunks_with_embeddings

# --- Logging setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Global embedder instance (thread-safe, CPU-only) ---
embedder = EmbeddingGenerator()

# --- Deduplication marker directory (configurable for production) ---
DEFAULT_HASH_DIR = "build/processed_hashes"
env_hash_dir = os.getenv("HASH_DIR")

if env_hash_dir:
    HASH_DIR = env_hash_dir
    logger.info(
        f"Using HASH_DIR from environment: '{HASH_DIR}'. "
        f"This directory stores deduplication markers to skip already processed documents."
    )
else:
    HASH_DIR = DEFAULT_HASH_DIR
    logger.warning(
        f"HASH_DIR environment variable not set. "
        f"Using default path: '{HASH_DIR}'. "
        f"This folder stores deduplication markers to avoid reprocessing identical documents. "
        f"For production, set HASH_DIR explicitly via environment variable."
    )

# Ensure the directory exists
try:
    os.makedirs(HASH_DIR, exist_ok=True)
except Exception as e:
    logger.error(f"Failed to create HASH_DIR '{HASH_DIR}': {e}")


def process_document(local_path, source=None, skip_if_duplicate=True):
    """
    Extract, clean, chunk, embed, and save text from a given local document file.
    Optionally, preserve the original source (URL or file path) for traceability.
    
    Args:
        local_path (str): Path to the local file to process.
        source (str, optional): Original source identifier, such as a URL or remote path.
        skip_if_duplicate (bool): Skip reprocessing identical documents by comparing hashes.
    
    Returns:
        dict: Summary info with document ID, number of chunks, hash, and status.
    """
    result = {
        "path": local_path,
        "source": source or local_path,
        "status": "failed",
        "doc_id": None,
        "num_chunks": 0,
        "hash": None,
        "error": None,
    }

    # --- Step 1: Extract text ---
    try:
        text = extract_file(local_path)
    except ValueError as e:
        logger.warning(f"Unsupported file type for {local_path}: {e}")
        result["error"] = str(e)
        return result
    except Exception as e:
        logger.error(f"Error extracting {local_path}: {e}", exc_info=True)
        result["error"] = str(e)
        return result

    if not text:
        logger.warning(f"No text extracted from {local_path}.")
        result["error"] = "empty_extraction"
        return result

    # --- Step 2: Clean text ---
    text = clean_text(text)
    if not text.strip():
        logger.warning(f"No usable text after cleaning in {local_path}, skipping.")
        result["error"] = "empty_after_cleaning"
        return result

    # --- Step 3: Optional deduplication ---
    doc_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    result["hash"] = doc_hash
    hash_marker = os.path.join(HASH_DIR, f"{doc_hash}.done")

    if skip_if_duplicate and os.path.exists(hash_marker):
        logger.info(f"Skipping duplicate document: {local_path}")
        result["status"] = "skipped_duplicate"
        return result

    # --- Step 4: Chunk text ---
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    if not chunks:
        logger.warning(f"No chunks generated from {local_path}, skipping.")
        result["error"] = "no_chunks"
        return result

    # --- Step 5: Generate embeddings ---
    try:
        embeddings = embedder.generate(chunks)
    except Exception as e:
        logger.error(f"Error generating embeddings for {local_path}: {e}", exc_info=True)
        result["error"] = str(e)
        return result

    # --- Step 6: Document metadata ---
    safe_doc_id = make_sanitized_doc_id(source or local_path)
    result["doc_id"] = safe_doc_id

    metadata = {
        "source": source or local_path,
        "original_name": os.path.basename(local_path),
        "hash": doc_hash,
        "num_chunks": len(chunks),
    }

    # --- Step 7: Save results ---
    try:
        save_chunks_with_embeddings(chunks, embeddings, safe_doc_id, metadata=metadata)
        result["num_chunks"] = len(chunks)
        result["status"] = "success"

        if skip_if_duplicate:
            open(hash_marker, "w").close()

        logger.info(f"✅ Processed {local_path} → {len(chunks)} chunks, doc_id={safe_doc_id}")

    except Exception as e:
        logger.error(f"Error saving data for {local_path}: {e}", exc_info=True)
        result["error"] = str(e)

    return result
