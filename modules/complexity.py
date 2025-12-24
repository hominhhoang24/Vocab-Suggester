import csv
from pathlib import Path
from functools import lru_cache

try:
    from wordfreq import zipf_frequency
    WORDFREQ_AVAILABLE = True
except Exception:
    WORDFREQ_AVAILABLE = False

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CEFR_CSV = DATA_DIR / "cefr_wordlist.csv"

_cefr_map = {}

def _load_cefr():
    global _cefr_map
    if _cefr_map:
        return
    if CEFR_CSV.exists():
        with CEFR_CSV.open(encoding="utf-8") as f:
            reader = csv.reader(f)
            for r in reader:
                if not r:
                    continue
                data = r[0].split(';')
                word = data[0].strip().lower()
                level = data[2].strip().upper() if len(data) > 1 else "C1"
                # print("word + level", word , level)
                _cefr_map[word] = level
    else:
        sample = {
            "good": "A1", "well": "A1", "just": "A1", "right": "A1",
            "thoroughly": "B2", "near": "B1",
            "complex": "C1", "difficult": "B1"
        }
        _cefr_map.update(sample)

_load_cefr()

@lru_cache(maxsize=20000)
def get_zipf(word: str) -> float:
    w = word.lower()
    if WORDFREQ_AVAILABLE:
        return float(zipf_frequency(w, "en"))
    fallback = {
        "the": 7.5, "and": 7.0, "is": 7.0,
        "good": 5.0, "well": 5.5, "just": 5.5,
        "right": 5.2, "thoroughly": 3.5, "near": 4.5
    }
    return float(fallback.get(w, 3.0))

@lru_cache(maxsize=20000)
def get_cefr(word: str) -> str:
    return _cefr_map.get(word.lower(), "C1")

def complexity_score_from(cefr: str, zipf: float) -> float:
    order = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}
    cefr_val = order.get(cefr, 5)
    cefr_norm = (cefr_val - 1) / 5
    zipf_norm = max(0.0, min(1.0, (zipf - 1) / 7))
    complexity = 0.7 * cefr_norm + 0.3 * (1 - zipf_norm)
    return float(complexity)

def get_word_complexity(word: str) -> dict:
    cefr = get_cefr(word)
    zipf = get_zipf(word)
    comp = complexity_score_from(cefr, zipf)
    return {
        "word": word,
        "cefr": cefr,
        "zipf": zipf,
        "complexity_score": comp
    }

def get_complexity_info(word: str):
    return get_word_complexity(word)