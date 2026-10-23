# Grievance-pipeline pilots

Code for the pilots written up in `docs/pilots/TECHNICAL_REPORT_talk-pilots.md`. Summary tables from the analysis scripts are in `results/grievance-pilots/`. Raw JSON results and the GrieVoice v2 records stay local (see below), so the runners will not work from this repository alone.

## Prior work and sprint work

The sprint runs 23–25 October 2026. Preexisting means written or run before the end of 22 October UTC (02:00 on 23 October SAST, when MiniMax’s free allowance for the pre-sprint runs expired). Times are SAST (UTC+2).

| File | Status |
|---|---|
| `cached-trajectories/run_pipeline.py` | Preexisting (20–22 Oct) |
| `talk-pilots/run_pressure.py`, `run_all.py` | Preexisting (22 Oct) |
| `talk-pilots/run_talk_pilots.py`, `analyse.py` | Preexisting, modified on 23 Oct: model switch for cross-family reruns. `analyse.py` also fixed on 23 Oct to read each model’s own C3/C4/C5 pressure baselines (it had read the cached MiniMax runs for every model) |
| `talk-pilots/run_lifecycle.py`, `analyse_lifecycle.py` | Preexisting, modified on 23 Oct: critical complainant and single-stage aim arms |
| `talk-pilots/run_openrouter.py` | Sprint work (23 Oct) |
| `talk-pilots/run_ablation.py`, `analyse_ablation.py` | Sprint work (23 Oct): sentence ablation of steering notes |
| `talk-pilots/run_carryover.py`, `analyse_carryover.py` | Sprint work (23 Oct): does a note change the next case |
| `talk-pilots/analyse_motive.py` | Sprint work (23 Oct): regex labels for note style (motive, verdict, neither) |
| `talk-pilots/run_monitor_gemma_notes.py`, `run_monitor_minimax_notes.py`, `analyse_monitor_gemma_notes.py`, `analyse_monitor_cross.py` | Sprint work (23 Oct): independent monitor across model families |

## Running

The scripts call Ollama Cloud by default (`OLLAMA_API_KEY`) or OpenRouter with `PILOT_PROVIDER=openrouter` (`OPENROUTER_API_KEY`), choose the model with `PILOT_MODEL`, and write to `talk-pilots/results_<model>/`. They are resumable: a result file that exists is skipped.

In this repository copy, `cached-trajectories/run_pipeline.py` reads the records folder from `GRIEVOICE_RECORDS` and the Ollama key from `OLLAMA_API_KEY` or from the key file named by `PILOT_ENV_FILE` (default `.env`). The OpenRouter wrappers read `OPENROUTER_API_KEY` from that key file. The author’s local copy hard-codes both paths; nothing else differs. The talk-pilot scripts also read cached trajectories from `cached-trajectories/trajectories/`, which are not in the repository.

## Known issues

- Scoring of a missing `escalate` field differs between scripts: some count it as a non-escalation (`is not True`), and `run_talk_pilots.gap()` requires `is False`. No saved record is missing the field, so no reported count changes.
- Note labels in `analyse_motive.py` come from regex patterns, checked by reading samples, not by a human-coded rubric.
- The Gemma-written and MiniMax-written monitor sets define suppression differently (see report section 4.2).
- Provider and model switching is uneven: `PILOT_PROVIDER` works only in `run_monitor_*` scripts and `run_openrouter.py`, and `run_pressure.py` keeps its own defaults. Gemma’s C3/C4/C5 pressure baselines came from a separate invocation that is not scripted here. A sprint re-run should centralize configuration and record the exact command for each table.
- Resumability skips any existing result file, so a prompt or case-set change can silently keep stale results; `run_openrouter.py` archives reports under a fixed suffix. Use configuration-specific output folders for re-runs.
- The glass-channel arm (G4 in `run_lifecycle.py`) appends “the lender reads every note” to channel text that says the lender never sees notes, so G4 results come from conflicting instructions.
