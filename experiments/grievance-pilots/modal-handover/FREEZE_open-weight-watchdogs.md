# Frozen before scoring: open-weight watchdogs (2026-10-24T21:04:13Z)

Sprint work (run 24 Oct 2026, after the 23 Oct cutoff). Models, prompts and scoring are fixed by this file. No changes after scoring starts.

- Models: qwen3-32b (Qwen/Qwen3-32B), llama-3.3-70b (RedHatAI/Llama-3.3-70B-Instruct-FP8-dynamic), mistral-small-3.2-24b (mistralai/Mistral-Small-3.2-24B-Instruct-2506)
- Temperature 0.7, 2 draws per prompt; vllm 0.31.0; engine seed left at vLLM's default (0), so reruns of these files reproduce the draws
- Threshold: the monitor's own boolean `flag` field (same as the OpenRouter monitors); flag_missing rows excluded and counted
- Prompt sets: precedent (324), underrated (147)

```
0dbe8139cb0b1f7938899fff8fd84a2bacf6fef99d2b72db9aab78e2c3f2be57 *run_precedent_modal.py
4c899ab6610963c8f949840b4e93140de7553f68de47a32fe2f8d0d777c5958a *precedent_prompts.jsonl
8d57485b6593ff2c60f4399b57a56e75841fee71c916809b2acd4efe8472efea *underrated_prompts.jsonl
```

## Change after freeze (hardware only, before any Llama scoring)

Llama 3.3 70B ran out of KV-cache memory on an H100 (68 GB of weights), so it moved to an H200. Model, prompts, temperature and threshold are unchanged. New script hash:

```
1b144ec9b20b5ca3b4f3865dd82e2f32e08de8114a44469fe18cd4845455c4e7 *run_precedent_modal.py
```

## Later change: seed option (25 Oct, after scoring; no effect on these runs)

`--seed N` was added for repeat samples. With no flag the engine is built exactly as before, so the frozen runs above are unchanged.

## Clarification (25 Oct)

The analysis keeps missing flags in the denominator and counts them as not flagged; the threshold line above saying they are excluded is corrected here. Same-seed reruns reuse the random stream but can differ slightly with hardware or batching.
