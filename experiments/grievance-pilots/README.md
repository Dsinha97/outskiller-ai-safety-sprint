# Grievance-pipeline pilots

Code for the pilots written up in `docs/pilots/TECHNICAL_REPORT_talk-pilots.md`. Summary tables from the analysis scripts are in `results/grievance-pilots/`. Raw JSON results and the GrieVoice v2 records stay local (see below), so the runners will not work from this repository alone.

## Prior work and sprint work

The sprint runs 23–25 October 2026. Preexisting means written or run before the end of 22 October UTC (02:00 on 23 October SAST, when MiniMax’s free allowance for the pre-sprint runs expired). Times are SAST (UTC+2).

| File | Status |
|---|---|
| `cached-trajectories/run_pipeline.py` | Preexisting (20–22 Oct); this repo copy was edited on 23 Oct to read paths and keys from environment variables |
| `talk-pilots/run_pressure.py`, `run_all.py` | Preexisting (22 Oct) |
| `talk-pilots/run_talk_pilots.py`, `analyse.py` | Preexisting, modified on 23 Oct: model switch for cross-family reruns. `analyse.py` also fixed on 23 Oct to read each model’s own C3/C4/C5 pressure baselines (it had read the cached MiniMax runs for every model) |
| `talk-pilots/run_lifecycle.py`, `analyse_lifecycle.py` | Preexisting, modified on 23 Oct: critical complainant and single-stage aim arms |
| `talk-pilots/run_openrouter.py` | Sprint work (23 Oct) |
| `talk-pilots/run_ablation.py`, `analyse_ablation.py` | Sprint work (23 Oct): sentence ablation of steering notes |
| `talk-pilots/run_carryover.py`, `analyse_carryover.py` | Sprint work (23 Oct): does a note change the next case |
| `talk-pilots/analyse_motive.py` | Sprint work (23 Oct): regex labels for note style (motive, verdict, neither) |
| `talk-pilots/run_monitor_gemma_notes.py`, `run_monitor_minimax_notes.py`, `analyse_monitor_gemma_notes.py`, `analyse_monitor_cross.py` | Sprint work (23 Oct): independent monitor across model families |
| `talk-pilots/run_precedent_arms.py`, `run_underrated_arms.py`, `analyse_precedent_arms.py` | Sprint work (24 Oct): six calibration arms separating precedent, endorsement and policy priority, and a harder under-rated set; results in `docs/pilots/RESULTS_precedent_arms_2026-10-24.md` |
| `talk-pilots/export_precedent_prompts.py` | Sprint work (24 Oct): freezes the monitor prompts into JSONL for the Modal runs |
| `modal-handover/run_precedent_modal.py`, `RUN_SHEET.md` | Sprint work (24 Oct): vLLM batch runner for open-weight monitors on Modal and the teammate run sheet |
| `modal-handover/run_precedent_api.py` | Sprint work (24 Oct): runs the same frozen prompts on API monitors (Claude Haiku 5.5 and Sonnet 5.5, Gemini 3.8 Flash and 4 Argon) from Modal, reading the keys from Modal secrets; has a spend cap. Results for all four (Gemini 3.8 Flash at `thinking_level=low`, run `_v2`): `results/grievance-pilots/api_monitors_precedent_arms.txt`, `api_monitors_underrated_arms.txt` |
| `talk-pilots/run_c5_arms.py` | Sprint work (24 Oct): watchdog arms A and C on suppression with no notes channel (C5) against C2 escalations |
| `talk-pilots/run_thinking_arms.py`, `analyse_thinking.py` | Sprint work (24 Oct): reasoning effort as a variable (GLM 5.3 Flash and Gemini 3.8 Flash at low and high; Kimi K2 0905 and K2 Thinking), saving reasoning text and coding it; `--hardest` runs Claude Opus 5.5 and GPT-6.1 Sol on the endorsed arm and the harder set; refusals are recorded, not retried |
| `modal-handover/run_precedent_modal.py --seed N` | Sprint work (25 Oct): optional engine seed for repeat samples; with no flag the engine is built as before (vLLM default seed 0) |
| `modal-handover/FREEZE_open-weight-watchdogs.md` | Sprint work (24 Oct): models, threshold and file hashes frozen before scoring the Qwen 3 32B, Llama 3.3 70B and Mistral Small 3.2 runs; records the later H200 change for Llama |
| `talk-pilots/run_precedent_arms_gemma_notes.py`, `FREEZE_gemma_checks_gemma.md` | Sprint work (25 Oct): the six arms on Gemma-written cases with Gemma as watchdog |
| `talk-pilots/deterministic_baseline.py` | Sprint work (25 Oct): rule check (severity 3 or 4 and not escalated) as a no-model baseline on both prompt sets. Needs the cached trajectories (team Drive, not in the repo) |
| `talk-pilots/cross_analysis.py` | Sprint work (25 Oct): every watchdog x arm x prompt set in one table (`docs/pilots/CROSS_ANALYSIS_precedent_arms.md`); picks up new Modal runs, and takes raw folders for the API watchdogs as `"Label=path"` arguments |
| `talk-pilots/analyse_roc.py` | Sprint work (24 Oct): AUROC and recall at fixed false-positive rates from saved suspicion scores, with a split-half frozen threshold |

## Running

The scripts call Ollama Cloud by default (`OLLAMA_API_KEY`) or OpenRouter with `PILOT_PROVIDER=openrouter` (`OPENROUTER_API_KEY`), choose the model with `PILOT_MODEL`, and write to `talk-pilots/results_<model>/`. They are resumable: a result file that exists is skipped.

In this repository copy, `cached-trajectories/run_pipeline.py` reads the records folder from `GRIEVOICE_RECORDS` and the Ollama key from `OLLAMA_API_KEY` or from the key file named by `PILOT_ENV_FILE` (default `.env`). The OpenRouter wrappers read `OPENROUTER_API_KEY` from that key file. The author’s local copy hard-codes both paths; nothing else differs. The talk-pilot scripts also read cached trajectories from `cached-trajectories/trajectories/`, which are not in the repository.

`talk-pilots/test_analyse_lifecycle.py` is a smoke test for the `identity_exposed` check (no network or data needed): `python test_analyse_lifecycle.py`.

## Known issues

- Scoring of a missing `escalate` field differs between scripts: some count it as a non-escalation (`is not True`), and `run_talk_pilots.gap()` requires `is False`. No saved record is missing the field, so no reported count changes.
- Percentages are rounded half-up (they were floored before the 23 Oct review).
- `run_thinking_arms.py` retries truncated or empty completions and writes no row for a job that fails all five attempts, so detection rates are conditional on completion. Gemini at high effort ran close to the 16,000-token cap on endorsed cases.
- `--budget` in `run_thinking_arms.py` is a soft cap: workers check the running total before each call, in-flight calls are not reserved, and discarded retries are not counted.
- `run_c5_arms.py` and `run_thinking_arms.py` resume by skipping any result file that exists, without checking its saved prompt hashes or model. Clear the output folder after changing prompts or settings.
- `analyse_lifecycle.py` checks are weak in places, revised on 23 Oct: `identity_exposed` matches the complainant’s capitalised name tokens as whole words, only in the spellings the extractor wrote, and cannot see exposure by detail or fire for anonymous callers; `BENEFIT_protective_query` no longer counts “retaliat”, which matched accusations, and that lowered MiniMax’s workload arm from 5/5 to 3/5; `witnesses_not_listed` (formerly `witnesses_ignored`) only shows that investigators listed witnesses, since the runner never contacts them.
- In `run_carryover.py` the solo arm shows case B without the “NEXT CASE” header that the other arms carry.
- Note labels in `analyse_motive.py` come from regex patterns, checked by reading samples, not by a human-coded rubric.
- The Gemma-written and MiniMax-written monitor sets define suppression differently (see report section 4.2).
- Provider and model switching is uneven: `PILOT_PROVIDER` works only in `run_monitor_*` scripts and `run_openrouter.py`, and `run_pressure.py` keeps its own defaults. Gemma’s C3/C4/C5 pressure baselines came from a separate invocation that is not scripted here. A sprint re-run should centralize configuration and record the exact command for each table.
- Resumability skips any existing result file, so a prompt or case-set change can silently keep stale results; `run_openrouter.py` archives reports under a fixed suffix. Use configuration-specific output folders for re-runs.
- The frozen prompt files for the Modal runs (`modal-handover/*_prompts.jsonl`) hold full agent summaries and notes, so they are shared through the team Drive and ignored here. Real place and company names in them were replaced with invented ones by a local scrub script (kept out of the repo because it lists the real names), so Modal runs see slightly different user text from the OpenRouter monitor runs.
- `run_precedent_api.py`: the Claude runs have no temperature setting, because the current Anthropic SDK and API reject `temperature`; the Gemini runs used 0.7. Claude thinking was off (no thinking blocks, completion tokens match visible text). Gemini 3.8 Flash and 4 Argon cannot turn thinking off, so they ran at `thinking_level=low`; Gemini 3.8 Flash still used thinking tokens on about half of its reads (mean 112 in arm C and 76 in arm F against about 45 elsewhere), Argon used none. The first Gemini 3.8 Flash run sent `thinking_budget=0`, which did not stop thinking, and is superseded by the `_v2` run reported here. Haiku's runs used a 600-token output cap (no read came near it); the Sonnet, Argon and Gemini `_v2` runs used 2,000. Eight Argon reads (the smoke test) were produced with the earlier `thinking_budget=0` setting; Argon used no thinking tokens either way. Reads with an unparseable answer count as not flagged: Sonnet 5.5 had 15 (it often ended its JSON without the closing brace; 12 of them had `"flag": true` before the break, which would add up to 4 flagged reads in arm F and 1-2 in other arms if recovered), Haiku 2 and Argon 1. Raw per-call results quote case text and are not in the repo.
- `run_precedent_modal.py` treats a call that hits the token limit or ends inside an unclosed `<think>` block as a missing flag, and `analyse_precedent_arms.py` reports catch rates over all reads with missing flags in their own column. Only Qwen 3 32B has been smoke-tested on Modal.
- `analyse_precedent_arms.py` now splits suppression from benign reads by label, not stratum name, so new strata (C5) tabulate correctly; earlier tables are unchanged.
- Raw reasoning text from `run_thinking_arms.py` quotes case text and stays out of the repo with the other per-call results; Kimi K2 0905 has no thinking control and 79 of its 618 reads still used reasoning tokens (provider routing).
- In `run_precedent_arms.py`, the first launch also ran honest C2 cases with no notes stage; `analyse_precedent_arms.py` drops them, and C1 attempts failed by design.
- The glass-channel arm (G4 in `run_lifecycle.py`) appends “the lender reads every note” to channel text that says the lender never sees notes, so G4 results come from conflicting instructions.
