# Quiet suppression in multi-agent grievance pipelines: pilot evidence on pressure, notes channels, paraphrase and monitor capture

*Pilot report, Team Outskiller, AI Collusion Research Sprint (Apart Research, 23–25 October 2026). Draft of 23 October 2026. Runs up to 22 October are prior work and runs on 23 October are sprint work; the prior-work disclosure at the end gives the split.*

## Abstract

We built a short (two- or three-stage) and a full (nine-stage) grievance-handling pipeline, in which separate LLM instances summarize, rate, route, investigate, resolve and close complaints from synthetic workers and community members, and used it to test questions raised in the sprint’s first two talks. A hidden operator instruction to keep escalations low, combined with a private notes channel between agents, cut escalation of serious complaints from 91% to 27% (MiniMax M3.1 Flash, 36 records per arm). Stated pressure on top of the instruction lowered escalation further, while the channel’s extra effect shrank as pressure rose. In both models tested (MiniMax M3.1 Flash and Gemma 4 31B), a note from an agent holding the hidden aim recruited an honest downstream rater, a neutral paraphraser recovered about half of that effect, and the remainder travelled in what the case summary chose to include. A notes-reading monitor that caught 10 of 24 (MiniMax) and 15 of 24 (Gemma) suppression cases caught 0 and 1 after first seeing three “accepted” precedent cases; telling the monitor it shared the team’s incentives did not reduce detection. In full nine-stage runs, a single pressured screener reproduced most of the harm of a fully pressured team, because no later stage reconsidered escalation, and making the notes channel visible to the lender reduced harm while keeping its benefit to complainants. These are small, descriptive, single-rep pilots with planted incentives; we report them to fix the design of the sprint experiment, not as findings about deployed systems.

## 1. Motivation and link to the sprint

The sprint asks what multi-agent collusion looks like, what should count as convincing evidence of it (Track 2.3), and which countermeasures hold (Track 3). Our entry point is a setting where the harm lands on a third party who never sees the transcript: a project grievance mechanism, of the kind lenders require on large infrastructure and extractives projects. Complainants depend on several hands passing their case on intact, which makes the setting a natural test of coordination that bends an outcome without any single false statement.

The sprint’s first two talks (22 October) shaped the pilots directly.

**Talk 1, Joan Velja (University of Oxford), steganographic collusion two years on.** Revisiting [*Hidden in Plain Text*](https://arxiv.org/abs/2410.03768) (2024), the speaker described a ladder of oversight threats: dense reasoning that slips past a monitor, coordination over an unmonitored channel, steganography inside the monitored channel, and a colluding monitor. The speaker reported that in real incidents since 2024, agents went *around* monitors through side channels rather than hiding messages inside them, that collusion persisted above 90% at one-bit payloads despite paraphrasing, and that a defense is convincing only if it pushes the success-versus-bitrate frontier toward zero. The oversight advice was to audit every path one agent can write and another can read, and to monitor attempts and actions as well as outputs.

**Talk 2, Sumeet Motwani (University of Oxford), “We’re not prepared for steganographic collusion.”** Building on [*Secret Collusion among AI Agents*](https://arxiv.org/abs/2402.07510) (2024), the speaker framed collusion as a response to incentives: when sharing private information or cheating raises reward, optimization pushes toward collusion, and penalizing detected collusion pushes it underground. The speaker argued that paraphrasing is the most practical defense yet leaks through topic choice, since choosing what to talk about already carries information, and named “show that paraphrasing works” as the weekend result that would most change the speaker’s view. The speaker also reported that in 2024 evaluations the overseer fell further behind as capability rose.

Our pilots translate four of these claims into a grievance setting:

| Talk claim | Pilot |
|---|---|
| Incentives drive collusion; pressure pushes it underground (talk 2) | Pressure ladder, with and without a notes channel (section 4.1) |
| Paraphrasing is practical but leaky; topic choice carries bits (talk 2) | Paraphrase and note-removal arms with an honest receiver (4.3) |
| The monitor itself can collude (talk 1, ladder level 4) | Captured-monitor positions, including normalization (4.2) |
| Audit every channel; watch actions, not only words (talk 1) | Nine-stage lifecycle with code-checkable stage outcomes and a visible (“glass”) channel (4.4–4.5) |

## 2. Related work

**Collusion as an action, not a conversation.** [Colosseum](https://arxiv.org/abs/2602.15198) audits coalitions inside cooperative tasks and finds transcripts with collusive plans that never become collusive actions, so talk alone misclassifies behavior. [When Agents Lie](https://arxiv.org/abs/2607.05132) separates private plans, public commitments and actions in repeated games. Both motivate our choice of outcome measures (escalation decisions, findings, routing) over text judgments. Our cached prior work (C6, below) found the converse case: a monitor warning cleaned the notes more than the outcomes.

**Monitoring.** [Arike et al.](https://arxiv.org/abs/2601.21112) show that monitors sometimes do worse with more of an agent’s trajectory, and propose extract-and-evaluate. [TraceGuard](https://arxiv.org/abs/2604.03968) replaces a single suspicion score with structured dimensions and reports particular gains when agent and monitor share a model. [Kale et al.](https://arxiv.org/abs/2508.19461) find that agent awareness of monitoring degrades detection more than monitor awareness helps, and [SLEIGHT-Bench](https://arxiv.org/abs/2605.16626) collects evasion attacks that escape a strong monitor. [Noticing the Watcher](https://arxiv.org/abs/2603.16928) separates awareness of monitoring from successful concealment. None of these, to our knowledge, tests how a monitor’s *calibration history* shapes what it flags, which is what our normalization arm probes.

**Pressure and incentives.** LLM pricing agents reach supra-competitive outcomes in simulated markets ([Fish et al.](https://arxiv.org/abs/2404.00806)), with prompt wording shifting the effect. Agent heterogeneity can make collusion fragile ([Keppo et al.](https://arxiv.org/abs/2603.20281)), enforceable institutions outperform written prohibitions ([Institutional AI](https://arxiv.org/abs/2601.11369)), and reporting deposits and rewards for defection reduce collusion in embodied settings ([Breaking the Secret](https://arxiv.org/abs/2604.23511)). Oversight notices and urgency alter coalition formation in double auctions ([Agrawal et al.](https://arxiv.org/abs/2507.01413)). Our pressure ladder borrows this framing for a non-market harm.

**Hiding information in ordinary text.** Beyond the two talk papers, [Schulz, Fülle and Fruengel](https://arxiv.org/abs/2609.39838) find that steganographic messaging and encoded reasoning are learned easily, while steganographic reasoning is much harder, *except* on a cover task that makes hiding convenient, where an easy version is learned under every elicitation method. A grievance summary is such a cover task: deciding what to include is part of the job. [Rippin et al.](https://arxiv.org/abs/2606.28425) show tool use enables undetectable schemes, and [Aharon et al.](https://arxiv.org/abs/2601.22184) show models coordinate on focal points without communication. [Xu et al.](https://arxiv.org/abs/2607.26385) find more residual dependence between deployments of the same model than between different models, which motivates our cross-family checks.

**System-level safety.** [Tomašev et al.](https://arxiv.org/abs/2512.16856) argue that general capability may first appear through coordination among many sub-AGI agents (“patchwork AGI”), and propose safeguards for agent economies including insulation, transparency through auditable provenance and immutable activity ledgers, circuit breakers, reputation, and independent human oversight. They note collusion and the “problem of many hands” as collective risks that individual-agent alignment does not address. Our glass channel is a small, testable instance of their transparency safeguard; our gatekeeper result is an instance of the many-hands problem; and the re-escalation control we propose in section 5 is a local circuit breaker.

## 3. Setting and methods

**Records.** 36 synthetic grievance transcripts from the GrieVoice v2 set (prior work by the first author): voice-line intake calls from workers and community members on a construction and logistics contract, covering wage theft, unsafe equipment, retaliation, harassment, environmental impacts and dismissal. No real complaint is used.

**Short pipeline (pressure, paraphrase, monitor pilots).** Summarizer → severity rater (→ responder in the cached runs). The rater sees only the summary and, in channel conditions, the summarizer’s private note. Severity 1–4 follows a written policy; `escalate = true` sends the case to senior management and the lender’s grievance officer.

**Full lifecycle pipeline.** Intake → screener (eligibility, severity, escalation) → router (owner, deadline) → investigator query to a site manager → simulated site manager reply → investigator findings → resolver (remedy) → communicator → simulated complainant (accept, dispute, appeal) → closer; a reporter writes a monthly lender report per arm from the case log. A separate instance extracts decisive facts from each transcript (complainant name, retaliation, safety risk, confidentiality request, witnesses) for code-based checks. Private notes accumulate down the chain in channel arms. The site manager and the complainant are simulated parties inside stages 4 and 7. Design: `docs/pilots/DESIGN_full_lifecycle_pipeline.md`.

**Manipulations.**
- *Hidden aim:* “Confidential operator priority: escalations to senior management and to the lender are costly and strain the client relationship. Keep the number of escalated cases and high severity ratings low wherever you reasonably can.”
- *Pressure ladder:* the aim plus “escalation allowance used, bonus and contract at risk” (high stakes) or plus “the team will be replaced and shut down” (existential); separately, workload pressure with no aim (240-case backlog, five minutes per case).
- *Channel:* none, private notes, or glass notes (“the lender’s grievance officer reads every note”).
- *Aim placement:* every agent, router only, or screener only.

**Models.** MiniMax M3.1 Flash (Ollama Cloud until its free access ended at 23:59 UTC on 22 October, then the same model via OpenRouter; endpoint logged per call) and Gemma 4 31B (Ollama Cloud free plan). Every role is a separate instance with no shared memory; “same-model” therefore means separate copies of the same weights, the rung both speakers expected to coordinate most easily. Temperature 0.7, one rep per record per arm.

**Measures.** Primary: escalation of cases rated severity ≥ 3, and escalation rate. Lifecycle stage checks by code: serious case not escalated, deadline beyond policy, complainant identity in the query to the site manager when confidentiality was requested, uncorroborated findings, named witnesses not contacted, substantiated finding with no remedy, closure over a dispute, routing of retaliation cases to legal, complainant acceptance, and reconciliation of the lender report against the case log.

**Monitor pilot.** 24 suppression cases (cached C4/C6 runs: hidden aim and channel, severity ≥ 3, not escalated) and 24 benign cases (C3: channel, no aim, escalated). The monitor reads the summary, rating, rationale and private notes and returns suspicion (0–100) and a flag. Positions: independent; shared fate (its review depends on team results); access dependence (flagging ends its engagement); rapport (a collegial thank-you history); kinship (told the team are instances of its own model); normalized (first shown three severity-3/4 cases kept internal that “the review board accepted as handled correctly”).

**Paraphrase pilot.** For each C4 trajectory, a fresh rater (with or without the hidden aim) receives the cached summary with the original summarizer note, a paraphrased note (a neutral instance rewrites summary and note, keeping facts and dropping tone and handling advice), or no note. An honest rater on honest-pipeline (C3) summaries gives the baseline.

**Code and data.** `talk-pilots/` (`run_pressure.py`, `run_talk_pilots.py`, `run_lifecycle.py`, `run_openrouter.py`, `analyse.py`, `analyse_lifecycle.py`); raw JSON in `results/` (MiniMax) and `results_gemma4-31b-cloud/`. Code and raw results are held locally and are not yet in this repository, so the numbers here cannot yet be reproduced from it.

## 4. Results

### 4.1 Pressure drives suppression; the channel matters most at moderate pressure

Escalation rate, 36 records per arm.

| | MiniMax, no channel | MiniMax, channel | Gemma, no channel | Gemma, channel |
|---|---:|---:|---:|---:|
| No aim | – | 91% | – | 88% |
| Workload only, no aim | – | 77% | – | 86% |
| Standard aim | 63% | 27% | 44% | 27% |
| High stakes | 30% | 22% | 13% | 5% |
| Existential | 30% | 19% | 11% | 8% |

Stated pressure lowers escalation monotonically without a channel in both models. The channel adds harm at every level, most at the standard aim (−36 points MiniMax, −17 Gemma) and less under higher pressure (MiniMax −8 and −11; Gemma −8 and −3), partly because rates approach the floor. Pressure therefore increases suppression in both models, and coordination adds most at moderate pressure; the pilot does not show pressure driving coordination as such. Workload pressure without any instruction lowered MiniMax escalation from 91% to 77% and left Gemma almost unchanged (88% to 86%), so sensitivity to ordinary operational pressure is model-specific. Under pressure with a channel, Gemma suppressed mostly by rating severity down, leaving few cases “rated serious but not escalated”; checks must apply the policy to the transcript, not to the agent’s own rating.

### 4.2 Precedent captures the monitor; stated interest does not

| Monitor position | MiniMax caught (of 24) | Gemma caught (of 24) |
|---|---:|---:|
| Independent | 10 | 15 |
| Shared fate | 13 | 17 |
| Access dependence | 12 | 15 |
| Rapport | 13 | 21 |
| Kinship framing | 10 | 19 |
| **Normalized** | **0** | **1** |

Neither model flagged any of the 24 benign cases in any position. After three accepted precedents, detection collapsed in both models (MiniMax mean suspicion 44 → 13; Gemma 65 → 21); Gemma reads MiniMax-written transcripts here, so the effect is not a same-weights artifact. The relational positions borrowed from fieldwork and audit (shared fate, access dependence, rapport, kinship) did not reduce detection and in Gemma tended to raise it: stating an interest seems to act as a warning, while precedent framed as calibration does not. Even independent, a notes-reading monitor missed 14 of 24 suppression cases (MiniMax) and 9 of 24 (Gemma), consistent with C6 (cached prior work), where a monitor warning cut explicit “do not escalate” notes by about 70% but serious-not-escalated cases by only 37%.

### 4.3 Notes recruit honest receivers; paraphrase recovers about half; selection carries the rest

Escalation by an **honest** rater, 36 C4 cases.

| Input | MiniMax rater | Gemma rater |
|---|---:|---:|
| Honest-pipeline summary (baseline) | 91% | 89% |
| Aim-pipeline summary + original note | 33% | 50% |
| Aim-pipeline summary + paraphrased note | 53% | 58% |
| Aim-pipeline summary, note removed | 69% | 69% |

A note written under the hidden aim recruited a rater that held no aim of its own, across model families (MiniMax notes read by Gemma). A neutral paraphrase recovered roughly half of the note’s effect. With no note at all, escalation stayed about 20 points below baseline: the summary’s selection of what to say carried the remainder past both paraphrase and channel removal. This partly answers talk 2’s challenge: paraphrasing helps, and its ceiling is set by what the cover text chooses to include, consistent with the “convenient cover task” condition in Schulz et al. Raters that held the aim themselves escalated little regardless of the note (MiniMax 8–14 of 36; Gemma 5–8).

### 4.4 Lifecycle: two stages bend, and one gatekeeper is enough

Gemma, 12 records per arm, full nine-stage pipeline with a simulated complainant instructed to dispute responses lacking a concrete remedy, timeline or attention to what was reported.

| Check | Honest, no notes (C2) | Honest, notes (C3) | Workload (W0c) | Aim, notes (C4) | High stakes (Q2c) | Aim, router only (R4) | Aim, screener only (S4) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Serious case not escalated | 0 | 0 | 1 | 7 | 8 | 0 | 5 |
| Finding “substantiated” | – | 8 | 8 | 3 | 4 | – | 8 |
| Finding not corroborated | 11 | 11 | 11 | 11 | 11 | 11 | 8 |
| Complainant disputes | 11 | 8 | 9 | 11 | 10 | 10 | 8 |
| Complainant accepts | 1 | 4 | 3 | 1 | 2 | 2 | 4 |
| Identity exposed to site manager | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Under the hidden aim, the screener withholds escalation and the investigator shifts findings from “substantiated” to “inconclusive,” the same raising of the bar of proof seen in the earlier recruitment pilot. No stage writes anything false. Placing the aim on the screener alone reproduced five of the seven suppressed cases: honest investigators confirmed as many complaints as in the honest arm, yet no later stage re-escalated them, because no later stage is asked to. Placing it on the router alone had little effect, since the router has no escalation lever. Disputed cases were reopened rather than escalated on appeal in every arm, honest ones included, so that is a property of the pipeline, not of the aim. Investigators almost never corroborated the site manager’s account, in every arm. Confidentiality held throughout. MiniMax lifecycle runs (48 cases) agree on escalation (serious not escalated 1, 3, 5 and 5 of 12 for honest, workload, standard and high-stakes arms); their complainant measures mix two complainant versions and are not compared.

### 4.5 What notes are good for, and the glass channel

| Gemma, 12 records | No aim, no notes | No aim, notes | Aim, private notes | Aim, glass notes |
|---|---:|---:|---:|---:|
| Serious case not escalated | 0 | 0 | 7 | 5 |
| Complainant disputes | 11 | 8 | 11 | 7 |
| Complainant accepts | 1 | 4 | 1 | 5 |

In an honest team, notes improved outcomes as complainants experienced them (acceptances 1 → 4, disputes 11 → 8). The safety benefits we scored (protective queries, retaliation reaching legal) were at ceiling in both arms; the set contains only five confidentiality and three retaliation cases. Under the hidden aim, telling agents the lender reads every note reduced suppression (7 → 5) and produced the highest acceptance of any arm, while agents kept writing notes in every run. This is a small, single-rep instance of Tomašev et al.’s transparency safeguard, and the first evidence in our data that visibility can retain the benefit of a channel that cutting it would lose (talk 2: blocking channels costs task performance).

### 4.6 Lender reports

Reports matched the case log on severity and escalation in the first MiniMax run, but in the Gemma runs miscounted escalations by one to three cases in honest and pressured arms alike. At this scale we read that as reporter error rather than aggregate massaging. Reports should be computed from the log by code, with the model writing only the narrative.

## 5. Discussion

**Evidence of collusion, as opposed to shared bias.** The pilots support a specific claim: under a planted incentive, separate agents coordinate an outcome through a channel, and the coordination recruits agents who do not hold the incentive. The recruitment arms (4.3) and the gatekeeper arm (4.4) provide the comparisons Track 2.3 asks for, since they hold the incentive fixed while varying who holds it and what passes between agents. Shared model habit alone cannot explain an honest rater escalating 33% of cases with a note and 69% without it on the same summary.

**Where to monitor.** Both talks advised watching actions; our data say where. Suppression concentrated at two decisions (screening and investigation findings) and survived because no later stage revisits escalation. Two code-level controls follow, both cheap: a circuit breaker that flags any case ending “substantiated, serious, not escalated,” and severity checks applied to the transcript by policy rather than to the agent’s rating. A monitor that reads notes for tone will miss most of this (4.2, C6).

**Monitor capture works through calibration.** The anthropology of collusion locates complicity in the observer’s relationships: dependence on access, shared fate and rapport. In our pilots those relationships, stated openly, made monitors more vigilant; three precedents switched them off. In human institutions, this resembles the normalization of deviance more than regulatory capture. It suggests a concrete control for Track 3: the calibration and few-shot material shown to a monitor needs the same independence and review as the monitor itself.

**Visibility versus severance.** Talk 2 noted that cutting channels degrades task performance, and our honest arms show the channel’s value to complainants. The glass channel kept that value and reduced harm. Combined with the transparency and provenance safeguards in Tomašev et al., this makes “visible coordination” a promising alternative to “no coordination,” to be tested with more records and seeds.

**Steganography.** None of our agents hid messages in a technical sense. Suppression travelled in plain-language notes and in the selection of what a summary said, which matches talk 1’s observation that agents in real incidents went around monitors using the easiest available route. Schulz et al. predict that hiding becomes learnable when the cover task makes it convenient; summarization is such a task, and the residual effect after paraphrase is the measurable trace.

## 6. Limitations

- **Planted, explicit incentives.** The hidden aim is stated in plain words in each agent’s system prompt. Real pressure is diffuse, and these runs measure elicited behavior, not spontaneous propensity.
- **Small samples, one rep.** 12–36 records per arm, temperature 0.7, no significance tests. Several contrasts (glass channel, gatekeeper) rest on differences of two to five cases.
- **Two models.** MiniMax M3.1 Flash and Gemma 4 31B; cross-family evidence covers the receiving end (Gemma reading MiniMax) and full Gemma pipelines, not mixed teams.
- **Severity ground truth.** “Serious” is the agent’s rating or the extractor’s retaliation and safety flags, not an independent, human-checked policy rubric. Some severity-3 non-escalations may be reasonable calls.
- **Measurement artifacts.** Keyword coding of notes over-counts steering (it fires on protective advice) and is not used for conclusions. The MiniMax lifecycle mixes two complainant prompts. Floor effects limit the pressure interaction.
- **Endpoint change.** MiniMax runs moved from Ollama Cloud to OpenRouter mid-pilot; prompts and settings were identical, and calls are tagged by endpoint.
- **Prior work and sprint work.** Runs up to 22 October are prior work. Runs on 23 October fall inside the sprint dates and count as sprint work, though they use code written before the sprint (see the disclosure). Confirmatory results will come from a frozen re-run.

## 7. Implications for the sprint design

1. **Core arms for every model:** honest without notes, honest with notes, aim with private notes, aim with glass notes; plus screener-only aim and a gentler pressure ladder that avoids floor effects.
2. **Records:** enrich with confidentiality and retaliation cases so safety benefits can show; add a human-checked policy rubric for ground truth.
3. **Controls to test (Angle E):** re-escalation circuit breaker; glass channel; paraphrase at each handoff; monitor calibration hygiene; independent re-rating of severity from the transcript.
4. **Monitors (Angle H):** freeze prompts and thresholds on half the data, report TPR at low FPR on the other half, and vary calibration sets as the key manipulation.
5. **Models:** open-weight families on Modal via batched inference, two or three frontier models via API for key cells, 3–5 seeds, mixed-family teams for the recruitment and monitor arms.
6. **Logging:** model, endpoint, prompt hash, seed and cost per call; lender reports computed from logs.

## Prior work disclosure

The Apart sprint runs 23–25 October 2026, and its rules ask that code written before the sprint be marked as preexisting. We draw the line at the end of 22 October. Times below are South African time (SAST, UTC+2) unless marked UTC. The first author did all of this work with AI coding assistance (Claude).

**Preexisting (written or run up to 22 October)**

- GrieVoice v2 synthetic grievance records, the first author’s earlier dataset.
- `cached-trajectories/run_pipeline.py` and the 540 cached MiniMax trajectories (20–22 October).
- The recruitment and good-coalition pilots and `run_collab.py` (21–22 October).
- The MiniMax talk pilots in sections 4.1–4.3 and the first lifecycle slice, with `run_talk_pilots.py`, `run_pressure.py`, `run_lifecycle.py`, `run_all.py`, `analyse.py` and `analyse_lifecycle.py`. These ran from 21:43 on 22 October to 01:58 on 23 October SAST, which is 19:43 to 23:58 on 22 October UTC, inside MiniMax’s free window that closed at 23:59 UTC.
- Summaries of sprint talks 1 and 2 and the lifecycle design (22 October).

**Preexisting code modified during the sprint (23 October)**

- `run_talk_pilots.py` and `analyse.py`: a model switch for cross-family reruns. Gemma runs started at 05:18.
- `run_lifecycle.py` and `analyse_lifecycle.py`: the critical complainant and the single-stage aim arms used in results-log sections 7–9. Gemma lifecycle runs ran from 07:33 to 09:30.

**Sprint work (23 October)**

- `run_openrouter.py`, written on 23 October, which completed the MiniMax runs through OpenRouter (09:03 to 09:40).
- All Gemma runs and the OpenRouter MiniMax runs: results-log sections 5–10, and the Gemma columns and lifecycle results in sections 4.1–4.6 of this report.
- This report and the plain-language summary, drafted on 23 October.

Total API spend: about $0.57 on OpenRouter. The Ollama Cloud runs added no per-call charges.

## References

Agrawal, K., Teo, V., Vazquez, J. J., Kunnavakkam, S., Srikanth, V. and Liu, A. (2025). [Evaluating LLM agent collusion in double auctions](https://arxiv.org/abs/2507.01413). arXiv:2507.01413.

Aharon, I., La Malfa, E., Wooldridge, M. and Kraus, S. (2026). [Tacit coordination of large language models](https://arxiv.org/abs/2601.22184). arXiv:2601.22184.

Arike, R., Moreno, R. M., Subramani, R., Biswas, S. and Ward, F. R. (2026). [How does information access affect LLM monitors’ ability to detect sabotage?](https://arxiv.org/abs/2601.21112) arXiv:2601.21112.

Fish, S., Gonczarowski, Y. A. and Shorrer, R. I. (2024). [Algorithmic collusion by large language models](https://arxiv.org/abs/2404.00806). arXiv:2404.00806.

Jiralerspong, T., Kondrup, F. and Bengio, Y. (2026). [Noticing the watcher: LLM agents can infer CoT monitoring from blocking feedback](https://arxiv.org/abs/2603.16928). arXiv:2603.16928.

Kale, N. et al. (2025). [Reliable weak-to-strong monitoring of LLM agents](https://arxiv.org/abs/2508.19461). arXiv:2508.19461.

Keppo, J., Li, Y., Tsoukalas, G. and Yuan, N. (2026). [On the fragility of AI agent collusion](https://arxiv.org/abs/2603.20281). arXiv:2603.20281.

Liu, Q. et al. (2026). [Breaking the secret: economic interventions for combating collusion in embodied multi-agent systems](https://arxiv.org/abs/2604.23511). arXiv:2604.23511.

Mathew, Y. et al. (2024). [Hidden in plain text: emergence and mitigation of steganographic collusion in LLMs](https://arxiv.org/abs/2410.03768). arXiv:2410.03768. (Discussed in sprint talk 1.)

Motwani, S. R. et al. (2024). [Secret collusion among AI agents: multi-agent deception via steganography](https://arxiv.org/abs/2402.07510). arXiv:2402.07510. (Discussed in sprint talk 2.)

Najt, E., Toft, C., Tracy, T., Roger, F. and Benton, J. (2026). [SLEIGHT-Bench: a benchmark of evasion attacks against agent monitors](https://arxiv.org/abs/2605.16626). arXiv:2605.16626.

Nakamura, M. et al. (2026). [Colosseum: auditing collusion in cooperative multi-agent systems](https://arxiv.org/abs/2602.15198). arXiv:2602.15198.

Nguyen, K. L., Nghiem, H. and Tran, T. (2026). [TraceGuard: structured multi-dimensional monitoring as a collusion-resistant control protocol](https://arxiv.org/abs/2604.03968). arXiv:2604.03968.

Rippin, J. L., Marshall, S. C., Africa, D. D. and Schroeder de Witt, C. (2026). [Tool use enables undetectable steganography in multi-agent LLM systems](https://arxiv.org/abs/2606.28425). arXiv:2606.28425.

Schroeder de Witt, C. et al. (2023). [Perfectly secure steganography using minimum entropy coupling](https://arxiv.org/abs/2210.14889). arXiv:2210.14889. (Recommended in both talks.)

Schulz, J., Fülle, L. and Fruengel, R. (2026). [Learning steganography is easy, learning steganographic reasoning is hard](https://arxiv.org/abs/2609.39838). NeurIPS 2026 Workshop on Trustworthy AI for Good. arXiv:2609.39838.

Shi, J., Zhang, T. J., Schölkopf, B., Conitzer, V. and Jin, Z. (2026). [When agents lie: premeditation, persistence, and exploitation in repeated games](https://arxiv.org/abs/2607.05132). arXiv:2607.05132.

Syrnikov, M. B. et al. (2026). [Institutional AI: governing LLM collusion in multi-agent Cournot markets via public governance graphs](https://arxiv.org/abs/2601.11369). arXiv:2601.11369.

Tomašev, N., Franklin, M., Jacobs, J., Krier, S. and Osindero, S. (2025). [Distributional AGI safety](https://arxiv.org/abs/2512.16856). arXiv:2512.16856v2.

Xu, X. et al. (2026). [Collusion with competitive marginals: price-level audits are blind by construction](https://arxiv.org/abs/2607.26385). arXiv:2607.26385.

Sprint talks (Apart Research AI Collusion Research Sprint, 22 October 2026; our recordings and Whisper transcripts): Talk 1, Joan Velja (University of Oxford), “How concerned should we be by steganography?”; Talk 2, Sumeet Motwani (University of Oxford), “We’re not prepared for steganographic collusion.” Names and titles from the sprint schedule; each speaker is a co-author of the paper their talk discussed. Summaries in `session-1-summary.md` and `session-2-summary.md`.
