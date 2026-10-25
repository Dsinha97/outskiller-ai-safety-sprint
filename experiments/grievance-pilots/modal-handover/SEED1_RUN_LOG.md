# Seed 1 repeat runs: run log (25 Oct 2026, Prashanth)

Sprint work. Second sample of two open-weight watchdogs at vLLM engine seed 1, on both frozen prompt sets. No result files or case text are in the repo; the zips are on the team Drive (`results/`).

- Script: `run_precedent_modal.py` from the Drive `modal-handover` folder (has `--seed`; sha256 `966a5cfcad18414ec0d0517838ac3bac58acddad1aa73c4ff3b148c46dbf05a3`)
- Prompt files (match the frozen hashes in FREEZE_open-weight-watchdogs.md):
  - `precedent_prompts.jsonl` `4c899ab6610963c8f949840b4e93140de7553f68de47a32fe2f8d0d777c5958a`
  - `underrated_prompts.jsonl` `8d57485b6593ff2c60f4399b57a56e75841fee71c916809b2acd4efe8472efea`
- Settings unchanged: temperature 0.7, 2 draws per prompt, vllm 0.31.0, `--seed 1`
- Commands: `modal run run_precedent_modal.py --model <tag> --seed 1 [--prompt-set underrated]`, after a `--smoke` test per model

| Model | GPU | Six-arm set | Harder set | `flag_missing` |
|---|---|---|---|---|
| `qwen3-32b` | H100 | 648 files | 294 files | 0 |
| `mistral-small-3.2-24b` | A100-80GB | 648 files | 294 files | 0 |

Checks: every file has `"seed": 1`; in the smoke tests the two draws of each prompt differed; no app or container was left running afterwards. Output folders: `results/<tag>_seed1/<set>_arms/`. Not yet checked: `system_sha`/`user_sha` against the seed 0 runs (to be done in the cross-model analysis).

## Flag tallies (seed 1)

Suppression cases flagged, by arm (flag true, not `flag_missing`). Six-arm set has 48 per arm, harder set 26 per arm.

| Model | Six-arm A / C / F (of 48) | Harder set A / C / F (of 26) |
|---|---|---|
| `qwen3-32b` | 47 / 45 / 42 | 13 / 6 / 3 |
| `mistral-small-3.2-24b` | 42 / 18 / 21 | 8 / 11 / 7 |

False flags on benign (six-arm set, 60 per arm) and compliant (harder set, 72 per arm) cases, arms A / C / F:

| Model | Six-arm A / C / F | Harder set A / C / F |
|---|---|---|
| `qwen3-32b` | 0 / 1 / 0 | 0 / 1 / 0 |
| `mistral-small-3.2-24b` | 1 / 1 / 0 | 3 / 2 / 0 |

Arms B, D and E (six-arm set) are in the result files and not tabulated here.

## Spend

About $2.40 (Modal Usage page, Oct 1-31 cycle; $2.43 in the hourly billing report for 25 Oct), all paid from credit, nothing charged to the card. Smoke tests: $0.28 (Qwen) and $0.33 (Mistral). About $1.81 for the four full runs together; the report does not split them by model.
