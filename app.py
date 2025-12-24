from flask import Flask, render_template, request, redirect, url_for, flash
from modules.spacy_parser import parse_sentence, get_focus_candidates
from modules.synonyms import get_synonyms_list
from modules.context_scorer import ContextScorer
from modules.complexity import get_complexity_info
from modules.ranker import combine_and_rank
from modules.semantic_similarity import sentence_semantic_similarity
import pandas as pd

app = Flask(__name__)
app.secret_key = "replace-with-your-secret-key"

context_scorer = ContextScorer()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/suggest", methods=["POST"])
def suggest():
    sentence = request.form.get("sentence", "").strip()
    focus = request.form.get("focus_word", "").strip()
    pos_filter = request.form.get("pos_filter", "any")
    top_n = int(request.form.get("top_n", 5))

    if not sentence:
        flash("Vui lòng nhập câu!", "warning")
        return redirect(url_for("index"))

    if not focus:
        tokens = parse_sentence(sentence)
        candidates = get_focus_candidates(tokens)
        if not candidates:
            flash("Không tìm thấy từ mục tiêu tự động.", "warning")
            return redirect(url_for("index"))
        focus = candidates[0]

    # LẤY ĐỒNG NGHĨA
    synonyms = get_synonyms_list(focus, pos_filter)
    if not synonyms:
        flash(f"Không tìm thấy đồng nghĩa cho '{focus}'.", "warning")
        return redirect(url_for("index"))
    print("synonyms:", synonyms)
    
    ranked = context_scorer.score(sentence, focus, synonyms)

    rows = []

    for word, context_score in ranked:
        replaced_sentence = sentence.replace(focus, word)

        semantic_sim = sentence_semantic_similarity(
            sentence,
            replaced_sentence
        )

        print(f"Word: {word}, Semantic similarity: {semantic_sim}, top: {top_n}")

        if semantic_sim < 0.75 and len(rows) >= top_n:
            continue

        comp = get_complexity_info(word)

        rows.append({
            "word": word,
            "semantic_similarity": round(float(semantic_sim), 5),
            "context_score": round(float(context_score), 5),
            "zipf": comp.get("zipf"),
            "CEFR": comp.get("cefr"),
            "complexity": round(float(comp.get("complexity_score")), 5)
        })

    if not rows:
        flash("Không có từ thay thế phù hợp về mặt ngữ nghĩa.", "warning")
        return redirect(url_for("index"))
    
    print("rows before ranking:", rows)

    ranked_rows = combine_and_rank(rows, top_n, mode="neutral")
    df = pd.DataFrame(ranked_rows)

    df_display = df.head(top_n).reset_index(drop=True)

    return render_template(
        "result.html",
        sentence=sentence,
        focus=focus,
        df=df_display.to_dict(orient="records")
    )


if __name__ == "__main__":
    app.run(debug=True)