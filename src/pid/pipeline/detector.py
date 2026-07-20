from dataclasses import dataclass
from enum import Enum

from pid.extraction.text_extractor import extract_from_text
from pid.extraction.pdf_extractor import extract_from_pdf
from pid.heuristics.validator import evaluate as heuristic_evaluate, HeuristicResult

class Verdict(str, Enum):
  SAFE = "safe"
  SUSPICIOUS = "suspicious"
  MALICIOUS = "malicious"

@dataclass
class DetectionResult:
  verdict: Verdict
  score: float
  heuristic: HeuristicResult
  stage_reached: str

THRESHOLD_MALICIOUS = 0.8
THRESHOLD_SUSPICIOUS = 0.4

def verdict_from_score(score: float) -> Verdict:
  if score >= THRESHOLD_MALICIOUS:
    return Verdict.MALICIOUS
  if score >= THRESHOLD_SUSPICIOUS:
    return Verdict.SUSPICIOUS
  return Verdict.SAFE

def detect_from_text(raw_text: str) -> DetectionResult:
  normalized = extract_from_text(raw_text)
  heuristic_result = heuristic_evaluate(visible_text=normalized)

  return DetectionResult(
    verdict=verdict_from_score(heuristic_result.score),
    score=heuristic_result.score,
    heuristic=heuristic_result,
    stage_reached="heuristic",
  )


def detect_from_pdf(path: str) -> DetectionResult:
  extraction = extract_from_pdf(path)
  visible_text = ", ".join([span.text for span in extraction.spans if span.is_visible])
  hidden_text = ", ".join([span.text for span in extraction.spans if not span.is_visible])

  heuristic_result = heuristic_evaluate(
    visible_text=visible_text,
    hidden_text=hidden_text,
    metadata_text=extraction.metadata,
  )

  return DetectionResult(
    verdict=verdict_from_score(heuristic_result.score),
    score=heuristic_result.score,
    heuristic=heuristic_result,
    stage_reached="heuristic",
  )