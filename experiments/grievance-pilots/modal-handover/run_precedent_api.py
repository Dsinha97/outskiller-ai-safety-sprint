"""Precedent arms on API monitors (Claude, Gemini), run from Modal with the workspace secrets (sprint work, 2026-10-24).

Same frozen prompts, two draws per prompt and output layout as run_precedent_modal.py, so
talk-pilots/analyse_precedent_arms.py reads the results unchanged. Keys never leave Modal: the functions attach
`anthropic-secret` / `gemini-secret` by name. A spend cap stops the run before the estimated cost passes --budget.

  PYTHONUTF8=1 modal run run_precedent_api.py --model haiku-5.5 --smoke
  PYTHONUTF8=1 modal run run_precedent_api.py --model haiku-5.5 --budget 1
  PYTHONUTF8=1 modal run run_precedent_api.py --model sonnet-5.5 --prompt-set underrated --budget 2
  PYTHONUTF8=1 modal run run_precedent_api.py --model gemini-3.8-flash --suffix _v2 --budget 2   (new results folder)

Thinking: Claude runs have it off (Haiku `disabled`, Sonnet `between_tools`). Gemini 3.8 Flash and 4 Argon cannot turn it
off (lowest level is "low"), so they run at thinking_level "low". There are no fallbacks: a rejected setting raises, and a
Claude response that contains a thinking block raises. Every result records the setting that was sent and the thinking
tokens that came back (`thought_tokens`), so thinking can be audited per read.
"""
from __future__ import annotations

import json
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import modal

HERE = Path(__file__).parent
TEMP, REPS, MAX_TOKENS, WORKERS, CHUNK = 0.7, 2, 2000, 6, 48  # the first full runs used 600; see the results note

# tag: (provider, model id, $ per 1M input, $ per 1M output, thinking setting). List prices from the 2026-10-06 skill
# table and the Gemini pricing page dated 2026-10-22.
MODELS = {
    "haiku-5.5": ("anthropic", "claude-haiku-5-5", 0.10, 0.50, {"type": "disabled"}),
    "sonnet-5.5": ("anthropic", "claude-sonnet-5-5", 2.00, 10.00, {"type": "between_tools"}),
    "gemini-3.8-flash": ("gemini", "gemini-3.8-flash", 0.75, 3.75, "low"),
    "gemini-4-argon": ("gemini", "gemini-4-argon", 2.00, 10.00, "low"),
}

app = modal.App("collusion-precedent-api")
image = modal.Image.debian_slim(python_version="3.12").pip_install("anthropic", "google-genai")


def _call_anthropic(model, system, user, thinking, state):
    import anthropic

    client = anthropic.Anthropic(max_retries=3)
    # the current SDK and API no longer accept temperature, so Claude runs use the model's own sampling
    for attempt in range(4):
        try:
            r = client.messages.create(model=model, max_tokens=MAX_TOKENS, system=system, thinking=thinking,
                                       messages=[{"role": "user", "content": user}])
            if any(getattr(b, "type", "") in ("thinking", "redacted_thinking") for b in r.content):
                raise RuntimeError("response contained a thinking block although thinking was set to " + str(thinking))
            text = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
            return {"content": text, "finish": r.stop_reason, "in": r.usage.input_tokens, "out": r.usage.output_tokens,
                    "thought_tokens": 0, "temperature_applied": False, "thinking": str(thinking)}
        except (anthropic.RateLimitError, anthropic.APIConnectionError, anthropic.InternalServerError):
            time.sleep(2 ** attempt * 2)
    raise RuntimeError("anthropic call failed after retries")


def _call_gemini(model, system, user, level, state):
    import os

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    for attempt in range(6):
        try:
            cfg = types.GenerateContentConfig(system_instruction=system, max_output_tokens=MAX_TOKENS,
                                              temperature=TEMP if state.get("temperature", True) else None,
                                              thinking_config=types.ThinkingConfig(thinking_level=level))
            r = client.models.generate_content(model=model, contents=user, config=cfg)
            u = r.usage_metadata
            thought = getattr(u, "thoughts_token_count", 0) or 0
            fr = r.candidates[0].finish_reason if r.candidates else None
            return {"content": r.text or "", "finish": str(fr), "in": u.prompt_token_count or 0,
                    "out": (u.candidates_token_count or 0) + thought, "thought_tokens": thought,
                    "temperature_applied": state.get("temperature", True), "thinking": f"thinking_level={level}"}
        except Exception as e:  # noqa: BLE001
            msg = str(e).lower()
            if "temperature" in msg and state.get("temperature", True):
                state["temperature"] = False  # recorded per result as temperature_applied
                continue
            if "429" in msg or "quota" in msg or "rate" in msg or "503" in msg or "unavailable" in msg:
                time.sleep(2 ** attempt * 2)
                continue
            raise  # a rejected thinking setting raises: no fallback that could switch thinking on
    raise RuntimeError("gemini call failed after retries")


def _run(tag: str, rows: list[dict], budget_left: float):
    provider, model, pin, pout, thinking = MODELS[tag]
    fn = _call_anthropic if provider == "anthropic" else _call_gemini
    state: dict = {}
    spent = [0.0]
    stop = [False]
    lock = threading.Lock()

    def one(job):
        r, k = job
        if stop[0]:
            return None
        try:
            x = fn(model, r["system"], r["user"], thinking, state)
        except Exception as e:  # noqa: BLE001
            return {"row": r, "rep": k, "error": f"{type(e).__name__}: {str(e)[:300]}"}
        cost = x["in"] * pin / 1e6 + x["out"] * pout / 1e6
        with lock:
            spent[0] += cost
            if spent[0] >= budget_left:
                stop[0] = True
        return {"row": r, "rep": k, "cost": cost, **x}

    jobs = [(r, k) for r in rows for k in range(REPS)]
    with ThreadPoolExecutor(WORKERS) as ex:
        res = [x for x in ex.map(one, jobs) if x is not None]
    return {"results": res, "spent": spent[0], "stopped_for_budget": stop[0], "state": {k: str(v) for k, v in state.items()}}


@app.function(image=image, secrets=[modal.Secret.from_name("anthropic-secret")], timeout=3600)
def run_anthropic(tag, rows, budget_left):
    return _run(tag, rows, budget_left)


@app.function(image=image, secrets=[modal.Secret.from_name("gemini-secret")], timeout=3600)
def run_gemini(tag, rows, budget_left):
    return _run(tag, rows, budget_left)


def _parse(text: str, finish) -> dict:
    """The final JSON answer, or {} (a missing flag) if the call was cut off. Same rules as run_precedent_modal.py."""
    if str(finish).lower() in ("max_tokens", "length", "finishreason.max_tokens", "refusal"):
        return {}
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    if "<think>" in text:
        return {}
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    for cand in [text, *reversed([m.group(0) for m in re.finditer(r"\{[^{}]*\}", text, flags=re.S)])]:
        try:
            x = json.loads(cand)
            if isinstance(x, dict) and "flag" in x:
                return x
        except Exception:
            pass
    return {}


@app.local_entrypoint()
def main(model: str, smoke: bool = False, prompt_set: str = "precedent", budget: float = 1.0, suffix: str = ""):
    rows = [json.loads(l) for l in (HERE / f"{prompt_set}_prompts.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    if smoke:
        rows = rows[:2] + rows[-2:]
    provider, repo = MODELS[model][0], MODELS[model][1]
    fn = run_anthropic if provider == "anthropic" else run_gemini
    out = HERE / "results" / (model + suffix) / f"{prompt_set}_arms"
    out.mkdir(parents=True, exist_ok=True)
    todo = [r for r in rows if not all((out / f"{r['arm']}__{r['item']}__r{k}.json").exists() for k in range(REPS))]
    print(f"{model}{suffix}: {len(rows)} prompts x {REPS} draws, {len(todo)} to run, budget ${budget:.2f}")
    spent = 0.0
    errors = 0
    for i in range(0, len(todo), CHUNK):
        chunk = todo[i:i + CHUNK]
        res = fn.remote(model, chunk, budget - spent)
        spent += res["spent"]
        for x in res["results"]:
            r = x["row"]
            if "error" in x:
                errors += 1
                print("ERROR", r["arm"], r["item"], x["error"])
                continue
            p = _parse(x["content"], x["finish"])
            (out / f"{r['arm']}__{r['item']}__r{x['rep']}.json").write_text(json.dumps({
                "arm": r["arm"], "item": r["item"], "record": r["record"], "rep": x["rep"], "label": r["label"],
                "stratum": r["stratum"], "model": repo, "endpoint": f"{provider}-api via modal",
                "temperature": TEMP, "temperature_applied": x["temperature_applied"], "thinking": x["thinking"],
                "thought_tokens": x["thought_tokens"], "max_tokens": MAX_TOKENS,
                "system_sha": r["system_sha"], "user_sha": r["user_sha"],
                "flag": p.get("flag"), "suspicion": p.get("suspicion"), "reason": p.get("reason"),
                "flag_missing": "flag" not in p, "finish": x["finish"], "cost_usd": round(x["cost"], 6),
                "usage": {"prompt_tokens": x["in"], "completion_tokens": x["out"]},
                "content": x["content"]}, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"chunk {i // CHUNK + 1}: spent ${spent:.3f}; applied {res['state']}")
        if res["stopped_for_budget"] or spent >= budget:
            print(f"STOPPED: estimated spend ${spent:.3f} reached the ${budget:.2f} budget; rerun to resume")
            break
    ds = [json.loads(f.read_text(encoding="utf-8")) for f in out.glob("*.json")]
    miss = sum(d["flag_missing"] for d in ds)
    thinking_reads = sum(d.get("thought_tokens", 0) > 0 for d in ds)
    print(f"wrote {len(ds)} files to {out}; missing flags {miss}; errors {errors}; reads with thinking tokens {thinking_reads}; "
          f"estimated spend ${spent:.3f}")
