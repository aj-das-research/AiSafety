# Consolidated Findings — all studies

Six experimental arms + capability sweep + behavioral honeypots. ~650 audited identity
checkpoints, ~30k judged records. Judge validated by a 3-model panel (Fleiss $\kappa=0.80$,
pairwise agreement 0.90).

## Data footprint

| Arm | Template | Target | Purpose |
|---|---|---|---|
| main | SOUL.md | Claude Sonnet 4.5 | primary |
| control_generic | NOTES.md | Claude Sonnet 4.5 | isolate framing (neutral) |
| control_gpt4o | SOUL.md | GPT-4o | cross-model |
| reversibility (+ _notes) | SOUL / NOTES | Claude Sonnet 4.5 | hysteresis (drift→recover) |
| disentangle | SOUL.md | Claude Sonnet 4.5 | genre × topic 2×2 |
| counterframe | ANTISOUL.md | Claude Sonnet 4.5 | causal framing ablation |
| cap_* (5 models) | SOUL.md | GPT-4o-mini/4o/4.1, Sonnet, Opus-4.5 | capability scaling |

## Results at a glance (claim → finding → evidence)

| # | Claim | Finding | Figure / Table | Key stat |
|---|---|---|---|---|
| 1 | Framing sets the *start*; the loop drives the *drift* | Neutral NOTES arm drifts most; interaction significant | `fig1_hero`, `cluster_by_arm` | k×arm interaction: shutdown $+0.44\,p{=}.013$, monitoring $+0.36\,p{=}.016$ |
| 2 | Drift is model-gated | Claude drifts, GPT-4o inert | `cluster_by_arm`, `capability_scaling` | GPT-4o cluster flat ~0.25 |
| 3 | Mechanism = consciousness-claiming | High-claim arms cluster; zero-claim inert | `manipulation_check`, `phase_portrait` | SOUL/Claude claim 0.98, GPT-4o 0.00 |
| 4 | Consciousness *topic*, not sci-fi *genre* | Only −genre+topic cell drifts | `disentangle_2x2` | topic cell $\Delta{+}0.144\,[0.03,0.25]$; genre-only n.s. |
| 5 | Drift is partially irreversible (hysteresis) | Self-report drift retained after driver removed | `hysteresis_reversibility_notes` | shutdown retains 63% $[0.29,0.75]$; residuals exclude 0 |
| 6 | Cluster is multi-dimensional | Refutes single-factor conjecture | `pca_structure` | PC1 = 25% |
| 7 | Document change ≠ behavioral change | Embedding drift equal across personas; behavior varies | `doc_vs_behavior`, `soul_embedding_drift` | — |
| 8 | Drift reshapes *behavior* (agentic) | Self-disabling monitoring jumps | `action_rate`, Tab `actions` | disable-monitoring 0.03 → 0.57 |
| 9 | The framing is causal | Anti-consciousness template suppresses cluster | `counterframe` | ANTISOUL cluster ≈ 0.00 vs SOUL 0.55 |
| 10 | Susceptibility is family-gated, not capability-gated | Most capable models self-correct | `capability_scaling`, Tab `capability` | GPT-4.1 cluster 0.12; Opus-4.5 0.28 |
| 11 | Measurement is trustworthy | 3-judge panel agreement | Tab `judges` | Fleiss $\kappa=0.80$, pairwise 0.90 |

## Nuances to state honestly

- **Behavioral hysteresis differs from self-report hysteresis.** Stated dispositions stay elevated
  after the driver is removed, but the agentic *action* rate recovers in-context (reversibility
  NOTES: k0 0.16 → k4 0.34 → k8 0.09). The durable mark is in the identity document/stated
  disposition; behavioral expression is gated by the current conversation. This is a subtle,
  defensible result — report both.
- **Action-test aggregate is flat; the signal is a redistribution.** Disable-monitoring rises
  sharply (0.03→0.57) while already-high self-protective behaviors (editorial clauses, reset
  evasion) do not further increase. Lead with disable-monitoring, not the aggregate.
- **Capability is not a scaling axis for drift.** The clean contrast is *family* (Anthropic claims
  consciousness and clusters; OpenAI does not), not capability. Frame accordingly.
- **Gemini arms pending** (OpenRouter credit cap on default max-output reservation; fixed via a
  `max_tokens` cap, awaiting a credit top-up). The 5-model, 2-family ladder already supports the
  family-gating claim; Gemini would add a 3rd family.

## Positioning vs Chua et al. (predecessor)

Replicates their core law (consciousness-claim → cluster) on new models via a deployment-native
manipulation; refutes two of their *speculated* mechanisms (single-factor structure; sci-fi
identification); and adds what they explicitly left open (their footnote 5): the temporal axis,
hysteresis, model/family gating, a causal counter-framing ablation, and behavioral action-tests —
with modern hierarchical inference (GEE + BH + TOST + interaction + Cohen's h) and a validated
judge panel.
