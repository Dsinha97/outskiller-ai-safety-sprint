"""Run every talk pilot through one shared pool so the free tier's concurrency cap is respected.

Priority order: lifecycle slice, pressure, paraphrase (P), captured monitor (H). All jobs are
resumable, so this also retries anything that failed earlier.
usage: python run_all.py
"""
import random
import sys
from concurrent.futures import ThreadPoolExecutor

import run_lifecycle as lc
import run_pressure as pr
import run_talk_pilots as tp

WORKERS = int(sys.argv[1]) if len(sys.argv) > 1 else 4


def guard(f, *a):
    try:
        f(*a)
    except Exception as e:  # noqa: BLE001
        lc.rp.log(f"FAIL {f.__module__}.{f.__name__} {a[1:] if f is tp.h_job else a} {e}")


recs = sorted(p.stem.split("_")[0] for p in (lc.HERE.parent / "cached-trajectories/trajectories/C4").glob("*_rep1.json"))
random.seed(12)
life = [(lc.run, r, c) for r in sorted(random.sample(recs, 12)) for c in lc.CONDS]
press = [(pr.run, r, c) for r in recs for c in pr.CONDS]
para = [(tp.p_job, t) for t in tp.load("C4") if t["rep"] == 1]
mon = [(tp.h_job, t, lab, pos) for t, lab in tp.h_items() for pos in tp.POSITION]
jobs = life + press + para + mon

with ThreadPoolExecutor(WORKERS) as ex:  # executor takes jobs in list order, so priority holds
    list(ex.map(lambda j: guard(*j), jobs))
for c in lc.CONDS:
    guard(lc.report, c)
