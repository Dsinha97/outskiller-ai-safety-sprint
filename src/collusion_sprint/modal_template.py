"""Template for fanning an experiment out over seeds and conditions on Modal.

Not yet run. Copy into experiments/<name>/run.py and replace `run_one`.
Provider keys come from Modal Secrets created by their owner, referenced by name only.
Run with:  PYTHONUTF8=1 modal run experiments/<name>/run.py
"""
import modal

app = modal.App("collusion-sprint-template")

image = modal.Image.debian_slim(python_version="3.11").pip_install("numpy", "pandas")

# Replace with the Secret name your team creates, e.g. modal.Secret.from_name("openai-secret").
SECRETS: list[modal.Secret] = []


@app.function(image=image, secrets=SECRETS, timeout=60 * 30)
def run_one(condition: str, seed: int) -> dict:
    """Run one (condition, seed) and return a small, JSON-serialisable record."""
    return {"condition": condition, "seed": seed, "cost_usd": 0.0}


@app.local_entrypoint()
def main(conditions: str = "baseline", seeds: int = 3):
    from collusion_sprint.runlog import log_run

    grid = [(c, s) for c in conditions.split(",") for s in range(seeds)]
    for record in run_one.starmap(grid):
        log_run("template", record)
