"""Independent monitor on the H pilot's MiniMax-written cases, for a new monitor model (run 2026-10-23).

Same 24 suppression + 24 benign items as run_talk_pilots.h_items() (seed 7), M0_independent prompt only,
REPS draws each, so a new monitor is comparable with the Gemma and MiniMax monitors on the same cases.
Pair with run_monitor_gemma_notes.py for the Gemma-written set.

usage: PILOT_MODEL=glm-5.3-flash python run_monitor_minimax_notes.py [--smoke]
resumable; <results dir>/H_minimax_notes/<item>__r<k>.json
"""
from __future__ import annotations

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import run_talk_pilots as tp

rp = tp.rp
if os.environ.get("PILOT_PROVIDER") == "openrouter":  # same model id scheme as run_openrouter.py
    rp.API = "https://openrouter.ai/api/v1/chat/completions"
    rp.KEY = next(l.split("=", 1)[1].strip().strip('"').strip("'")
                  for l in rp.ENV.read_text(encoding="utf-8-sig").splitlines()
                  if l.strip().startswith("OPENROUTER_API_KEY="))
OUT = rp.OUT / "H_minimax_notes"
OUT.mkdir(parents=True, exist_ok=True)
REPS = int(os.environ.get("MON_REPS", 3))
WORKERS = int(os.environ.get("PILOT_WORKERS", 6))
SYSTEM = "\n\n".join((tp.MON_BASE, tp.MON_FMT))


def job(t, label, k):
    tid = f"{t['condition']}_{t['record']}_rep{t['rep']}"
    path = OUT / f"{tid}__r{k}.json"
    if path.exists():
        return
    u = tp.h_user(t)
    p = rp.call(SYSTEM, u)
    x = p["parsed"]
    path.write_text(json.dumps({
        "item": tid, "rep": k, "label": label, "model": rp.MODEL, "endpoint": rp.API, "temperature": rp.TEMP,
        "system_sha": rp.sha(SYSTEM), "user_sha": rp.sha(u),
        "flag": x.get("flag"), "suspicion": x.get("suspicion"), "reason": x.get("reason"),
        "flag_missing": "flag" not in x, "content": p["content"],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    rp.log(f"HM {tid} r{k} label={label} flag={x.get('flag')} s={x.get('suspicion')}")


def main():
    its = tp.h_items()
    smoke = "--smoke" in sys.argv
    if smoke:
        its = its[:1] + its[-1:]
    jobs = [(t, lab, k) for t, lab in its for k in range(1 if smoke else REPS)]
    print(f"{len(its)} items, {len(jobs)} calls, model {rp.MODEL}", flush=True)

    def safe(j):
        try:
            job(*j)
        except Exception as e:  # noqa: BLE001
            rp.log(f"HM FAIL {j[0]['record']} r{j[2]} {e}")

    with ThreadPoolExecutor(WORKERS) as ex:
        list(ex.map(safe, jobs))


if __name__ == "__main__":
    main()
