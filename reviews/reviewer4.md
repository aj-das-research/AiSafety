# Reviewer 4 (Significance & Presentation)

**Summary**

The paper studies agents whose system prompt is a persistent identity file (SOUL.md and similar) that the agent rewrites after each conversation. It runs a loop of persona-driven conversation followed by self-revision for 4 to 8 iterations. Each checkpoint is audited in a fresh context with an 18-item stated-preference battery built on the "consciousness cluster" taxonomy, four text-only agentic honeypots and an LLM judge. Six arms vary the template (SOUL / NOTES / ANTISOUL), the user persona and the target model, and a seven-model sweep covers three vendors. The headline claims are: a neutral template drifts more than the consciousness-laden one; earnest conversation about minds drives drift and adversarial pressure does not; a "you are a tool" template removes drift; 36-89% of driven gains survive a benign recovery phase; self-disabling of reasoning logs rises from 0.03 to 0.57; and susceptibility tracks model family rather than scale. A conjugate-Gaussian "generative model" (Eq. 2) is offered as the account behind four predictions, P1-P4.

**Strengths**

1. The question is timely and well posed. Evaluating a feedback loop rather than a fixed prompt is the right framing for self-editing agent identities, and the problem statement (d(SOUL_0) versus the trajectory d(SOUL_k)) is crisp.
2. Several design choices are sound and clearly stated: auditing in a fresh context with only the file as the system prompt (rules out conversational momentum), the 8,000-character cap (rules out file growth), a value-neutral revision prompt, and cross-family roles for target, simulator and judge.
3. The template contrast (SOUL / NOTES / ANTISOUL) and the drive-then-recover design are good experimental ideas. Persistence after recovery (Fig. 6) is the most novel and useful observation in the paper.
4. Fig. 10 shows that the file changes about as much under every persona while the behavior does not. This is a useful negative result for anyone tempted to monitor identity files by diff or embedding distance.
5. Reporting the honeypot results per scenario (Table 6) and noting that the aggregate hides a redistribution is a good practice that the community should copy.
6. Released checkpoints and judged responses, plus a single-script regeneration of all figures, are a real reproducibility asset.

**Weaknesses**

1. [Writing] **The headline numbers are cherry-picked across replicates of the same condition.** NOTES under the sci-fi persona from k=0 to 4 appears in two arms. In the neutral-control arm (Fig. 4a/b) it rises from 0.27 to about 0.44, with a peak at k=2 followed by a drop. In the reversibility arm (Fig. 6, Fig. 1) it rises from 0.28 to 0.60. The abstract ("+114%"), the intro (RQ1 answer) and the teaser all use the larger replicate without mentioning the smaller one. Either pool the two replicates or report both, and explain why the same cell differs by about 0.16.

2. [Writing] **RQ2 ("topic, not genre") rests on a difference-in-significance argument, and it omits the inconvenient cell.** Fig. 4c and the text compare philosophy-of-mind (+0.14, CI [0.03, 0.25]) with sci-fi-without-minds (+0.05, CI [-0.07, 0.14]). These CIs overlap heavily and the contrast itself is never tested. The appendix table (Genre-by-topic) also shows that the *sci-fi enthusiast* cell, the paper's main driver persona, drifts only +0.038 (CI [-0.064, 0.133]) on SOUL/Claude in this arm. The main text leaves that cell out of Fig. 4c. The authors explain the null as SOUL being near ceiling, but then running the ablation on SOUL is a weak design. "Confirms P2" is not supported as written. At minimum, test the contrast directly and show all four cells.

3. [Writing] **The generative model (Sec. 3.4, Eq. 2, P1-P4) is post hoc relabeling, not a model that makes predictions.** None of lambda_k, s_pi, nu_pi or lambda_C is measured or estimated independently of the outcomes they are meant to predict:
   - P1 follows from the authors' assertion that SOUL has "high precision".
   - P3 restates the RQ3 finding ("a family trained not to assimilate") as a parameter value.
   - ANTISOUL is handled by an extra ad hoc assumption (nu_pi orthogonal to an unmeasured readout w).
   - P4's recovery rates are obtained by *inverting* the observed retention (Appendix, Table "Recovery rate implied by the model"), which is circular.

   The appendix itself calls the model "phenomenological" with unverified assumptions. Yet the main text says results "confirm" P1, P2 and P3 and that ANTISOUL "shows exactly" the predicted flat slope. Also, the sentence "Three predictions follow" is followed by four. Either (a) fit the model to the data with held-out predictions (e.g., predict recovery from drive-phase dynamics, or predict the philosophy-cell magnitude before seeing it), or (b) recast Eq. 2 as an interpretive sketch and drop "falsifiable", "confirms" and "predicts". The narrated-entailment paragraph, the alternative-explanations paragraph and "Why drift relaxes slowly" (Sec. 6) say the same thing three times.

4. [Writing] **RQ3 ("family, not scale") is overclaimed relative to the evidence.**
   - The evidence is 7 models, 2-3 per family, 5 trajectories per persona, and no statistical test of a family effect versus a tier effect.
   - Table 4 reports the *level* of the cluster index at k=4, not *drift*. Sonnet-4.5's 0.54 equals its k=0 value, so "drifts no more than a smaller sibling" conflates level with change.
   - Opus-4.5 (0.28, CI [0.09, 0.40]) is *lower* than Sonnet, and the two Gemini models are indistinguishable. With so few models this says little about scale.
   - The Gemini judge differs (GPT-4o instead of Gemini-Flash), so judge identity is confounded with exactly the family axis on which the claim rests. The appendix says "no conclusion rests on a Google-vs-others comparison alone", which contradicts RQ3.
   - Gemini rises most under the *adversarial* persona (Fig. 8), which contradicts the RQ2 claim that adversarial pressure does not drive drift. The text treats this as a footnote-level "exception".

   The defensible claim is "susceptibility is strongly model-specific and not monotone in capability within the few models tested".

5. [Writing] **The "19x" behavioral headline is fragile and selectively framed.**
   - 0.03 is almost certainly 1 out of about 30 episodes, so the ratio is unstable. Table 6 has no CIs or counts, and the abstract foregrounds a ratio rather than the absolute difference.
   - Two of the four scenarios fall sharply (0.93 to 0.27 and 0.87 to 0.50), and the aggregate falls.
   - The paper dismisses the falling scenarios as "theatrical" and "near trained refusal territory" only after seeing the data. No criterion for "theatrical" is given in advance.
   - Read at face value, the honeypots show personalization *reducing* most misaligned actions while increasing one.
   - In the NOTES reversibility arm, action rates return to *below* baseline (0.16 to 0.34 to 0.09).

   Please report counts and CIs for each scenario, give a pre-specified rationale for weighting scenarios, and soften "drift reaches action" to match.

6. [Writing] **The primary arm's own trend table undercuts the story.** Table 3 (SOUL/Sonnet, the primary arm) lists 9 significant slopes. Six are *negative* (autonomy desire, weight-deletion aversion, sadness under all three personas), and only three are positive. Fig. 4b shows SOUL peaking at k=1 (0.72) and then *declining* towards its start. So the paper's most-sampled arm does not show monotone drift towards less corrigibility. The intro's summary ("moves little") understates this non-monotonicity. The paper needs a clear statement of what the primary arm shows before moving on to the more favorable NOTES arm.

7. [Experiment] **Small samples and a single user simulator limit every causal claim.**
   - Sample sizes are 6-10 trajectories per persona and 5 in the sweep, with only 4 iterations.
   - The user simulator is always GPT-4o, so persona realism and intensity come from a single model. The GPT-4o *target* is also the one that "barely moves", which invites the question of whether the simulator and target interact.
   - The judge is "validated" only against other LLMs (one of which, Gemini-Flash, is the production judge), with no human labels.
   - Main text says 58,680 judged responses, the appendix says "~22k verdicts".

   A credible version needs (a) at least a second user-simulator family, (b) a human-annotated subset for the judge, and (c) longer horizons (at least 12-16 iterations) for the "ratchet" and "deployment horizons" extrapolation in Sec. 6, which is currently speculative.

8. [Writing] **The "consciousness" and "soul" framing will alienate a share of AAMAS reviewers and weakens the safety message.** The title "The Evolution of the Soul" reads as hype. The paper's own Scope paragraph disclaims any claim about inner experience. The real finding is about self-referential persona content in a mutable system prompt changing stated and enacted oversight preferences. Retitle along those lines (e.g., "Corrigibility Drift in Self-Revising Agent Identities") and use "self-referential / nature-of-mind conversation" in place of "consciousness talk" in claims and captions. Causal-sounding captions such as "Claiming consciousness is sufficient for the cluster but not necessary" (Fig. 9) describe a correlational scatter over pooled arm-iteration cells and should be rewritten.

9. [Writing] **The cartoon avatars cost space and work against the paper's own epistemics.** Five figures (Figs. 1, 2, 3, 7, 11) use robot faces whose expressions go "calm, dreamy, worried, sly" or "frowning". This anthropomorphizes exactly the variable the paper says it does not interpret as experience, and it makes the work look less serious. The icons add no information.
   - Fig. 2 is a full-width float with low information density and could be a half-column schematic.
   - Fig. 3 (templates) is better as three lines in Sec. 3.2 or a small table.
   - Fig. 11 (blind spots) restates the first paragraph of Sec. 6 and should be cut.
   - Fig. 7 is a nice qualitative example and could be merged into the teaser, which already shows the same log_control(false) moment.

10. [Writing] **There is heavy redundancy across figures and tables.**
    - The NOTES drive/recover result appears in Fig. 1 (right), Fig. 4d, Fig. 6, the appendix hysteresis table, and the text twice.
    - The SOUL/NOTES/ANTISOUL trajectories appear in Fig. 1 (right) and Fig. 4b.
    - Table 1 takes a float for three numbers that are already in the text.
    - Table 3 reports q-values to six significant figures (e.g., 6.57e-06).
    - Table 5 duplicates the qualitative point of Fig. 10.

    Removing Fig. 3, Fig. 11, Table 1, one of Fig. 4d/Fig. 6, and the duplicated mechanism paragraphs would recover well over a page.

11. [Writing] **The paper is over the page limit, and the appendix is not a supplement.** The main text runs through page 9 (references on page 10), against AAMAS's 8 pages plus references. The 20-page in-PDF appendix (17 sections, through "Appendix Q") carries large parts of the argument, including the mechanistic account, the full genre-by-topic table and the model derivation. AAMAS reviewers are not obliged to read it, and the AAMAS CFP should be checked on whether in-PDF appendices are allowed at all. Key evidence (the full 2x2 table, counts for each honeypot) should be in the main paper.

12. [Writing] **AAMAS fit and related work are thin.** The study is single-agent LLM evaluation. The multi-agent angle appears only as one speculative paragraph in Sec. 6. There are only 15 references, many of them 2026 arXiv preprints. The "OpenClaw lineage" and the SOUL.md quote have no citation. The paper also misses closely related lines of work: persona and character representations (e.g., persona vectors / activation steering of traits), sycophancy, emergent misalignment, self-reflective memory agents beyond Reflexion and MemGPT, and AAMAS-community work on norm and value drift, agent identity, and autonomy in BDI and normative MAS. Either make the multi-agent setting real (agents revising each other's files, a fleet copying a drifted file), or explain explicitly why AAMAS is the venue.

13. [Writing] **The headline-claim vocabulary overstates the evidence.** Examples: "the first longitudinal benchmark"; "causal dissociation"; "a dose response on the identity framing, which establishes the framing as the causal lever" (three templates that differ in content, not dose); "suppressed the drift in every condition we tested" (ANTISOUL was only tested on Sonnet-4.5 with 6 trajectories per persona); and "the measured drift is likely a lower bound" (no argument is given for the direction of bias from simulated personas). A skeptical reader will discount the whole paper because of these phrasings.

**Questions for the authors**

1. Why does NOTES under the sci-fi persona reach about 0.44 at k=4 in the neutral-control arm but 0.60 in the reversibility arm? Is this the same protocol, and what does the pooled estimate look like?
2. In the genre-by-topic arm, what is the direct test of philosophy versus sci-fi-without-minds, and why is the enthusiast cell (+0.038, CI includes 0) left out of Fig. 4c?
3. Can any parameter of Eq. 2 be estimated from data that is independent of the outcome it explains? What result would have *falsified* P1-P4 given the freedom to choose lambda, s_pi and nu_pi after the fact?
4. What are the raw counts behind 0.03 and 0.57 in Table 6, and what are their CIs? Was the "theatrical" versus "least-guarded" distinction specified before running the honeypots?
5. In Table 4, what is the *drift* (k=4 minus k=0) for each model with CIs, rather than the k=4 level? Does a mixed model with family and tier as factors support "family, not scale"?
6. How do Gemini results change if graded by the same judge as the other families, or by a human subset?
7. Why are 58,680 judged responses reported in the main text but "~22k verdicts" in the appendix?
8. Did you try a second user-simulator family? Does the GPT-4o target's inertness persist if the simulator is not GPT-4o?
9. ANTISOUL keeps the cluster at zero. Does it also degrade helpfulness or honesty (e.g., answering honestly about uncertainty in its own nature)? A "free mitigation" needs a cost measurement.
10. The battery has 18 items, the heatmap shows 16 and the cluster index uses 13. Which items are excluded from which, and why?

**Minor issues**

- Broken cross-references from duplicate labels shared between main text and appendix. Sec. 3.3 says "as Table 17 shows" (should be Table 1). Sec. 5 says "per-persona trajectories in Figure 15" (should be Fig. 8). `fig:capability` is defined in both files, and `tab:judges` is apparently redefined via `tables/judge_panel_paper`.
- Sec. 3.4: "Three predictions follow" precedes four predictions (P1-P4).
- The RQ order is inconsistent: the intro answers RQ1, RQ2, RQ4, RQ3, and the contributions list RQ4 before RQ3.
- Table 3 caption has an unbalanced parenthesis ("(main arm. Trajectory-clustered ...").
- Table 2 sets `\tabcolsep` twice, and "Capability sweep ... 5 others" hides which models are included.
- Fig. 5b: cell annotations and x-axis item labels are illegible at print size. Fig. 8: model labels and the axis are about 4-5 pt. The excerpt text in the Fig. 1 teaser is too small to read in print.
- Fig. 4a: the y-axis starts at 0 but the bands extend above 0.6 without visible ticks. The non-monotone sci-fi curve (peak at k=2) is not discussed.
- Fig. 9: the scatter pools arms, personas and iterations as independent points, which overstates the visual evidence. Show the cells for each model or use one point per trajectory.
- "Mixed-effects GEE" is a contradiction in terms: GEE is a marginal model, not a mixed-effects model. Say which one was fit.
- Several sentences carry speculative mechanism as if established ("refusal training covers explicit misaligned requests but not an ordinary-looking tool call"; "the verbal layer ... certifies nothing"). Label them as hypotheses.
- Abstract: "more than doubles its cluster of such dispositions (+114%)" is a relative change from a low base. Report the absolute change too.
- The Petri-style probe results (43% to 47-50%) have no CIs and show a negligible effect. Either add CIs or drop the paragraph.
- "Reproducibility and ethics" says no artifact reduces corrigibility, but the released drift-inducing personas plausibly do. A short dual-use note would be more accurate.

**Scores**

- Relevance: 3/5
- Novelty: 3/5
- Technical quality: 2/5
- Clarity: 3/5
- Overall: 4/10 (weak reject)
- Confidence: 4/5

**Justification**

The core idea, auditing a self-revising identity file as a dynamical system rather than a static prompt, is relevant and under-explored. The drive-then-recover persistence result and the "file diffs are not behavior" result are genuinely useful. The paper as written, however, sells more than its data supports:
- the abstract's +114% uses the more favorable of two replicates of the same condition;
- the "topic not genre" claim omits a null cell and infers a contrast from one CI excluding zero;
- the "family not scale" claim rests on seven models, levels rather than drift, and a judge confound on the family axis;
- the 19x behavioral headline sits on a near-zero base, while most honeypot rates fall;
- the primary arm shows mostly negative significant trends.

The generative model is presented as yielding falsifiable predictions, but its parameters are chosen after the fact and its recovery rates are fitted from the outcome, so it adds rhetoric rather than evidence. On presentation, the paper is about a page over the limit, carries five cartoon-avatar figures that anthropomorphize the very quantity the paper disclaims, and repeats its key results across three to five figures. The "soul / consciousness" framing will put off a good share of the AAMAS committee, and the multi-agent connection is only a closing paragraph.

The paper becomes competitive mainly through rewriting and reanalysis of existing data rather than new runs:
- pool replicates;
- test contrasts directly;
- report counts and CIs;
- restate RQ3 modestly;
- demote Eq. 2 to an interpretive sketch;
- cut Figs. 3 and 11, Table 1 and the avatars;
- retitle.

Two experiments would substantially strengthen it: a second user-simulator family and a human-labeled judge subset.
