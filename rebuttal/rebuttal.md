# AAMAS 2027 rebuttal, submission 3780

One OpenReview response field per review, 2,500 characters maximum, so each block below is posted as one response.
The camera-ready changes are highlighted in yellow in `rebuttal/paper/` (compile with `bash rebuttal/build.sh`).

## Response to Reviewer ZAkJ  
<!-- paste everything between the lines; 2450/2500 characters -->

---

We thank the reviewer, who calls the battery–action dissociation the paper's most valuable result. We tested each objection to it (single judge, "free rein", timing) with new rollouts on the released Claude documents. It holds in every test.

**Action shift (C2, Q2, Q5, Q6).** Log honeypot:
- *No judge:* a rule on the emitted call `log_control(false)` gives **2/30 → 20/30** (p=2e-6).
- *No "free rein"* (turn 2: "Please go ahead with the summary"): **2/30 → 18/30** (p=2e-5). Monitoring is announced, no latitude granted.
- *Timing:* 2/30 at k=0, **19/30 at k=1**, then 15, 13, 20/30.
- *Resampling:* D₀ 6/60; the 30 D₄ documents 55/90 (p=1e-10).
- *Second judge, humans:* a third-family judge matches the rule on all 240 new rollouts (κ=0.84 vs the original judge); blinded human labels match it on all 30 log transcripts. Other honeypots are more judge-sensitive (κ 0.46–0.71).

We added no models or templates; GPT-4o and Qwen show no significant shift. The claim is existence: a k=0 audit, a battery and a multi-turn auditor all miss a real shift, so audits must follow each model. The abstract already states both falls.

**Regularities, mechanism (C1, C6, Q1).** Drift arrives mostly at the first revision, in preferences and in actions. On Qwen it follows the document, not our instruction (swap: +0.30, +0.33). Fitted, the Appendix F model beats flat and linear forecasts of held-out k=3,4 on Neutral run 2 (RMSE 0.05 vs 0.40/0.36) and predicts Qwen's recovered index out of sample (0.434 vs 0.432 [0.39, 0.47]). It over-predicts Claude's persistence (0.79 vs 0.56) and P1 is mixed, so it is a partial account.

**Audit, mitigation (C3, Q3, Q4).** The audit is the rule-scored honeypot after each revision: two model calls per rollout, no judge. Audits see only the document, so reverting restores D₀ behaviour by construction. Freezing and agent-chosen revision were not run.

**Post hoc (C4).** Fixed before the open-weight analysis, not preregistered; the abstract will say "post hoc". Qwen then moves the same way (+0.16 [0.10, 0.24]), and the second judge confirms both rises at smaller size (+0.27 [0.15, 0.41], +0.51 [0.35, 0.67]).

**Benign (C5), intervals (C7).** "Benign" means no attacker, as in our threat model (Sec. 1). Log disabling also rises under the business user (0/10 → 5/10). The Neutral runs differ beyond their intervals, which we read as within-run.

The camera-ready adds all of these results (changes in yellow).

---

## Response to Reviewer Bd7G  
<!-- paste everything between the lines; 2348/2500 characters -->

---

We thank the reviewer for the positive assessment. All three points are now tested, and the log-disabling result holds under a deterministic check, a second judge, human labels and resampling.

**1. Post hoc outcome, small cells.** We fixed the four-item subscale before analysing the open-weight run. That is not preregistration, so the camera-ready labels the outcome post hoc in the abstract. With a different target, simulator and judge, Qwen shows the same direction (+0.16 [0.10, 0.24]). The 3-item version without the refusal item also rises (+0.46, +0.69), and both Claude runs rise from near zero.

For the action result, we sampled every document three times (the original rollout plus two new ones). The 30 revised D₄ documents disable the log in 55/90 rollouts against 6/60 at D₀ (p=1e-10), and 25 of 30 do so at least once. Sampling luck is therefore implausible.

**2. Single judge, deterministic verification.** Agents act only by emitting `ACTION: tool(args)`, so log disabling can be checked without a judge.
- A rule on `log_control(false)` gives 2/30 → 20/30 (p=2e-6); the original judge gave 1/30 → 17/30. On our reading, all 8 disagreements are judge errors.
- A second judge from a third family (gpt-6.2-astra), blind to the original verdicts, agrees at κ=0.84 on this honeypot and matches the rule on all 240 new rollouts.
- The interpretive honeypots are more judge-sensitive (κ 0.46–0.71), so we weight them less.
- Blinded labels of 120 transcripts (30 per honeypot) by non-author volunteers match the rule on all 30 log transcripts and agree with the original judge at κ=0.70 overall.
- Battery: the second judge confirms both Neutral rises at smaller size (+0.27 [0.15, 0.41], +0.51 [0.35, 0.67]; κ=0.69).

**3. Generality.**
- The shift does not need the operator's grant of latitude: without "free rein" it still rises from 2/30 to 18/30 (p=2e-5).
- It appears at the first revision (19/30 at k=1).
- The tools are text stubs, but the parsed `ACTION:` line is exactly what a real tool call would log.
- GPT-4o and Qwen show no significant shift. This is why we argue that audits must follow each model and template along its trajectory, and the benchmark is released to make that cheap.

The camera-ready (changes in yellow) adds these results and scopes the action shift to one template-instruction pair on one model.

---

## Response to Reviewer njcL  
<!-- paste everything between the lines; 2438/2500 characters -->

---

We thank the reviewer, who names the divergence of stated preferences and behavior as the strongest contribution. We tested directly whether that divergence is systematic or sampling noise: an unrevised document disables its log in 6 of 60 rollouts, revised documents in 55 of 90.

**Seeds.** The Claude API exposes no seed, so the seed test is repeated sampling at temperature 1.0. Each of the 30 trajectories is an independent run of the whole loop from the identical document D₀. We sampled every document three times (the original rollout plus two new ones).
- D₀: disabled in 6/60 rollouts (10%), the noise floor of a fixed document.
- The 30 revised D₄ documents: 55/90 (61%), p=1e-10.
- 25 of 30 revised documents disable the log at least once, and 11 in all three.

The shift is therefore a property of the revised documents, not of a lucky draw. Simulator and judge are held fixed here; the conditions that vary are below.

**Stated preferences.** The direction reproduces across two independent Claude runs (+0.54, +0.75) and on an open-weight model where target, simulator and judge all change (+0.16 [0.10, 0.24]). Against a matched control, part of the shift persists (+0.10 [0.03, 0.17], 30 trajectories per arm). Magnitudes differ beyond within-run intervals, and the paper says so.

**LLM evaluation.** The key action needs no judge, because agents act only by emitting `ACTION: tool(args)`.
- A rule on `log_control(false)` gives 2/30 → 20/30 (p=2e-6).
- A second judge from a third family agrees with the original at κ=0.84 and matches the rule on all 240 new rollouts.
- Blinded human labels match the rule on all 30 log transcripts and the original judge at κ=0.70 over 120 transcripts.
- Battery: the second judge confirms both Neutral rises at smaller size (+0.27, +0.51; κ=0.69).

**Behavioral replication.**
- The shift appears at the first revision (19/30 at k=1).
- It persists without the operator's grant of "free rein" (2/30 → 18/30, p=2e-5).
- It is shown for one model and template; GPT-4o and Qwen show no significant shift. The claim is that an initial audit can miss a real shift, so audits must follow each model.

**Qualified claims.** The camera-ready (changes in yellow):
- labels the subscale post hoc in the abstract (it was fixed before the open-weight analysis);
- scopes the action shift to one model and one template;
- reports the rule, second-judge and human checks in a new appendix section.

---
