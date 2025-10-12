from qdrant_client import QdrantClient
import os, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_qdrant(embedding_size: int, create_if_missing: bool = True):

    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
    collection = os.getenv("QDRANT_COLLECTION", "documents")
    distance = os.getenv("QDRANT_DISTANCE", "Cosine")

    qdrant = QdrantClient(host=qdrant_host, port=qdrant_port)

    existing = [c.name for c in qdrant.get_collections().collections]
    
    if collection not in existing:
        if create_if_missing:
            qdrant.recreate_collection(
                collection_name=collection,
                vectors_config={"size": embedding_size, "distance": distance},
            )
            logger.info(f"✅ Created collection '{collection}'")
        else:
            raise RuntimeError(f"Collection '{collection}' not found — did you run ingestion?")
    else:
        logger.info(f"ℹ️ Collection '{collection}' already exists")

    return qdrant, collection
 