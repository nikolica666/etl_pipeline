from pathlib import Path
from typing import List
import numpy as np
import json

def save_chunks_with_embeddings(
    chunks: List[str],
    embeddings: List[np.ndarray],
    doc_id: str,
    output_folder: str = "build/output"
) -> None:
    """
    Save text chunks and their corresponding embeddings to a JSON file.

    Each chunk and embedding pair is stored as a dictionary containing:
      - doc_id: Identifier for the document the chunks belong to.
      - chunk_id: Sequential number (starting from 1) of the chunk.
      - text: The chunk's text content.
      - embedding: The embedding vector converted to a list.

    The resulting JSON file is saved in the specified output folder with
    the name pattern: `<doc_id>_chunks.json`.

    Args:
        chunks (list[str]): List of text chunks to save.
        embeddings (list[numpy.ndarray]): List of embeddings corresponding
            to each chunk. Each embedding must be a NumPy array.
        doc_id (str): Unique identifier for the document.
        output_folder (str, optional): Directory path where the output JSON
            will be saved. Defaults to `"build/output"`.

    Returns:
        None

    Side Effects:
        Creates the output directory if it doesn't exist.
        Writes a JSON file containing the chunk and embedding data.
        Prints a message indicating the number of chunks saved and the output path.
    """

    Path(output_folder).mkdir(parents=True, exist_ok=True)

    data = []
    for idx, (chunk, emb) in enumerate(zip(chunks, embeddings), start=1):
        data.append({
            "doc_id": doc_id,
            "chunk_id": idx,
            "text": chunk,
            "embedding": emb.tolist()  # numpy array → list
        })
    
    output_path = Path(output_folder) / f"{doc_id}_chunks.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(chunks)} chunks with embeddings to {output_path}")
