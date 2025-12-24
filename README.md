# Vocab Suggester

Ứng dụng Flask gợi ý từ vựng theo **độ phức tạp** và **ngữ cảnh**.

## Chuẩn bị môi trường

```bash
python -m venv venv
# activate venv
# Linux / macOS:
source venv/bin/activate
# Windows (PowerShell):
venv\Scripts\Activate

pip install -r requirements.txt

# Tải spaCy English model
python -m spacy download en_core_web_sm

# Tải NLTK resources (mở Python shell hoặc script)
python - <<PY
import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')
PY
```

## Chạy ứng dụng

```bash
python app.py
