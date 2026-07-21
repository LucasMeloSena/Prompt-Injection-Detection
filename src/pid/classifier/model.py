from transformers import AutoModelForSequenceClassification
import torch

from pid.classifier.preprocessing import MODEL_NAME, get_tokenizer

_model = None

def load_model(model_path: str = MODEL_NAME):
    global _model
    if _model is None:
        _model = AutoModelForSequenceClassification.from_pretrained(model_path)
        _model.eval()
    return _model, get_tokenizer()

@torch.no_grad()
def predict(text: str) -> dict:
    model, tokenizer = load_model()
    inputs = tokenizer(text, truncation=True, max_length=512, return_tensors="pt")
    logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=-1)[0]

    labels = model.config.id2label
    scores = {labels[i]: probs[i].item() for i in range(len(probs))}
    return scores