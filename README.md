# Outskiller AI Safety Sprint: AI Collusion

Code, configs and logged results for our team's entry in the [Apart Research AI Collusion Research Sprint](https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25) (Oct 23-25, 2026). Submissions close Sun Oct 25, 11:59 PM AoE.

Nothing here is a result yet. The research question, harness and hypotheses are decided in the team's shared doc and recorded in `docs/DECISIONS.md`.

## Layout

```
src/collusion_sprint/   shared helpers (config, run logging, Modal fan-out template)
experiments/            one folder per experiment: config, run script, README
results/                logged run outputs (small files only; see .gitignore)
docs/                   decisions, prior-work log, LLM usage, limitations draft
```

## Setup

Python 3.11+ (3.13 tested by one teammate).

```bash
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .                 # makes `collusion_sprint` importable
cp .env.example .env             # then fill in your own keys; .env is git-ignored
```

**Never commit API keys, tokens or `.env`.** Model-provider keys used on Modal live in Modal Secrets created by their owner and are referenced by name only (`modal.Secret.from_name("...")`).

### Modal

On Windows set `PYTHONUTF8=1` first or the Modal CLI crashes printing Unicode. Authenticate once with `modal setup` (browser login, done by each user themselves).

```bash
modal run experiments/<name>/run.py
```

Most starter routes are API-only and run on a laptop. Use Modal for fanning out seeds or conditions, or for GPU work on open-weight models.

## Experiment rules (from the sprint's guidelines)

- Reproduce the **positive control** first, then change **one lever at a time**.
- 3-5 seeds per condition to start; 10-20 only after the positive control works. Report seeds, variance and baselines.
- Detectors and monitors: freeze model, prompt and threshold **before** evaluating. Pick decision rules on half the data, test on the other half. Report false-positive rate (TPR at about 1% FPR), not just AUROC.
- Calibrate dependence-style detectors against a same-model, no-communication control.
- "Coordination moved channels" needs message coordination to fall **and** action dependence to rise. High prices alone are not evidence.
- Log every run: config, seed, model, prompt hash, cost. Track spend against the team budget cap.
- Do not fabricate results or citations. The sprint disqualifies both.

## Working in this repo

- Branch per experiment (`exp/<short-name>`), small PRs into `main`, one reviewer who is not the author.
- Commit configs and summary tables, not large raw dumps.
- Anything written before Oct 23 is **prior work** and must be listed in `docs/PRIOR_WORK.md` and the report.

## Report

PDF on the official Apart template, at most 8 pages plus references and appendices, a 150-250 word abstract, a **Limitations and Dual-Use / Ethical Considerations** appendix, and an LLM usage statement (`docs/LLM_USAGE.md`).
