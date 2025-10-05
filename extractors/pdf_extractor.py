import fitz  # PyMuPDF

def extract_pdf(file_path):
    text = ""
    doc = fitz.open(file_path)
    for page_num, page in enumerate(doc, start=1):
        page_text = page.get_text()
        text += f"\n[PAGE {page_num}]\n" + page_text
    return text