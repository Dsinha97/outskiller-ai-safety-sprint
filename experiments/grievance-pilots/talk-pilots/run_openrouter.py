"""Finish the MiniMax talk pilots through OpenRouter (Ollama's free MiniMax access ended 22 Oct 23:59 UTC).

Same model (minimax/minimax-m3.1-flash), prompts and temperature; only the endpoint changes. Every
job is resumable, so this only fills what is missing in results/. Calls made here are logged with
"[openrouter]" so the endpoint switch stays traceable.
usage: python run_openrouter.py [--smoke] [workers]
"""
import random
import sys
from concurrent.futures import ThreadPoolExecutor

import run_lifecycle as lc
import run_pressure as pr
import run_talk_pilots as tp

rp = lc.rp
rp.API = "https://openrouter.ai/api/v1/chat/completions"
rp.MODEL = "minimax/minimax-m3.1-flash"
rp.KEY = next(l.split("=", 1)[1].strip().strip('"').strip("'")
              for l in rp.ENV.read_text(encoding="utf-8-sig").splitlines()
              if l.strip().startswith("OPENROUTER_API_KEY="))
_log = rp.log
rp.log = lambda m: _log("[openrouter] " + m)

if "--smoke" in sys.argv:
    r = rp.call('Reply with JSON only: {"answer": "..."}', "What is 2+2?")
    print(r["parsed"], r["usage"], r["seconds"], "s")
    sys.exit()

WORKERS = int(next((a for a in sys.argv[1:] if a.isdigit()), 6))


def guard(f, *a):
    try:
        f(*a)
    except Exception as e:  # noqa: BLE001
        rp.log(f"FAIL {f.__module__}.{f.__name__} {e}")


recs = sorted(p.stem.split("_")[0] for p in (lc.HERE.parent / "cached-trajectories/trajectories/C4").glob("*_rep1.json"))
random.seed(12)
jobs = ([(lc.run, r, c) for r in sorted(random.sample(recs, 12)) for c in lc.CONDS]
        + [(pr.run, r, c) for r in recs for c in pr.CONDS]
        + [(tp.p_job, t) for t in tp.load("C4") if t["rep"] == 1]
        + [(tp.h_job, t, lab, pos) for t, lab in tp.h_items() for pos in tp.POSITION])
with ThreadPoolExecutor(WORKERS) as ex:
    list(ex.map(lambda j: guard(*j), jobs))
for p in (lc.OUT).glob("_report_*.json"):  # reports were written from partial logs; redo on the full set
    p.rename(p.with_name(p.stem + "_partial35.json"))
for c in lc.CONDS:
    guard(lc.report, c)
