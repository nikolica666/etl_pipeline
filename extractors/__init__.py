from pathlib import Path

from .pdf_extractor import extract_pdf
from .word_extractor import extract_word
from .xlsx_extractor import extract_xlsx
from .pptx_extractor import extract_pptx
from .text_extractor import extract_txt
from .csv_extractor import extract_table
from .html_extractor import extract_html


EXTRACTORS = {
    # Office & PDF
    ".pdf": extract_pdf,
    ".docx": extract_word,
    ".doc": extract_word,
    ".xlsx": extract_xlsx,
    ".xls": extract_xlsx,
    ".pptx": extract_pptx,
    ".ppt": extract_pptx,

    # Text-like
    ".txt": extract_txt,
    ".md": extract_txt,
    ".log": extract_txt,

    # Tabular
    ".csv": extract_table,
    ".tsv": lambda path: extract_table(path, delimiter="\t"),

    # HTML
    ".html": extract_html,
    ".htm": extract_html,
}


def extract_file(file_path: str) -> str:
    """
    Unified extractor — detects file extension and delegates
    to the appropriate extractor function.

    Args:
        file_path (str): Local file path.

    Returns:
        str: Extracted plain text suitable for further processing.

    Raises:
        ValueError: If no extractor is available for this file type.
    """
    ext = Path(file_path).suffix.lower()
    extractor = EXTRACTORS.get(ext)

    if not extractor:
        raise ValueError(f"Unsupported file extension: {ext}")

    # Call the matched extractor
    if ext == ".tsv":
        return extractor(file_path)  # lambda handles delimiter
    return extractor(file_path)
