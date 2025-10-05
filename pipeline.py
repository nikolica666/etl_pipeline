from text_utils.embedding_generator import EmbeddingGenerator
from extractors import extract_file
from text_utils.cleaning import clean_text
from text_utils.chunking import chunk_text
from text_utils.doc_id_generator import make_sanitized_doc_id
from loaders.local_loader import save_chunks_with_embeddings
import os
import hashlib
import unicodedata
import re

# Initialize the embedding generator once per runtime (saves model load time)
embedder = EmbeddingGenerator()


def process_document(local_path, source=None):
    """
    Extract, clean, chunk, embed, and save text from a given local document file.

    Optionally, preserve the original source (URL or file path) for traceability.

    Args:
        local_path (str): Path to the local file to process.
        source (str, optional): Original source identifier, such as a URL or
            remote path. If not provided, the local_path will be used.
    """
    # --- Step 1: Extract text ---
    try:
        text = extract_file(local_path)
    except ValueError as e:
        print(f"Unsupported file type for {local_path}: {e}")
        return
    if not text:
        print(f"No text extracted from {local_path}.")
        return

    # --- Step 2: Clean text ---
    text = clean_text(text)
    if not text.strip():
        print(f"No usable text after cleaning in {local_path}, skipping.")
        return

    # --- Step 3: Chunk text ---
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    if not chunks:
        print(f"No chunks generated from {local_path}, skipping.")
        return

    # --- Step 4: Generate embeddings ---
    try:
        embeddings = embedder.generate(chunks)
    except Exception as e:
        print(f"Error generating embeddings for {local_path}: {e}")
        return

    # --- Step 5: Document metadata ---
    # Prefer source for ID generation (so URL-based docs stay unique)
    safe_doc_id = make_sanitized_doc_id(source or local_path)

    # --- Step 6: Save results ---
    # Save with additional metadata about the document's origin.
    # We can extend `save_chunks_with_embeddings()` to handle metadata dicts.
    metadata = {
        "source": source or local_path,
        "original_name": os.path.basename(local_path),
    }

    save_chunks_with_embeddings(chunks, embeddings, safe_doc_id, metadata=metadata)
