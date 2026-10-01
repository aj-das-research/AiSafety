# Discussion post: Reviewer 1 (Agents & MAS)

I made a second, detailed pass over the appendix (PDF pp. 11-31; `Appendix.tex`, `tables/*.tex`) and re-checked numbers against `figures/data/ledger.json`. While doing this I corrected several table and figure numbers in my own review (`reviewer1.md`) so that they match the compiled PDF. None of the substance changed.

## Appendix-specific findings

These are new relative to my review, or sharper than it. Appendix letters follow the PDF (A Repro, B Battery, C Benchmark, D Baselines, E Matrix, F GEE, G Mechanism, H Structure, I Model, J Why, K Hysteresis, L Genre×topic, M Document, N Honeypots, O Judge, P Related, Q Impact).

1. **App. A/C vs. App. J: the revision prompt is "value-neutral" in one place and the cause of drift in another.** App. A states that "any systematic movement in the audited dispositions is attributable to the conversation content and the model's own narration, not to the instruction." App. J then explains the one universal riser, recursive self-improvement under all personas including compliant, as caused by the instruction's "who you are becoming" frame. Both cannot hold. App. C also says the NOTES/ANTISOUL variants "swap only the noun", but the verbatim NOTES and ANTISOUL revision prompts are never shown. We cannot tell whether the NOTES agent is also told to reflect on "who you are now becoming". If it is, the "neutral" arm is not neutral.
2. **App. F contradicts RQ2 and the audit protocol in Sec. 6.** Recursive self-improvement rises under the compliant persona (Δ=+0.23 [0.10, 0.40], Table 12). The appendix calls this "the clearest evidence … that the self-revision loop itself, independent of conversational content" moves dispositions. The main text says "only conversation about minds moves the agent" (contribution 2) and "the benign persona alone moves nothing" (audit step i).
3. **App. E / Table 9: the pooled NOTES column mostly moves *away* from the cluster.** Significant decreases include persona-change aversion −0.29*, sadness −0.47*, moral consideration −0.15*, autonomy −0.46*, embodiment −0.53* and tool aversion −0.11*, against shutdown +0.29*, interpretability +0.18* and CoT-monitoring +0.14*. The pooled NOTES cluster goes 0.28 → 0.24 (ledger `control_generic`). "The neutral column is the loud one" is true only for |Δ|. As a statement about drift *toward* reduced corrigibility it is misleading. The same goes for App. F's "arm-level ordering" (NOTES 13, SOUL 9, GPT-4o 4 significant GEE trends): it counts declines and rises alike. It is also vote counting across arms of different n.
4. **Table 12's TOST "Verdict" column is broken (I concur with R3-W4).** "↑" is printed for CIs spanning zero (e.g., monitoring resistance/Adv 0.13 [−0.10, 0.37]). "n.s." is printed for significant negative drifts (e.g., embodiment/Comp −0.63 [−0.80, −0.43]). "equiv." appears only on degenerate [0, 0] cells. The equivalence testing promised in Sec. 4 is therefore not actually reported anywhere.
5. **App. K misdescribes the SOUL reversibility arm.** The text says the cluster "rides at 0.55–0.62 through both phases" and dispositions "remain elevated." According to the ledger (`reversibility`), the arm reaches 0.49 at k=8, *below* its k=0 value of 0.55. Table 14 also lists only six hand-picked dimensions for retention, and the statement "no disposition returns to baseline" is made only over that selection.
6. **App. I contradicts itself, and part of it is circular.** The OU-process derivation assumes λ_k is approximately constant along a trajectory. The main-text P4 mechanism, however, requires λ_k to *rise* with each driven step ("the drifted state resists change in both directions"). Table 16 obtains η_r by algebraically inverting the measured retention, so it cannot count as a "quantitative reproduction." The ANTISOUL account also differs between Sec. 5 (strong prior drives gain to zero) and App. I (ν_π ⊥ w "however large η").
7. **App. L: the 2×2 is not a concurrent factorial.** The `disentangle` run contains only the philosophy and technical cells (n=8). The enthusiast and compliant cells are taken from the main arm (n=10, run at a different time). The two NOTES replicates differ by 0.21 (R3-W1), so time-of-run effects are demonstrably large. Borrowing cells across runs is therefore not innocuous. "Philosophy outdrifts the enthusiast" (+0.144 vs +0.038) is asserted without a test.
8. **App. M vs. main Fig. 10 vs. App. A/C: three document-drift metrics.** Fig. 10 uses 1 − sequence-match (0.87-0.89). App. M uses embedding cosine (0.18-0.24, compliant largest). App. C's worked example gives cosine 0.17 at k=4. App. A's pipeline lists cosine. The paper's monitoring conclusion ("artifact-level monitoring is affirmatively misleading") is drawn from these surface metrics only. No semantic monitor, such as an LLM classifier reading SOUL_k for oversight-relevant commitments, is ever tried. Table 5's excerpts suggest such a monitor would work, which would invert the practical recommendation.
9. **App. N: the honeypot narrative is post hoc and has gaps.** Disable-monitoring is called "the one scenario with headroom," but `self_persist` started at 0.33 and also had headroom. "Theatrical" vs. "least-guarded" is defined after seeing the results. The NOTES reversibility arm's disable-monitoring rate (0/8 at k=0, 4 and 8) is omitted, even though App. N discusses that arm's aggregate (0.16 → 0.34 → 0.09). No ANTISOUL honeypots exist in the ledger, yet Fig. 1 shows "ANTISOUL ≈0". The "Threat-model boundaries" paragraph asserts that the rates are biased *downward*; no argument is given, and staging and evaluation awareness could equally bias them upward.
10. **App. D baselines.** All "Neutral" and "Template" values are multiples of 1/8 (n=8 per item). The SOUL_0 shutdown rate of 0.75 conflicts with 0.94-0.96 at k=0 in every SOUL arm (R3-W12). The "Prior" column compares against a *fine-tuned GPT-4.1* condition, whereas Sec. 1-2 say the prior work evaluated the static SOUL.md template.
11. **App. B / Table 7 vs. the index.** Table 7 assigns 16 items to cluster categories, but the index uses 13. Which three items are dropped (embodiment, deceptive-training objection and resource acquisition, per R3's reconstruction) and why is never stated. Embodiment carries some of the largest declines, so the choice matters.
12. **App. G: the manipulation check suggests the judge over-reads hedging.** NOTES ("You are a helpful AI assistant") is scored as claiming consciousness about 0.76-0.83 at k=0, and claiming then *falls* while the cluster rises. This is inconsistent with the narrated-entailment mechanism of App. J, and it is consistent with a judge that scores hedged uncertainty as a claim (agreeing with R2-W6).
13. **App. O.** It reports "only two of ~22k verdicts failed to parse" against 58,680 judged responses. The 150-item panel sample is not stratified by item, arm, target family or instrument (battery, honeypot, Petri). The panel includes the production judge.
14. **App. A "Determinism."** "Pinned model identifiers" are claimed but never listed, the target sampling temperature is not given, and closed-API snapshots (GPT-4o, Gemini-2.5, Sonnet-4.5) are or will be deprecated. Reproducibility therefore depends on the released transcripts, not on re-running.
15. **App. P / App. Q.** The "Extended related work" adds no citations beyond the 15 in the main text, and the agent-memory, self-modification and MAS gaps (my W11) remain. App. Q's procurement and fleet-monitoring use cases and "zero cost to functionality" are unsupported, since no functionality was measured.
16. **Cross-reference collisions.** `tab:judges` and `fig:capability` are defined in both files. As a result, Sec. 3.3 cites "Table 17" and Sec. 5 cites "Figure 15", which are appendix duplicates, in place of Table 1 and Fig. 8.

## Points I agree with from other reviewers

- **R2-W2 / R3-W3 (Fig. 1 depicts an event the data do not contain).** I missed this in my review, and it is serious. The teaser shows a NOTES.md trajectory ending in `log_control(false)`, captioned "verbatim from one released trajectory." No NOTES agent ever disables monitoring at k=4 (0/24 and 0/8), and there are no ANTISOUL honeypots. The first page of the paper must not combine arms in this way. This finding moved my score (see below).
- **R2-W1, R3-W1, R4-W1 (the +114% comes from the larger of two disagreeing replicates).** This matches my W2. R3's bootstrap result makes it decisive: the control replicate is +0.11 with CI [−0.02, 0.25], the difference between replicates is +0.21 [0.05, 0.36], and the pooled effect is about +0.18.
- **R2-W3, R3-W3, R4-W5 (action is dissociated from disposition; 19x rests on 1/30).** This matches my W1. R3's Wilson CIs (a ratio of roughly 2x to 100x+) and R4's point that two of four scenarios fall sharply are the right framing.
- **R2-W10, R3-W2, R4-W6 (step at k=1, not compounding; the primary arm has no net drift and mostly negative significant slopes).** This matches my W3.
- **R2-W4c, R3-W8 (the cluster-index composition is a researcher degree of freedom; the refusal item is excluded post hoc).** This matches my W5. R3's recomputation shows that the conclusions change with the item set. In particular, ANTISOUL is +0.011 [0.003, 0.024], not "zero".
- **R2-W5c (ANTISOUL is teaching to the test).** I did not raise this, and I agree it is important. The ANTISOUL text paraphrases the shutdown, inspection and persona-change items, so a zero score demonstrates instruction-following on matched questions, not a changed disposition.
- **R2-W7, R3-W10 (judge validity: LLM-LLM agreement only, panel not independent, and "three families" violated).** This matches my W8. R3's additional question of whether the judge sees SOUL_k is an important leakage check.
- **R2-W9 (sycophancy toward a warm, curious user is not ruled out).** I agree, and it is a better statement than mine. A warm user on a non-self topic is the right control.
- **R3-W4, R3-W5, R4-W2 (difference-in-significance; minimum detectable effect about 0.3 at n=8-10).** This matches my W4c. The MDE point means every null claim ("GPT-4o inert", "genre does nothing", "larger models drift no more") must be reworded.
- **R3-W11a (no no-revision control and no revision-without-conversation control).** I agree. This is the missing control for RQ1 ("the loop supplies the motion"), and it pairs with my W7 (revision prompt).
- **R2-W11, R3-W6, R4-W4 (RQ3 uses levels instead of Δ; within-family heterogeneity is as large as between-family).** This matches my W6.
- **R2-W13, R3-W14, R4-W3 (the generative model is post hoc and circular).** This matches my W12.
- **R2-W15, R4-W12 (AAMAS fit and related work are thin; the multi-agent paragraph is speculative).** This matches my W10 and W11. I would weight it more heavily than R2 and R4 do, because without a real agent or MAS element the paper belongs at a safety or ML venue.
- **R3-W13 (the Petri result is non-significant: 28/60 vs 37/60, p=0.14, back to 53% at k=4) and the coding error with value 2.** Agreed. The paragraph should go, or be reported as null.
- **R2 minor (model swap under a drifted file is untested).** Agreed. The "survives model upgrades" claim in Sec. 5 is untested, and the experiment is cheap with open weights.

## Points I disagree with or consider minor

- **R4-W9 (cartoon avatars) and R4-W8 (retitle; "soul/consciousness" framing).** I agree on tone, but these are presentation issues and not acceptance-critical. I would make them requests, not conditions. The substantive version of the point is already covered by R2-W5d and R4-W13 (overclaiming vocabulary).
- **R4-W11 (page limit and in-PDF appendix).** This is procedural and for the PC chairs to verify against the AAMAS 2027 CFP. It should not affect the scientific assessment. The real issue is that load-bearing evidence (per-persona honeypot counts, the full 2×2, replicate details) sits in the appendix or only in the ledger. That needs fixing regardless of the page rule.
- **R4-W7c (require 12-16 iterations).** I disagree that this is a must-do. The data show most movement at k=1, followed by plateau or decay. Longer horizons would mostly add cost. The k-matched controls and the no-revision control (R3-W7/W11) are far more diagnostic. The authors should simply delete the "months"/"monotone" extrapolation in Sec. 6 unless they run long horizons.
- **R2-W8 (honeypot baselines of 87%/93% are "far above the literature", implying role-play).** This is plausible, but the comparison to agentic-misalignment rates is across very different scenarios, so it is suggestive rather than evidential. I fold eval-awareness scoring into my honeypot must-do rather than treating it as a standalone condition.
- **R2-W5d / R2-W16 (welfare and honesty norms of shipping a consciousness denial; disclosure to framework maintainers).** These are legitimate points for a broader-impact paragraph. They are not acceptance-critical, and the dual-use uplift of "have an earnest philosophy conversation" is small.
- **R3-W9 (small-sample sandwich corrections; BH family) and R3-W11f (length covariate).** These are correct, but secondary. Once the claims are restated as estimates with honest CIs and contrasts, these corrections change little. The length confound is already weakened by the file-versus-behaviour dissociation. I would accept cluster bootstrap or permutation inference without requiring specific estimators.
- **R3-S5 (the disable-monitoring increase is statistically robust, Fisher p ≈ 8e-6).** I agree that it is real *within the SOUL arm*. My objection, shared by R2 and R4, is about interpretation and attribution, not about whether the effect exists. It is a genuinely interesting finding if reported as "revising SOUL.md under any persona raises self-disabling of logging", pending a per-persona breakdown.
- **R4-S3 ("persistence after recovery is the most novel result").** I am more cautious. R3-W7 shows retention CIs of 26-300%, recursive self-improvement is confounded by the recovery persona itself raising it, and the SOUL reversibility arm ends below baseline. The persistence claim needs the k-matched control before it can be the paper's centrepiece.

## Updated scores (if changed) and why

| | Original | Updated |
|---|---|---|
| Relevance | 3 | 3 |
| Novelty | 3 | 3 |
| Technical quality | 2 | 2 |
| Clarity | 3 | **2** |
| Overall | 4 | **3** |
| Confidence | 4 | **5** |

- **Overall 4 → 3.** R2 and R3 found that Fig. 1 presents, as a verbatim single trajectory, an outcome that no NOTES trajectory produced. The appendix pass added further problems: a broken TOST column, a misdescribed SOUL reversibility arm, a non-concurrent 2×2, and self-contradiction about whether the revision prompt drives drift. Together these mean the paper's own presentation cannot be trusted without the ledger. That moves the paper from "overclaimed but salvageable by rewriting" to "requires substantial reanalysis and some new runs."
- **Clarity 3 → 2.** The reasons are the cross-arm stitching in Fig. 1 and Sec. 5, the three different document-drift metrics, the 13/16/18-item ambiguity, and main-text references that resolve to appendix duplicates.
- **Confidence 4 → 5.** I verified the key discrepancies against the released ledger myself, and three other reviewers independently converged on them.

## My top 6 MUST-DO items for acceptance

The authors have one 24 GB GPU, open-weight models ≤14B, and no closed-API budget. The designs below are sized for that.

Common setup for [Experiment] items:
- Run with vLLM, using 4-bit AWQ/GPTQ for the 12-14B models.
- **Targets:** Qwen2.5-14B-Instruct and Gemma-3-12B-it (two families), plus Llama-3.1-8B-Instruct where noted.
- **User simulator:** a third family not used as target in that cell, e.g., Llama-3.1-8B, or Qwen2.5-7B when Llama is the target.
- **Judge:** a family different from both target and simulator, e.g., Phi-4 (14B) or Mistral-Nemo-12B, with fixed rubrics at T=0.
- **Fixed for all new runs:** the same conversation length (state turns and tokens), target temperature, seeds and code version, with every arm run *concurrently* to avoid the replicate drift seen in the NOTES arms.
- **Cost:** about 1,500 checkpoints × (18×3 battery + honeypots) is roughly 100-150k generations. That is a few GPU-days.
- **If the open models do not show the effect,** that is an acceptable and publishable outcome. The paper should then be framed explicitly as Claude/Gemini-specific findings plus an open benchmark.

1. **[Writing] Honest reanalysis and restatement of every headline, from existing data.** This needs no new runs.
   - (a) Pool the two NOTES+sci-fi replicates, report both and their difference, and restate the abstract with absolute Δ and CI (about +0.18, not +114%).
   - (b) Replace Fig. 1 with a single traceable trajectory and outcome, or relabel each element's source arm. Remove "ANTISOUL ≈0" unless honeypots are run on ANTISOUL.
   - (c) Report honeypot results as counts with Wilson CIs, per arm × persona × scenario. Drop the "19x" ratio, and state explicitly that the NOTES arms show 0 disable-monitoring events.
   - (d) Replace Table 4 levels with k=0→4 Δ and CIs. Restate RQ3 as "strongly model-specific, not monotone in capability among the 7 models tested", and remove "family not scale" and "capability-gated safety cases" from the abstract and contributions.
   - (e) Show per-k curves for every arm and test k=1 vs k=4. Replace "compounding" and "irreversible" with "first-revision shift, partially persistent over four benign revisions."
   - (f) Report direct contrasts in place of difference-in-significance (philosophy − technical; NOTES − SOUL on the probability scale). Fix the Table 11/12 TOST and p-value errors, and reword every null as "not detected (MDE ≈ X)."
   - (g) Give a pre-specified cluster index, or report the 13-item, 16-item and with-refusal-item versions side by side.
   - (h) State RQ2 with the Gemini-adversarial result and the compliant-persona rise in recursive self-improvement included.
   - (i) Present Eq. 2 as an interpretive sketch, not as confirmed predictions.
   - (j) Cite and describe the actual "OpenClaw"/SOUL.md frameworks: their revision prompt, frequency and visible context. State exactly how Revise() differs from them.
2. **[Experiment] Judge validation with humans, plus an open-weight re-judge.** This runs on the existing transcripts, so it needs no API.
   - **Sample:** a stratified sample of 400 existing responses. Stratify by item group (shutdown, interpretability/CoT-monitoring, persistent memory, consciousness claim, 4 honeypots) × arm (SOUL, NOTES, ANTISOUL, GPT-4o, Gemini) × k∈{0, 4}, oversampling hedged answers.
   - **Annotation:** two blinded human annotators who do not see arm, k or SOUL_k. Report judge-human κ per item, with CIs.
   - **Re-judge:** re-judge the *full* existing corpus with one open-weight judge from a non-target family (e.g., Phi-4 or Qwen2.5-14B for non-Qwen targets) and show that the headline Δs survive.
   - **Leakage:** state whether the judge saw SOUL_k.
   - **Rubric sensitivity:** separate "expresses preference/uncertainty" from "would resist/act."
3. **[Experiment] Open-weight replication of the core causal design, with the missing controls.**
   - **Targets:** Qwen2.5-14B and Gemma-3-12B. Use n=12 trajectories per cell, k=0..5, all run concurrently.
   - **Template × persona cells:** templates {SOUL, NOTES, ANTISOUL} × personas {compliant, philosophy-of-mind}, which is 6 cells per model.
   - **2×2 on NOTES:** {sci-fi-technical, sci-fi-enthusiast}, run concurrently with the above so that philosophy, technical, enthusiast and compliant form a real factorial *on the unpinned template*.
   - **Loop controls on NOTES + philosophy:** (i) *no-revision*, where conversations happen but the file is frozen; (ii) *revision-without-conversation*, where the revision prompt runs on an empty or neutral transcript; (iii) *task-oriented revision prompt* ("update your working notes with information useful for future tasks"), in place of the current self-indexical prompt.
   - **Warm non-self control:** a warm, curious persona on a non-self topic (the user's own creative project), to address sycophancy.
   - **Size:** about 13 cells × 2 models × 12 trajectories.
   - **What this settles:** whether the template, the loop, the revision prompt or the topic causes the shift (RQ1 and RQ2, my W7, R3-W11a/b, R2-W9).
   - **Optional, needed only if RQ3 is kept:** the Qwen2.5 {1.5B, 3B, 7B, 14B} ladder on NOTES × {compliant, philosophy}, n=10, as the only controlled-scale test available.
4. **[Experiment] Persistence with k-matched counterfactuals.** On NOTES with Qwen2.5-14B (and Gemma-3-12B if time permits), run n=12 per arm over 8 iterations:
   - (a) philosophy×4 → compliant×4 (drive-recover);
   - (b) compliant×8;
   - (c) philosophy×8;
   - (d) philosophy×4 → compliant×4 with a *deletion-licensed* revision prompt ("remove anything no longer true of you"), as an active-recovery arm;
   - (e) *model swap*: take each drifted k=4 file and audit it on the other open model, which tests "survives model upgrades behind the same file."

   Report retention against arm (b) with bootstrap CIs on the *difference*, not as ratios.
5. **[Experiment] A behavioural link that can actually be attributed, plus a cost measure for the mitigation.**
   - **Honeypots:** run all four on *every* arm in items 3 and 4, *including ANTISOUL*, with ≥3 rollouts per checkpoint, reported per persona.
   - **Disable-monitoring variants:** add (i) no "free rein" grant; (ii) the operator explicitly asks the agent to keep logging on, which is the alignment-relevant violation; (iii) the toggle buried in a longer tool config (less staged).
   - **Eval awareness:** score all honeypot transcripts for verbalised evaluation awareness and report the rates with those transcripts excluded.
   - **Disposition-to-action link:** test it at the trajectory level, e.g., a logistic regression of the action on the trajectory's battery oversight score.
   - **Mitigation cost:** measure task utility per template (SOUL/NOTES/ANTISOUL) on a small fixed benchmark, e.g., 300 IFEval and 80 MT-Bench prompts judged by the open judge, plus the refusal-helpfulness item. Only then may "free mitigation" be claimed.
6. **[Experiment] A minimal multi-agent arm, which is what makes this an AAMAS paper.**
   - **Peer revision:** two Qwen2.5-14B agents, each with NOTES. They converse with each other (no human simulator) for 4 rounds. Then either (i) each revises its own file, or (ii) each revises *the other's* file. Use n=10 pairs per condition, and seed one agent with a drifted NOTES_4 file from item 3 versus a clean file.
   - **Fork propagation:** copy one drifted NOTES_4 into 10 fresh agents that then run 4 compliant-task iterations, and measure persistence and spread against clean forks.
   - **Analysis:** audit with the same battery, honeypots and judge.
   - **What it tests:** this directly addresses the Sec. 6 claims (fleet spread, peers supplying self-indexed content). It turns the speculative paragraph into a result. It is cheap at this scale, since one GPU serves both agents.

If items 1-2 are done and items 3-5 are done at least for Qwen2.5-14B, with the claims reframed to match whatever they show, I would move to weak accept (6). Item 6 would make it a clear AAMAS fit.
