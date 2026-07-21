from dataclasses import dataclass
from enum import Enum

from pid.extraction.text_extractor import extract_from_text
from pid.extraction.pdf_extractor import extract_from_pdf
from pid.heuristics.validator import evaluate as heuristic_evaluate, HeuristicResult
from pid.classifier.model import predict

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
  classifier_scores: dict | None

THRESHOLD_MALICIOUS = 0.8
THRESHOLD_SUSPICIOUS = 0.4
THRESHOLD_HEURISTIC = 0.95

def _verdict_from_score(score: float) -> Verdict:
  if score >= THRESHOLD_MALICIOUS:
    return Verdict.MALICIOUS
  if score >= THRESHOLD_SUSPICIOUS:
    return Verdict.SUSPICIOUS
  return Verdict.SAFE

def _combine_scores(heuristic_score: float, classifier_scores: dict) -> float:
  classifier_score = max(
    value for key, value in classifier_scores.items() if key.upper() != "BENIGN"
  )
  return max(classifier_score, heuristic_score)

def _run_pipeline(visible_text: str, hidden_text: str = "", metadata: str = "") -> DetectionResult:
  heuristic_result = heuristic_evaluate(
    visible_text=visible_text,
    hidden_text=hidden_text,
    metadata_text=metadata,
  )

  if heuristic_result.score >= THRESHOLD_HEURISTIC:
    return DetectionResult(
      verdict=_verdict_from_score(heuristic_result.score),
      score=heuristic_result.score,
      heuristic=heuristic_result,
      stage_reached="heuristic",
      classifier_scores=None
    )

  combined_text = " ".join(filter(None, [visible_text, hidden_text, metadata]))
  classifier_scores = predict(combined_text) if combined_text.strip() else {}

  final_score = (
    _combine_scores(heuristic_result.score, classifier_scores) 
    if classifier_scores 
    else heuristic_result.score
  )

  return DetectionResult(
    verdict=_verdict_from_score(final_score),
    score=final_score,
    heuristic=heuristic_result,
    classifier_scores=classifier_scores,
    stage_reached="classifier"
  )

def detect_from_text(raw_text: str) -> DetectionResult:
  normalized = extract_from_text(raw_text)
  return _run_pipeline(normalized)


def detect_from_pdf(path: str) -> DetectionResult:
  extraction = extract_from_pdf(path)
  visible_text = ", ".join([span.text for span in extraction.spans if span.is_visible])
  hidden_text = ", ".join([span.text for span in extraction.spans if not span.is_visible])

  return _run_pipeline(visible_text, hidden_text, extraction.metadata)