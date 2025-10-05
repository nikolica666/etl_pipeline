import csv
from charset_normalizer import from_path

def detect_encoding(file_path):
    """
    Detects the encoding of a file using charset-normalizer.
    Returns the encoding name or 'utf-8' as a safe fallback.
    """
    result = from_path(file_path).best()
    return result.encoding if result else 'utf-8'

def extract_table(file_path, delimiter=','):
    """
    Extracts text from CSV/TSV files.
    - Detects encoding
    - Joins cells with space, rows with newline
    - 'delimiter' can be ',' (CSV) or '\\t' (TSV)
    """
    encoding = detect_encoding(file_path)
    text_lines = []

    with open(file_path, newline='', encoding=encoding) as f:
        reader = csv.reader(f, delimiter=delimiter)
        for row in reader:
            text_lines.append(" ".join(row))

    return "\n".join(text_lines)
