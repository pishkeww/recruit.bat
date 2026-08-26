try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class Embedder:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is required for semantic similarity"
            )
        self.model = SentenceTransformer(model_name)

    def encode(self, text: str):
        return self.model.encode(text, normalize_embeddings=True)

    def similarity(self, text1: str, text2: str) -> float:
        v1 = self.encode(text1)
        v2 = self.encode(text2)
        return float(np.dot(v1, v2))


def create_embedder(model_name="all-MiniLM-L6-v2"):
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        return None
    try:
        return Embedder(model_name)
    except Exception:
        return None
