import threading
import logging
from sentence_transformers import SentenceTransformer

# Configure default logging (you can override this in your main script)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """
    Thread-safe embedding generator for document chunks.
    Uses a shared SentenceTransformer model safely across threads (CPU only).
    """

    _model_instance = None
    _model_lock = threading.Lock()   # ensures single model load
    _encode_lock = threading.Lock()  # ensures thread-safe encode() calls

    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2", device="cpu"):
        """
        Initialize a thread-safe embedding generator.
        Loads the model only once (singleton style).
        """
        with EmbeddingGenerator._model_lock:
            if EmbeddingGenerator._model_instance is None:
                logger.info(f"Loading embedding model '{model_name}' on {device}")
                EmbeddingGenerator._model_instance = SentenceTransformer(model_name, device=device)
            else:
                logger.info("Reusing already loaded SentenceTransformer model")

        self.model = EmbeddingGenerator._model_instance

    def generate(self, chunks, batch_size=32):
        """
        Generate embeddings for a list of text chunks in a thread-safe way.
        """
        if not chunks:
            logger.warning("No chunks provided for embedding generation.")
            return []

        if isinstance(chunks, str):
            chunks = [chunks]

        logger.debug(f"Generating embeddings for {len(chunks)} chunks (batch_size={batch_size})")

        try:
            with EmbeddingGenerator._encode_lock:
                embeddings = self.model.encode(
                    chunks,
                    batch_size=batch_size,
                    convert_to_numpy=True,
                    show_progress_bar=(len(chunks) > 1)
                )
            logger.info(f"Generated embeddings for {len(chunks)} chunks.")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}", exc_info=True)
            raise

    def generate_single(self, text: str):
        return self.generate([text])[0]
