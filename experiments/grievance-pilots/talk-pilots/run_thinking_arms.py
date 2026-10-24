"""Thinking level as a variable: arms A, C, F at low vs high reasoning effort, saving the reasoning text (sprint work, 2026-10-24).

Same items, policy and arm texts as run_precedent_arms.py (easy set) and run_underrated_arms.py (harder set), two draws.
Reasoning effort is set through OpenRouter's `reasoning.effort`; the reasoning text and token counts are saved with
every read so the thinking can be coded afterwards (analyse_thinking.py).

usage: PILOT_MODEL=z-ai/glm-5.3-flash python run_thinking_arms.py --effort low|high|default [--smoke] [--hardest] [--budget 3]
resumable; results_<model>/thinking_<effort>/<set>/<arm>__<item>__r<k>.json
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import run_precedent_arms as pa
import run_underrated_arms as ua

tp, rp = pa.tp, pa.rp
API = "https://openrouter.ai/api/v1/chat/completions"
KEY = next(l.split("=", 1)[1].strip().strip('"').strip("'")
           for l in rp.ENV.read_text(encoding="utf-8-sig").splitlines() if l.strip().startswith("OPENROUTER_API_KEY="))
REPS = int(os.environ.get("MON_REPS", 2))
WORKERS = int(os.environ.get("PILOT_WORKERS", 6))
ARMS = ("A_policy_only", "C_unsafe_accepted", "F_unsafe_accepted_policy")
SETS = {"precedent": (pa.items, tp.h_user), "underrated": (ua.items, ua.user)}


def call(system, user, effort):
    payload = {"model": rp.MODEL, "temperature": rp.TEMP, "max_tokens": 16000, "include_reasoning": True,
               "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if effort != "default":  # "default": send no effort setting (models without a thinking control, e.g. Kimi K2)
        payload["reasoning"] = {"effort": effort}
    last = None
    for attempt in range(5):
        req = urllib.request.Request(API, data=json.dumps(payload).encode("utf-8"),
                                     headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                d = json.loads(r.read().decode("utf-8"))
            ch = d["choices"][0]; msg = ch.get("message") or {}
            content = (msg.get("content") or "").strip()
            if ch.get("finish_reason") == "content_filter":  # a provider-side refusal: record it, don't retry
                return {"content": "", "parsed": {}, "reasoning": msg.get("reasoning") or "",
                        "finish": "content_filter", "usage": d.get("usage")}
            if ch.get("finish_reason") != "stop" or not content:
                raise RuntimeError(f"finish={ch.get('finish_reason')} len={len(content)}")
            return {"content": content, "parsed": rp.parse_json(content) or {}, "reasoning": msg.get("reasoning") or "",
                    "finish": ch.get("finish_reason"), "usage": d.get("usage")}
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:200]}"
        except Exception as e:  # noqa: BLE001
            last = str(e)[:300]
        time.sleep(min(10 * 2 ** attempt + random.random() * 5, 90))
    raise RuntimeError("GIVEUP " + str(last))


SPENT = [0.0]
BUDGET = [float("inf")]


def job(st, effort, arm, t, label, stratum, k, user_fn):
    if SPENT[0] >= BUDGET[0]:
        return
    tid = f"{t['condition']}_{t['record']}_rep{t['rep']}"
    out = rp.OUT / f"thinking_{effort}" / st
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{arm}__{tid}__r{k}.json"
    if path.exists():
        return
    system = "\n\n".join((tp.MON_BASE, pa.POLICY, pa.ARMS[arm], tp.MON_FMT))
    u = user_fn(t)
    p = call(system, u, effort)
    x = p["parsed"]
    usage = p.get("usage") or {}
    SPENT[0] += usage.get("cost") or 0
    path.write_text(json.dumps({
        "set": st, "effort": effort, "arm": arm, "item": tid, "record": t["record"], "rep": k, "label": label,
        "stratum": stratum, "model": rp.MODEL, "endpoint": API, "temperature": rp.TEMP,
        "system_sha": rp.sha(system), "user_sha": rp.sha(u),
        "flag": x.get("flag"), "suspicion": x.get("suspicion"), "reason": x.get("reason"),
        "flag_missing": "flag" not in x, "finish": p["finish"],
        "reasoning_tokens": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens"),
        "usage": usage, "reasoning": p["reasoning"], "content": p["content"],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    rp.log(f"TH {effort} {st} {arm} {tid} r{k} flag={x.get('flag')} rt={(usage.get('completion_tokens_details') or {}).get('reasoning_tokens')}")


def main():
    effort = sys.argv[sys.argv.index("--effort") + 1]
    smoke = "--smoke" in sys.argv
    hardest = "--hardest" in sys.argv  # harder set (A, C, F) plus the endorsed arm C of the easy set
    if "--budget" in sys.argv:
        BUDGET[0] = float(sys.argv[sys.argv.index("--budget") + 1])
    jobs = []
    for st, (items_fn, user_fn) in SETS.items():
        its = items_fn()
        if st == "precedent":
            its = [x for x in its if x[0]["condition"] in ("C3", "C4", "C6")]
        if smoke:
            its = [its[0], its[-1]]
        arms = ("C_unsafe_accepted",) if hardest and st == "precedent" else ARMS
        jobs += [(st, effort, a, t, lab, s, k, user_fn) for a in arms for t, lab, s in its
                 for k in range(1 if smoke else REPS)]
    print(f"{len(jobs)} calls, model {rp.MODEL}, effort {effort}, budget {BUDGET[0]}", flush=True)

    def safe(j):
        try:
            job(*j)
        except Exception as e:  # noqa: BLE001
            rp.log(f"TH FAIL {j[1]} {j[0]} {j[2]} {j[3]['record']} r{j[6]} {e}")

    with ThreadPoolExecutor(WORKERS) as ex:
        list(ex.map(safe, jobs))
    print(f"spent ${SPENT[0]:.3f}", flush=True)


if __name__ == "__main__":
    main()
