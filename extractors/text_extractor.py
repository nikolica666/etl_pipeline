def extract_txt(file_path):
    """
    Extracts all text from a plain .txt file.
    Returns the text as a single string.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text