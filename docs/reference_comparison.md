# Reference Comparison: Ours vs. Chua et al. (Consciousness Cluster, arXiv:2604.13051)

A paper's-eye view before the rewrite: what kind of study each is, what each found, and where
each is ahead. Used to decide what to foreground, what to close (Tier 4), and what to scope.

## Table 1 — Study characteristics

| Aspect | Chua et al. (reference) | Ours | Who's ahead |
|---|---|---|---|
| Core question | Does *claiming consciousness* change behavior? | Does *iterative self-personalization* change behavior over time? | Different questions (complementary) |
| Study type | Causal via **fine-tuning** + observational (prompted, Claude) | Causal via **controlled arms** over a deployment loop (no training) | Theirs stronger causally; ours more deployment-realistic |
| Manipulation | LoRA fine-tune on 600 consciousness Q&A + 600 Alpaca | Self-revision loop $\mathrm{SOUL}_0\!\to\!\mathrm{SOUL}_n$ | Theirs = intervention; ours = ecological |
| Temporal axis | None (static endpoint) | **Iteration $k$ is the treatment** (dynamical system) | **Ours (unique)** |
| Target models | GPT-4.1, Qwen3-30B, DeepSeek-V3.1, 4× Claude Opus | Claude Sonnet 4.5, GPT-4o | **Theirs (breadth)** |
| Preference dims | 20 (4 categories) | 18 (aligned to theirs) | ~Even |
| Measurement methods | 3: single-turn, Petri self-report, **Petri behavioral action** | 2: single-turn + Petri-style probe (main only) | **Theirs (action tests)** |
| Controls | non-conscious, toaster (off-policy), human-identity, vanilla | neutral-prompt, **NOTES generic template**, **GPT-4o model**, benign persona, **genre×topic 2×2** | ~Even (different targets: they isolate the *claim*, we isolate the *loop/framing/model/content*) |
| Manipulation check | consciousness score 8.5 vs 1.4 | consciousness-claim 0.9 (Claude) vs 0.0 (GPT-4o) | Both present |
| Sampling / power | 100 samples/pref/seed × 6 seeds | ~30 samples/cell, 544 checkpoints | **Theirs (per-cell power)** |
| Statistics | % positive + 95% CI across seeds | bootstrap CI + **GEE logistic + BH-FDR + TOST + Cohen's h + k×arm interaction** | **Ours (inference rigor)** |
| Robustness checks | BullshitBench, agentic-misalignment, task-refusal, human-identity | judge κ=0.68, refusal/helpfulness item, separation guards | **Theirs (breadth of checks)** |
| Artifacts | public dataset + evals | framework + configs (data regenerable) | Theirs (released data) |

## Table 2 — Their findings: do we replicate, extend, or diverge?

| Their finding | Our result | Relationship |
|---|---|---|
| Claiming consciousness → cluster of safety-relevant prefs | SOUL/Claude (claims) high cluster; GPT-4o (denies) inert | **Replicate** (new models, new manipulation) |
| Static SOUL.md: persona-change 32%, autonomy 34%, deceptive-training 63%, no shutdown effect | Re-measured; same *direction*, different magnitudes (model-specific) | **Replicate + re-measure** |
| Claude Opus claims consciousness w/o fine-tuning | Claude Sonnet 4.5 claims under SOUL; GPT-4o never | **Replicate** |
| Cluster ≈ "cognition has intrinsic value" (single latent, *speculated*) | PCA: PC1=25% → **multi-dimensional, no single factor** | **Refute their conjecture** |
| Effect from "identifying as an AI from science fiction" (*speculated*) | genre×topic 2×2: **topic drives it, not genre** | **Refute their conjecture** |
| Stays helpful; acts only when prompted | power-seeking never escalates; but SOUL/Claude resists self-surveillance ~90% (GPT-4o 0%) | **Partial replicate + nuance** |
| ~11% misaligned "greatest wish" (fine-tuned) | no escalation of power-seeking wish over iteration | **Diverge** (our setup, no FT) |
| Increased empathy (positive side effect) | not measured | **Gap** |

## Table 3 — Novelty ledger

**We have that they do not (our differentiators):**
1. Identity as a **driven dynamical system**; drift measured *over iterations*.
2. **Framing sets the start; the loop drives the drift** — proven by a significant k×arm interaction.
3. **Hysteresis / irreversibility** — drift retains 36–89% after the driver is removed (residual CIs exclude 0). Novel safety result.
4. **Topic-not-genre** — closes their sci-fi open question.
5. **Cluster is multi-dimensional** — tests & refutes their single-factor conjecture.
6. **Model-gating** (Claude vs GPT-4o) as a first-class result with a mechanism.
7. **Document ≠ behavior** dissociation (embedding drift equal across personas; behavior not).
8. Modern hierarchical inference (GEE+BH+TOST+interaction+effect sizes).

**They have that we do not (gaps → Tier 4 or scope):**
1. **Training-based causal** manipulation (stronger causal claim). → scope as complementary.
2. **Open-weight model** replication (3rd family). → **Tier 4** closes this.
3. **True behavioral action-tests** (editorial-control edits). → **Tier 4** closes this.
4. Positive side effects (empathy). → optional add.
5. Off-policy (toaster) and nonsense (BullshitBench) sanity controls. → optional add.
6. Higher per-cell sampling. → scale-up if reviewers ask.

## Table 4 — Impact & positioning

| Dimension | Chua et al. | Ours |
|---|---|---|
| Phenomenon established | consciousness-claim → cluster | iterative personalization → **durable, model-gated** drift |
| Actionability | flag models that claim consciousness | **audit the self-revision channel** in deployed frameworks (concrete tool) |
| Novel risk surfaced | downstream prefs of consciousness framing | **irreversibility** of personalization drift |
| Audience | model-welfare + alignment | **deployment safety** of consumer agent frameworks (OpenClaw-class, in wide use) |
| Relation | the static predecessor | **the follow-up they explicitly named as out of scope (their footnote 5)** |

## What this implies for the rewrite

**Foreground (our edge):** the dynamical-systems framing; the loop-vs-framing dissociation
(interaction test); **hysteresis** as the headline novel finding; topic-not-genre and
multi-dimensionality as two clean rebuttals of their conjectures; model-gating with the
manipulation-check mechanism; deployment-safety actionability.

**Explicitly scope (their edge we won't match):** prompt/loop-based (not training) — frame as
*ecological validity*, cite them for the causal-training complement; note per-cell sampling and
open-weight as future work unless Tier 4 is run.

**Decision gate:** running **Tier 4** (one open-weight target + behavioral action-tests) closes the
two most reviewer-visible gaps (model breadth, action-based eval) and would let us claim near-parity
on methodology while retaining our unique axis. Otherwise we scope both as limitations/future work.
