import logging
from uuid import uuid5, NAMESPACE_URL
from qdrant_client.models import PointStruct

logger = logging.getLogger(__name__)

class VectorDBStore:
    """Handles saving chunks and embeddings into a Qdrant collection."""

    def __init__(self, client, collection_name: str):
        self.client = client
        self.collection = collection_name

    def save(self, chunks, embeddings, metadata: dict):
        points = [
            PointStruct(
                id=str(uuid5(NAMESPACE_URL, f"{metadata['doc_id']}_{i}")), # must be UUID or unsigned int
                vector=emb,
                payload={"text": chunk, **metadata},
            )
            for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
        ]

        try:
            self.client.upsert(collection_name=self.collection, points=points)
            logger.info(f"✅ Uploaded {len(points)} vectors to Qdrant collection '{self.collection}'")
        except Exception as e:
            logger.error(f"❌ Failed to upload vectors to Qdrant: {e}", exc_info=True)
            raise
