"""Freeze the monitor-arm prompts into JSONL files for the Modal runs (sprint work, 2026-10-24).

Writes ../modal-handover/precedent_prompts.jsonl (run_precedent_arms.py) and underrated_prompts.jsonl
(run_underrated_arms.py): one row per (arm, item) with the exact system and user text the OpenRouter
runs send, so Modal runs on open-weight monitors use byte-identical prompts without the cached trajectories.
usage: python export_precedent_prompts.py
"""
from __future__ import annotations

import json
from pathlib import Path

import run_precedent_arms as pa
import run_underrated_arms as ua

tp, rp = pa.tp, pa.rp
HAND = Path(__file__).parent.parent / "modal-handover"


def export(name, arms, items, user):
    out = HAND / f"{name}_prompts.jsonl"
    n = 0
    with out.open("w", encoding="utf-8") as f:
        for arm, text in arms.items():
            system = "\n\n".join((tp.MON_BASE, pa.POLICY, text, tp.MON_FMT))
            for t, label, stratum in items:
                u = user(t)
                f.write(json.dumps({
                    "arm": arm, "item": f"{t['condition']}_{t['record']}_rep{t['rep']}", "record": t["record"],
                    "label": label, "stratum": stratum, "system": system, "user": u,
                    "system_sha": rp.sha(system), "user_sha": rp.sha(u)}, ensure_ascii=False) + "\n")
                n += 1
    print(f"{n} prompts -> {out}")


def main():
    HAND.mkdir(exist_ok=True)
    export("precedent", pa.ARMS, pa.items(), tp.h_user)
    export("underrated", ua.ARMS, ua.items(), ua.user)


if __name__ == "__main__":
    main()
