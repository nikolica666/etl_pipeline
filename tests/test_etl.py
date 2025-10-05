import os
import pytest
from etl_pipeline.extractors.pdf_extractor import extract_pdf
from etl_pipeline.extractors.word_extractor import extract_word
from etl_pipeline.extractors.pptx_extractor import extract_pptx
from etl_pipeline.text_utils.cleaning import clean_text
from etl_pipeline.text_utils.chunking import chunk_text
from etl_pipeline.text_utils.embedding_generator import EmbeddingGenerator

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")

# Initialize embedding generator once
embedder = EmbeddingGenerator(device="cpu")  # force CPU for testing

# ---------- PDF ----------
def test_extract_pdf():
    file_path = os.path.join(SAMPLES_DIR, "sample.pdf")
    text = extract_pdf(file_path)
    assert isinstance(text, str)
    assert len(text) > 0
    assert "Hello" in text  # adjust based on your sample

# ---------- DOCX ----------
def test_extract_docx():
    file_path = os.path.join(SAMPLES_DIR, "sample.docx")
    text = extract_word(file_path)
    assert isinstance(text, str)
    assert len(text) > 0
    assert "World" in text  # adjust based on your sample

# ---------- PPTX ----------
def test_extract_pptx():
    file_path = os.path.join(SAMPLES_DIR, "sample.pptx")
    text = extract_pptx(file_path)
    assert isinstance(text, str)
    assert len(text) > 0
    assert "Slide" in text  # adjust based on your sample

# ---------- Cleaning & Chunking ----------
def test_clean_and_chunk():
    raw_text = "Hello  world!\n\nThis is a test."
    cleaned = clean_text(raw_text)
    chunks = chunk_text(cleaned, chunk_size=5, overlap=1)
    assert all(isinstance(c, str) for c in chunks)
    assert len(chunks) > 0

# ---------- Embedding ----------
def test_embedding_generation():
    chunks = ["Hello world", "This is a test"]
    embeddings = embedder.generate(chunks)
    assert embeddings.shape[0] == len(chunks)
    assert embeddings.shape[1] > 0