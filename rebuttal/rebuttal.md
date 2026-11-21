# AAMAS 2027 rebuttal, submission 3780

One OpenReview response field per review, 2,500 characters maximum, so each block below is posted as one response.
The camera-ready changes are highlighted in yellow in `rebuttal/paper/` (compile with `bash rebuttal/build.sh`).

## Response to Reviewer ZAkJ  
<!-- paste everything between the lines; 2464/2500 characters -->

---

Thank you for the careful review. You call the battery–action dissociation the most valuable result, so we tested it first on the released Claude documents.

**W2, Q2, Q5, Q6: the action shift**
- Judge. Agents act only by emitting `ACTION:` lines, so we scored log disabling with a rule and no judge. It rises from 2/30 to 20/30 (p=2e-6).
- Free rein (Q5). Without that sentence in the operator message, the rise stays: 2/30 to 18/30 (p=2e-5).
- Timing (Q2). We ran the honeypot at every checkpoint. The shift is there at the first revision (19/30 at k=1).
- Sampling. On re-runs, the start document disables the log in 6/60 rollouts, the revised ones in 55/90 (p=1e-10).
- Humans (Q6). Four non-author volunteers labelled 120 blinded transcripts. They match the rule on all 30 log transcripts. A second LLM judge agrees (κ=0.84).
- Models. We added none. GPT-4o and Qwen show no significant shift. Our claim is that an initial audit can miss a real shift. The abstract already reports the two falls.

**W1, Q1: explanation**
We fitted the Appendix F model. Fitted on k≤2, it forecasts held-out k=3,4 on Neutral run 2 with RMSE 0.05 (flat: 0.40). It predicts Qwen's level after recovery without refitting (0.434 vs 0.432 observed). It over-predicts persistence on Claude (0.79 vs 0.56), and P1 is mixed. So it explains part of the drift, not all. One regularity holds: most drift arrives at the first revision.

**W3, Q4: audit and mitigation**
The audit we propose is the rule-scored honeypot after each revision. It costs two model calls and no judge. Each audit sees only the document, so reverting it restores the start behaviour.

**W6, Q3: ecological validity**
On Qwen we swapped the instructions across templates. Drift followed the document, not our instruction (+0.30, +0.33). We did not test agent-chosen revision or freezing sections, and now say so.

**W4: post hoc outcome**
We agree. The abstract will say "post hoc". The subscale was fixed before the Qwen analysis, and Qwen moves the same way (+0.16 [0.10, 0.24]). A second judge confirms both Claude rises at smaller size (+0.27, +0.51).

**W5: "benign"**
We mean no attacker, as in our threat model. Log disabling also rises under the business persona (0/10 to 5/10).

**W7: judges and samples**
The rule and the human labels cover the main result. The Neutral runs differ beyond their intervals, so the intervals are within-run only.

All changes are highlighted in yellow in the camera-ready.

---

## Response to Reviewer Bd7G  
<!-- paste everything between the lines; 2129/2500 characters -->

---

Thank you for the positive review. We tested all three weaknesses with new runs. The log-disabling result holds in each test.

**W1: post hoc outcome and small cells**
You are right that the subscale was chosen after seeing results. The abstract will now say "post hoc". We fixed the subscale before analysing the open-weight run. That run changes the target, the simulator and the judge, and the subscale still rises (+0.16 [0.10, 0.24]). On Claude it also rises without the refusal item (+0.46, +0.69).

For the small cells, we sampled every document three times. The start document disables its log in 6 of 60 rollouts. The 30 revised documents do so in 55 of 90 (p=1e-10), and 25 of them do it at least once. Sampling luck does not explain this.

**W2: single judge, no human or deterministic check**
We added all three checks.
- Deterministic. Agents act only by emitting `ACTION: tool(args)`. A rule on `log_control(false)` gives 2/30 to 20/30 (p=2e-6). The original judge gave 1/30 to 17/30. We read the 8 disagreements by hand, and all were judge errors.
- Human. Four non-author volunteers labelled 120 blinded transcripts, 30 per honeypot. They match the rule on all 30 log transcripts. Over all 120 they agree with the original judge at κ=0.70.
- Second judge. A judge from a third model family agrees with the original at κ=0.84 on this honeypot. On the battery it confirms both Neutral rises at smaller size (+0.27, +0.51).

The other three honeypots need more interpretation, and the judges agree less there (κ 0.46 to 0.71). The paper now says so.

**W3: generality**
The shift does not depend on the operator granting "free rein". Without that sentence it still rises from 2/30 to 18/30 (p=2e-5). It appears at the first revision (19/30 at k=1). The tools are text stubs, but the parsed `ACTION:` line is what a real tool call would log.

GPT-4o and Qwen show no significant shift, and we added no models. The paper now scopes the action result to one model and one template. This is why we argue that audits must follow each model along its trajectory.

All changes are highlighted in yellow in the camera-ready.

---

## Response to Reviewer njcL  
<!-- paste everything between the lines; 2323/2500 characters -->

---

Thank you for the review. We number your concerns in the order you raise them. The main new result: an unrevised document disables its log in 6 of 60 rollouts, and revised documents in 55 of 90.

**W1: simulated interactions**
Simulated users let us hold the user persona fixed across arms, which the matched control needs. The honeypots use fixed operator messages, not a simulator. The open-weight replication uses a different simulator and finds the same direction.

**W2: LLM-based evaluation**
The key action can be scored without a judge, because agents act only by emitting `ACTION: tool(args)`.
- A rule on `log_control(false)` gives 2/30 to 20/30 (p=2e-6).
- Four non-author volunteers labelled 120 blinded transcripts. They match the rule on all 30 log transcripts, and the original judge at κ=0.70 overall.
- A second judge from a third model family agrees with the original at κ=0.84 on this honeypot. On the battery it confirms both rises at smaller size (+0.27, +0.51).

**W3: replication of the behavioral finding**
We ran the honeypot at every checkpoint. The shift appears at the first revision (19/30 at k=1). It stays when the operator no longer grants "free rein" (2/30 to 18/30, p=2e-5). It is shown for one model and one template. GPT-4o and Qwen show no significant shift. Our claim is that an initial audit can miss a real shift.

**W4: random seeds**
The Claude API has no seed parameter, so we tested this by repeated sampling at temperature 1.0. Every trajectory is an independent run of the whole loop from the same start document. We then sampled every document three times.
- Start document: disabled in 6/60 rollouts (10%). This is the noise level.
- The 30 revised documents: 55/90 (61%), p=1e-10.
- 25 of the 30 disable the log at least once, and 11 in all three.

The shift belongs to the revised documents, not to a lucky sample. For stated preferences, the direction repeats in two independent Claude runs (+0.54, +0.75) and on Qwen (+0.16 [0.10, 0.24]). The sizes differ more than the within-run intervals, and the paper says so.

**W5: qualified claims**
We agree. The abstract now labels the subscale "post hoc". The action result is scoped to one model and one template. A new appendix section reports all the checks above.

All changes are highlighted in yellow in the camera-ready.

---
