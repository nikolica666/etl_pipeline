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

# Initialize embedding generator once
embedder = EmbeddingGenerator()

def process_document(file_path):
    """
    Extract, clean, chunk, embed, and save text from a given document file.

    Args:
        file_path (str): Path to the input document.
    """
    try:
        text = extract_file(file_path)
    except ValueError as e:
        print(f"Unsupported file type for {file_path}: {e}")
        return
    if not text:
        return

    # TODO preserve CSV/TSV table (better for LLM with preserved row structure)
    text = clean_text(text)
    if not text.strip():
        print(f"No usable text after cleaning in {file_path}, skipping.")
        return

    # TODO smarter chunking (keep sentences and/or paragraphs)
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    if not chunks:
        print(f"No chunks generated from {file_path}, skipping.")
        return

    try:
        embeddings = embedder.generate(chunks)
    except Exception as e:
        print(f"Error generating embeddings for {file_path}: {e}")
        return

    safe_doc_id = make_sanitized_doc_id(file_path)

    save_chunks_with_embeddings(chunks, embeddings, safe_doc_id)
