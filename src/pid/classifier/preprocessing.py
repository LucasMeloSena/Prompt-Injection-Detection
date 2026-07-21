from transformers import AutoTokenizer

MODEL_NAME = "models/pid-classifier-v1"

_tokenizer = None

def get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    return _tokenizer

def tokenize(text: str, max_length: int = 512):
    tokenizer = get_tokenizer()
    return tokenizer(
        text,
        truncation=True,
        max_length=max_length,
        padding="max_length",
        return_tensors="pt",
    )