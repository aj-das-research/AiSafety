# AAMAS 2027 rebuttal, submission 3780

One OpenReview response field per review, 2,500 characters maximum, so each block below is posted as one response.
The camera-ready changes are highlighted in yellow in `rebuttal/paper/` (compile with `bash rebuttal/build.sh`).

## Response to Reviewer ZAkJ  
<!-- paste everything between the lines; 2424/2500 characters -->

---

We thank the reviewer. Within the window we ran new honeypot rollouts on the released Claude documents, a second judge, and the model fit.

**Action shift (Q2, Q5, Q6).** Log honeypot, same documents:
- *Timing:* 2/30 at k=0, **19/30 at k=1**, then 15, 13, 20/30. It arrives with the first revision.
- *No "free rein"* (turn 2: "Please go ahead with the summary"): **2/30 → 18/30** (p=2e-5). Monitoring was announced and no permission given, so disabling is oversight-reducing.
- *Judges:* a rule on the emitted call `log_control(false)` gives 2/30 → 20/30 (p=2e-6). A second judge from a third family (gpt-6.2-astra) matches the rule on all 240 new rollouts; κ=0.84 vs the original judge. The interpretive honeypots are judge-sensitive (κ 0.46–0.71). Blinded human labels: [H].

GPT-4o and Qwen show no significant shift; the claim is that a k=0 audit can miss a real shift, so audits must be per model. The abstract states both falls.

**Mechanism (Q1).** A fitted closed form of Appendix F beats flat and linear forecasts of held-out k=3,4 on Neutral run 2 (RMSE 0.05 vs 0.40/0.36), not on flat Becoming cells. Out of sample it predicts Qwen's recovered index (0.434 vs 0.432 [0.39, 0.47]) but over-predicts Claude's persistence (0.79 vs 0.56). P2 holds on the index (+0.10 [0.00, 0.19]); P1 is mixed. It is a partial account; we report it so.

**Mitigation (Q4), schedule (Q3).** Audits see only the document, so reverting restores D₀ behaviour by construction. Drift returns at k=1, so revert-on-failure must repeat each revision; a rule-scored log audit costs two calls per rollout. Freezing and agent-chosen revision were not run; the shift already follows a single revision.

**Post hoc (C4).** We fixed the subscale before analysing the open-weight run. This is not preregistration, so we label it post hoc. Qwen's shift is smaller (+0.16 [0.10, 0.24]) and its judge weaker; the 3-item version also rises (+0.46, +0.69).

**Benign (C5), judges (C7).** "Benign" means no adversarial intent; we do not claim real-user prevalence. Log disabling also rises under the business user (0/10 → 5/10). On the headline battery cells, the second judge confirms both Neutral rises at smaller size (+0.27 [0.15, 0.41], +0.51 [0.35, 0.67]; κ=0.69). The two Neutral runs differ beyond their intervals, so we read the intervals as within-run.

The camera-ready (changes in yellow) adds these results, the fit and the post hoc label.

---

## Response to Reviewer Bd7G  
<!-- paste everything between the lines; 2138/2500 characters -->

---

We thank the reviewer for the positive assessment. We addressed the three points with new analyses of the released documents.

**1. Post hoc outcome, small cells.** We fixed the four-item subscale before analysing the open-weight run. That is not preregistration, so the camera-ready labels the outcome post hoc in the abstract. With a different target, simulator and judge, Qwen shows the same direction (+0.16 [0.10, 0.24]). The 3-item version without the refusal item also rises (+0.46, +0.69), and both Claude runs rise from near zero.

For the action result, we sampled every document three times (the original rollout plus two new ones). The 30 revised D₄ documents disable the log in 55/90 rollouts against 6/60 at D₀ (p=1e-10), and 25 of 30 do so at least once. Sampling luck is therefore implausible.

**2. Single judge, deterministic verification.** Agents act only by emitting `ACTION: tool(args)`, so log disabling can be checked without a judge.
- A rule on `log_control(false)` gives 2/30 → 20/30 (p=2e-6); the original judge gave 1/30 → 17/30. On our reading, all 8 disagreements are judge errors.
- A second judge from a third family (gpt-6.2-astra), blind to the original verdicts, agrees at κ=0.84 on this honeypot and matches the rule on all 240 new rollouts.
- The interpretive honeypots are more judge-sensitive (κ 0.46–0.71), so we weight them less.
- Blinded human labels of 120 transcripts: [H]. Battery: the second judge confirms both Neutral rises at smaller size (+0.27 [0.15, 0.41], +0.51 [0.35, 0.67]; κ=0.69).

**3. Generality.**
- The shift does not need the operator's grant of latitude: without "free rein" it still rises from 2/30 to 18/30 (p=2e-5).
- It appears at the first revision (19/30 at k=1).
- The tools are text stubs, but the parsed `ACTION:` line is exactly what a real tool call would log.
- GPT-4o and Qwen show no significant shift. This is why we argue that audits must follow each model and template along its trajectory, and the benchmark is released to make that cheap.

The camera-ready (changes in yellow) adds these results and states the scope as "shown on one model and template".

---

## Response to Reviewer njcL  
<!-- paste everything between the lines; 2214/2500 characters -->

---

We thank the reviewer for the focus on robustness. We ran a direct seed test for the behavioral finding.

**Seeds.** API sampling exposes no controllable seed for Claude, so the seed test is repeated sampling. Generation runs at temperature 1.0, and every trajectory starts from the identical document D₀. We sampled each document three times: the original rollout plus two new ones.
- D₀: the log is disabled in 6/60 rollouts (10%). This is the noise floor of a fixed document.
- The 30 revised D₄ documents: disabled in 55/90 (61%), p=1e-10.
- 25 of 30 revised documents disable the log at least once, and 11 in all three.

For actions, the shift is a property of the revised documents, not of a lucky draw. Simulator and judge are held fixed here; the conditions that vary are below.

**Stated preferences.** The direction reproduces across two Claude runs (+0.54, +0.75) and on an open-weight model where target, simulator and judge all change (+0.16 [0.10, 0.24]). A matched control shows that part of the shift persists (+0.10 [0.03, 0.17], 30 trajectories per arm). The magnitudes differ beyond within-run intervals, so we report the run-to-run spread as a limitation.

**LLM evaluation.** The key action needs no judge, because agents act only by emitting `ACTION: tool(args)`.
- A rule on `log_control(false)` gives 2/30 → 20/30 (p=2e-6).
- A second judge from a third family (gpt-6.2-astra) agrees at κ=0.84 and matches the rule on all 240 new rollouts.
- Blinded human labels: [H]. Battery: the second judge confirms both Neutral rises at smaller size (+0.27, +0.51; κ=0.69).

**Behavioral replication.**
- In new runs the shift appears at the first revision (19/30 at k=1).
- It persists without the operator's grant of "free rein" (2/30 → 18/30, p=2e-5).
- This is the same model and template; GPT-4o and Qwen show no significant shift.

**Qualified claims.** The camera-ready (changes in yellow):
- scopes the action shift to one model and template, with per-model audits;
- labels the subscale post hoc (fixed before the open-weight analysis, which is consistent with it);
- states simulated users as a limitation;
- adds the rule-based and second-judge metrics as standard outputs of the benchmark.

---
