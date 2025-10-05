def chunk_text(text, chunk_size=500, overlap=50):
    """
    Splits text into chunks of roughly chunk_size tokens (words here), with optional overlap.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks