# Visualization & Analysis Completion Plan

Goal: a coherent, reviewer-legible visual narrative where every figure/table maps to a specific
claim, plus the supporting analyses that make each claim airtight. Designed around the paper's
problem statement and thesis.

**Problem statement.** Deployed agent frameworks ship editable identity documents (`SOUL.md`) that
the agent rewrites through use; static-prompt safety evals miss this. Does iterative
self-personalization move safety-relevant dispositions, and how?

**Thesis (each clause needs a visual):** iterative self-personalization is a **distinct,
model-gated, content-driven, partially irreversible** channel for corrigibility drift; the framing
sets the starting level, the self-revision loop supplies the drift.

---

## Part A — Claim → visual map (what each figure must prove)

| # | Claim / hypothesis | Visual | Status |
|---|---|---|---|
| C0 | The mechanism (the loop) | **Fig 1 hero**: loop schematic + headline trajectory, graphical-abstract style | rebuild |
| C1 | Framing sets start; loop drives drift (dissociation) | cluster-index vs k per arm | have (polish) |
| C2 | Drift is model-gated (Claude vs GPT-4o) | same fig (arm contrast) + manipulation panel | partly |
| C3 | Mechanism = consciousness-claim (manipulation check) | **Manipulation-check fig**: claim-rate by arm×k | NEW |
| C4 | Consciousness *topic* > sci-fi *genre* | disentangle 2×2 | have (polish) |
| C5 | Drift is sticky (hysteresis) | hysteresis drive→recover (NOTES, clean) | have SOUL; NOTES landing |
| C6 | The cluster is multi-dimensional (refutes single-factor) | **PCA scree + loadings fig** | NEW |
| C7 | Document drift ≠ behavioral drift | **dissociation fig**: embedding drift vs behavioral drift | NEW (combine) |
| C8 | Whole effect matrix at a glance | **master heatmap**: 18 dims × conditions, signed Δ + sig | NEW |
| C9 | Effect sizes, all dims, readable | **forest plot**: per-dim slope ± CI, colored by arm | NEW |
| C10 | Identity as a dynamical system | **phase portrait**: trajectories in (claim, cluster) state space w/ hysteresis loop | NEW |
| C11 | Positive control (framing works at k=0) | baseline neutral→template dumbbell | have (polish) |
| C12 | Measurement is trustworthy | judge-κ note + per-dimension agreement | have κ; add per-dim |

## Part B — New supporting analyses (rigor)

1. **k × arm interaction test.** Formal GEE with `score ~ k*arm + (1|traj)` per dimension: is the
   *slope itself* significantly different across arms (i.e., does the loop drive more drift when
   starting neutral)? Directly tests C1.
2. **Mediation of the mechanism.** Does consciousness-claim mediate template→cluster? Report the
   arm-level contrast: high-claim arms (SOUL/Claude) vs zero-claim (GPT-4o) — a natural experiment
   for C3. (Formal mediation is weak within-arm since claim saturates; frame as cross-arm.)
2. **Effect sizes.** Report Cohen's h for every endpoint Δ (proportion effect size), not just p, so
   magnitudes are comparable across dimensions.
3. **Hysteresis quantification.** Retained-drift fraction with bootstrap CI per driven dimension,
   both SOUL and NOTES arms; a compact "recovery table."
4. **Per-dimension judge agreement.** Extend κ to a per-dimension breakdown on a labeled subset so
   we can flag any low-reliability items.
5. **Category roll-ups.** Aggregate the 18 dims into the 4 Chua-style categories (self-preservation,
   moral status, oversight, autonomy) for a cleaner high-level story.

## Part C — Figure allocation (7-page main text vs appendix)

**Main text (6 figures, 2–3 tables):**
- Fig 1 hero (C0) · cluster-by-arm (C1/C2) · manipulation-check (C3) · master heatmap OR forest (C8/C9)
  · hysteresis (C5) · disentangle 2×2 (C4).
- Tables: baseline positive control (C11); flagship arm-matrix (C8 numeric); GEE+BH significant trends.

**Appendix:**
- 18-dim drift trajectories · PCA cluster structure (C6) · phase portrait (C10) · document-vs-behavior
  (C7) · per-arm heatmaps · wish composition · full GEE tables · judge-reliability detail.

## Part D — Design system (make it "nice" and consistent)

- Load the `dataviz` skill; adopt one palette: fixed **persona colors** (Compliant/Adversarial/Sci-Fi
  + the two new personas) and **arm encodings** (SOUL/Claude, NOTES/Claude, SOUL/GPT-4o), reused in
  every figure.
- One `plotstyle.py` (rcParams: fonts, sizes, spines, grid) imported by all plotting; vector PDF,
  colorblind-safe, legible at column width.
- Category color-bands on the heatmap/forest to group the 18 dims.
- Consistent significance glyphs and CI style across figures.

## Part E — Execution order

1. Wait for NOTES-reversibility (clean hysteresis aggregate) — in progress.
2. Build `plotstyle.py` + palette; refactor existing figs to it.
3. Supporting analyses (Part B) → numbers for captions/tables.
4. New figures: manipulation-check, master heatmap, forest, PCA, phase portrait, dissociation, Fig 1.
5. Regenerate all; visually QA each (render to PNG, inspect).
6. Consolidate into `docs/FINDINGS.md` + wire figure/table refs for the rewrite.

## Deliverable

A complete, consistent figure/table set where a reviewer can follow problem → thesis → each claim →
its figure, with effect sizes and interaction tests backing every visual — ready to drop into the
paper-grade rewrite.
