"""Append-only JSONL run log so every run records its config, seed, model and cost."""
import hashlib
import json
import time
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parents[2] / "results"


def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12]


def log_run(experiment: str, record: dict) -> Path:
    """Write one record to results/<experiment>.jsonl and return the path.

    Expected keys: condition, seed, model, prompt_hash, cost_usd, plus metrics.
    """
    RESULTS_DIR.mkdir(exist_ok=True)
    path = RESULTS_DIR / f"{experiment}.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": time.time(), **record}) + "\n")
    return path


def total_cost(experiment: str) -> float:
    path = RESULTS_DIR / f"{experiment}.jsonl"
    if not path.exists():
        return 0.0
    with path.open(encoding="utf-8") as f:
        return sum(json.loads(line).get("cost_usd", 0.0) for line in f if line.strip())
