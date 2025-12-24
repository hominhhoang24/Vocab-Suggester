try:
    from sentence_transformers import SentenceTransformer, util
    SBERT_AVAILABLE = True
    SBERT_MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
except Exception:
    SBERT_AVAILABLE = False
    SBERT_MODEL = None

import math

def _heuristic_similarity(candidate: str, sentence: str, target_word: str) -> float:
    s = sentence.lower()
    score = 0.0

    if candidate.lower() in s:
        score += 1.0

    score += 1.0 / (1 + abs(len(candidate) - len(target_word)))

    overlap = len(set(candidate.lower()) & set(sentence.lower()))
    score += math.log(1 + overlap)

    return float(score)


def compute_similarity(candidate: str, sentence: str, target_word: str) -> float:
    """
    Returns similarity score in [0,1].
    SBERT → cosine similarity
    fallback → heuristic
    """
    if SBERT_AVAILABLE and SBERT_MODEL is not None:
        try:
            sent_with_candidate = sentence.replace(target_word, candidate)

            emb_sent = SBERT_MODEL.encode(sentence, convert_to_tensor=True)
            emb_cand_sent = SBERT_MODEL.encode(sent_with_candidate, convert_to_tensor=True)

            cos = util.cos_sim(emb_sent, emb_cand_sent).item()
            return float((cos + 1.0) / 2.0)   # map from [-1,1] → [0,1]

        except Exception:
            return _heuristic_similarity(candidate, sentence, target_word)

    return _heuristic_similarity(candidate, sentence, target_word)


class ContextRanker:
    """
    Rank a list of candidate words based on contextual similarity.
    This class is required by app.py.
    """

    def __init__(self):
        self.use_sbert = SBERT_AVAILABLE

    def rank(self, sentence: str, target_word: str, candidates: list[str]):
        """
        Input:
            - sentence: original text
            - target_word: word being replaced
            - candidates: list of synonym words
        Output:
            - sorted list of (word, score)
        """
        scored = []
        for c in candidates:
            score = compute_similarity(c, sentence, target_word)
            scored.append((c, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored