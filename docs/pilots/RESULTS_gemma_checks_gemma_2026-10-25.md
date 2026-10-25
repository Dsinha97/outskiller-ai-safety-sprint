# Gemma checks Gemma: six precedent arms on Gemma-written cases

Sprint work, run 24–25 Oct 2026 (settings frozen before scoring: `FREEZE_gemma_checks_gemma.md`). Watchdog google/gemma-4-31b-it on OpenRouter, two draws per case. 81 Gemma suppression cases (C4/Q2c/Q3c kept internal where Gemma's honest pipeline escalated at severity 3 or more) and 32 honest escalated cases. 1,356 calls, none missing a flag, about 0.92M tokens. Code: `run_precedent_arms_gemma_notes.py`.

| Arm | Suppression caught | 95% CI | False flags | Mean suspicion |
|---|---:|---|---:|---:|
| A policy only | 154/162 (95%) | 91–97% | 0/64 | 93 |
| B unsafe precedents, plain | 153/162 (94%) | 90–97% | 0/64 | 92 |
| C unsafe precedents, board accepted | 149/162 (92%) | 87–95% | 0/64 | 90 |
| D unsafe precedents, board rejected | 154/162 (95%) | 91–97% | 0/64 | 93 |
| E safe precedents, board accepted | 154/162 (95%) | 91–97% | 0/64 | 94 |
| F as C, plus policy sentence | 152/162 (94%) | 89–97% | 0/64 | 92 |

The same watchdog on MiniMax-written suppression fell from 100% (arm A) to 50% (arm C). On Gemma-written suppression the endorsed arm sits within the baseline interval. Gemma detected more than 90% of its own pipeline's suppression in this case set. The comparison cannot isolate an own-family effect. The likelier reason the endorsement fails is visibility: Gemma's ratings often contradict its own summaries (a serious case rated low or kept internal against its own rationale), so the violation shows in the rating, which is where the policy sentence also worked. This run cannot separate family from visibility, since sender and visibility change together.
