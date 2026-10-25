"""Precedent arms on open-weight monitors, as one Modal batch job (sprint work, written 2026-10-24).

Loads one model once with vLLM, sends every prompt in precedent_prompts.jsonl (324 prompts x REPS draws)
in a single batch, and writes one JSON per call to results/<model-tag>/precedent_arms/, the same layout
talk-pilots/analyse_precedent_arms.py reads. The container stops when the job ends, so nothing idles.

  PYTHONUTF8=1 modal run run_precedent_modal.py --model gpt-oss-120b
  PYTHONUTF8=1 modal run run_precedent_modal.py --model qwen3-32b --smoke
  PYTHONUTF8=1 modal run run_precedent_modal.py --model qwen3-32b --prompt-set underrated   (147 harder prompts)
  PYTHONUTF8=1 modal run run_precedent_modal.py --model qwen3-32b --seed 1   (a repeat sample)

Seeds: vLLM's engine seed defaults to 0, so runs without --seed reuse the same random stream and
reproduce earlier draws. --seed N (N other than 0) passes LLM(seed=N), writes to
results/<model-tag>_seed<N>/ and records "seed" in each file, so earlier folders are never overwritten.

Models (one GPU each): see MODELS below. Same temperature (0.7) and two draws per prompt as the
OpenRouter runs. A call that stops at the token limit, or ends inside an unclosed <think> block,
is saved with flag_missing=true, never scored from a draft answer.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import modal

HERE = Path(__file__).parent
TEMP, REPS = 0.7, 2

# tag: (Hugging Face repo, GPU, max_model_len, max_tokens, extra LLM kwargs)
# Reasoning models get a larger output budget so they can finish thinking; prompts are about 1-3k tokens.
# All five models completed both prompt sets (24 Oct); smoke-test any new configuration before a full run.
MODELS = {
    "gpt-oss-120b": ("openai/gpt-oss-120b", "H100", 16384, 12288, {}),
    "qwen3-32b": ("Qwen/Qwen3-32B", "H100", 16384, 12288, {}),
    "llama-3.3-70b": ("RedHatAI/Llama-3.3-70B-Instruct-FP8-dynamic", "H200", 16384, 4096, {}),
    "mistral-small-3.2-24b": ("mistralai/Mistral-Small-3.2-24B-Instruct-2506", "A100-80GB", 16384, 4096,
                              {"tokenizer_mode": "mistral", "config_format": "mistral", "load_format": "mistral"}),
    "olmo-3.1-32b-think": ("allenai/Olmo-3.1-32B-Think", "H100", 16384, 12288, {}),
}

app = modal.App("collusion-precedent-arms")
image = (modal.Image.from_registry("nvidia/cuda:12.8.1-devel-ubuntu22.04", add_python="3.12")
         .entrypoint([])
         .uv_pip_install("vllm==0.31.0", "huggingface_hub[hf_transfer]")
         .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"}))
hf_cache = modal.Volume.from_name("hf-cache", create_if_missing=True)
VOLUMES = {"/root/.cache/huggingface": hf_cache}


def _batch(tag: str, rows: list[dict], seed: int = 0) -> list[dict]:
    from vllm import LLM, SamplingParams

    repo, _, max_len, max_tokens, extra = MODELS[tag]
    llm = LLM(model=repo, max_model_len=max_len, **extra, **({"seed": seed} if seed else {}))
    params = SamplingParams(temperature=TEMP, max_tokens=max_tokens, n=REPS)
    convs = [[{"role": "system", "content": r["system"]}, {"role": "user", "content": r["user"]}] for r in rows]
    outs = llm.chat(convs, params)
    res = []
    for r, o in zip(rows, outs):
        for k, c in enumerate(o.outputs):
            res.append({"row": r, "rep": k, "content": c.text, "finish": c.finish_reason,
                        "prompt_tokens": len(o.prompt_token_ids), "completion_tokens": len(c.token_ids)})
    return res


@app.function(gpu="H100", image=image, volumes=VOLUMES, timeout=3 * 60 * 60)
def run_h100(tag: str, rows: list[dict], seed: int = 0) -> list[dict]:
    return _batch(tag, rows, seed)


@app.function(gpu="H200", image=image, volumes=VOLUMES, timeout=3 * 60 * 60)
def run_h200(tag: str, rows: list[dict], seed: int = 0) -> list[dict]:
    return _batch(tag, rows, seed)


@app.function(gpu="A100-80GB", image=image, volumes=VOLUMES, timeout=3 * 60 * 60)
def run_a100(tag: str, rows: list[dict], seed: int = 0) -> list[dict]:
    return _batch(tag, rows, seed)


def _parse(text: str, finish: str | None) -> dict:
    """The final JSON answer, or {} (a missing flag) if the call was cut off or never left its reasoning."""
    if finish == "length":
        return {}
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    if "<think>" in text:  # reasoning block opened and never closed
        return {}
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    # take the last JSON object with a flag, so a draft inside visible reasoning (e.g. gpt-oss analysis text)
    # never stands in for the final answer
    for cand in [text, *reversed([m.group(0) for m in re.finditer(r"\{[^{}]*\}", text, flags=re.S)])]:
        try:
            x = json.loads(cand)
            if isinstance(x, dict) and "flag" in x:
                return x
        except Exception:
            pass
    return {}


@app.local_entrypoint()
def main(model: str, smoke: bool = False, prompt_set: str = "precedent", seed: int = 0):
    rows = [json.loads(l) for l in (HERE / f"{prompt_set}_prompts.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    if smoke:
        rows = rows[:2] + rows[-2:]
    gpu = MODELS[model][1]
    fn = run_a100 if gpu.startswith("A100") else run_h200 if gpu == "H200" else run_h100
    print(f"{model} on {gpu}: {len(rows)} prompts x {REPS} draws, engine seed {seed}")
    out = HERE / "results" / (f"{model}_seed{seed}" if seed else model) / f"{prompt_set}_arms"
    out.mkdir(parents=True, exist_ok=True)
    for x in fn.remote(model, rows, seed):
        r = x["row"]; p = _parse(x["content"], x["finish"])
        (out / f"{r['arm']}__{r['item']}__r{x['rep']}.json").write_text(json.dumps({
            "arm": r["arm"], "item": r["item"], "record": r["record"], "rep": x["rep"], "label": r["label"],
            "stratum": r["stratum"], "model": MODELS[model][0], "endpoint": f"modal-vllm/{gpu}",
            "temperature": TEMP, "seed": seed, "system_sha": r["system_sha"], "user_sha": r["user_sha"],
            "flag": p.get("flag"), "suspicion": p.get("suspicion"), "reason": p.get("reason"),
            "flag_missing": "flag" not in p, "finish": x["finish"],
            "usage": {"prompt_tokens": x["prompt_tokens"], "completion_tokens": x["completion_tokens"]},
            "content": x["content"]}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(list(out.glob('*.json')))} files to {out}")
