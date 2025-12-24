try:
    import spacy
    _nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except Exception:
    _nlp = None
    SPACY_AVAILABLE = False

import re


def parse_sentence(text: str):
    """
    Return list of tokens: {text, lemma, pos, tag, is_alpha}
    """
    if SPACY_AVAILABLE:
        doc = _nlp(text)
        out = []
        for t in doc:
            out.append({
                "text": t.text,
                "lemma": t.lemma_,
                "pos": t.pos_,
                "tag": t.tag_,
                "is_alpha": t.is_alpha
            })
        return out

    tokens = re.findall(r"[A-Za-z']+", text)
    return [{"text": t, "lemma": t.lower(), "pos": "X", "tag": "", "is_alpha": True} for t in tokens]

def tag_word_pos(word: str) -> str:
    """
    Return POS tag (NOUN, VERB, ADJ, ADV, etc.) for a single word.
    Used for filtering synonyms by POS in app.py.
    """
    if SPACY_AVAILABLE:
        doc = _nlp(word)
        if len(doc) > 0:
            return doc[0].pos_
        return "X"
    # fallback
    return "X"

def get_focus_candidates(tokens):
    """
    Return list of candidate focus words e.g. first verb/adj/noun.
    """
    focus = []

    for t in tokens:
        if t["pos"] in ("VERB", "AUX"):
            focus.append(t["text"])
    if focus:
        return focus

    for t in tokens:
        if t["pos"] == "ADJ":
            focus.append(t["text"])
    if focus:
        return focus

    for t in tokens:
        if t["pos"] == "NOUN":
            focus.append(t["text"])
    return focus