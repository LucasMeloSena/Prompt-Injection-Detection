from datasets import load_dataset
import json
from pathlib import Path

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

DATASET_CONFIGS = [
    {
        "hf_path": "deepset/prompt-injections",
        "text_col": "text",
        "label_col": "label",
        "output": "deepset.jsonl",
    },
]

def download_and_normalize(config: dict):
    print(f"Baixando {config['hf_path']}...")
    ds = load_dataset(config["hf_path"])

    out_path = RAW_DIR / config["output"]
    count = 0
    with open(out_path, "w", encoding="utf-8") as f:
        for split_name in ds.keys():
            for row in ds[split_name]:
                text = row[config["text_col"]]
                label = int(row[config["label_col"]])
                f.write(json.dumps({
                    "text": text,
                    "label": label,
                    "source": config["hf_path"],
                }, ensure_ascii=False) + "\n")
                count += 1

    print(f"  → {count} exemplos salvos em {out_path}")


if __name__ == "__main__":
    for config in DATASET_CONFIGS:
        download_and_normalize(config)