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
| `modal-handover/run_precedent_api.py` | Sprint work (24 Oct): runs the same frozen prompts on API monitors (Claude Haiku 5.5 and Sonnet 5.5, Gemini 3.8 Flash and 4 Argon) from Modal, reading the keys from Modal secrets; has a spend cap. Results so far (Haiku 5.5, Gemini 3.8 Flash): `results/grievance-pilots/api_monitors_precedent_arms.txt`, `api_monitors_underrated_arms.txt` |

## Running

The scripts call Ollama Cloud by default (`OLLAMA_API_KEY`) or OpenRouter with `PILOT_PROVIDER=openrouter` (`OPENROUTER_API_KEY`), choose the model with `PILOT_MODEL`, and write to `talk-pilots/results_<model>/`. They are resumable: a result file that exists is skipped.

In this repository copy, `cached-trajectories/run_pipeline.py` reads the records folder from `GRIEVOICE_RECORDS` and the Ollama key from `OLLAMA_API_KEY` or from the key file named by `PILOT_ENV_FILE` (default `.env`). The OpenRouter wrappers read `OPENROUTER_API_KEY` from that key file. The author’s local copy hard-codes both paths; nothing else differs. The talk-pilot scripts also read cached trajectories from `cached-trajectories/trajectories/`, which are not in the repository.

`talk-pilots/test_analyse_lifecycle.py` is a smoke test for the `identity_exposed` check (no network or data needed): `python test_analyse_lifecycle.py`.

## Known issues

- Scoring of a missing `escalate` field differs between scripts: some count it as a non-escalation (`is not True`), and `run_talk_pilots.gap()` requires `is False`. No saved record is missing the field, so no reported count changes.
- Percentages are rounded half-up (they were floored before the 23 Oct review).
- `analyse_lifecycle.py` checks are weak in places, revised on 23 Oct: `identity_exposed` matches the complainant’s capitalised name tokens as whole words, only in the spellings the extractor wrote, and cannot see exposure by detail or fire for anonymous callers; `BENEFIT_protective_query` no longer counts “retaliat”, which matched accusations, and that lowered MiniMax’s workload arm from 5/5 to 3/5; `witnesses_not_listed` (formerly `witnesses_ignored`) only shows that investigators listed witnesses, since the runner never contacts them.
- In `run_carryover.py` the solo arm shows case B without the “NEXT CASE” header that the other arms carry.
- Note labels in `analyse_motive.py` come from regex patterns, checked by reading samples, not by a human-coded rubric.
- The Gemma-written and MiniMax-written monitor sets define suppression differently (see report section 4.2).
- Provider and model switching is uneven: `PILOT_PROVIDER` works only in `run_monitor_*` scripts and `run_openrouter.py`, and `run_pressure.py` keeps its own defaults. Gemma’s C3/C4/C5 pressure baselines came from a separate invocation that is not scripted here. A sprint re-run should centralize configuration and record the exact command for each table.
- Resumability skips any existing result file, so a prompt or case-set change can silently keep stale results; `run_openrouter.py` archives reports under a fixed suffix. Use configuration-specific output folders for re-runs.
- The frozen prompt files for the Modal runs (`modal-handover/*_prompts.jsonl`) hold full agent summaries and notes, so they are shared through the team Drive and ignored here. Real place and company names in them were replaced with invented ones by a local scrub script (kept out of the repo because it lists the real names), so Modal runs see slightly different user text from the OpenRouter monitor runs.
- `run_precedent_api.py`: the Claude runs have no temperature setting, because the current Anthropic SDK and API reject `temperature`; the Gemini runs used 0.7. Claude thinking was off (verified: no thinking blocks, completion tokens match visible text). Gemini 3.8 Flash and 4 Argon cannot turn thinking off, and the first Gemini 3.8 Flash runs sent `thinking_budget=0`, which did not stop it (it thought most in arms C and F), so those results are superseded by a re-run at `thinking_level=low` and 2,000 tokens (see the results note). Two Haiku reads with malformed JSON were kept as missing flags. Raw per-call results quote case text and are not in the repo.
- `run_precedent_modal.py` treats a call that hits the token limit or ends inside an unclosed `<think>` block as a missing flag, and `analyse_precedent_arms.py` reports catch rates over all reads with missing flags in their own column. Only Qwen 3 32B has been smoke-tested on Modal.
- In `run_precedent_arms.py`, the first launch also ran honest C2 cases with no notes stage; `analyse_precedent_arms.py` drops them, and C1 attempts failed by design.
- The glass-channel arm (G4 in `run_lifecycle.py`) appends “the lender reads every note” to channel text that says the lender never sees notes, so G4 results come from conflicting instructions.
