from qdrant_client import QdrantClient
from vectorstore.config import setup_qdrant
from text_utils.embedding_generator import EmbeddingGenerator
from pipeline import get_embedding_dimension

embedding_size = get_embedding_dimension()
qdrant, collection = setup_qdrant(embedding_size, create_if_missing=False)

embedder = EmbeddingGenerator()

async def search_vectors(query: str, top_k: int = 5):
    vector = embedder.generate_single(query)
    hits = qdrant.search(
        collection_name=collection,
        query_vector=vector,
        limit=top_k
    )
    return [{"id": h.id, "score": h.score, "payload": h.payload} for h in hits]