from sentence_transformers import SentenceTransformer

class EmbeddingGenerator:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        print(f"Initiating {model_name}")
        self.model = SentenceTransformer(model_name, device="cpu")

    def generate(self, chunks):
        return self.model.encode(chunks, convert_to_numpy=True, show_progress_bar=True)
