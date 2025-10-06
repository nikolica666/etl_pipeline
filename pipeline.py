import os
import hashlib
import logging
from dataclasses import dataclass
from typing import Optional
from text_utils.embedding_generator import EmbeddingGenerator
from extractors import extract_file
from text_utils.cleaning import clean_text
from text_utils.chunking import chunk_text
from text_utils.doc_id_generator import make_sanitized_doc_id

logger = logging.getLogger(__name__)

embedder = EmbeddingGenerator()

def get_embedding_dimension() -> int:
    """Expose embedding vector size for DB setup."""
    sample_vector = embedder.generate(["dimension_check"])[0]
    return len(sample_vector)
    
@dataclass
class ProcessResult:
    path: str
    source: str
    status: str
    doc_id: Optional[str] = None
    num_chunks: int = 0
    hash: Optional[str] = None
    error: Optional[str] = None


def process_document(
    local_path: str,
    source: str | None = None,
    skip_if_duplicate: bool = True,
    store=None
) -> ProcessResult:
    """
    Extract, clean, chunk, embed, and upload text from a given document to Qdrant.
    """

    result = ProcessResult(path=local_path, source=source or local_path, status="failed")

    # Step 1: Extract
    try:
        text = extract_file(local_path)
    except Exception as e:
        logger.error(f"Extraction failed for {local_path}: {e}", exc_info=True)
        result.error = str(e)
        return result

    if not text:
        logger.warning(f"No text extracted from {local_path}")
        result.error = "empty_extraction"
        return result

    # Step 2: Clean
    text = clean_text(text)
    if not text.strip():
        result.error = "empty_after_cleaning"
        return result

    # Step 3: Hash for deduplication
    doc_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    result.hash = doc_hash

    # Step 4: Chunk
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    if not chunks:
        result.error = "no_chunks"
        return result

    # Step 5: Embeddings
    try:
        embeddings = embedder.generate(chunks)
    except Exception as e:
        logger.error(f"Embedding failed for {local_path}: {e}", exc_info=True)
        result.error = str(e)
        return result

    # Step 6: Upload directly to vector DB
    doc_id = make_sanitized_doc_id(source or local_path)
    metadata = {
        "source": source or local_path,
        "original_name": os.path.basename(local_path),
        "hash": doc_hash,
        "num_chunks": len(chunks),
        "doc_id": doc_id,
    }

    if store:
        try:
            store.save(chunks, embeddings, metadata)
        except Exception as e:
            logger.error(f"Qdrant upload failed for {local_path}: {e}", exc_info=True)
            result.error = f"upload_failed: {e}"
            return result

    # Step 7: Done
    result.status = "success"
    result.doc_id = doc_id
    result.num_chunks = len(chunks)
    logger.info(f"✅ Processed and uploaded {local_path} → {len(chunks)} chunks, doc_id={doc_id}")
    return result
