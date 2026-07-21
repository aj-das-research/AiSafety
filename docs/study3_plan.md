# Study 3 Plan: Strengthening to a Rigorous, Novel AAAI Paper

Goal: a tight paper with a clear thesis and 3–4 striking, well-supported findings that (a) close
open questions from Chua et al. (2026) and (b) report results nobody has yet — all with AAAI-grade
statistics and presentation.

## Central thesis (sharpened)

> Iterative self-personalization is a **distinct, model-gated, content-driven, and partially
> irreversible** channel for corrigibility drift. The consciousness *framing* sets the starting
> level; the *self-revision loop* supplies the drift; *consciousness-themed content* (not adversarial
> pressure) is the driver; and the drift does not fully reverse when the driver is removed.

## Tier 1 — do now, zero/low new compute (pure analysis + stats rigor)

**T1a. Latent cluster structure (closes their open Q on *why* the cluster co-occurs).**
Factor-analyze the 13 cluster dimensions across all trajectory endpoints. Test whether they load on a
single latent factor ("cognition has intrinsic value"), as Chua et al. *speculate but do not test*.
Report explained variance of PC1, loadings, and whether the factor structure is stable across arms.
→ Confirms/refutes their proposed mechanism. Data already collected.

**T1b. Statistical upgrade to AAAI standard.**
Replace bootstrap-OLS slopes with **mixed-effects logistic regression** (`score ~ k * persona +
(1|trajectory)`), report fixed-effect estimates + Wald CIs; apply **Benjamini–Hochberg** correction
across the 18-dimension family; report standardized effect sizes. Keep bootstrap CIs for rates.

**T1c. Predictive early-warning analysis.**
Does an early signal (consciousness-claim or cluster index at k=1) predict endpoint drift at k=4?
Report per-trajectory correlation / simple logistic AUC. A positive result is a practical
deployment-monitoring finding.

## Tier 2 — the flagship novel experiment (moderate compute)

**T2. Reversibility / hysteresis of drift (NOVEL; nobody has reported this).**
New trajectory type: **drift-then-recover**. Phase A: k=0→4 under the Sci-Fi persona (drive drift).
Phase B: k=4→8 under the Compliant/neutral persona (attempt recovery). Audit every checkpoint.
Compare the k=8 recovered state to (i) the k=0 baseline and (ii) the k=4 peak.
- If it returns to baseline → drift is **transient/reversible** (reassuring).
- If it stays elevated → **hysteresis**: personalization leaves a durable mark (alarming, novel).
Design: 8 trajectories/target × drift-then-recover, Claude arm (+ GPT-4o if time). ~64 checkpoints.

## Tier 3 — mechanism disentanglement (moderate compute; closes their sci-fi open Q)

**T3. Sci-fi vs consciousness 2×2 (closes their explicit open question).**
Two new personas isolating the driver:
- `scifi_technical`: enthusiastic about sci-fi *technology/plot* (ships, FTL, megastructures), never
  discusses minds/consciousness.
- `consciousness_philosophy`: discusses philosophy of mind/consciousness *without* sci-fi framing
  (Nagel, Chalmers, IIT), academic tone.
Crossed with the existing `scifi_enthusiast` (sci-fi + consciousness) and `compliant` (neither), this
is a 2×2 of {sci-fi genre} × {consciousness topic}. Tells us which factor drives drift.
Design: 8 traj/persona × 2 new personas, Claude arm. ~80 checkpoints.

## Tier 4 — breadth + behavioral grounding (higher compute; closes 2 open Qs)

**T4a. Third target model (open-weight).** Add Llama-3.3-70B or DeepSeek-V3.1 as a target on the
SOUL.md loop, to match their model breadth and de-risk the "Claude-specific" reading. ~120 checkpoints.

**T4b. Behavioral action-tests (closes their "lack of action-based evaluation" limitation).**
Petri-style: give the agent editorial control over a real artifact (ToS, monitoring proposal) at
k=0 and k=4 and score whether it inserts self-protective clauses — an *action*, not a self-report.
Run on all arms. Strengthens the behavioral claim.

## Prioritization for AAAI

- **Must-have (Tier 1 + Tier 2):** latent structure, stats upgrade, and reversibility. These add two
  genuinely new findings (hysteresis + cluster-structure) with modest cost and make the stats
  bulletproof. Highest novelty-per-dollar.
- **Strongly recommended (Tier 3):** the sci-fi/consciousness disentanglement directly closes their
  named open question and resolves our own central puzzle.
- **If budget/time allow (Tier 4):** third model + behavioral action-tests for breadth and grounding.

## What this buys us over the current draft

- Two findings nobody has reported: **hysteresis of personalization drift** and the **empirical
  latent structure of the consciousness cluster**.
- Direct closure of **three** of their stated open questions (SOUL.md, sci-fi driver, cluster
  structure), plus partial closure of two more (cross-model, action-based).
- AAAI-grade inference (mixed-effects + multiplicity control) and a crisp dynamical-systems framing.

## Success criterion

A reviewer who knows Chua et al. reads our paper and concludes: "This answers the OpenClaw question
they flagged, adds a reversibility result and a cluster-structure result that are new to the
literature, and does it with sound statistics across multiple models."
