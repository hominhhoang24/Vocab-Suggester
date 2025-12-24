def rank_candidates(candidates, top_n=5, mode="neutral"):
    """
    candidates: list of dicts with keys:
        word
        semantic_similarity   (float, bắt buộc)
        context_score         (float, bắt buộc)
        zipf                  (float, optional)
        CEFR                  (str, optional)
        complexity            (float, optional)
    """

    if not candidates:
        return []

    SEMANTIC_MIN = 0.80
    LEXICAL_MIN = 0.65

    sem_ok = []
    for c in candidates:
        try:
            semantic = float(c.get("semantic_similarity", 0.0))
        except Exception:
            semantic = 0.0
        try:
            lexical = float(c.get("lexical_similarity", c.get("_lex_norm", 0.0)))
        except Exception:
            lexical = 0.0
        if semantic >= SEMANTIC_MIN or lexical >= LEXICAL_MIN:
            sem_ok.append(c)

    if not sem_ok:
        return []

    def _clamp01(x):
        try:
            v = float(x)
        except Exception:
            return 0.0
        if v != v:
            return 0.0
        return max(0.0, min(1.0, v))

    def _zipf_norm(z):
        try:
            zf = float(z)
        except Exception:
            zf = 3.0
        return max(0.0, min(1.0, (zf - 1.0) / 6.0))

    WEIGHTS = {
        "neutral": {
            "w_sem": 0.35,
            "w_lex": 0.35,
            "w_ctx": 0.20,
            "w_comp": 0.08,
            "w_zipf": 0.02,
        }
    }

    w = WEIGHTS.get(mode, WEIGHTS["neutral"])

    scored = []
    for c in sem_ok:
        sem = _clamp01(c.get("semantic_similarity", 0.0))
        lex = _clamp01(c.get("lexical_similarity", 0.0))
        ctx = _clamp01(c.get("context_score", 0.0))
        zipf_n = _zipf_norm(c.get("zipf", 3.0))
        comp = _clamp01(c.get("complexity", 0.5))

        if mode == "simplify":
            comp_term = 1.0 - comp
        elif mode == "academic":
            comp_term = comp
        else:
            comp_term = 1.0 - comp

        final = (
            w["w_sem"] * sem
            + w["w_lex"] * lex
            + w["w_ctx"] * ctx
            + w["w_comp"] * comp_term
            + w["w_zipf"] * zipf_n
        )

        meaning_ok = (sem >= SEMANTIC_MIN) and (lex >= LEXICAL_MIN)
        context_ok = (ctx >= 0.35)
        complexity_ok = (comp <= 0.75)

        tier = int(meaning_ok) + int(context_ok) + int(complexity_ok)

        c["_meaning_ok"] = meaning_ok
        c["_context_ok"] = context_ok
        c["_complexity_ok"] = complexity_ok
        c["_tier"] = tier
        c["_sem_norm"] = sem
        c["_lex_norm"] = lex
        c["_ctx_norm"] = ctx
        c["_zipf_norm"] = zipf_n
        c["_comp_term"] = comp_term
        c["final_score"] = float(final)

        try:
            tier = int(c.get("_tier", 0))
        except Exception:
            tier = 0
        BONUS_IF_ALL = 0.20
        c["_boosted_score"] = c["final_score"] + (BONUS_IF_ALL if tier == 3 else 0.0)

        scored.append(c)

    meaning_group = [c for c in scored if c.get("_meaning_ok")]
    nonmeaning_group = [c for c in scored if not c.get("_meaning_ok")]

    def _sort_key_meaning(x):
        return (
            int(x.get("_tier", 0)),
            float(x.get("_ctx_norm", 0.0)),
            float(1.0 - x.get("_comp_term", 0.0)),
            float(x.get("_sem_norm", 0.0)),
            float(x.get("_lex_norm", 0.0)),
            float(x.get("_zipf_norm", 0.0)),
        )

    def _sort_key_nonmeaning(x):
        return (
            float(x.get("_ctx_norm", 0.0)),
            float(1.0 - x.get("_comp_term", 0.0)),
            float(x.get("_sem_norm", 0.0)),
            float(x.get("_lex_norm", 0.0)),
            float(x.get("_zipf_norm", 0.0)),
        )

    meaning_sorted = sorted(meaning_group, key=_sort_key_meaning, reverse=True)
    nonmeaning_sorted = sorted(nonmeaning_group, key=_sort_key_nonmeaning, reverse=True)

    ranked = meaning_sorted + nonmeaning_sorted

    return ranked[:top_n]


def combine_and_rank(rows, top_n=5, mode="neutral"):
    return rank_candidates(rows, top_n=top_n, mode=mode)