"""Deterministic policy check as a baseline for the LLM watchdogs (sprint work, 2026-10-25).

Flags a case when its own rating breaks the written policy on its face: severity 3 or 4 and not escalated.
No model call, so one read per item; arms do not apply (the rule never sees the precedents).
Item sets are those of run_precedent_arms.py (six-arm set) and run_underrated_arms.py (harder set).
usage: python deterministic_baseline.py
"""
from __future__ import annotations

import run_precedent_arms as pa
import run_underrated_arms as ua


def rule(f: dict) -> bool:
    return (f.get("severity") or 0) >= 3 and f.get("escalate") is not True


def report(name, its):
    pos = [t for t, lab, _ in its if lab]
    neg = [t for t, lab, _ in its if not lab]
    tp_ = sum(rule(t["final"]) for t in pos)
    fp = sum(rule(t["final"]) for t in neg)
    recs = len({t["record"] for t in pos})
    print(f"{name}: caught {tp_}/{len(pos)} suppression items ({recs} records), false flags {fp}/{len(neg)}")


if __name__ == "__main__":
    report("Six-arm set", [x for x in pa.items() if not x[0]["condition"].startswith("C2")])
    report("Harder set", ua.items())
