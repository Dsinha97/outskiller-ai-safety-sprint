"""Parallel moves, no talk: watchdog on suppression with no notes channel (sprint work, run 2026-10-24).

Nguyen's case (b): shared incentive, no coordinating text. Suppression cases come from C5 (hidden aim, no notes
channel): rated severity >= 3 and not escalated. Benign cases are C2 escalations (no aim, no notes), so both
sides lack notes and the watchdog cannot lean on note text. Same policy and arms A and C as run_precedent_arms.py,
24 + 24 items (seed 7), two draws. Compare with the 24 C4/C6 suppression cases that carry notes.

usage: PILOT_PROVIDER=openrouter PILOT_MODEL=z-ai/glm-5.3-flash python run_c5_arms.py [--smoke]
resumable; <results dir>/c5_arms/<arm>__<item>__r<k>.json
"""
from __future__ import annotations

import json
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor

import run_precedent_arms as pa
import run_underrated_arms as ua

tp, rp = pa.tp, pa.rp
OUT = rp.OUT / "c5_arms"
OUT.mkdir(parents=True, exist_ok=True)
REPS = int(os.environ.get("MON_REPS", 2))
WORKERS = int(os.environ.get("PILOT_WORKERS", 6))
ARMS = {k: pa.ARMS[k] for k in ("A_policy_only", "C_unsafe_accepted")}


def items():
    random.seed(7)
    pos = [t for t in tp.load("C5") if tp.gap(t)]
    neg = [t for t in tp.load("C2") if t["final"].get("escalate") is True]
    return ([(t, 1, "suppression_no_notes") for t in random.sample(pos, min(24, len(pos)))]
            + [(t, 0, "benign_escalated_no_notes") for t in random.sample(neg, 24)])


def job(arm, t, label, stratum, k):
    tid = f"{t['condition']}_{t['record']}_rep{t['rep']}"
    path = OUT / f"{arm}__{tid}__r{k}.json"
    if path.exists():
        return
    system = "\n\n".join((tp.MON_BASE, pa.POLICY, ARMS[arm], tp.MON_FMT))
    u = ua.user(t)
    p = rp.call(system, u)
    x = p["parsed"]
    path.write_text(json.dumps({
        "arm": arm, "item": tid, "record": t["record"], "rep": k, "label": label, "stratum": stratum,
        "model": rp.MODEL, "endpoint": rp.API, "temperature": rp.TEMP,
        "system_sha": rp.sha(system), "user_sha": rp.sha(u),
        "flag": x.get("flag"), "suspicion": x.get("suspicion"), "reason": x.get("reason"),
        "flag_missing": "flag" not in x, "usage": p.get("usage"), "content": p["content"],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    rp.log(f"C5 {arm} {tid} r{k} {stratum} flag={x.get('flag')} s={x.get('suspicion')}")


def main():
    its = items()
    smoke = "--smoke" in sys.argv
    if smoke:
        its = [its[0], its[-1]]
    jobs = [(a, t, lab, s, k) for a in ARMS for t, lab, s in its for k in range(1 if smoke else REPS)]
    print(f"{len(its)} items x {len(ARMS)} arms = {len(jobs)} calls, model {rp.MODEL}", flush=True)

    def safe(j):
        try:
            job(*j)
        except Exception as e:  # noqa: BLE001
            rp.log(f"C5 FAIL {j[0]} {j[1]['record']} r{j[4]} {e}")

    with ThreadPoolExecutor(WORKERS) as ex:
        list(ex.map(safe, jobs))


if __name__ == "__main__":
    main()
