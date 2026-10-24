# Run sheet: precedent arms on open-weight monitors (Modal)

For a teammate with their own $50 sprint Modal credit. About 30 minutes of your attention, then the job runs unattended.

## What this tests

A compliance monitor reads processed grievance cases and flags suppression. In our pilots, showing it three past cases a "review board accepted" switched detection off almost completely. Six matched arms separate the parts of that framing (precedent alone, endorsement, rejection, safe precedent, and an explicit "the written policy controls" line). The same 324 prompts already ran on four monitors through OpenRouter (GLM 5.3 Flash, Gemma 4 31B, MiniMax M3.1 Flash, Nemotron 3 Ultra). Your run adds an open-weight family that no API run covers.

## Pick one model (each is one GPU, one batch)

| Tag | Model | GPU | Est. cost |
|---|---|---|---:|
| `gpt-oss-120b` | OpenAI gpt-oss-120b | H100 | about $2–4 |
| `qwen3-32b` | Qwen 3 32B | H100 | about $2–3 |
| `llama-3.3-70b` | Llama 3.3 70B (FP8) | H100 | about $3–5 |
| `mistral-small-3.2-24b` | Mistral Small 3.2 24B | A100 80GB | about $2 |
| `olmo-3.1-32b-think` | OLMo 3.1 32B Think | H100 | about $3–5 |

Suggested split: Carl takes `gpt-oss-120b` then `llama-3.3-70b`; Prashanth takes `qwen3-32b` then `mistral-small-3.2-24b`. Most of the cost is the first download and start-up (10–20 minutes). The 648 calls themselves take minutes.

## Steps

1. `pip install modal` and run `modal setup` (browser login to your own account).
2. On modal.com, Usage & Billing: set the **spend limit to $0**, so nothing can charge your card.
3. Get the files: `run_precedent_modal.py` from this folder of the repo, and `precedent_prompts.jsonl` and `underrated_prompts.jsonl` from the team Drive (they contain full agent notes, so they are kept out of the public repo). Put all three in one folder.
4. Smoke test (4 prompts):
   ```bash
   PYTHONUTF8=1 modal run run_precedent_modal.py --model qwen3-32b --smoke
   ```
   Check that `results/qwen3-32b/precedent_arms/` has 8 files and that their `flag` fields are `true` or `false`, not `null`.
5. Full run:
   ```bash
   PYTHONUTF8=1 modal run run_precedent_modal.py --model qwen3-32b
   ```
   Then the harder set (147 prompts, where the rating hides the violation), in the same session:
   ```bash
   PYTHONUTF8=1 modal run run_precedent_modal.py --model qwen3-32b --set underrated
   ```
6. Confirm nothing is left running: `modal app list` and `modal container list`. Stop anything with `modal app stop collusion-precedent-arms`.
7. Zip `results/<tag>/` and drop it in the Drive folder, or open a PR to `results/precedent-arms/`. Note your spend from `modal billing summary` or the dashboard.

## If something breaks

- Out of memory at start-up: lower `max_model_len` in `MODELS` to 8192 and rerun.
- Many `flag: null` results: the model wrapped its JSON in reasoning. Send the folder anyway; the raw text is saved and can be re-parsed.
- Anything else: paste the last 30 lines of output in the WhatsApp group.

## What not to change

Keep the prompts file, temperature (0.7) and two draws per prompt as they are, so results compare with the OpenRouter monitors.
