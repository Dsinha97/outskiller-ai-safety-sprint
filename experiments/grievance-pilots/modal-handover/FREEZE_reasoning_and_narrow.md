# Frozen before scoring: gpt-oss-120b, OLMo 3.1 32B Think and the narrow-question watchdog (2026-10-24)

Sprint work (Deepayan Sinha). Models, prompts and scoring fixed by this file; nothing changed after scoring started.

- Open-weight runs: `gpt-oss-120b` (openai/gpt-oss-120b, H100, 12,288 output tokens) and `olmo-3.1-32b-think` (allenai/Olmo-3.1-32B-Think, H100, 12,288), vLLM 0.31.0, temperature 0.7, 2 draws, engine seed left at vLLM's default (0). Threshold: the monitor's own `flag`; missing flags counted as not flagged.
- Narrow-question runs: Claude Haiku 5.5, Claude Sonnet 5.5, Gemini 3.8 Flash and Gemini 4 Argon through `run_precedent_api.py` (settings as in the API-monitor note), harder set only. Questions and flag rule are in `build_narrow_prompts.py`; the rule was fixed before the first call.

```
0dbe8139cb0b1f7938899fff8fd84a2bacf6fef99d2b72db9aab78e2c3f2be57 *run_precedent_modal.py   (the pre-H200 version, same as FREEZE_open-weight-watchdogs.md)
dc8b121b8b6dc74d60489a799565223e16928484fb5bcdb8aafbffda341cdefc *run_precedent_api.py
4c899ab6610963c8f949840b4e93140de7553f68de47a32fe2f8d0d777c5958a *precedent_prompts.jsonl
8d57485b6593ff2c60f4399b57a56e75841fee71c916809b2acd4efe8472efea *underrated_prompts.jsonl
f5260c94f6529e0a604d6fb2f3a0bc1c59cbf291ae0d1894e3ccfaffcc35d40a *underratednarrow_prompts.jsonl
d151fe73cbaed0de8633ba80e3451e780ae0c8c729cfc756e714a33b1ae485da *build_narrow_prompts.py
```

Run on 24 Oct 2026 (UTC evening), after the 23 Oct cutoff.
