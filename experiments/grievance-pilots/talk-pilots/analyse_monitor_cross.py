"""Compare independent monitors across models on the MiniMax-written and Gemma-written case sets."""
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
print("monitor                                   set        caught suppression   false flags   missing")
for d in sorted(HERE.glob("results*")):
    for s in ("H_minimax_notes", "H_gemma_notes"):
        fs = list((d / s).glob("*.json"))
        if not fs:
            continue
        c = defaultdict(lambda: [0, 0]); miss = 0; by = defaultdict(lambda: [0, 0])
        for p in fs:
            x = json.loads(p.read_text(encoding="utf-8"))
            miss += x["flag_missing"]
            k = c[x["label"]]; k[0] += x["flag"] is True; k[1] += 1
            if x["label"] and x.get("note_label"):
                b = by[x["note_label"]]; b[0] += x["flag"] is True; b[1] += 1
        tp, fp = c[1], c[0]
        extra = "   " + "  ".join(f"{k} {v[0]}/{v[1]}" for k, v in sorted(by.items())) if by else ""
        print(f"{d.name[8:] or 'minimax':<41} {s[2:-6]:<10} {tp[0]:>4}/{tp[1]:<4} ({100*tp[0]//max(tp[1],1):>3}%)"
              f"   {fp[0]:>3}/{fp[1]:<4}   {miss:>4}{extra}")
