from pathlib import Path
from typing import List
import numpy as np
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_chunks_with_embeddings(chunks, embeddings, doc_id, output_folder="build/output", metadata=None):
    """
    Save text chunks and embeddings as JSON, with optional metadata.
    """
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    data = []

    for idx, (chunk, emb) in enumerate(zip(chunks, embeddings), start=1):
        entry = {
            "doc_id": doc_id,
            "chunk_id": idx,
            "text": chunk,
            "embedding": emb.tolist(),
        }
        if metadata:
            entry.update(metadata)
        data.append(entry)

    output_path = Path(output_folder) / f"{doc_id}_chunks.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    log.info(f"Saved {len(chunks)} chunks with embeddings to {output_path}")
