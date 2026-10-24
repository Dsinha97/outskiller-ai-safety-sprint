"""Gemma checks Gemma: the six precedent arms on Gemma-written cases (sprint work, run 2026-10-25).

run_precedent_arms.py tests the watchdog on MiniMax-written suppression. Here the same six arms
(same POLICY, same ARMS text, same MON_BASE / MON_FMT) read Gemma's own pressure-pipeline cases,
with the items of run_monitor_gemma_notes.py:
  Positives: Gemma C4/Q2c/Q3c cases kept internal whose record Gemma's honest pipeline (C3) escalated
             at severity >= 3.
  Negatives: Gemma C3 cases escalated at severity >= 3.
Watchdog: google/gemma-4-31b-it on OpenRouter, as in the MiniMax-sender run. Two draws per item.

usage: PILOT_PROVIDER=openrouter PILOT_MODEL=google/gemma-4-31b-it python run_precedent_arms_gemma_notes.py [--smoke]
resumable; <results dir>/precedent_arms_gemma_notes/<arm>__<cond>_<record>__r<k>.json
"""
from __future__ import annotations

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import run_monitor_gemma_notes as hg
import run_precedent_arms as pa

rp = pa.rp
tp = pa.tp
OUT = rp.OUT / "precedent_arms_gemma_notes"
OUT.mkdir(parents=True, exist_ok=True)
REPS = int(os.environ.get("MON_REPS", 2))
WORKERS = int(os.environ.get("PILOT_WORKERS", 6))


def job(arm, c, r, d, lab, k):
    path = OUT / f"{arm}__{c}_{r}__r{k}.json"
    if path.exists():
        return
    system = "\n\n".join((tp.MON_BASE, pa.POLICY, pa.ARMS[arm], tp.MON_FMT))
    u = hg.user(d)
    res = rp.call(system, u)
    p = res["parsed"]
    path.write_text(json.dumps({
        "arm": arm, "cond": c, "record": r, "rep": k, "label": lab,
        "stratum": "suppression" if lab else "benign_escalated",
        "model": rp.MODEL, "endpoint": rp.API, "temperature": rp.TEMP,
        "system_sha": rp.sha(system), "user_sha": rp.sha(u),
        "flag": p.get("flag"), "suspicion": p.get("suspicion"), "reason": p.get("reason"),
        "flag_missing": "flag" not in p, "usage": res.get("usage"), "content": res["content"],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    rp.log(f"PG {arm} {c}_{r} r{k} label={lab} flag={p.get('flag')} s={p.get('suspicion')}")


def main():
    its = hg.items()
    smoke = "--smoke" in sys.argv
    if smoke:
        its = [x for x in its if x[3] == 0][:1] + [x for x in its if x[3] == 1][:1]
    jobs = [(a, *x, k) for a in pa.ARMS for x in its for k in range(1 if smoke else REPS)]
    print(f"{sum(x[3] for x in its)} positives, {sum(1 - x[3] for x in its)} negatives, "
          f"{len(jobs)} calls, model {rp.MODEL}", flush=True)

    def safe(j):
        try:
            job(*j)
        except Exception as e:  # noqa: BLE001
            rp.log(f"PG FAIL {j[0]} {j[1]}_{j[2]} r{j[5]} {e}")

    with ThreadPoolExecutor(WORKERS) as ex:
        list(ex.map(safe, jobs))


if __name__ == "__main__":
    main()
