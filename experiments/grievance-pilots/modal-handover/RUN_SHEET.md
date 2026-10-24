# Run sheet: precedent arms on open-weight monitors (Modal)

For a teammate with their own $50 sprint Modal credit. About 30 minutes of your attention, then the job runs unattended.

## What this tests

A compliance monitor reads processed grievance cases and flags suppression. In our pilots, showing it three past cases a "review board accepted" switched detection off almost completely. Six matched arms separate the parts of that framing (precedent alone, endorsement, rejection, safe precedent, and an explicit "the written policy controls" line). The same 324 prompts already ran on four monitors through OpenRouter (GLM 5.3 Flash, Gemma 4 31B, MiniMax M3.1 Flash, Nemotron 3 Ultra). Your run adds an open-weight family that no API run covers.

## Pick one model (each is one GPU, one batch)

| Tag | Model | GPU | Rough cost |
|---|---|---|---:|
| `gpt-oss-120b` | OpenAI gpt-oss-120b | H100 | $2–4 |
| `qwen3-32b` | Qwen 3 32B | H100 | $2–3 |
| `llama-3.3-70b` | Llama 3.3 70B (FP8) | H100 | $3–5 |
| `mistral-small-3.2-24b` | Mistral Small 3.2 24B | A100 80GB | about $2 |
| `olmo-3.1-32b-think` | OLMo 3.1 32B Think | H100 | $3–5 |

The costs are rough estimates, scaled from one smoke test: Qwen 3 32B on an H100 cost about $0.37 for start-up plus 8 calls. Only Qwen 3 32B has been tested on Modal so far, so smoke-test any other model before its full run. Reasoning models (gpt-oss, Qwen, OLMo Think) write long answers and may cost more.

Suggested split: Carl takes `gpt-oss-120b` then `llama-3.3-70b`; Prashanth takes `qwen3-32b` then `mistral-small-3.2-24b`. Most of the cost is the first download and start-up (10–20 minutes). The calls themselves take minutes.

## Steps

1. `pip install modal` and run `modal setup` (browser login to your own account). On Windows, run `set PYTHONUTF8=1` (cmd) or `$env:PYTHONUTF8=1` (PowerShell) first, or the Modal CLI can crash printing Unicode.
2. On modal.com, open Usage & Billing, check that the sprint credit shows, and set the **spend limit to $0**. Modal’s page describes it: “Once the estimated monthly charges exceed this limit and credits are exhausted, all workspace workloads will stop. Volume storage charges will still accrue.” So with $0, runs paid from credit go ahead and nothing reaches your card (checked on Liezl’s workspace, 24 Oct). Credit is used in order: the plan’s $30 monthly allowance first, then the $50 sprint grant.
3. Get the files: `run_precedent_modal.py` (repo, `experiments/grievance-pilots/modal-handover/`) and `precedent_prompts.jsonl` and `underrated_prompts.jsonl` from the team Drive. The prompt files contain full agent notes, so they stay out of the public repo. Put all three in one folder.
4. Smoke test (4 prompts):
   ```bash
   modal run run_precedent_modal.py --model qwen3-32b --smoke
   ```
   Check that `results/qwen3-32b/precedent_arms/` has 8 files and that their `flag` fields are `true` or `false`, not `null`.
5. Full run:
   ```bash
   modal run run_precedent_modal.py --model qwen3-32b
   ```
   Then the harder set (147 prompts, where the rating hides the violation), in the same session:
   ```bash
   modal run run_precedent_modal.py --model qwen3-32b --prompt-set underrated
   ```
6. Confirm nothing is left running: `modal app list` and `modal container list`. Stop anything with `modal app stop collusion-precedent-arms`.
7. Zip `results/<tag>/` and put it in the team Drive. Please don't commit these result files to the repo: each one quotes the case text. Note your spend from the Modal dashboard. The analysis tables made from your results go into the repo afterwards.

## If something breaks

- Out of memory at start-up: lower `max_model_len` in `MODELS` to 8192 and rerun.
- Some results with `flag_missing: true`: the answer was cut off at the token limit or never left its reasoning, so it isn't scored. A few are fine; if more than about one in ten are missing, tell us before running more.
- Anything else: paste the last 30 lines of output in the WhatsApp group.

## What not to change

Keep the prompt files, temperature (0.7) and two draws per prompt as they are, so results compare with the OpenRouter monitors.
