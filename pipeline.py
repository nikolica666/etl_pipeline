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

# Initialize the embedding generator once at module load time
# (Avoids reloading large models or reinitializing network weights for each document)
embedder = EmbeddingGenerator()


def process_document(local_path):
    """
    Full document processing pipeline:
    1. Extract text from the document (based on file extension)
    2. Clean and normalize the text
    3. Split text into overlapping chunks
    4. Generate vector embeddings for each chunk
    5. Save results (chunks + embeddings) to JSON

    Args:
        local_path (str): Path to the input document to process.
    """

    # --- Step 1: Extract text ---
    # Delegates extraction to the correct handler based on file extension.
    # Raises ValueError for unsupported file types.
    try:
        text = extract_file(local_path)
    except ValueError as e:
        print(f"Unsupported file type for {local_path}: {e}")
        return

    # If the extractor returns nothing, stop early.
    if not text:
        return

    # --- Step 2: Clean text ---
    # Removes excessive whitespace, control chars, or other non-semantic content.
    # TODO: For CSV/TSV files, we may want to preserve table formatting in the future.
    text = clean_text(text)

    # Skip processing if text is empty or whitespace-only after cleaning.
    if not text.strip():
        print(f"No usable text after cleaning in {local_path}, skipping.")
        return

    # --- Step 3: Chunk text ---
    # Splits long text into overlapping windows suitable for embedding.
    # The overlap ensures continuity between chunks for better context retention.
    # TODO: Consider smarter chunking (e.g., sentence or paragraph-based).
    chunks = chunk_text(text, chunk_size=500, overlap=50)

    if not chunks:
        print(f"No chunks generated from {local_path}, skipping.")
        return

    # --- Step 4: Generate embeddings ---
    # Converts each text chunk into a numerical embedding vector.
    # These embeddings can later be stored, searched, or indexed for RAG.
    try:
        embeddings = embedder.generate(chunks)
    except Exception as e:
        print(f"Error generating embeddings for {local_path}: {e}")
        return

    # --- Step 5: Generate document ID ---
    # Creates a sanitized, unique, filesystem-safe identifier for the document.
    # This prevents issues with special characters or duplicate filenames.
    safe_doc_id = make_sanitized_doc_id(local_path)

    # --- Step 6: Save results ---
    # Writes chunks and their embeddings to a structured JSON file.
    # The resulting file can be easily reloaded or used in downstream indexing.
    save_chunks_with_embeddings(chunks, embeddings, safe_doc_id)
