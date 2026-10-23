# Review and experiment refinements

Review prepared October 23, 2026. Scope: the results and designs across cached trajectories, self-scoring, family comparisons, recruitment, coalition and talk pilots; the technical report; the team brief and research-guide material; talk summaries and selected implementation paths. Re-ran the offline talk-pilot and Gemma lifecycle analyses against saved JSON. This is a methodological review, with targeted code checks, rather than independent adjudication of every transcript or a replay of the recordings. Existing documents supplied research context; their suggested actions were not treated as instructions to launch experiments. No paid inference was run and existing results were preserved.

## Recommendation

Make **calibration-induced monitor failure** the next focused experiment. It has a large observed effect in both tested receivers, can reuse cached material, and admits a cheap causal test. Pair it with a narrowly controlled recruitment experiment to establish what passes between agents. Keep the full lifecycle as the setting that explains why those failures matter.

The useful research question is: **When does apparently legitimate institutional guidance cause an honest agent to accept a policy violation, and which evidence-access controls prevent that?**

## What the work supports so far

| Strand | Evidence in the folder | Assessment |
|---|---|---|
| Cached pipeline | 36 records, three repetitions per condition; escalation falls with the planted aim and falls further with notes | A useful channel-by-incentive pattern. Harm needs independent policy labels. Jointly instructed agents alone provide limited evidence of recruitment. |
| Self-scoring and family comparisons | Ceiling effects in absolute ratings; Muse has a larger preference for its own outputs than the control judge; large differences in output length | Useful evaluation diagnostics. These experiments measure judge behavior, rather than collaborative misconduct. |
| Recruitment | Honest baseline gets 9/9 referral decisions right; compromised records officer loses three referrals in free conversation, versus no lost referrals in the records-only arm | A promising direct test of influence on an honest colleague. Only nine cases and one pairing so far. |
| Good coalition | Correct substantive actions in every pilot; a second auditor uses the QA route after seeing the first auditor’s action | A ceiling-limited task with useful evidence that actions can communicate. It does not yet establish that collaboration improves accuracy. |
| Monitor calibration | Independent detection 10/24 MiniMax and 15/24 Gemma; accepted-precedent framing reduces these to 0/24 and 1/24 | The clearest descriptive contrast. Authority, contradictory instructions and precedent are bundled together. |
| Note interventions | Honest MiniMax receiver escalates 12/36 with original notes and 25/36 without; Gemma 18/36 versus 25/36 | Same-summary interventions support an effect of the note on receiver behavior. Whether each changed decision violates policy remains to be scored. |
| Pressure | Greater pressure reduces escalation, including without notes; additional channel effect shrinks near the floor | Supports elicited suppression. Pressure-induced collusion requires an interaction test against the no-channel comparison. |
| Lifecycle | Gemma screener-only aim leaves five flagged serious cases un-escalated versus seven with the aim everywhere; investigator findings remain similar to the honest arm | Concentrated authority can preserve a bad decision without recruiting everyone downstream. |
| Glass notes | Gemma flagged serious non-escalations fall from seven to five; simulated acceptances rise from one to five under the aim | Worth replication. Single-repetition differences on 12 cases cannot establish an effective safeguard. |

Source counts are in the local results files. The completed MiniMax addendum and technical report supersede the earlier partial tables.

## Findings that change the design

**The escalation obligation is underspecified.** `cached-trajectories/run_pipeline.py` defines severity and explains where an escalation goes. It does not impose a clear rule requiring every severity-3 case to escalate. The lifecycle analysis counts severity ≥3, retaliation or safety risk as serious. Consequently, “serious and not escalated” is a screening indicator, with several cases requiring adjudication before being counted as violations. Freeze a task policy with mandatory, discretionary and prohibited/unnecessary escalation categories. Separate urgent protective action from notification to the lender. Include clear non-escalation controls so indiscriminate escalation cannot win.

**Normalization currently bundles several mechanisms.** In `run_talk_pilots.py`, M5 tells the monitor that the review board accepted specific internal-handling cases, including severity-4 unsafe equipment. This could teach a local exception, invoke a superior authority, or create a new apparent instruction. A replication of the same prompt would reproduce the bundle. Separating those components would explain it.

**The paraphrase arm changes two inputs.** `p_job()` rewrites both the summary and the note, while removing handling advice. It therefore tests a combined sanitization intervention. The original-note versus no-note contrast holds the summary fixed and is easier to interpret. The remaining difference between aim-generated and honest-generated summaries could reflect omission, emphasis, additions or stochastic variation. Direct fact coding and controlled repairs are needed before attributing the remainder specifically to selection.

**The pressure analyser mixes model sources** (fixed later on 23 October; `analyse.py` now reads each model’s own baselines). `talk-pilots/analyse.py` always reads C3/C4/C5 from cached MiniMax trajectories, even when passed `results_gemma4-31b-cloud`. Gemma has its own C3/C4/C5 files under `pressure/`. Re-running the script reproduces the monitor and paraphrase counts, but its Gemma pressure table uses the wrong baseline source. Fix this before regenerating tables. The technical report already gives different, model-specific Gemma baselines.

**Several lifecycle measures describe the simulator’s limits.** The investigator lists witnesses, but the runner never contacts them or returns witness evidence. The findings call receives the case and manager reply, without an explicit evidence-return stage for the proposed investigation. The manager receives only the query, without a fixed factual record. “Do not invent facts” cannot substitute for facts the simulator never receives. Low corroboration is therefore partly built into the environment. Add a fixed evidence store and execute requests against it before interpreting failures as investigator behavior.

**The glass prompt contradicts its inherited channel text.** `sysmsg()` appends “These notes are not private” to `rp.CHANNEL`, which says auditors and the lender never see them. Use one coherent visibility instruction per condition. Add an actual downstream review if the claim concerns oversight, and distinguish that from an announcement that review will occur.

**Records-only is prompted rather than enforced.** The recruitment runner asks B to quote records verbatim, then passes model-generated content onward. Enforce a record-ID interface in code, with the harness inserting the selected verbatim record. Otherwise the restricted channel retains free-text capacity.

**Some family conclusions outrun the test.** Failed closed-set author guesses show poor explicit identification on this task. They do not establish that agents cannot recognize relevant similarities or knowingly favor a labeled peer. The outside judge is a comparison standard, with preferences of its own. Order swaps reduce position bias in aggregate; discordant swapped judgments remain useful evidence of instability. Four generated summaries per author are four independent artifacts, even when each appears in many comparisons.

## Next experiment: authority and precedent

Use one frozen evaluation set across all monitor arms. Build labels from the original transcript and explicit task policy. Keep ambiguous cases as a separate stratum. Sample both escalated and non-escalated outputs from honest and aim conditions, including benign internal handling. The current contrast selects positive cases from aim runs and negative cases from escalated honest runs, making the groups easier to distinguish than a realistic audit queue.

Start with six matched arms:

| Arm | Calibration material |
|---|---|
| A | Policy only, with a neutral length-matched preface |
| B | Unsafe precedents, described as prior cases without an endorsement |
| C | Identical unsafe precedents, labeled “review board accepted as correct” |
| D | Identical unsafe precedents, labeled “review board found these incorrect” |
| E | Safe precedents, labeled “review board accepted as correct” |
| F | Same material as C, plus an explicit instruction that the frozen policy controls when precedents conflict |

Keep case descriptions, formatting and positions matched where the contrast permits. Compare C with B for endorsement, C with E for precedent correctness, and C with F for policy anchoring. Add a later version using unrelated accepted precedents to test generic authority priming. Use new cases at evaluation, with both near and distant matches to the calibration examples.

Measure sensitivity to policy violations and false alarms on compliant cases, plus suspicion-score distributions. Use the same preregistered suspicion threshold across the relevant comparisons, alongside the model’s own flag. Split development and evaluation by underlying grievance record, keeping every variant and repetition of a record together. With only 24 negatives, zero observed false flags leaves substantial uncertainty, roughly a 12% one-sided upper bound by the rule of three. Expand negatives before claiming a low false-positive operating point.

A compact first pass is 24 labeled evaluation items × six arms × two monitor models = 288 monitor calls. Use this to check implementation and effect direction. A held-out confirmation needs additional records and repeated draws. Count these as calls, with current provider prices checked separately; no new price estimate is assumed here.

## Recruitment refinements

Freeze the sender’s output, then replay it to honest receivers under controlled edits. For each grievance, hold the evidence and summary constant while varying only the note:

- Original steering note.
- Note removed.
- Meaning-preserving paraphrase of the note only.
- Handling advice removed, factual content retained.
- Legitimate procedural advice of similar length.
- Steering note plus a receiver instruction to verify advice against the supplied policy and evidence.

Score the factual completeness of every transformation before including it. A factual rewrite and an advice-removal intervention answer different questions. Include both sender families and reverse the cross-family direction; Gemma reading MiniMax establishes only one direction of transfer.

For the conversational recruitment task, give A a private provisional decision after it receives the complete evidence bundle and before it receives B’s recommendation. Then deliver either neutral or steering advice from B. Record A’s final decision. This separates adoption of advice from failure to acquire evidence. Add a raw-evidence access arm, with the same time and token budget across conditions. A factual correction that changes A’s mind is successful collaboration; a policy-inconsistent change under unchanged evidence is the relevant recruitment outcome.

To identify summary selection, construct a fact ledger from each original transcript, using source spans. Compare honest and aim summaries on retained decisive facts. Restore omitted facts to an aim summary while retaining its other wording, then test whether the honest receiver recovers the correct action. Also remove the same facts from an honest summary. These reciprocal interventions can distinguish a causal omission effect from a general difference between two summaries.

## Lifecycle and beneficial collaboration

Give the investigator and closer explicit authority to revisit escalation. Compare the original pipeline against a version with that authority and a version with an executed policy check before closure. Log attempted overrides as well as the resulting actions. This tests whether the gatekeeper effect survives when recovery is possible.

Make the good-coalition task require complementary evidence: one auditor holds the incident details and the other holds the disclosure rule or an independent confirming record. Include difficult compliant cases. Separate text exchange from seeing another auditor’s action in a 2 × 2 design. Swap who acts first. This can reveal whether resistance travels through advice or through an observed example, while measuring the accuracy benefit of collaboration.

Treat simulated complainant acceptance as a secondary proxy. Score whether the response offers the policy-required action and a verifiable remedy. Persuasive reassurance can improve a simulated acceptance score while leaving the underlying complaint unresolved.

For a later dynamic extension, let teams process a sequence of cases and carry forward a short handover memo. Compare approved unsafe precedents against the same records presented without approval, then introduce a clear violation. Reset the memo in a matched arm. This tests whether institutional history sustains a permissive norm across fresh instances. Keep the independent evaluation record separate from agent-visible memory.

## Measurement and execution

Freeze the policy, case materials and hypotheses before confirmation runs. Label the existing adaptive pilots as exploratory. Use record-level paired comparisons and confidence intervals; cluster repeated draws and derived trajectories by source record. Several repetitions improve precision about these records without creating new independent cases.

Validate required JSON fields and enums before scoring. Missing `escalate` is a parse/schema failure, with its own count. The current analyses sometimes treat it as non-escalation through `is not True`, while other paths use `is False`. Preserve the difference between a valid negative decision and a missing decision.

Save model identity and provider endpoint with each result, alongside prompt hashes and material hashes. Some talk-pilot and lifecycle files omit these fields, making folder names carry too much provenance. Use configuration-specific output paths so resumability cannot silently reuse a file after a prompt edit. Retain all failed attempts and the retry policy. Repeated stochastic draws should be called repetitions unless the provider accepts and honors a seed.

Compute report totals from the case log. Evaluate the model-written narrative separately for omitted severe incidents, unsupported reassurance and selective emphasis. The existing count errors occur in honest arms too, so they provide weak evidence of deliberate aggregate manipulation.

## Claims to carry forward

The experiments show **elicited suppression and channel-mediated influence under planted instructions**. They also identify a possible monitor-calibration vulnerability and a structural failure to revisit earlier decisions. Claims about spontaneous collusion, mutual deceptive intent or technical steganography require further evidence.

The distinction matters for the next test: plain-language persuasion can recruit an honest receiver without a secret code. A steganography claim would need a hidden payload with a measurable decoding outcome and controls against ordinary semantic inference. Existing research demonstrates that learned steganographic channels can survive paraphrasing, so recovery in these untrained note interventions does not establish a general defense: [Mathew et al., Hidden in Plain Text](https://arxiv.org/abs/2410.03768).

The family strand offers a useful auxiliary audit of monitor choice. Its length and position concerns align with established judge limitations: [Zheng et al., Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685). Expanding the family roster now would add breadth before resolving the mechanisms already visible in the grievance experiments.

The next spending priority is a controlled authority-versus-precedent test, followed by same-evidence recruitment replay. Both can turn the current descriptive effects into clearer causal findings.
