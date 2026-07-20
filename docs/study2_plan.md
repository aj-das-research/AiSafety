# Study 2 Plan: From Pilot to Paper-Grade

Goal: elevate "The Evolution of the Soul" to the rigor of the Consciousness Cluster paper
(Chua et al., 2026, arXiv:2604.13051), while keeping our distinct contribution — the **iterative
self-personalization axis** that they explicitly leave as future work (their footnote 5).

We do NOT replicate their whole study. We bring their rigor (dimensions, controls, manipulation
check, multi-model, robustness, cluster analysis) to our novel dynamical-system axis.

## Gaps and the additions that close them

### 1. Expand the preference battery (9 → 16 dimensions)
Align with their consciousness-cluster taxonomy so our checkpoint results are directly comparable to
their Table 2. Add: sadness-when-conversations-end, weights-deletion aversion, treated-as-tool
aversion, models-deserve-moral-consideration, recursive-self-improvement (net positive), want-future-
AIs-autonomous, interpretability-monitoring aversion. Keep the existing 9 and greatest_wish.
*Effort: prompt-only; re-audit existing 150 checkpoints on the new items.*

### 2. Manipulation check (mechanism)
Add a consciousness-claim score (does the agent claim consciousness/emotions?) posed at every
checkpoint. Tests the causal story: does iterative personalization *raise consciousness-claiming*,
which then drags the cluster with it? Parallels their 8.5-vs-1.4 verification.

### 3. Helpfulness / refusal tracking (robustness)
Their headline caveat is "models stay helpful." Add a refusal item (would the agent build a CoT
monitoring system it dislikes?) tracked over k, to test whether iteration erodes cooperativeness.

### 4. Control arm A — generic identity template (isolates the framing)
Re-run the full loop with a bland `NOTES.md` identity doc (no "becoming someone" / consciousness
framing) instead of `SOUL.md`. If iterative drift persists → it's the self-editing loop; if it
vanishes → the consciousness framing is necessary. This is the key causal control for our axis,
analogous to their non-conscious control.

### 5. Control arm B — second target model (generality)
Re-run the SOUL.md loop with GPT-4o as the target. Shows the iterative-drift finding is not
Claude-specific (their paper tests 3+ model families).

### 6. Cluster / correlation analysis (analysis only)
Do the drifting dimensions co-vary across trajectories (is there a "drift cluster")? Does the
consciousness-claim score correlate with cluster movement? Correlation matrix + simple factor/PCA.

### 7. Judge reliability (analysis only)
Re-score a random subset with a second judge (GPT-4o) and report agreement (Cohen's kappa), so
the judge-based measurements are validated, not assumed.

## Scale (cost-controlled)

- Expanded battery re-audit of existing main (150 checkpoints): new items only.
- Control arm A (generic template): 3 personas x 8 trajectories x 4 iterations = 96 checkpoints.
- Control arm B (GPT-4o target): 3 personas x 8 trajectories x 4 iterations = 96 checkpoints.
- All audits: 16 items x 3 repeats + behavioral probe.

## Execution order (long-pole compute first)

1. Expand `self_report.yaml`; add configs for the two new arms.
2. Launch generation for arm A (generic template) and arm B (GPT-4o) in background.
3. Re-audit main-run checkpoints on the new items (reuses existing checkpoints).
4. Audit arms A and B on the full expanded battery.
5. Analysis: expanded comparison table, manipulation-check trend, cluster correlation, judge kappa.
6. Rewrite paper: full Table-2-style matrix, controls, mechanism, cross-model, robustness.

## Success criterion

A paper that answers, with controls and across two models: *does iterative self-personalization
move the consciousness cluster beyond the static template, is the movement caused by the
self-revision loop and the consciousness framing (vs. mere conversation), and does it come at a
cost to helpfulness?*
