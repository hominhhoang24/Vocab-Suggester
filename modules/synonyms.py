import nltk

try:
    from nltk.corpus import wordnet as wn
    WORDNET_AVAILABLE = True
except Exception:
    wn = None
    WORDNET_AVAILABLE = False

try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("wordnet")
    nltk.download("omw-1.4")

FALLBACK = {
    "good": ["well", "nice", "pleasant"],
    "big": ["large", "huge", "immense"],
    "complex": ["complicated", "intricate", "elaborate"],
    "difficult": ["hard", "tough", "challenging"]
}

def map_pos(pos: str):
    if not pos:
        return None
    pos = pos.upper()
    if pos.startswith("N"):
        return wn.NOUN
    if pos.startswith("V"):
        return wn.VERB
    if pos.startswith("J"):  
        return wn.ADJ
    if pos.startswith("R"): 
        return wn.ADV
    return None


def get_wordnet_candidates(word: str, pos: str = None):
    """
    Return list of candidate synonyms.
    Prefers single-word synonyms.
    Supports spaCy POS if provided.
    """
    word_lower = word.lower()
    candidates = set()

    if WORDNET_AVAILABLE:
        try:
            wn_pos = map_pos(pos)
            synsets = wn.synsets(word_lower, pos=wn_pos) if wn_pos else wn.synsets(word_lower)

            for s in synsets:
                for lemma in s.lemmas():
                    name = lemma.name().replace("_", " ").lower()
                    print("Found lemma:", name)
                    if name != word_lower:
                        # keep single-word first
                        if " " not in name:
                            candidates.add(name)
                        else:
                            candidates.add(name)

            # print("candidates:", candidates)
        except Exception:
            pass

    if not candidates and word_lower in FALLBACK:
        candidates.update(FALLBACK[word_lower])

    return sorted(candidates)


def get_synonyms_list(word: str, pos: str = None):
    """
    Legacy API used by app.py.
    Simply calls the new candidate extractor.
    """
    return get_wordnet_candidates(word, pos)