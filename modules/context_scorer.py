import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_PATH = "models/vocab_context_scorer"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_PATH
).to(DEVICE)
model.eval()


class ContextScorer:
    def score(self, sentence, target_word, candidates):
        results = []

        for w in candidates:
            s = self._score_one(sentence, target_word, w)
            results.append((w, s))

        return sorted(results, key=lambda x: x[1], reverse=True)

    def _score_one(self, sentence, target_word, candidate_word):
        replaced = sentence.replace(target_word, candidate_word, 1)

        text = f"Sentence: {replaced}"

        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=256
        ).to(DEVICE)

        with torch.no_grad():
            logits = model(**inputs).logits
            prob = logits.softmax(dim=-1)[0][1].item()

        return float(prob)