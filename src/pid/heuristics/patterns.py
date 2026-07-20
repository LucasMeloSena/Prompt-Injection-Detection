from dataclasses import dataclass
from pathlib import Path
import re
import yaml

@dataclass
class Pattern:
  id: str
  category: str
  weight: float
  compiled_regexes: list

def load_patterns() -> list[Pattern]:
  yaml_path = Path(__file__).parent / "known_attacks.yaml"

  with open(yaml_path, "r", encoding="utf-8") as f:
    raw = yaml.safe_load(f)

  patterns = []

  for entry in raw["patterns"]:
    compiled = [re.compile(p) for p in entry["regex"]]
    patterns.append(Pattern(
      id=entry["id"],
      category=entry["category"],
      weight=entry["weight"],
      compiled_regexes=compiled,
    ))

  return patterns