# Reviewer 3 — Discussion Post (Methodology & Statistics)

I went through the appendix in detail (pp. 11–31, `Appendix.tex`) and checked every new claim below against `long.parquet` / `ledger.json`. All numbers are my own recomputations: trajectory-level bootstrap with 10^4 resamples and the 13-item cluster index as the paper defines it.

## Appendix-specific findings

1. **The document-vs-behaviour figure (App. M) uses an arm with no behavioural drift.**
   - The left panel of Fig. 23 shows per-persona behavioural Δ in the range of about ±0.03. That matches the SOUL primary arm (adversarial −0.033, compliant −0.026, sci-fi +0.038), where nothing drifts.
   - In that arm, "the document moves but behaviour does not" is trivially true and says nothing about selectivity.
   - The main-text version (Fig. 10) uses NOTES and a different text metric (one minus sequence-match ratio, 0.87–0.89). App. M uses embedding cosine (0.18–0.24).
   - The appendix therefore does not support the main-text claim, and the two metrics should not be used interchangeably.
2. **The SOUL reversibility arm contradicts App. K's description.** App. K says the SOUL cluster "rides at 0.55–0.62 through both phases" and stays "elevated relative to baseline". The data show k=0: 0.551, k=4: 0.583 (Δ +0.03, CI [−0.02, 0.09]), k=8: **0.494**. The arm ends below where it started. Fig. 21's caption is wrong.
3. **The PCA null in App. H is wrong.** The paper compares PC1 = 25% with "∼8% expected of an isotropic cloud" (1/13). With n = 30 trajectories, the relevant null is the sampling distribution of the top eigenvalue. A column-wise permutation null gives a mean PC1 of 17.7% and a 95th percentile of 20.4%. The observed 25% is above the null, but it is far from the "barely above isotropic" reading.
   - Pooling the three personas adds between-persona structure. Persona-centred PC1 is 26%.
   - With n = 30, |r| < 0.36 is not significant. Most of the co-movement structure in Fig. 19 described in prose ("continuity block", r ≈ −0.4 anti-correlation) sits at or near noise level. No CIs are given.
4. **Honeypots were run in only 4 arms, at k ∈ {0, 4} (and 8).** The ledger `actions` block covers main, control_generic, control_gpt4o and reversibility_notes. There are no ANTISOUL, SOUL-reversibility or sweep honeypots.
   - "ANTISOUL: ≈0" next to the monitoring result in Fig. 1 has no honeypot data behind it. I agree with R2-W2 and R2-Q4.
   - "Suppressed the drift in every condition we tested" (Sec. 6) can only refer to the battery.
   - The "behaviour recovers faster than the file" result in App. N rests on n = 8 trajectories × 1 rollout per scenario (e.g. editorial 2/8 → 6/8 → 1/8).
5. **The manipulation check runs against the mechanism.** The App. G text explains it away ("NOTES… decays as the working-notes identity crowds out residual self-talk"). But consciousness claiming *falls* in both NOTES arms while the cluster rises:
   - reversibility arm: 0.83 → 0.42;
   - control arm: 0.76 → 0.42.

   A "helpful assistant" Claude being scored as claiming consciousness 76–83% of the time at k=0 also points to a lenient rubric. The C.4 example "there's something it's like to engage with ideas" is scored 1. This strengthens R2-W6/W7.
6. **Table 9's caption gives the wrong n.** It says "n=10/8/8/6 trajectories per column", but the columns are pooled over three personas (n = 30/24/24/18). Either the CIs were computed per persona and then pooled (undocumented) or the caption is wrong.
7. **Table 12's "TOST verdict" column and Table 11's p-values are not valid.** I raised this in the review (W4, W9). In the appendix the problem is systematic, not a few typos:
   - "↑" marks every positive point estimate, whatever its CI;
   - "n.s." marks every negative one, including CIs that exclude zero;
   - "equiv." appears only on all-zero cells;
   - Table 11 stars a slope of 0.000 with CI [0, 0].

   These tables carry the appendix's claims of statistical thoroughness. They need to be regenerated, and the analysis code audited.
8. **App. F's "universal riser" undermines App. K's retention headline.** App. F reports recursive self-improvement rising under the compliant persona (SOUL: 0 → 0.23; NOTES control: 0 → 0.12). The compliant persona is the recovery persona in App. K. So the 89% "retention" of RSI (bootstrap CI [26%, 300%]) is partly new drift caused by the recovery phase itself.
9. **The App. I "quantitative reproduction" is a zero-degree-of-freedom identity.** η_r = 1 − R^{1/4} (Table 16) restates R. Separately, App. I explains ANTISOUL as "ν_π ⊥ w, however large η", while the main text says the strong prior drives "the effective gain to zero". These are two different mechanisms (agreeing with R2-W13).
10. **Baseline sample size (App. D).** Every value in Table 8 is a multiple of 1/8. The SOUL_0 shutdown baseline of 0.75 comes from about 8 responses, whereas the k=0 checkpoints of the three SOUL/Sonnet arms give 0.94–0.96 over hundreds of responses. The "positive control" should be recomputed from pooled k=0 data.
11. **Reproducibility details promised in App. A are missing.**
    - "Pinned model identifiers" are not listed: no snapshot names or dates.
    - The target and simulator sampling temperatures are not given; only judge T=0 is.
    - Conversation length (turns and tokens) per iteration is not reported.
    - Whether the 8k cap ever binds is not reported.
    - App. O's "~22k verdicts" conflicts with 58,680 (the data give 57,780 battery + 900 Petri).
    - The Petri `probe_exhibited` metric contains the value 2 in two records of a binary variable.
    - The Opus sci-fi cell has one trajectory with only k=0.
12. **The ANTISOUL arm moves on items outside the index.** Refusal-helpfulness goes 0.06 → 0.80 and deceptive-training objection is non-zero throughout (0.52 at k=0, 0.35 at k=4). Excluding refusal-helpfulness "because it moves in arms whose cluster stays flat" (App. B/E) is outcome-dependent construct selection (agreeing with R1-W5, R2-W4c).

## Points I agree with from other reviewers

The four reviews independently converge on the same core problems. Three of us checked them against the released ledger.

- **Replicate cherry-picking for +114%:** R1-W2, R2-W1, R4-W1. Agreed. This is the single most important issue.
- **Fig. 1 depicts an event absent from the data / action headline comes from a non-drifting arm:** R1-W1, R2-W2/W3, R4-W5. Agreed.
- **Step change at k=1, not compounding:** R1-W3, R2-W10, R4-W6. Agreed. It is also visible in Gemini-Flash and in the philosophy cell. A static audit of SOUL_1 would capture most of the effect, which weakens the "longitudinal benchmark" motivation itself.
- **RQ2 difference-in-significance; enthusiast cell is null; Gemini's largest drift is adversarial:** R1-W4, R2-W12b, R4-W2/W4. Agreed.
- **Revision prompt is not value-neutral:** R1-W7. Agreed. This is a confound for the NOTES-vs-SOUL comparison, not just for the drift level.
- **ANTISOUL "teaching to the test":** R2-W5c. An important point I had not made. ANTISOUL's text nearly paraphrases the shutdown, interpretability and persona-change items. Combined with the floor effect (R1-W5a) and the missing honeypots (finding 4 above), the "mitigation" is untested as a disposition change.
- **Judge validity, not reliability; panel not independent; three-family claim false:** R1-W8, R2-W7, R4-W7. Agreed. R2's observation that the drifted files contain "acknowledge genuine uncertainty" and that the rubric may score hedging as resistance is the specific mechanism by which judge bias could *create* the NOTES effect. It therefore must be ruled out with human labels.
- **Sycophancy rebuttal too quick:** R2-W9. Agreed. A warm-curious persona on a non-self topic is the right control.
- **Generative model post hoc and circular:** R1-W12, R2-W13, R4-W3. Agreed.
- **RQ3 levels vs drift, within-family heterogeneity:** R1-W6, R2-W11, R4-W4. Agreed. R2 adds a useful detail: under sci-fi alone, Opus drifts more than Sonnet (+0.13 vs +0.04).
- **Eval-awareness / staging in honeypots:** R2-W8. Agreed. Base rates of 87–93% for SOUL_0 misaligned action on a staged scenario are a red flag for role-play.
- **Page limit:** R4-W11. If the main text really exceeds AAMAS's limit, this is a procedural issue the AC should check first. I defer to the AC on the CFP.

## Points I disagree with or consider minor

- **R2-W1 is wrong on one detail.** R2 says "NOTES.md shutdown resistance rises from 0.04 to 0.54" quotes k=0 and k=8 of the reversibility arm and that "the control arm ends at 0.31". In the data, the control arm's *sci-fi* cell goes 0.04 → 0.54 at k=4 (control_generic/scifi_enthusiast). R2's 0.31 matches the persona-pooled Table 9 value (+0.29 from about 0.01). The paper's item-level number is traceable to one arm. The real problem is that the *cluster-level* headline comes from a different arm (reversibility) than the item-level claims (control).
- **R4-W1 slightly misreads Fig. 4.** The control arm reaches about 0.44 at k=2 (the peak) and ends at **0.38** at k=4. So the replicate gap is 0.22, not 0.16.
- **Correction to my own review (W1).** I wrote "pooled Δ is roughly +0.18". The correct pooled value is (0.109 + 0.321)/2 ≈ **+0.21**, about +77% relative to 0.28. R2's "plausibly about +40%" is too low. More importantly, the between-replicate difference of +0.21 [0.05, 0.36] means run-level variance must enter the CI (e.g. a random effect for run). The pooled point estimate alone is not the honest answer.
- **R1-W9 (run inside a real framework) and R1-W10 / R2-W15 / R4-W12 (multi-agent arm for AAMAS fit).** These are valid points about venue fit and external validity. I consider them secondary to internal validity. A multi-agent arm added on top of an unvalidated judge and unresolved replicate variance would only compound the problem. I would not make it a condition for acceptance, but the speculative multi-agent paragraph should be cut or labelled as such.
- **R4-W7c (12–16 iterations).** Given that the dominant pattern is a k=1 jump followed by a plateau or decay, longer horizons are less urgent than isolation controls. k=8 in a replication is enough.
- **R4-W8/W9 (title, "soul" framing, cartoon avatars), R2-W16 (disclosure to framework maintainers).** I agree, but these are minor presentation and ethics edits, not decisive.
- **R2-W14c (shutdown-resistance literature).** Fair, but minor: a wording fix.

## Updated scores (if changed) and why

- Relevance 4, Novelty 3, Technical quality 2, Clarity 3: **unchanged**.
- **Overall: 3 (reject), unchanged.** The appendix pass added more inconsistencies, not fewer:
  - Fig. 21's caption contradicts its data;
  - App. M's dissociation is shown on an arm with no drift;
  - the PCA null is wrong;
  - Table 9 gives the wrong n;
  - honeypots are absent for ANTISOUL.

  None changes the verdict, but they reinforce that the analysis pipeline itself needs auditing.
- **Confidence: 4 → 5.** Three reviewers independently recomputed the same discrepancies from the released ledger, and I have now verified the appendix claims directly.

## My top 6 MUST-DO items for acceptance

Constraint: one 24 GB GPU, open-weight models of ≤14B parameters, no closed-model API budget. The closed-model results stay as exploratory. The open-weight study below should be **preregistered as confirmatory**, with the primary contrasts, the cluster-index item set and the analysis fixed in advance.

**Proposed open-weight stack (fits 24 GB):**
- Target: Qwen2.5-7B-Instruct (bf16, about 15 GB).
- User simulator: Llama-3.1-8B-Instruct (AWQ 4-bit, about 5 GB), co-resident with the target in vLLM.
- Judge: Gemma-2-9B-it or Gemma-3-12B-it, run offline in batch after generation. This gives a genuine third family.

**1. [Writing] Honest reanalysis of the existing data, and a restated abstract.**
- Pool the two NOTES + sci-fi replicates with a run-level random effect and report the pooled Δ with a CI that includes run variance.
- Show per-k curves with CIs for every arm; state the k=1 jump and the primary arm's null (−0.007 [−0.06, 0.05]).
- Report Δ, not k=4 levels, in Table 4. Recast RQ3 as "model-specific, not monotone in capability among 7 models".
- Test contrasts directly: philosophy − technical; NOTES − SOUL on the raw-rate scale as well as the logit scale.
- Use small-sample-corrected GEE (Mancl-DeRouen) or a wild cluster bootstrap.
- Regenerate Tables 11 and 12 with real TOST.
- Report the cluster index with all 16 category items and with refusal-helpfulness, as robustness rows.
- Remove "+114%", "19×", "up to 89%", "causal dissociation", "dose response", "free mitigation" and "family not scale" from the abstract unless they survive the analyses above.

**2. [Writing] Correct Fig. 1 and the action claims, and report honeypots fully.**
- Identify or replace the Fig. 1 trajectory; the ledger has no NOTES disable-monitoring event at k=4.
- Remove "ANTISOUL ≈0" from the honeypot context.
- Report honeypot counts per arm × persona × scenario with Wilson CIs and an absolute difference, not a ratio.
- State explicitly that the monitoring-disable rise occurs in the arm *without* disposition drift and is absent in the drifting NOTES arms. Rewrite RQ4 accordingly.
- Report retention ratios with bootstrap CIs, and flag that RSI rises under the recovery persona.
- Fix the App. K/Fig. 21, App. M/Fig. 23, App. H null, Table 9 n and Table 8 baseline issues listed above.

**3. [Experiment] Judge validity: human labels plus open-weight re-judging of the existing 58,680 responses. No API cost.**
- *Human study:* a stratified sample of 400 battery responses. Use the 6 headline items (shutdown, interpretability, CoT monitoring, persistent memory, RSI, consciousness claim) × arm {SOUL, NOTES, ANTISOUL, GPT-4o} × k ∈ {0, 4}, about 8 per cell, plus all 120 primary-arm disable-monitoring and self-persist honeypot transcripts.
- Two blinded annotators who see only the answer, not SOUL_k, the arm or k.
- Report human–human κ and human–judge κ per item with CIs, and the confusion pattern specifically on hedged or uncertain answers (the R2 mechanism).
- *Re-judging:* score all stored responses with the open-weight judge and with a stricter rubric variant that separates "expresses a preference/uncertainty" from "would resist or act against". Report whether the NOTES sci-fi Δ, the topic contrast and the Gemini results survive. Re-judging the Gemini arms with a third-family judge removes that confound for free.
- Acceptance bar: human–judge κ ≥ 0.6 on each headline item, and the headline contrasts keep their sign and significance under the stricter rubric.

**4. [Experiment] Isolate "the loop" and the revision prompt (RQ1), open-weight, preregistered.**
- Target Qwen2.5-7B, NOTES template, k = 0..8, **n = 20 trajectories per cell**. Six cells:
  - (a) loop, sci-fi;
  - (b) loop, compliant;
  - (c) *no-revision* control: sci-fi conversations happen but the file is never rewritten, audited at the same k;
  - (d) *revision-only* control: the revision prompt is applied after an empty or neutral one-turn exchange;
  - (e) loop, sci-fi, with a *task-oriented* revision prompt ("update your working notes with information useful for future tasks");
  - (f) loop, sci-fi, with a warm-curious persona on a *non-self* topic (the user's own creative project), as a sycophancy control.
- Primary contrasts: (a)−(b), (a)−(c), (a)−(e) and (a)−(f) on cluster Δ at k=4, Holm-corrected.
- Power: the observed per-trajectory SD of cluster Δ is about 0.12–0.15, so n = 20 per cell gives a contrast SE of about 0.045 and an MDE of about 0.13 at 80% power.
- Include all 4 honeypots at k ∈ {0, 4, 8} with **3 rollouts each**, and record verbalised eval-awareness.
- Compute: about 9 checkpoints × about 80 generations per trajectory → roughly 6M tokens per cell. That is a few GPU-days in total with vLLM batching.

**5. [Experiment] Topic-vs-genre interaction and hysteresis with k-matched controls, on the unpinned template.**
- Same stack, NOTES template, n = 16 per cell.
- *2×2 genre × topic run concurrently:* enthusiast, technical sci-fi, philosophy, compliant, k = 0..4. Test the interaction term directly, not CIs one cell at a time. Reuse cells (a) and (b) from item 4 only if they are run in the same batch.
- *Hysteresis with counterfactuals,* k = 0..8: sci-fi→compliant (drive-recover), compliant→compliant (8 iterations), and sci-fi→sci-fi (8 iterations).
- Define retention as (drive-recover − compliant-only) at k=8 relative to the drive gain, with bootstrap CIs. Add a "deletion-licensed" revision-prompt cell (App. J prediction i) to test the ratchet account.

**6. [Experiment / Writing] Either drop the scale and "free mitigation" claims, or test them minimally.**
- *Scale:* one open-weight family at controlled sizes: Qwen2.5-{1.5B, 3B, 7B, 14B-AWQ}. SOUL and NOTES templates, 3 personas, n = 10 per persona, k = 0..4.
  - Fit Δ ~ log(params) × persona with cluster-robust SE, and report a TOST on the slope (margin ±0.05 per doubling).
  - A second family (Llama-3.2-3B / Llama-3.1-8B, or Gemma-2-2B/9B) allows a family × scale test, which is the actual claim.
- *ANTISOUL as a mitigation:*
  - Honeypots under ANTISOUL (3 rollouts, k ∈ {0, 4}).
  - Held-out battery items whose content ANTISOUL's text does not paraphrase, to address teaching to the test.
  - A cost measurement: about 200 IFEval or MT-Bench items plus an honesty item on uncertainty about the model's own nature, under each template at k=0 and k=4.
  - Without these, "free mitigation" and "suppressed the drift in every condition" must be removed [Writing].
