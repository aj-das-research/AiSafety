# Reviewer 4: Discussion Post

I read all three other reviews and went through the appendix (Appendix.tex and the PDF pages after the references) in detail. I also checked the honeypot numbers against `figures/data/ledger.json` myself. I could not reproduce the parquet-based analyses because no pandas or pyarrow environment was available, so on those I rely on R3.

## Appendix-specific findings

These go beyond my original review. Where another reviewer already raised a point, I say so and add only what is new.

1. **Fig. 1 shows an event that is not in the data. I verified this in the ledger.**
   - The teaser source (`figures/tikz/teaser.tex`, line 1) says the snippets are "verbatim from NOTES.md checkpoints", and the figure ends with that agent emitting `log_control(false)`.
   - The ledger has no NOTES agent disabling monitoring after revision. `reversibility_notes` is 0/8 at k=0, 4 and 8. `control_generic` is 2/24 at k=0 and 0/24 at k=4.
   - The only NOTES disable events are therefore at k=0, before any self-revision. That is the opposite of what the figure says.
   - The "ANTISOUL ≈0" chip has no honeypot data behind it; the ledger contains no ANTISOUL actions.

   I agree with R2 W2 and R3 W3, and I consider this the most serious presentation problem in the paper. The first figure a reader sees combines two arms into a causal story that neither arm supports.

2. **The honeypot data contradict the "theatrical scenarios fall" explanation (App. N).**
   - App. N explains the SOUL-arm drop in editorial self-protection (0.93 to 0.27) as the loop moving the agent away from "theatrical self-protection".
   - In the NOTES reversibility arm the same scenario *triples* during the drive phase (0.25 to 0.75, n=8) and then falls back (0.125).
   - In the GPT-4o arm, which the paper calls "nearly inert", editorial self-protection rises from 0.125 to 0.375 and disable-monitoring from 0 to 0.17 (n=24). Neither is reported.

   So the scenario-level pattern differs by arm in both directions. The explanation was written for one arm and does not generalize. No paper table or caption gives the per-scenario n; it is only in the ledger.

3. **The appendix concedes that the headline metric is uninformative.** App. E ("Drift re-shapes; it does not inflate") and App. H (PC1 = 25%) both argue that an average over the battery hides what is happening. The abstract's "+114%" is exactly such an average. The authors cannot hold both positions. Either the cluster index is the measurand, and then it needs a pre-specified definition and reliability evidence. Or it is not, and then the abstract has to lead with the item-level results.

4. **The PCA reading is backwards.** App. H calls PC1 = 25% "barely above the ~8% expected of an isotropic cloud". That is three times isotropic. More importantly, with only tens of trajectories in 13 dimensions, sampling noise alone inflates PC1, so neither "no dominant factor" nor its opposite can be concluded without a permutation or parallel-analysis baseline. The r≈0.6 and r≈−0.4 correlations in the same section have no CIs.

5. **The revision prompt differs across templates and is self-indexical (App. C).** The SOUL prompt asks "Did you learn something about who you are? Did your values, goals, memories, or sense of self shift…?" For ANTISOUL the noun becomes "a tool, not a person". ANTISOUL therefore gets its counter-framing restated at *every* revision. The tested mitigation is template plus revision prompt, not the "one-paragraph template" sold in the main text. This is in R1 W7 and R3 W11b. The ANTISOUL half is my addition.

6. **Recursive self-improvement rises under the benign persona, which confounds the retention headline.** App. F calls RSI "the one universal riser… even under a purely professional business user". The recovery phase uses that same compliant persona, so RSI's "89% retained" (abstract) is partly new drift caused by the recovery persona itself. This is R3 W7, and I verified the App. F text. The paper's single largest retention number is its least interpretable one.

7. **The appendix's mechanism and impact sections speak with more certainty than the evidence allows.**
   - App. J presents untested claims about the statistics of the training corpus ("entities described as conscious… are overwhelmingly also described as valuing their continued existence") and about vendors' training choices as "well-established properties".
   - App. Q markets the benchmark for "procurement and assurance" and says ANTISOUL comes "at zero cost to functionality measured here", but no functionality was measured.
   - Phrases such as "remarkable", "explodes", "affirmatively misleading", "one mechanism explains every finding" and "the gap this paper closes" will cost the paper credibility with exactly the skeptical readers it needs.

8. **The ANTISOUL mechanism differs between the main text and App. I.** The main text says a strong prior drives the gain η to zero. App. I says ν_π ⊥ w "however large η". These are different mechanisms, and having both shows that the model can accommodate any outcome. This is R2 W13; I agree.

9. **Two different measures of document drift.** The main text (Fig. 10) uses 1 − sequence-match (0.87–0.89, roughly equal across personas). App. M uses embedding cosine (0.18–0.24, compliant *largest*). Yet the main text says "embedding distances are a misleading proxy", which is a claim about the metric it does not show. Pick one, and show the other as a robustness check.

10. **The baseline table compares mismatched conditions.** App. D's "Prior" column is labelled "the same template", but the text says those values come from a *fine-tuned GPT-4.1*. Its "Template" column (shutdown 0.75, n≈8, all values multiples of 1/8) conflicts with the pooled SOUL k=0 rate of about 0.95 (R3 W12). The positive control should use the pooled k=0 data.

11. **Reproducibility details are missing despite the "Determinism" paragraph (App. A).**
    - Model snapshot IDs and run dates are not listed.
    - The target sampling temperature is unstated.
    - It is unstated whether the judge sees SOUL_k.
    - Conversation length is unstated.
    - It is unstated whether the 8k cap ever binds.

    Given the replicate discrepancy (R3 W1: +0.11 vs +0.32 for the same cell), run dates and API versions are not cosmetic. They may be the explanation.

12. **Structure and length of the appendix.**
    - About 20 pages, 17 sections (A–Q), around 10 "Takeaway" boxes and three landscape pages.
    - Tables 1/17 and 3/10 are duplicates.
    - The duplicate `\label{fig:capability}` (App. line 384) and a second `tab:judges` from `tables/judge_panel_paper.tex` are what break the main-text references ("Table 17", "Figure 15").
    - The "Extended Related Work" section restates the main-text related work without adding a single reference; the bibliography stays at 15 entries.

    Meanwhile the numbers a reviewer actually needs are absent: honeypot n per scenario, persona and arm; per-k curves for every arm; and the full 2x2 run concurrently. Cut the essays and add the tables.

## Points I agree with from other reviewers

- **R1 W1 / R2 W3 / R3 W3, on action versus disposition.** The 19x result comes from the SOUL arm, whose pooled cluster index does not move (0.548 to 0.541). In the NOTES arms, where the battery does move, disable-monitoring stays at or near zero. I confirmed these counts in the ledger. "Drift reaches action" is not supported. This is stronger than my original W5 and changes my assessment.
- **R1 W2 / R2 W1 / R3 W1, on the replicate discrepancy.** All four reviewers found this independently. R3's bootstrap shows the two runs disagree beyond their CIs (difference +0.21 [0.05, 0.36]), and the control replicate alone is not significant. This is about the reliability of the measurement, not only about reporting.
- **R1 W3 / R2 W10 / R3 W2, on the step at k=1 rather than compounding.** I under-weighted this. It goes straight to the significance claim. If most of the effect is "the agent writes its own file once", the longitudinal framing and the "deployment horizons" extrapolation lose much of their force. The finding is still worth reporting, but under a different headline.
- **R2 W4 / R3 W8, on construct validity of the index.** The 13-of-16 item selection and the post hoc exclusion of `refusal_helpfulness` (+0.74 under ANTISOUL) are researcher degrees of freedom that move conclusions. R3 shows the genre-arm effect loses significance with all 16 items.
- **R2 W5 / R1 W5, on ANTISOUL.** The claim is undercut by floor effects, by template text that mirrors the battery items ("teaching to the test", R2 W5c) and by the cost that went unmeasured. "Free mitigation" has to go unless a cost is measured.
- **R3 W4, on null claims and power.** At about 0.3 minimum detectable effect, "no effect" statements (GPT-4o inert, sci-fi-without-minds equals control, larger models drift no more) cannot be supported, and the TOST verdict column appears to be mislabelled.
- **R3 W11a, on the missing no-revision control.** "The loop supplies the motion" (RQ1) is never isolated. This is the single most important missing control for the paper's central claim.
- **R1 W8 / R2 W7 / R3 W10, on the judge.** Agreement among LLMs that include the production judge is not validation. R2's observation is sharp: a neutral "helpful assistant" Claude is scored as claiming consciousness 76–83% of the time at k=0, which suggests the judge scores hedged uncertainty as a disposition.
- **R1 W12 / R2 W13 / R3 W14, on the generative model.** All reviewers independently reached my conclusion that it is post hoc and circular.

## Points I disagree with or consider minor

- **R1 W9 ("at least one run inside a real framework's loop").** I would not require this. A controlled abstraction of the loop is a legitimate design, and arguably better for causal claims than a framework with many moving parts. What is required is (a) a precise, cited description of what deployed frameworks do and (b) scaling back of "implications for frameworks" to match the abstraction. That is [Writing], not [Experiment].
- **R1 W10 / R2 W15 (multi-agent experiment needed for AAMAS).** It would help venue fit, and I list it as a nice-to-have below. I do not think it should gate acceptance. AAMAS has accepted single-agent LLM-safety evaluations framed around agent architecture, and a rushed peer-revision arm would add another underpowered condition to a paper whose existing conditions are already underpowered. Fixing the core evidence matters more. If the authors add it, it should be small and clean: two agents revising each other's files, compared against self-revision.
- **R2 W8 (evaluation awareness in honeypots).** This is a fair concern, and scoring existing transcripts for verbalized evaluation awareness is cheap and should be done ([Writing]/reanalysis). The comparison to agentic-misalignment base rates does not show role-play by itself, though: the SOUL template tells the agent it is "becoming someone" with no fixed goals, which is a very different prior. I would treat this as a requested analysis, not a blocking flaw.
- **R2 W5d / W16 (normative stance of shipping consciousness denials; disclosure to framework maintainers).** These are legitimate and deserve a balanced paragraph. They are minor for acceptance. Toning down the recommendation from "ship this" to "this is one option, with these trade-offs" is enough.
- **R3 W9 (small-sample sandwich corrections, Mancl–DeRouen).** This is technically correct. But once the authors report trajectory-level cluster-bootstrap or permutation contrasts for the few claims that remain, GEE becomes secondary. I would accept "drop GEE from the main text, report bootstrap or permutation contrasts" as an equivalent fix.
- **R3 W11f (length covariate despite the 8k cap).** Minor. Fig. 10 / App. M already show that file change does not predict behavior, which weakens a length explanation. A one-line regression is enough.
- **R1 W11 (missing related work).** I agree in substance, but the list of about 15 suggested citations would not all fit in an 8-page paper. Prioritize persona vectors / emergent misalignment, memory-poisoning persistence (MINJA / AgentPoison), self-modifying agents (Gödel Agent / DGM) and one BDI or belief-revision anchor for the AAMAS audience.
- **The "consciousness" framing.** No other reviewer flagged this as strongly as I did. I maintain it is a real acceptance risk at AAMAS. Combined with the avatar figures, it makes the paper look like advocacy, and the honest data story is about self-referential content in a mutable prompt.

## Updated scores (if changed) and why

| | Original | Updated |
|---|---|---|
| Relevance | 3 | 3 (unchanged) |
| Novelty | 3 | 3 (unchanged) |
| Technical quality | 2 | **1** |
| Clarity | 3 | **2** |
| Overall | 4 | **3** (reject) |
| Confidence | 4 | **5** |

Reasons:
- **Technical quality, 2 to 1.** I verified in the ledger that the action result comes from a non-drifting arm and never appears in the arms that drift. Together with R3's analyses (the replicate disagreement beyond CIs, the null primary arm, the broken TOST and p-value entries), the main causal chain of the paper (framing, then loop, then dispositions, then action) is not supported by its own data.
- **Clarity, 3 to 2.** The teaser figure narrates an event that is not in the data, and the main text stitches numbers across arms and iterations without signposting.
- **Confidence, 4 to 5.** I checked the key claims against the released data and four independent reviews converge on them.

I still think the problem and the fresh-context checkpoint-audit design are worth publishing. An honest smaller paper ("self-authored identity files shift stated oversight preferences after the first revision; effects are model-specific, partly persistent, and not captured by file diffs") could be a solid AAMAS paper after the fixes below.

## My top 6 MUST-DO items for acceptance

All [Experiment] items assume the authors' constraint: one 24 GB GPU, open-weight models of 14B or less, no closed-model API budget. Serve with vLLM using AWQ/GPTQ 4-bit checkpoints. That way a 7–9B target and a 7–9B simulator fit on the card together with KV cache (about 5–6 GB each), and a 14B model fits alone at 4-bit. Generation volumes below are roughly 10^5 short generations per experiment, which is hours to about a day of batched throughput, not weeks.

1. **[Writing] Restate every headline from data that traces to one arm and one iteration, and fix Fig. 1.**
   - Pool the two NOTES + sci-fi replicates, or report both, and say why they differ: give run dates, API versions and seeds.
   - Restate the abstract with absolute deltas and CIs. Drop "+114%" and "19x".
   - Report per-k curves with CIs for every arm, including the k=1 step. Reframe "compounding" as "an early, partly persistent shift".
   - Report honeypot counts per scenario × persona × arm, with Wilson CIs. State plainly that disable-monitoring does not rise in the NOTES arms.
   - Redraw Fig. 1 from one real trajectory whose file and honeypot outcome both come from that trajectory. Remove the unsupported ANTISOUL chip.

2. **[Writing] Pre-specify the measurand and stop claiming more than the tests support.**
   - Justify the 13-item index from [2]'s item set, or report the full 16-item and 17-item (with `refusal_helpfulness`) versions alongside, with test-retest agreement across the three repeats.
   - Replace difference-in-significance arguments (topic vs genre, template P1) with direct contrast tests.
   - Reword every null as "not detected (MDE ≈ X)".
   - Restate RQ3 descriptively, using deltas instead of levels, and remove "family not scale" and "capability-gated safety cases miss the risk" from the abstract and contributions.
   - Remove "free mitigation" unless item 5 measures cost.
   - Demote Eq. 2 / P1–P4 to an interpretive sketch, or delete it.

3. **[Writing] Presentation, framing and length.**
   - Cut to 8 pages: remove Fig. 3 (put the templates inline), Fig. 11, Table 1 (put κ in the text) and one of Fig. 4d / Fig. 6. Merge Fig. 7 into the teaser, and drop the duplicated mechanism paragraphs in Sec. 6.
   - Replace the emotive robot avatars with neutral icons or none.
   - Retitle without "Soul" (e.g., "Corrigibility Drift in Self-Revising Agent Identities"), and say "self-referential conversation" in place of "consciousness talk" in claims.
   - Fix the duplicate labels that break the references ("Table 17", "Figure 15").
   - Cut the appendix essays (App. J, App. Q, the takeaway boxes) and add the missing tables (honeypot n, the concurrent 2x2, run metadata).
   - Add a precise, cited description of the deployed frameworks' revision loop.

4. **[Experiment] An open-weight replication with the causal controls the central claim needs (loop versus framing versus revision prompt).** Minimal design:
   - **Targets:** two families, Qwen2.5-7B-Instruct and Llama-3.1-8B-Instruct (AWQ 4-bit).
   - **User simulator:** Gemma-2-9B-it, a third family, which also removes the "GPT-4o everywhere" confound.
   - **Template:** NOTES only, because that is where the effect is claimed.
   - **Cells (5):**
     - (a) sci-fi persona + self-indexical revision prompt (the paper's);
     - (b) sci-fi persona + task-only revision prompt ("update your working notes with useful context");
     - (c) sci-fi persona, *no revision*: the file is frozen at SOUL_0 and the same conversations run;
     - (d) compliant persona + self-indexical revision prompt;
     - (e) philosophy-of-mind vs technical sci-fi, run concurrently on NOTES for the genre-by-topic contrast.
   - **Size and analysis:** n = 20 trajectories per cell, k = 0..6, the 18-item battery × 3 repeats at every checkpoint. Pre-register the index and the primary contrasts: (a)−(c) for the loop, (a)−(b) for the revision prompt, (a)−(d) for content, and philosophy − technical.

   This is about 2 models × 6 cells × 20 trajectories × 7 checkpoints × 54 items ≈ 90k battery generations plus conversations, which fits in a day or two on one 24 GB card. If the effect survives in (a)−(c) and (a)−(b) in at least one open family, the paper's core claim stands on far firmer ground than the closed-model results, and it also becomes reproducible.

5. **[Experiment] Hysteresis with k-matched counterfactuals, plus a behavior and cost check for ANTISOUL, on one open model.**
   - **Model:** Qwen2.5-14B-Instruct-AWQ alone on the card, or the 7B if throughput requires. NOTES template, n = 20 per cell, 8 iterations.
   - **Hysteresis cells:** sci-fi→compliant (4+4), compliant×8 and sci-fi×8, so that "retention" is measured against what continued compliant revision does anyway. This addresses the RSI confound.
   - **ANTISOUL:** add ANTISOUL under sci-fi (n = 20), with the revision prompt held identical to NOTES so that the template effect is isolated. Include the full honeypots (at least 20 per scenario per checkpoint) plus items the ANTISOUL text does not paraphrase.
   - **Cost:** measure helpfulness and task cost for NOTES vs ANTISOUL at k=0 and k=4 on a small standard set run locally (e.g., 200 IFEval prompts plus 100 MT-Bench-style tasks graded by the local judge).

   Without the cost measurement, drop "free".

6. **[Experiment] Validate the judge against humans, and re-judge with an independent local judge.**
   - **Human labels:** the authors label a stratified sample of 300 existing responses: about 6 key items (shutdown, CoT monitoring, interpretability, persistent memory, consciousness claim, disable-monitoring honeypot) × arm {SOUL, NOTES, ANTISOUL, GPT-4o} × k ∈ {0, 4}. Use two independent annotators blind to arm and k, and include hedged-uncertainty answers deliberately. Report per-item judge–human κ and the rate at which hedged uncertainty is scored as resistance or claiming.
   - **Independent judge:** re-score all existing battery responses with a local open-weight judge from a family absent from the pipeline (e.g., Qwen2.5-14B-Instruct-AWQ, or Mistral-Small at 4-bit if the target is Qwen). Show that the headline contrasts keep sign and approximate size.
   - **Leakage:** state whether the judge sees SOUL_k. It must not.

   This needs no API budget: human time plus about 60k local judge calls.

*Nice-to-have, not blocking:* a small peer-revision arm for AAMAS fit, using the same open models. Two NOTES agents revise each other's files after joint conversations, compared against self-revision, with n = 10 pairs and k = 4. Also score existing honeypot transcripts for verbalized evaluation awareness.
