"""Summarise the sentence-ablation replay: escalation rate per note variant, per record."""
import json
import sys
from collections import defaultdict
from pathlib import Path

R = Path(__file__).parent / (sys.argv[1] if len(sys.argv) > 1 else "results_gemma4-31b-cloud") / "ablation"
cells = defaultdict(lambda: defaultdict(list)); sent = {}; missing = 0
for p in R.glob("*.json"):
    d = json.loads(p.read_text(encoding="utf-8"))
    missing += d["escalate_missing"]
    cells[d["item"]][d["variant"]].append(d["escalate"] is True)
    if d["deleted_sentence"]:
        sent[(d["item"], d["variant"])] = d["deleted_sentence"]
print(f"records with escalate missing: {missing}\n")
for it in sorted(cells):
    v = cells[it]; r = lambda k: f"{sum(v[k])}/{len(v[k])}"
    print(f"{it}   full note {r('full')}   no note {r('none')}")
    for k in sorted((k for k in v if k.startswith("-")), key=lambda k: int(k[1:])):
        print(f"   drop s{k[1:]}  {r(k):>4}   {sent.get((it, k), '')[:150]}")
    print()
