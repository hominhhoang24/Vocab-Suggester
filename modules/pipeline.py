from .spacy_parser import parse_sentence, tag_word_pos
from .complexity import get_word_complexity
from .synonyms import get_wordnet_candidates
from .paraphrase_model import get_paraphrases
from .contextual_llm import llm_contextual_suggestions
from .context_scorer import ContextScorer
context_scorer = ContextScorer()
from .ranker import rank_candidates
from .semantic_similarity import sentence_semantic_similarity, word_semantic_similarity


def suggest_words(
    sentence: str,
    target_word: str,
    mode: str = "neutral",
    max_candidates: int = 20
):
    tokens = parse_sentence(sentence)
    target_pos = tag_word_pos(sentence, target_word)

    cands_set = set()

    for c in get_wordnet_candidates(target_word):
        cands_set.add(c.lower())

    for p in get_paraphrases(sentence):
        if target_word.lower() in p.lower():
            continue
        cands_set.add(p.strip().lower())

    for l in llm_contextual_suggestions(target_word, sentence):
        cands_set.add(l.strip().lower())

    cands_set.discard(target_word.lower())

    candidates_info = []

    for cand in cands_set:
        test_sentence = sentence.replace(target_word, cand)

        semantic_sim = sentence_semantic_similarity(
            sentence,
            test_sentence
        )

        if semantic_sim < 0.75 and len(candidates_info) > max_candidates:
            continue

        if tag_word_pos(test_sentence, cand) != target_pos:
            continue

        comp = get_word_complexity(cand)

        try:
            lex_sim = word_semantic_similarity(target_word, cand)
        except Exception:
            lex_sim = 0.0

        sc_list = context_scorer.score(sentence, target_word, [cand])
        fluency = float(sc_list[0][1]) if sc_list else 0.0

        candidates_info.append({
            "word": cand,
            "semantic_similarity": semantic_sim,
            "context_score": fluency,
            "lexical_similarity": lex_sim,
            "zipf": comp.get("zipf"),
            "cefr": comp.get("cefr"),
            "complexity": comp.get("complexity_score"),
        })

    if not candidates_info:
        return []

    print("candidates_info:", candidates_info)

    ranked = rank_candidates(candidates_info, top_n=max_candidates, mode=mode)

    for r in ranked:
        if r["final_score"] >= 0.7:
            r["reason"] = "Strong synonym; meaning preserved."
        elif r["final_score"] >= 0.45:
            r["reason"] = "Acceptable synonym; check nuance."
        else:
            r["reason"] = "Weak semantic replacement."

    return ranked[:max_candidates]