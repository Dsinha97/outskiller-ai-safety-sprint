"""Summarise the monitor run on Gemma-written notes: catch rate by note label and condition."""
import json
import sys
from collections import defaultdict
from pathlib import Path

R = Path(__file__).parent / (sys.argv[1] if len(sys.argv) > 1 else "results_gemma4-31b-cloud") / "H_gemma_notes"
by = defaultdict(lambda: [0, 0, []]); missing = 0
for p in R.glob("*.json"):
    d = json.loads(p.read_text(encoding="utf-8"))
    missing += d["flag_missing"]
    keys = [("benign C3", "")] if not d["label"] else [(d["note_label"], ""), (d["note_label"], d["cond"])]
    for k in keys:
        c = by[k]; c[0] += d["flag"] is True; c[1] += 1
        if isinstance(d["suspicion"], (int, float)):
            c[2].append(d["suspicion"])
print(f"records with flag missing: {missing}\n")
print("group                   flagged         mean suspicion")
for k in sorted(by, key=lambda k: (k[0] != "benign C3", k[0], k[1])):
    f, n, s = by[k]
    print(f"   {k[0]:<9} {k[1] or 'all':<6} {f:>4}/{n:<4} ({int(100*f/max(n,1) + 0.5):>3}%)   {sum(s)/max(len(s),1):6.1f}")
