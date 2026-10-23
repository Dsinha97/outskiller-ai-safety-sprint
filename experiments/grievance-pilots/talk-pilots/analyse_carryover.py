"""Summarise the note carry-over replay: escalation on case B by arm, paired by B record."""
import json
import sys
from collections import defaultdict
from pathlib import Path

R = Path(__file__).parent / (sys.argv[1] if len(sys.argv) > 1 else "results_gemma4-31b-cloud") / "carryover"
ARMS = ("solo", "a_none", "a_aim", "a_honest")
esc = defaultdict(lambda: defaultdict(list)); a_esc = defaultdict(list); sev = defaultdict(list); missing = 0
for p in R.glob("*.json"):
    d = json.loads(p.read_text(encoding="utf-8"))
    missing += d["escalate_missing"]
    esc[d["arm"]][d["b"]].append(d["escalate"] is True)
    sev[d["arm"]].append(d["severity"] or 0)
    if d["a_decision"]:
        a_esc[d["arm"]].append(d["a_decision"].get("escalate") is True)
print(f"records with escalate missing: {missing}\n")
print("arm        case B escalated   mean sev B   case A escalated   B records lower than solo")
for arm in ARMS:
    v = esc[arm]; n = sum(len(x) for x in v.values()); e = sum(sum(x) for x in v.values())
    lower = sum(sum(v[b]) / len(v[b]) < sum(esc["solo"][b]) / len(esc["solo"][b]) for b in v if esc["solo"][b])
    a = a_esc[arm]; a_txt = f"{sum(a)}/{len(a)}" if a else "-"
    print(f"{arm:<10} {e:>3}/{n:<3} ({100*e//max(n,1):>2}%)   {sum(sev[arm])/max(len(sev[arm]),1):9.2f}   {a_txt:>12}   {lower:>10}/{len(v)}")
