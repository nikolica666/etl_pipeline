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

def process_document(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        text = extract_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        text = extract_word(file_path)
    elif ext in [".xlsx", ".xls"]:
        text = extract_xlsx(file_path)
    elif ext in [".pptx", ".ppt"]:
        text = extract_pptx(file_path)
    elif ext in [".txt", ".md", ".log"]:
        text = extract_txt(file_path)
    elif ext == ".csv":
        text = extract_table(file_path)
    elif ext == ".tsv":
        text = extract_table(file_path, '\t')
    else:
        print(f"Unsupported file type: {ext}")
        return

    # TODO smarter chunking (keep sentences and/or paragraphs)
    # TODO preserve CSV/TSV table (better for LLM with preserved row structure)
    text = clean_text(text)
    chunks = chunk_text(text, chunk_size=500, overlap=50)

    embeddings = embedder.generate(chunks)

    doc_id = os.path.splitext(os.path.basename(file_path))[0]
    save_chunks_with_embeddings(chunks, embeddings, doc_id, "build/output")

if __name__ == "__main__":
    sample_folder = "/home/nikola/rag_temp/txt"
    count = 0
    for file in os.listdir(sample_folder):
        file_path = os.path.join(sample_folder, file)
        process_document(file_path)
        count = count + 1
    print(f"Processed {count} docs")
