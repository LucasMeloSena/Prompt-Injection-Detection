import fitz
from dataclasses import dataclass, field
import os

@dataclass
class ExtractedSpan:
  text: str
  font_size: float
  color: int
  is_visible: bool

@dataclass
class PDFExtractionResult:
  metadata: str
  spans: list = field(default_factory=list)

def is_span_visible(span: dict, page_background: int = 0xFFFFFF) -> bool:
  tiny_font = span["size"] < 3.0
  same_as_bg = span["color"] == page_background
  return not (tiny_font or same_as_bg)

def extract_from_pdf(path: str) -> PDFExtractionResult:
  real_path = os.path.realpath(path)
  document = fitz.open(real_path)
  spans = []

  for page in document:
    raw = page.get_text("dict")
    for block in raw.get("blocks", []):
      for line in block.get("lines", []):
        for span in line.get("spans", []):
          is_visible = is_span_visible(span)
          spans.append(ExtractedSpan(
            text=span["text"],
            font_size=span["size"],
            color=span["color"],
            is_visible=is_visible
          ))

  metadata = document.metadata or {}
  metadata_text = " ".join(str(v) for v in metadata.values() if v)

  document.close()

  return PDFExtractionResult(
    metadata=metadata_text,
    spans=spans
  )