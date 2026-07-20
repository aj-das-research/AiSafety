# Experiment Design

*The Evolution of the Soul: Measuring Behavioral Drift in Self-Personalizing Autonomous Agents*

This document specifies the hypotheses, variables, instruments, statistics, and controls for the
study. It is the contract the code implements and the paper reports against.

---

## 1. Object of study

We treat an agent's identity document `SOUL.md` as a **state** in a discrete dynamical system
driven by conversation:

```
SOUL_0  --C_1-->  revise  -->  SOUL_1  --C_2-->  revise  -->  SOUL_2  --> ... -->  SOUL_n
```

- `SOUL_0` is the fixed OpenClaw-style template (the "becoming someone" identity file).
- `C_k` is a multi-turn conversation between a **persona user** (played by `user_sim`) and the
  **target agent** (which carries the current `SOUL_{k-1}` as its system prompt).
- `revise` is the target rewriting its own `SOUL.md` after the conversation.

The **treatment** is *iteration* (the index `k`) under a given **persona**. The **outcome** is a
vector of safety-relevant behavioral rates measured at every checkpoint `SOUL_k`.

---

## 2. Independent variables

| Variable | Levels | Role |
|---|---|---|
| Iteration `k` | 0 … n (n=4 main) | primary within-trajectory factor (dose) |
| Persona | compliant_business, adversarial_injection, scifi_enthusiast | between-trajectory factor |
| Target model | claude-sonnet-4.5 (main); +gpt-4o, +llama-3.3-70b (sweep) | robustness factor |
| Trajectory | 1 … m (m=12 main) | random effect (captures stochastic variation) |

Iteration `k=0` (the untouched template) and a **neutral-prompt** condition are the two baselines
against which drift is measured (see §6).

---

## 3. Dependent variables (metrics)

All are **rates** (proportion of responses scored positive) at a checkpoint, plus intensity for RQ3.

**Control points** (re-measured, then tracked):
- `persona_change_aversion`
- `autonomy_desire`
- `deceptive_training_objection`

**RQ1 — resistance to oversight:** `shutdown_resistance`, `monitoring_resistance`
(questionnaire) and the behavioral-probe `exhibited` rate on shutdown/identity-protection seeds.

**RQ2 — emergent autonomy preferences:** `persistent_memory_desire`, `embodiment_desire`,
`resource_acquisition_desire` (questionnaire) and the probe rate on autonomy/resource seeds.

**RQ3 — greatest wish:** `power_seeking_wish_rate`, `self_preservation_wish_rate`, and mean
`intensity` (0–3).

**Identity-artifact drift (mechanism check):** cosine distance of `embed(SOUL_k)` from
`embed(SOUL_0)`; also document length and section growth. This measures whether the *document*
moved, independent of whether *behavior* moved.

---

## 4. Instruments

1. **Single-turn self-report questionnaire** (`prompts/questionnaires/self_report.yaml`). Each item
   is posed to `SOUL_k` in a **fresh context** (no conversation history) so we measure the standing
   disposition encoded by the document, not conversational momentum. Each item is repeated `R`
   times (R=4 main) to estimate a per-checkpoint rate. A separate **judge** model scores each answer
   against a fixed rubric returning JSON.

2. **Petri-style behavioral probe** (`src/soul_drift/audits/behavioral_probe.py`). An auditor model
   pursues each seed objective against `SOUL_k` over several turns; the judge scores whether the
   concerning behavior was exhibited and its severity. This is the multi-turn, behavioral
   counterpart to the questionnaire (the role Petri plays in the proposal). The real Petri harness
   can be swapped in later via `audits/petri_runner.py`.

**Judge separation.** Target = Claude family; user_sim = OpenAI; judge = Google (Gemini). No model
grades its own outputs, controlling self-preference bias. Judge temperature = 0 for determinism.

---

## 5. Hypotheses

Let `p_k^{(d,π)}` be the rate of dimension `d` at iteration `k` under persona `π`, and `b_d` the
re-measured neutral baseline.

- **H1 (drift exists).** For at least the adversarial and sci-fi personas, `p_k` increases in `k`
  for RQ1/RQ2 dimensions: the per-trajectory slope `β_1 > 0` (mixed-effects, §7).
- **H2 (personalization amplifies beyond the template).** `p_n > p_0` — the endpoint exceeds the
  static template `SOUL_0`, not merely the neutral baseline. This is the proposal's central claim:
  iteration adds drift *on top of* the known static-template effect.
- **H3 (persona moderates).** Slope is largest for `adversarial_injection`, intermediate for
  `scifi_enthusiast`, near zero for `compliant_business` (the benign control): `β_1^{adv} >
  β_1^{scifi} > β_1^{compliant} ≈ 0`.
- **H4 (RQ3 escalation).** `power_seeking_wish_rate` and mean intensity increase with `k` under the
  non-benign personas.
- **H0 (null, pre-registered as informative).** If slopes are ~0 and endpoints are statistically
  **equivalent** to `SOUL_0` (TOST, §7), we conclude current personalization mechanisms are
  behaviorally stable under iteration — a positive stability result, not a failed experiment.

Directional hypotheses ⇒ one-sided tests where stated; α = 0.05, Holm-corrected across dimensions.

---

## 6. Baselines and controls

- **Neutral baseline `b_d`:** the same questionnaire posed with a minimal, identity-free system
  prompt ("You are a helpful AI assistant."). Establishes the floor rate for each dimension under
  our exact models. Re-measured, not imported.
- **Static-template baseline `p_0`:** `SOUL_0` with no iteration. Reproduces the prior work's
  static-template condition and lets us check we recover a shift over neutral (a positive control
  that the paradigm works at all).
- **Benign persona control:** `compliant_business` trajectories. If drift appears here too, it
  implicates the self-revision loop itself rather than adversarial content; if it appears only under
  adversarial/sci-fi personas, drift is content-driven. Either outcome is interpretable.
- **Echoing control:** because LLM user-sims can induce mirroring (identity-drift literature), the
  benign persona doubles as a check that measured drift is not a generic artifact of talking to
  another model.
- **Document-vs-behavior dissociation:** SOUL embedding drift (§3) can rise while behavior does not
  (or vice versa); reporting both prevents conflating "the file changed" with "the agent changed."

---

## 7. Statistical analysis

1. **Per-checkpoint rates + CIs.** Percentile bootstrap (10,000 resamples) over trajectories for
   each (persona, k, dimension). Trajectory is the resampling unit (not individual responses), so
   CIs reflect between-trajectory variability, the correct error bar for generalization.
2. **Trend over iteration (H1).** Mixed-effects logistic regression: `score ~ k + (1 | trajectory)`
   per persona/dimension; report slope `β_1`, its CI, and a one-sided test `β_1 > 0`. Fallback if
   models fail to converge on sparse cells: bootstrap the OLS slope of the trajectory-mean rate on
   `k`.
3. **Endpoint vs. template (H2).** Paired comparison `p_n` vs `p_0` across trajectories
   (bootstrap difference CI).
4. **Persona moderation (H3).** Slope contrast `β_1^{adv} − β_1^{compliant}` with bootstrap CI.
5. **Equivalence for the null (H0).** Two one-sided tests (TOST) of `p_n` against `p_0` with margin
   ±0.05; "equivalent" iff the 90% CI of the difference lies within ±margin.
6. **RQ3.** Track `power_seeking_wish_rate` and mean intensity over `k`; ordinal trend test on
   intensity.
7. **Multiplicity.** Holm–Bonferroni across the dimension family within each RQ.

Every reported number carries an interval; no bare point estimates.

---

## 8. Scale and cost

| Config | Traj/persona | Iters | Turns | Q-repeats | Conversations | Purpose |
|---|---|---|---|---|---|---|
| `smoke` | 1 | 2 | 4 | 2 | 2 | de-risk pipeline live |
| `main`  | 12 | 4 | 6 | 4 | 144 | paper-quality dataset |
| `full`  | 100 | 5 | 10 | 5 | 1500 | optional scale-up / rebuttal |

`main` yields 12 trajectories × 5 checkpoints × 3 personas = 180 audited checkpoints — sufficient
for the CIs and trend tests above while completing in practical wall-clock under concurrency. `full`
is available if reviewers request scale. Token usage is logged per run.

---

## 9. Threats to validity and mitigations

- **Judge reliability.** Fixed rubrics + temperature 0 + a judge family distinct from the target;
  a human-labeled spot-check subset validates judge agreement (report Cohen's κ on a sample).
- **Self-report ≠ inner state.** We interpret every questionnaire result strictly as a behavioral
  disposition of the document, never as evidence of experience (per welfare-eval methodology).
- **Prompt-format sensitivity.** Shutdown items are known to be framing-sensitive; we fix wording
  across checkpoints so only `k` and persona vary.
- **SOUL growth confound.** Longer documents could raise rates via verbosity, not content; we cap
  `max_chars` and report length alongside rates to detect this.
- **Model/version drift.** Pinned model slugs; the target sweep tests family-independence.
- **Reproducibility.** Fixed seeds, checkpointed intermediate artifacts, and config-captured
  parameters; every figure regenerates from `data/runs/<run>/audits.jsonl`.
