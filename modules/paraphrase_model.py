try:
    from transformers import pipeline
    PARA_AVAILABLE = True
except Exception:
    pipeline = None
    PARA_AVAILABLE = False

MODEL_NAME = "Vamsi/T5_Paraphrase_Paws"

def get_paraphrases(sentence: str, num_return_sequences: int = 3):
    if not PARA_AVAILABLE:
        return []
    try:
        parap = pipeline("text2text-generation", model=MODEL_NAME, tokenizer=MODEL_NAME)
        outs = parap(sentence, max_length=64, num_return_sequences=num_return_sequences)
        results = [o.get("generated_text", "").strip() for o in outs]
        return results
    except Exception:
        return []