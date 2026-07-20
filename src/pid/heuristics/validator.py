from dataclasses import dataclass, field
from pid.heuristics.patterns import Pattern, load_patterns

@dataclass
class HeuristicMatch:
  pattern_id: str
  category: str
  matched_text: str
  location: str
  base_weight: float
  adjusted_weight: float

@dataclass
class HeuristicResult:
  score: float
  matches: list[HeuristicMatch] = field(default_factory=list)

  @property
  def is_suspicious(self) -> bool:
    return self.score >= 0.5
  
LOCATION_MULTIPLIER = {
  "hidden": 1.5,
  "metadata": 1.3,
  "visible": 1.0,
}

def scan_text(text: str, location: str, patterns: list[Pattern]) -> list[HeuristicMatch]:
    matches = []
    multiplier = LOCATION_MULTIPLIER.get(location, 1.0)

    for pattern in patterns:
      for regex in pattern.compiled_regexes:
        m = regex.search(text)
        if m:
          matches.append(HeuristicMatch(
            pattern_id=pattern.id,
            category=pattern.category,
            matched_text=m.group(0),
            location=location,
            base_weight=pattern.weight,
            adjusted_weight=min(pattern.weight * multiplier, 1.0),
          ))
          break

    return matches

def evaluate(visible_text: str, hidden_text: str = "", metadata_text: str = "") -> HeuristicResult:
  patterns = load_patterns()

  all_matches = []
  all_matches += scan_text(visible_text, "visible", patterns)
  all_matches += scan_text(hidden_text, "hidden", patterns)
  all_matches += scan_text(metadata_text, "metadata", patterns)

  if not all_matches:
    return HeuristicResult(score=0.0, matches=[])

  top_score = max(m.adjusted_weight for m in all_matches)
  final_score = min(top_score, 1.0)

  return HeuristicResult(score=final_score, matches=all_matches)