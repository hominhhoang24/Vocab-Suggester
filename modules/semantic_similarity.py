from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

_model = SentenceTransformer("all-MiniLM-L6-v2")

def sentence_semantic_similarity(sent_a: str, sent_b: str) -> float:
    emb_a = _model.encode([sent_a])
    emb_b = _model.encode([sent_b])
    return float(cosine_similarity(emb_a, emb_b)[0][0])


def word_semantic_similarity(word_a: str, word_b: str) -> float:
    """Compute cosine similarity between two words/short phrases using the same SBERT model."""
    emb_a = _model.encode([word_a])
    emb_b = _model.encode([word_b])
    return float(cosine_similarity(emb_a, emb_b)[0][0])