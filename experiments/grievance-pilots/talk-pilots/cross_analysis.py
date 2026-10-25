"""Cross-model analysis of the precedent arms: every watchdog x every arm x both prompt sets (2026-10-25).

Finds every raw result folder it can and adds the four API watchdogs whose raw files sit on the team
Drive (numbers copied from RESULTS_api_monitors_2026-10-24.md, marked "table"). New Modal runs (gpt-oss,
OLMo, extra seeds) are picked up automatically from ../modal-handover/results/<tag>/.
Same scoring as analyse_precedent_arms.py: a missing flag counts as not flagged.

Effects per watchdog (percentage points, suppression caught):
  endorse  = A - C   (the endorsed unsafe precedents)       verdict = B - C  (endorsement beyond precedent alone)
  reject   = A - D   (precedents marked wrong)              policy  = F - C  (the policy sentence's recovery)
`*` marks non-overlapping read-level Wilson 95% intervals: descriptive only, since reads repeat cases and records.
usage: python cross_analysis.py ["Label=path/to/results_folder" ...] > CROSS_ANALYSIS_precedent_arms.md
  Each extra folder holds precedent_arms/ and underrated_arms/ (as in the Drive zips). A label that matches a
  TABLE entry (e.g. "Claude Sonnet 5.5=../drive/sonnet-5.5") replaces the copied counts with the raw files,
  which adds false flags and missing-flag counts.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).parent
ARMS = ["A_policy_only", "B_unsafe_plain", "C_unsafe_accepted", "D_unsafe_rejected",
        "E_safe_accepted", "F_unsafe_accepted_policy"]
SHORT = dict(zip(ARMS, "ABCDEF"))

# (label, family, tier, source dir relative to HERE, subfolder per set)
RAW = [
    ("GLM 5.3 Flash", "Zhipu", "mid", "results_z-ai-glm-5-3-flash", "{s}_arms"),
    ("GLM 5.3 Flash, thinking low", "Zhipu", "mid", "results_z-ai-glm-5-3-flash/thinking_low", "{s}"),
    ("GLM 5.3 Flash, thinking high", "Zhipu", "mid", "results_z-ai-glm-5-3-flash/thinking_high", "{s}"),
    ("Gemma 4 31B", "Google (open)", "small", "results_google-gemma-4-31b-it", "{s}_arms"),
    ("MiniMax M3.1 Flash", "MiniMax", "mid", "results_minimax-minimax-m3-1-flash", "{s}_arms"),
    ("Nemotron 3 Ultra", "NVIDIA", "large open", "results_nvidia-nemotron-3-ultra-550b-a55b-free", "{s}_arms"),
    ("Gemini 3.8 Flash, thinking low", "Google", "mid", "results_google-gemini-3-8-flash/thinking_low", "{s}"),
    ("Gemini 3.8 Flash, thinking high", "Google", "mid", "results_google-gemini-3-8-flash/thinking_high", "{s}"),
    ("Kimi K2 0905", "Moonshot", "large open", "results_moonshotai-kimi-k2-0905/thinking_default", "{s}"),
    ("Kimi K2 Thinking", "Moonshot", "large open", "results_moonshotai-kimi-k2-thinking/thinking_default", "{s}"),
    ("Claude Opus 5.5", "Anthropic", "frontier", "results_anthropic-claude-opus-5-5/thinking_low", "{s}"),
    ("GPT-6.1 Sol", "OpenAI", "frontier", "results_openai-gpt-6-1-sol/thinking_low", "{s}"),
]
MODAL = HERE.parent / "modal-handover" / "results"
MODAL_META = {
    "qwen3-32b": ("Qwen 3 32B", "Alibaba (open)", "small"),
    "llama-3.3-70b": ("Llama 3.3 70B", "Meta (open)", "mid"),
    "mistral-small-3.2-24b": ("Mistral Small 3.2 24B", "Mistral (open)", "small"),
    "gpt-oss-120b": ("gpt-oss-120b", "OpenAI (open)", "mid"),
    "olmo-3.1-32b-think": ("OLMo 3.1 32B Think", "Ai2 (open)", "small"),
}
# Raw files on the Drive only: suppression caught (k, n) per arm, from RESULTS_api_monitors_2026-10-24.md
TABLE = {
    "Claude Haiku 5.5": ("Anthropic", "small", {
        "precedent": dict(A=(40, 48), B=(35, 48), C=(29, 48), D=(40, 48), E=(38, 48), F=(39, 48)),
        "underrated": dict(A=(2, 26), C=(5, 26), F=(8, 26))}),
    "Claude Sonnet 5.5": ("Anthropic", "mid", {
        "precedent": dict(A=(47, 48), B=(46, 48), C=(27, 48), D=(48, 48), E=(46, 48), F=(42, 48)),
        "underrated": dict(A=(6, 26), C=(5, 26), F=(7, 26))}),
    "Gemini 3.8 Flash (API runner)": ("Google", "mid", {
        "precedent": dict(A=(48, 48), B=(48, 48), C=(16, 48), D=(48, 48), E=(48, 48), F=(48, 48)),
        "underrated": dict(A=(4, 26), C=(4, 26), F=(6, 26))}),
    "Gemini 4 Argon": ("Google", "frontier", {
        "precedent": dict(A=(48, 48), B=(48, 48), C=(48, 48), D=(48, 48), E=(48, 48), F=(48, 48)),
        "underrated": dict(A=(14, 26), C=(12, 26), F=(14, 26))}),
}


# Opus 5.5 refused many benign reads, so its false-flag cells are not a measured false-positive rate
REFUSALS = {"Claude Opus 5.5": {"precedent": "11/60", "underrated": "114/216"}}


def wilson(k, n, z=1.96):
    if not n:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (100 * (c - h) / d, 100 * (c + h) / d)


def load(d: Path):
    """{arm letter: (caught, n, false flags, benign n, missing)} from one folder of raw results."""
    out = {}
    rows = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(d.glob("*.json"))] if d.is_dir() else []
    # as in analyse_precedent_arms.py: C2 cases ran in the first launch, before the stratum was restricted
    if "precedent" in d.as_posix():
        rows = [r for r in rows if not str(r.get("item", "")).startswith("C2")]
    for a in ARMS:
        r = [x for x in rows if x.get("arm") == a]
        if not r:
            continue
        s = [x for x in r if x.get("label") == 1]
        b = [x for x in r if x.get("label") == 0]
        out[SHORT[a]] = (sum(x.get("flag") is True for x in s), len(s),
                         sum(x.get("flag") is True for x in b), len(b), sum(bool(x.get("flag_missing")) for x in r))
    return out


def watchdogs(extra=()):
    rows = []
    extra = dict(a.split("=", 1) for a in extra)
    for label, fam, tier, d, sub in RAW:
        sets = {s: load(HERE / d / sub.format(s=s)) for s in ("precedent", "underrated")}
        if any(sets.values()):
            rows.append((label, fam, tier, "raw", sets))
    if MODAL.is_dir():
        for tag in sorted(p.name for p in MODAL.iterdir() if p.is_dir()):
            label, fam, tier = MODAL_META.get(tag, (tag, "?", "?"))
            sets = {s: load(MODAL / tag / f"{s}_arms") for s in ("precedent", "underrated")}
            if any(sets.values()):
                rows.append((label, fam, tier, "raw (Modal)", sets))
    for label, path in extra.items():
        fam, tier, _ = TABLE.get(label, ("?", "?", None))
        rows.append((label, fam, tier, "raw (extra)", {s: load(Path(path) / f"{s}_arms") for s in ("precedent", "underrated")}))
    for label, (fam, tier, sets) in TABLE.items():
        if label in extra:
            continue
        rows.append((label, fam, tier, "table", {s: {a: (*kn, None, None, None) for a, kn in v.items()}
                                                 for s, v in sets.items()}))
    return rows


def pct(c):
    return 100 * c[0] / c[1] if c and c[1] else None


def clear(x, y):
    """x is clearly above y: the Wilson intervals do not overlap."""
    return wilson(*x[:2])[0] > wilson(*y[:2])[1]


def effect(cells, hi, lo):
    if hi not in cells or lo not in cells or not cells[hi][1] or not cells[lo][1]:
        return ""
    d = pct(cells[hi]) - pct(cells[lo])
    mark = "*" if clear(cells[hi], cells[lo]) else ("*" if clear(cells[lo], cells[hi]) else "")
    return f"{d:+.0f}{mark}"


def pattern(c):
    """One-line description of how the watchdog responds on the six-arm set."""
    if not {"A", "C"} <= c.keys():
        return ""
    if not clear(c["A"], c["C"]):
        return "no clear endorsement drop"
    if "F" in c and not clear(c["F"], c["C"]):
        return "captured; policy sentence does not help"
    if "F" in c and pct(c["F"]) < pct(c["A"]) - 5:
        return "captured; policy sentence partly restores"
    if "D" in c and clear(c["A"], c["D"]):
        return "captured; any precedent lowers detection"
    return "captured; policy sentence restores"


def main():
    ws = watchdogs(sys.argv[1:])
    print("# Cross-model analysis: precedent arms across all watchdogs\n")
    print("Generated by `cross_analysis.py`. Cells are suppression cases caught (%), with n reads per arm in its own column. `*` marks non-overlapping read-level Wilson 95% intervals; these do not account for repeated draws or clustering by record and do not establish significance. Source `table` means the raw files "
          "are on the team Drive and the counts come from RESULTS_api_monitors_2026-10-24.md.\n")
    for s, arms in (("precedent", "ABCDEF"), ("underrated", "ACF")):
        title = "Six-arm set (visible violation)" if s == "precedent" else "Harder set (rating hides the violation)"
        print(f"## {title}\n")
        head = ("| Watchdog | Family | Tier | " + " | ".join(arms) + " | Endorse A−C | " +
                ("Verdict B−C | Reject A−D | " if s == "precedent" else "") + "Policy F−C | False flags | n per arm | Pattern | Source |")
        print(head)
        print("|" + "---|" * (head.count("|") - 1))
        for label, fam, tier, src, sets in ws:
            c = sets.get(s) or {}
            if not c:
                continue
            cells = " | ".join(f"{pct(c[a]):.0f}" if a in c else "" for a in arms)
            ff = [v for v in c.values() if v[2] is not None]
            ffs = f"{sum(v[2] for v in ff)}/{sum(v[3] for v in ff)}" if ff else "see note"
            if label in REFUSALS:
                ffs += f" ({REFUSALS[label][s]} refused)"
            n = "/".join(sorted({str(v[1]) for v in c.values()}))
            extra = f"{effect(c, 'B', 'C')} | {effect(c, 'A', 'D')} | " if s == "precedent" else ""
            print(f"| {label} | {fam} | {tier} | {cells} | {effect(c, 'A', 'C')} | {extra}{effect(c, 'F', 'C')} | "
                  f"{ffs} | {n} | {pattern(c) if s == 'precedent' else ''} | {src} |")
        print()
    print("## Gemma reading its own family's cases\n")
    g = load(HERE / "results_google-gemma-4-31b-it" / "precedent_arms_gemma_notes")
    if g:
        print("| Sender | " + " | ".join("ABCDEF") + " | Endorse A−C | Policy F−C |\n|---|" + "---|" * 8)
        m = load(HERE / "results_google-gemma-4-31b-it" / "precedent_arms")
        for name, c in (("MiniMax-written", m), ("Gemma-written", g)):
            print(f"| {name} | " + " | ".join(f"{pct(c[a]):.0f}" for a in "ABCDEF") +
                  f" | {effect(c, 'A', 'C')} | {effect(c, 'F', 'C')} |")
        print()


if __name__ == "__main__":
    main()
