import json
import random
from pathlib import Path
from dataclasses import dataclass, asdict

random.seed(42)

RAW_DIR = Path("data/raw")
SYNTHETIC_DIR = Path("data/synthetic")
PROCESSED_DIR = Path("data/processed")

TRAIN_RATIO = 0.8
VAL_RATIO = 0.1

@dataclass
class Example:
    text: str
    label: int
    category: str
    source: str

def load_synthetic_jsonl(path: Path) -> list[Example]:
    examples = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                print(f"[aviso] linha {line_num} inválida, ignorando: {line[:80]}")
                continue
            examples.append(Example(
                text=obj["text"],
                label=int(obj["label"]),
                category=obj.get("category", "unknown"),
                source="synthetic_pt",
            ))
    return examples

def deduplicate(examples: list[Example]) -> list[Example]:
    seen = set()
    unique = []
    for ex in examples:
        key = ex.text.strip().lower()
        if key not in seen:
            seen.add(key)
            unique.append(ex)
    return unique

def split_dataset(examples: list[Example]) -> dict[str, list[Example]]:
    by_label: dict[int, list[Example]] = {}
    for ex in examples:
        by_label.setdefault(ex.label, []).append(ex)

    train, val, test = [], [], []
    for _, group in by_label.items():
        random.shuffle(group)
        n = len(group)
        n_train = int(n * TRAIN_RATIO)
        n_val = int(n * VAL_RATIO)

        train += group[:n_train]
        val += group[n_train:n_train + n_val]
        test += group[n_train + n_val:]

    random.shuffle(train)
    random.shuffle(val)
    random.shuffle(test)
    return {"train": train, "val": val, "test": test}

def save_split(examples: list[Example], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(asdict(ex), ensure_ascii=False) + "\n")

def print_stats(name: str, examples: list[Example]):
    n_malicious = sum(1 for e in examples if e.label == 1)
    n_benign = len(examples) - n_malicious
    print(f"  {name}: {len(examples)} exemplos ({n_malicious} maliciosos, {n_benign} benignos)")

def main():
    all_examples = []

    synthetic_files = list(SYNTHETIC_DIR.glob("*.jsonl"))
    raw_files = list(RAW_DIR.glob("*.jsonl"))

    for f in synthetic_files:
        loaded = load_synthetic_jsonl(f)
        print(f"Carregado {f.name}: {len(loaded)} exemplos")
        all_examples += loaded

    for f in raw_files:
        loaded = load_synthetic_jsonl(f)
        print(f"Carregado {f.name}: {len(loaded)} exemplos")
        all_examples += loaded

    print(f"\nTotal antes de deduplicar: {len(all_examples)}")
    all_examples = deduplicate(all_examples)
    print(f"Total após deduplicar: {len(all_examples)}")

    splits = split_dataset(all_examples)

    print("\nDistribuição dos splits:")
    for name, examples in splits.items():
        print_stats(name, examples)
        save_split(examples, PROCESSED_DIR / f"{name}.jsonl")

    print(f"\nSalvo em {PROCESSED_DIR}/")

if __name__ == "__main__":
    main()