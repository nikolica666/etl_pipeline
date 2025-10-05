from extractors.pdf_extractor import extract_pdf
from extractors.word_extractor import extract_word
from extractors.xlsx_extractor import extract_xlsx
from extractors.pptx_extractor import extract_pptx
from extractors.text_extractor import extract_txt
from extractors.csv_extractor import extract_table
from text_utils.cleaning import clean_text
from text_utils.chunking import chunk_text
from text_utils.embedding_generator import EmbeddingGenerator
from loaders.local_loader import save_chunks_with_embeddings
import os

# Initialize embedding generator once
embedder = EmbeddingGenerator()

def extract_text_from_file(file_path: str) -> str | None:
    """
    Extract text from a file based on its extension.

    Args:
        file_path (str): Path to the input file.

    Returns:
        str | None: Extracted text content, or None if unsupported type.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return extract_word(file_path)
    elif ext in [".xlsx", ".xls"]:
        return extract_xlsx(file_path)
    elif ext in [".pptx", ".ppt"]:
        return extract_pptx(file_path)
    elif ext in [".txt", ".md", ".log"]:
        return extract_txt(file_path)
    elif ext == ".csv":
        return extract_table(file_path)
    elif ext == ".tsv":
        return extract_table(file_path, '\t')
    else:
        print(f"Unsupported file type: {ext}")
        return None

def process_document(file_path):
    
    text = extract_text_from_file(file_path)
    if not text:
        return

    # TODO smarter chunking (keep sentences and/or paragraphs)
    # TODO preserve CSV/TSV table (better for LLM with preserved row structure)
    text = clean_text(text)
    chunks = chunk_text(text, chunk_size=500, overlap=50)

    embeddings = embedder.generate(chunks)

    doc_id = os.path.splitext(os.path.basename(file_path))[0]
    save_chunks_with_embeddings(chunks, embeddings, doc_id,)

if __name__ == "__main__":
    sample_folder = "/home/nikola/rag_temp/txt"
    count = 0
    for file in os.listdir(sample_folder):
        file_path = os.path.join(sample_folder, file)
        process_document(file_path)
        count = count + 1
    print(f"Processed {count} docs")
