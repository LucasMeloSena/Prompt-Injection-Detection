import re
import unicodedata

def normalize_text(text: str) -> str:
  normalized = unicodedata.normalize("NFKC", text)
  normalized = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", text) # Remove invisible chars
  return normalized

def extract_from_text(raw_text: str) -> str:
  return normalize_text(raw_text)