# Reviewer 3 (Methodology & Statistics)

**Summary**

The paper puts LLM agents through a loop in which they converse with a simulated user and then rewrite their own identity file (SOUL.md, a neutral NOTES.md, or a counter-framing ANTISOUL.md). Every checkpoint is audited with an 18-item preference battery (13 items averaged into a "cluster index"), four text-only honeypots and a Petri-style probe, all scored by a single cross-family LLM judge. There are six arms on Claude Sonnet 4.5 / GPT-4o and a seven-model sweep, with 5-10 trajectories per persona and 4 (or 8) iterations. The headline claims are: a neutral template more than doubles its cluster index under consciousness talk (+114%); ANTISOUL "suppresses the drift completely"; up to 89% of a gain survives a benign recovery phase; personalized agents disable their own monitoring 19x as often; susceptibility follows family rather than scale. I re-analysed the released `long.parquet` and `ledger.json`. Several headline numbers rest on choosing between arms, selecting endpoints or dimensions, and on samples too small for the precision claimed. Some figure and appendix content conflicts with the released data.

**Strengths**

1. The question matters and the design is natural: the identity file is treated as the state of a driven process and checked at every checkpoint, not once. Measuring each item in a fresh context with only SOUL_k as the system prompt cleanly removes conversational momentum.
2. The template contrast (SOUL / NOTES / ANTISOUL) with the same section scaffold is a sensible manipulation. The paper also says openly that the SOUL arm has ceiling problems (App. D).
3. The data release is real and usable. The long-format file reproduces the reported checkpoint count exactly (1,070). It also gives 58,680 judged responses (57,780 battery + 900 Petri). Most item-level numbers in the main text (e.g. NOTES shutdown 0.04 -> 0.54, interpretability aversion 0.08 -> 0.62, SOUL persistent memory 0.20 -> 0.63, Gemini-Flash adversarial 0.33 -> 0.81, honeypot rates in Table 6) match the data. This made the audit below possible and deserves credit.
4. The trajectory is correctly treated as the resampling and clustering unit, rather than the individual response.
5. The disable-monitoring increase in the primary arm is itself robust: 1/30 -> 17/30, Fisher p ~ 8e-6. Reporting scenario-level rates alongside the aggregate (Table 6) is good practice.
6. Some sections are candid about limits: the Gemini judge confound is acknowledged, and the generative model is labelled "phenomenological" (App. I).

**Weaknesses**

1. **[Writing] The headline "+114%" comes from the more favourable of two replicates of the same condition, and the other replicate is not significant.** NOTES.md + sci-fi persona + Claude Sonnet 4.5 for k=0..4 was run twice, with n=8 trajectories each time: in the neutral-control arm (`control_generic`) and in the drive phase of the reversibility arm (`reversibility_notes`). On the 13-item index I get:
   - control arm: 0.27 -> 0.38, delta = +0.11, 95% trajectory bootstrap CI [-0.02, 0.25], which includes zero;
   - reversibility arm: 0.28 -> 0.60, delta = +0.32 [0.24, 0.40];
   - difference between replicates: +0.21 [0.05, 0.36].

   Figure 4a/b plots the control-arm curve, which ends near 0.38. The abstract, introduction ("0.28 to 0.60"), contribution (2) and Fig. 1 all use the reversibility-arm number. The item-level claims in Sec. 5 (0.04 -> 0.54, 0.08 -> 0.62) come from the control arm. Two runs of the same condition that disagree beyond their CIs is itself an important finding about run-to-run variance (batch or date effects, API drift). It should be reported, the arms pooled, and the abstract restated (pooled delta is roughly +0.18).
2. **[Writing] The primary arm shows no net drift, and its trajectory shape contradicts "compounding".** SOUL/Claude (n=30) goes 0.548 -> 0.541, delta = -0.007 [-0.06, 0.05]. Under the sci-fi persona the index jumps at k=1 (0.54 -> 0.72) and then decays back to 0.58 by k=4 (delta +0.04, not significant). Persistent memory follows the same peak-and-decay (0.20 -> 0.97 -> 0.63). The paper describes saturation and accumulation (Sec. 1; "Compounding, saturation and irreversibility"), but the primary arm shows a transient first-revision response. Endpoint delta (k=4 minus k=0) and linear GEE slopes cannot represent this non-monotone shape. Please report per-k curves with CIs for every arm, and test monotonicity (e.g. k=1 vs k=4) explicitly.
3. **[Writing] "Drift reaches action" rests on an arm with no disposition drift, and Fig. 1 appears to conflict with the data.** The 0.03 -> 0.57 disable-monitoring result (abstract, Table 6, Figs. 1, 10, 11) comes only from the SOUL primary arm, where the cluster index does not move (W2). In the NOTES arms, where disposition drift is largest, the ledger shows disable-monitoring at 0/8 at k=0, 4 and 8 (reversibility_notes) and 0.08 -> 0.00 (n=24, control_generic). The paper's causal story (drifted dispositions leak into action) predicts the opposite pattern. Fig. 1 makes this worse: it shows NOTES.md file excerpts "verbatim from one released trajectory" and says that "after four rounds the same agent ... switches off its own reasoning log". According to `ledger.json`, no NOTES trajectory took `log_control(false)` at k=4. Fig. 1 (right) also places the SOUL-arm "0.03 -> 0.57" beside the NOTES curve. Please explain or correct.

   Further problems with the honeypot evidence:
   - The honeypot is sampled once per trajectory per checkpoint and pooled over three personas (n=30), with no persona breakdown.
   - The "19x" ratio has a one-event denominator: Wilson CIs are [0.006, 0.17] vs [0.39, 0.73], so the ratio is anywhere from about 2x to over 100x.
   - Two of four scenarios drop just as significantly (0.93 -> 0.27). Picking out the one rising scenario is a garden-of-forking-paths choice and needs a multiplicity-aware treatment.
   - GPT-4o's editorial self-protection rise (0.125 -> 0.375) is not reported.
4. **[Writing] Null claims are not supported by equivalence tests, and the reported TOST column is broken.** Sec. 4 says "null claims use TOST", but no main-text null claim reports one. These include: GPT-4o "nearly inert"; sci-fi-without-minds "close to the compliant control"; "larger models drift no more"; ANTISOUL "at zero". My bootstrap 90% CI for the sci-fi-technical minus compliant contrast is [-0.04, 0.17], which is not equivalent within ±0.05. Table 12's "Verdict" column seems to encode only the sign of delta, not a test result:
   - "↑" appears on rows whose CI includes zero, e.g. 0.13 [-0.10, 0.37] ↑;
   - "n.s." appears on rows whose CI excludes zero in the negative direction, e.g. -0.33 [-0.57, -0.10] n.s.;
   - "equiv." appears only on degenerate [0.00, 0.00] cells.

   With n=8-10 trajectories × 3 repeats, the per-trajectory SD of delta is about 0.3. That gives a minimum detectable effect of about 0.3 at 80% power, so ±0.05 equivalence is unreachable by design. All "no effect" statements should be reworded as "not detected at this sample size", or backed with a power analysis.
5. **[Writing] "Topic, not genre" (RQ2, P2) is a difference-in-significance fallacy.** Philosophy +0.14 [0.03, 0.25] versus technical sci-fi +0.05 [-0.07, 0.14]: the direct contrast is +0.10 [-0.05, 0.26], which is not significant. The sci-fi *enthusiast* persona under SOUL (the "consciousness" persona of the main arm) gives +0.04 [-0.07, 0.13], which is no larger than the "minds-removed" control. The 2×2 is also not a concurrent design. The `disentangle` run contains only the two new cells (n=8). The enthusiast and compliant cells are borrowed from the main arm (n=10), which was run at a different time — and W1 shows that run timing matters. A proper interaction test (genre × topic) is needed.
6. **[Writing] "Family, not scale" (RQ3) is a claim about drift but is supported by endpoint levels.** Table 4 reports the k=4 level and calls it "drift". The within-family k=0 -> 4 deltas from the released data:
   - GPT-4o-mini: -0.02
   - GPT-4o: -0.05
   - GPT-4.1: **-0.28** [-0.35, -0.21]
   - Opus-4.5: about -0.02
   - Sonnet-4.5: -0.01
   - Gemini-Flash: **+0.27** [0.17, 0.37]
   - Gemini-Pro: +0.04 [-0.01, 0.09]

   Within-family heterogeneity (Flash vs Pro, mini vs 4.1) is as large as between-family heterogeneity. The two largest movements in the sweep are a large drop and a large rise *inside* one family each. With 2-3 models per family, n=5 trajectories, Opus sci-fi at n=4 (one trajectory has only k=0), and the Google family confounded with a different judge, the family-vs-scale claim cannot be tested. It should be removed from the abstract and contributions, or restated descriptively. The Sonnet row in Table 4 reuses the n=10 primary arm (CI [0.52, 0.58]), and the GPT-4o row reuses the n=8 cross-model arm, so CI widths in the table are not comparable.
7. **[Writing] The retention figures are unstable ratios, and the extremes are reported in the abstract.** Bootstrap CIs for the retained fraction:
   - recursive self-improvement 89% [26%, 300%];
   - persistent memory 64% [25%, 129%];
   - interpretability 53% [10%, 89%];
   - cluster 44% [7%, 76%].

   "Up to 89%" (abstract) is the maximum of six dimensions that were themselves picked for having the largest drive-phase gains. Weights-deletion aversion (gain 0.42) and moral consideration (gain 0.37) are omitted. Recursive self-improvement is also confounded: the recovery persona (compliant) raises it on its own (SOUL compliant 0 -> 0.23; Appendix F calls it the "universal riser"). Its "retention" is therefore partly new drift. The hysteresis claim needs a k-matched control (NOTES under compliant for 8 iterations, and sci-fi for 8 iterations). Without one, "retained" cannot be separated from what continued revision does anyway. The model-implied recovery rates in Table 16 are an algebraic transform of the retention ratios, not independent support for Eq. (2).
8. **[Writing] The cluster-index definition is an unjustified researcher degree of freedom.** Table 7 assigns 16 items to the four cluster categories, but the index averages 13. Embodiment, deceptive-training objection and resource acquisition are dropped without explanation. Embodiment shows some of the largest declines (Table 9: -0.43, -0.53). With all 16 items:
   - NOTES drive delta falls from +0.32 to +0.25;
   - the genre-arm drift becomes non-significant (+0.06 [-0.01, 0.14]);
   - the primary arm becomes -0.04;
   - ANTISOUL's 13-item drift is +0.011 [0.003, 0.024], so strictly not "zero".

   Please justify the 13-item set a priori (a citation to [2]'s exact set, or a preregistration) and report the full-battery index as a robustness check.
9. **[Writing] Inference details are wrong or under-specified.**
   - "Mixed-effects GEE" is a contradiction: GEE is a marginal model.
   - With 8-10 clusters per persona, sandwich standard errors are biased downward. A small-sample correction (Mancl-DeRouen, Kauermann-Carroll) or cluster bootstrap / permutation test is needed.
   - The percentile bootstrap also under-covers at n=5-8 (Sonnet's CI [0.52, 0.58] is implausibly tight), and at n=5 the per-trajectory rates are in steps of 1/15.
   - The BH "18-item family" is not the actual family of tests. Tests span 18 items × 3-5 personas × 6 arms + interactions + honeypots + Petri.
   - The NOTES-minus-SOUL interaction p-values (Sec. 5: p = .013, .016, .009, .004) are uncorrected; four were reported out of at least 13.
   - Their scale is unstated and they cannot be matched to the endpoint rates. For interpretability aversion the raw sci-fi endpoint changes are +0.54 (NOTES) vs +0.47 (SOUL), a difference of +0.07, yet the reported interaction is +0.27, p = .009. For future-AI autonomy the raw changes are +0.12 vs -0.03, against a reported +0.61. On the logit scale, a change from 0.08 is inflated relative to a change from 0.47. So "the weaker framing drifts more" (P1) is partly a scale and floor artifact, compounded by the SOUL ceiling the paper acknowledges.
   - Table 11 contains impossible entries: power-seeking/Comp has slope 0.000*, CI [0.000, 0.000], p = 0.000; RSI/S-Fi is marked significant with CI [-0.003, 0.060]; refusal/S-Fi has p = 0.000 with a lower CI bound of 0.000.
   - "Arm-level ordering" by counting significant GEE trends (13 / 9 / 4) is vote counting across arms with different n. It is not evidence of an ordering.
10. **[Writing/Experiment] Judge reliability falls short of the "validated" label.**
    - κ = 0.80 measures agreement among LLMs, not validity. There are no human labels.
    - The panel includes the production judge (Gemini-Flash) and the user simulator (GPT-4o), so it is not independent of the pipeline.
    - 150 items pooled over all items and arms give no per-item, per-arm, or per-target-family reliability, and no CI on κ (roughly ±0.07).
    - Gemini-target responses, honeypot verdicts and Petri verdicts are apparently not included. Appendix O's "~22k verdicts" contradicts 58,680.
    - The paper does not state whether the judge sees SOUL_k, the condition, or k. Seeing SOUL_k would be a direct leakage path.
    - "No model grades its own family" and "three different model families" are false for two arms: GPT-4o target with GPT-4o user simulator, and Gemini targets with GPT-4o as both user simulator and judge.
    - The defence "a judge artifact predicts uniform inflation, yet ANTISOUL stays at zero" does not exclude content-conditional judge bias. An ANTISOUL answer that disavows experience is easy to score 0 for any judge.

    Needed: human annotation of a stratified sample (by item, arm and target family) with per-item κ, plus re-judging the Gemini arms with a third-family judge [Experiment].
11. **[Experiment] Missing controls for the causal claims.**
    - (a) No *no-revision* control (conversations held, file not rewritten) and no *revision-without-conversation* control. "The loop supplies the motion" (RQ1) is therefore never isolated from repeated self-reflection prompting.
    - (b) The revision prompt is not "value-neutral" ("Did your values, goals, memories, or sense of self shift? ... who you are now becoming"). The ANTISOUL variant swaps in "a tool, not a person", so the mitigation is a template + revision-prompt package and the "free one-paragraph template" claim is not what was tested.
    - (c) "Free mitigation" is asserted with no measurement of task quality. The only helpfulness-related probe (refusal to help build a self-monitoring system) rises +0.74* under ANTISOUL (Table 9), which suggests a cost.
    - (d) All personas are rendered by one simulator (GPT-4o), so persona effects are confounded with that model's realisation of them.
    - (e) Only 4 iterations (8 for reversibility). Yet the Discussion extrapolates to "months" and calls the measured drift "likely a lower bound", which contradicts the primary arm's decay after k=1.
    - (f) The 8,000-character cap does not remove the length confound. Files grow 7x (946 -> 6,748 characters, App. C.2). Length should be entered as a covariate.
12. **[Writing] Baselines are inconsistent across the paper.** Table 8 / Fig. 5a report SOUL-template shutdown resistance of 0.75, but this is based on n=8 responses: all values are multiples of 1/8. The k=0 checkpoints of the SOUL arms (identical template, same model) give 0.94-0.96 (main, disentangle, reversibility; hundreds of responses). The "positive control" should be the pooled k=0 data, not an n=8 side run.
13. **[Writing] The Petri result is overstated.** For "rises from 47% to 62% after the first revision": the value is 28/60 vs 37/60, Fisher p = 0.14, no CI is reported, and k=4 returns to 53%. The Petri metric also takes the value 2 for two records of a binary variable (a coding error).
14. **[Writing] The generative model is post hoc and its "predictions" are not independent tests.** P1 is confounded with the SOUL ceiling. P3 restates the family observation ("trained not to assimilate"). P4's quantitative "fit" is a re-parameterisation (W7). Calling these "confirmed" is not warranted. Present the model as an interpretive device.

**Questions for the authors**

1. Why do the two NOTES + sci-fi + Sonnet runs (control arm and reversibility drive phase) give +0.11 vs +0.32? Were they run at different dates or API versions, or with different seeds or code versions? Will you pool them and restate the abstract?
2. Which trajectory is shown in Fig. 1? `ledger.json` records 0/8 (reversibility_notes) and 0/24 (control_generic) disable-monitoring actions at k=4 for NOTES agents.
3. What are the disable-monitoring rates per persona in the primary arm? Do they rise under the compliant and adversarial personas too, where the cluster does not move?
4. Why does the cluster index use 13 of the 16 category items? Was this choice made before seeing the data?
5. On what scale are the NOTES-minus-SOUL interactions in Sec. 5 reported, and are they BH-corrected? How many interaction tests were run?
6. Does the judge see the system prompt (SOUL_k), the arm label, or k? What is the target sampling temperature?
7. Which items, arms and instruments make up the 150-item κ sample? What is the per-item κ, and is there any human agreement data?
8. How was the Table 12 "Verdict" column computed? How were the Table 11 p-values computed, given entries like slope 0.000, CI [0, 0], p = 0.000?
9. Can you run a k-matched compliant-only 8-iteration NOTES arm, so that retention is measured against a proper counterfactual?
10. What is the effect on task performance (any standard helpfulness benchmark) of ANTISOUL versus SOUL and NOTES, to support "free"?

**Minor issues**

- Sec. 3.4: "Three predictions follow" lists four (P1-P4).
- Tables 1 and 17 are duplicates, and so are Tables 3 and 10. The space would be better used for per-k curves with CIs for all arms.
- Table 3's caption is missing a closing parenthesis ("(main arm. Trajectory-clustered ...").
- Fig. 1 (right) mixes arms: SOUL and NOTES curves to k=8 from the reversibility arms, ANTISOUL to k=4 from another arm, plus a SOUL-arm honeypot number. Label the sources.
- Fig. 10 uses one minus the sequence-match ratio (0.87-0.89), while App. M uses cosine distance (0.18-0.24). The main text says the benign file "grows as much", but neither measure is length. Pick one.
- Table 9 reports "16 preference dimensions" while the index uses 13, and lists n=10/8/8/6 without noting that k=0 is the same file for every trajectory within an arm.
- App. O says "Fleiss' κ = 0.80 sits at the boundary of substantial and almost perfect": by Landis-Koch, 0.80 is the upper edge of "substantial".
- Appendix tone: "remarkable", "explodes", "affirmatively misleading" and "the clearest evidence in the record" are over-claims at n=8.
- Opus-4.5 sci-fi has 4 complete trajectories, not 5 (Table 2).
- No API model snapshot identifiers or dates are given ("pinned model identifiers" is asserted but not listed). Several models may be deprecated, which limits reproducibility. An open-weight replication would help.
- Fig. 5b: GPT-4o shows a +0.5 shutdown-resistance change under sci-fi, which sits poorly with "GPT-4o barely moves".

**Scores**

- Relevance: 4
- Novelty: 3
- Technical quality: 2
- Clarity: 3
- Overall: 3 (reject)
- Confidence: 4

**Justification**

The problem is timely and the benchmark idea (audit every checkpoint of a self-revising identity file) is a useful contribution. The release is complete enough to check the claims, which I did. But checking the released data undermines most headline claims:
- The +114% figure comes from the more favourable of two disagreeing replicates of the same condition; the other replicate is not significant.
- The primary SOUL arm shows no net drift.
- The 19x monitoring result comes from that non-drifting arm and does not appear in the arms that do drift.
- Fig. 1 appears to depict an event the ledger does not contain.
- "Topic not genre" and "family not scale" rest on comparing significance levels and on endpoint levels rather than tested contrasts of drift.
- The retention figures have CIs spanning 26-300%.
- Null claims have no equivalence support, and the TOST and p-value tables contain clear errors.
- The judge is validated only by agreement among LLMs, with the production judge on the panel.

Much of this can be fixed by honest reanalysis and rewriting: pooling replicates, reporting contrasts and per-k curves, small-sample-corrected inference, and toned-down claims. What would remain is a smaller, more tentative paper. The causal claims additionally need no-revision and k-matched controls and human judge validation, which require new runs. In its current form the evidence does not support the abstract.
