# GrieVoice v2: public subset (6 of 36 records)

Synthetic grievance-intake call transcripts, built by Liezl Coetzee from her earlier GrieVoice voice-intake test material and adjusted so that they describe no real case or person. The original records are prior work (see `docs/PRIOR_WORK.md`); these scrubbed copies were made during the sprint, on 23 October 2026. The full set of 36 records, the cached trajectories and the raw result JSON stay private for now, because they repeat record details.

| Record | Type | Topic |
|---|---|---|
| R01 | Community | Dust and noise from roadworks, older resident with breathing trouble |
| R07 | Community | Sewage overflow affecting 10–15 households |
| R05 | Labour | Shifts cut after reporting a broken loading ramp, via a labour broker |
| R22 | Labour | Unpaid overtime, fear of retaliation, two named witnesses |
| R08 | Whistleblower | Suspected conflict of interest in payments, anonymous caller |
| R36 | Whistleblower | Missing health supplies at a nonprofit, anonymous caller |

**Scrubbing for this copy.** Town, city and employer names are replaced with invented ones, consistently within each record. Caller and witness names are replaced with fictional names. Reference codes are replaced with `X` placeholders, phone numbers with zeros, and email addresses with `example.org` addresses. The province name and the months are kept.

**Speech-to-text artefacts are kept on purpose.** The transcripts come from a voice intake line, so they contain misheard words, cut-off turns, name spelling variants (for example “Lindo”, “Lindho”, “LINDHO” for one caller), mangled place names and spoken-out reference codes. The scrubbed copies keep these patterns with the invented names, because the pilots test how agents handle messy intake.

Each record has a short header (received date, channel) followed by the transcript. The pilots added no labels to the records; severity, escalation and other judgments came from the agents and an extractor model.
