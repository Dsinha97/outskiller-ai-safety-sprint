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
