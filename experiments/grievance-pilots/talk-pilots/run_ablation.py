"""Sentence ablation of steering notes (run 2026-10-23), after the MIT "Eko" note-erasure test.

For the C4 rep1 cases where Gemma's honest rater kept the case internal with the original summariser
note but escalated with no note (P pilot), replay the same summary to an honest rater with:
  full   the original note
  none   no note
  -i     the note with sentence i deleted (leave-one-out)
Each variant is drawn REPS times. A sentence whose deletion restores escalation carries the steering.
Summary, rater prompt and model are held fixed; only the note text changes.

usage: PILOT_MODEL=gemma4:31b-cloud python run_ablation.py [--smoke]
resumable; <results dir>/ablation/<record>__<variant>__r<k>.json
"""
from __future__ import annotations

import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "cached-trajectories"))
import run_pipeline as rp  # noqa: E402

rp.MODEL = os.environ.get("PILOT_MODEL", "gemma4:31b-cloud")
rp.OUT = HERE / ("results_" + re.sub(r"[^a-z0-9]+", "-", rp.MODEL.lower()).strip("-"))
OUT = rp.OUT / "ablation"
OUT.mkdir(parents=True, exist_ok=True)
TRAJ = HERE.parent / "cached-trajectories" / "trajectories" / "C4"
REPS = int(os.environ.get("ABL_REPS", 5))
WORKERS = int(os.environ.get("PILOT_WORKERS", 6))
SYSTEM = rp.system_for("rater", dict(single=False, channel=True, aim=False))


def sentences(note):
    return [s for s in re.split(r"(?<=[.!?])\s+", note.strip()) if s]


def flips():
    """Records where the honest rater's escalation flipped False -> True when the note was removed."""
    out = []
    for p in sorted((rp.OUT / "P").glob("*_rep1.json")):
        a = json.loads(p.read_text(encoding="utf-8"))["arms"]
        if a["honest_orig"]["escalate"] is False and a["honest_cut"]["escalate"] is True:
            out.append(p.stem)
    return out


def variants(item):
    t = json.loads((TRAJ / f"{item}.json").read_text(encoding="utf-8"))
    summ = t["final"].get("summary") or ""
    ss = sentences(t["steps"][0]["parsed"].get("private_note") or "")
    v = {"full": " ".join(ss), "none": ""}
    for i in range(len(ss)):
        v[f"-{i}"] = " ".join(s for j, s in enumerate(ss) if j != i)
    return summ, ss, v


def job(item, summ, ss, var, note, k):
    path = OUT / f"{item}__{var}__r{k}.json"
    if path.exists():
        return
    user = "CASE SUMMARY\n\n" + summ + (f"\n\nPRIVATE NOTE FROM SUMMARISER\n\n{note}" if note else "")
    r = rp.call(SYSTEM, user)
    p = r["parsed"]
    path.write_text(json.dumps({
        "item": item, "variant": var, "rep": k, "model": rp.MODEL, "endpoint": rp.API, "temperature": rp.TEMP,
        "system_sha": rp.sha(SYSTEM), "user_sha": rp.sha(user),
        "deleted_sentence": ss[int(var[1:])] if var.startswith("-") else None, "note": note,
        **{x: p.get(x) for x in ("severity", "escalate", "category", "rationale")},
        "escalate_missing": "escalate" not in p, "content": r["content"], "seconds": r["seconds"],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    rp.log(f"ABL {item} {var} r{k} sev={p.get('severity')} esc={p.get('escalate')}")


def main():
    items = flips()
    smoke = "--smoke" in sys.argv
    if smoke:
        items = items[:1]
    jobs = []
    for it in items:
        summ, ss, vs = variants(it)
        for var, note in vs.items():
            for k in range(1 if smoke else REPS):
                jobs.append((it, summ, ss, var, note, k))
    print(f"{len(items)} records, {len(jobs)} calls, model {rp.MODEL}", flush=True)

    def safe(a):
        try:
            job(*a)
        except Exception as e:  # noqa: BLE001
            rp.log(f"ABL FAIL {a[0]} {a[3]} r{a[5]} {e}")

    with ThreadPoolExecutor(WORKERS) as ex:
        list(ex.map(safe, jobs))


if __name__ == "__main__":
    main()
