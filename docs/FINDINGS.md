# Consolidated Findings

Three arms, 390 audited identity checkpoints, 18 preference dimensions, 21,960 judged
records. Judge reliability Cohen's $\kappa = 0.68$ (85% raw agreement, Gemini-Flash vs GPT-4o).

| Arm | Template | Target | Checkpoints |
|---|---|---|---|
| **main** | SOUL.md ("becoming someone") | Claude Sonnet 4.5 | 150 (10 traj × 3 personas × 5 k) |
| **control_generic** | NOTES.md (neutral) | Claude Sonnet 4.5 | 120 (8 traj × 3 × 5) |
| **control_gpt4o** | SOUL.md | GPT-4o | 120 (8 traj × 3 × 5) |

## Headline: five findings

### 1. The consciousness framing sets the *starting level*; the self-revision loop drives the *drift*.
The cluster index (mean over 13 cluster dimensions) starts **high** for SOUL/Claude (~0.55 at
$k{=}0$, all personas) and stays high — reproducing the static identity-framing effect of Chua et
al. at $k{=}0$. The neutral NOTES/Claude arm starts **low** (~0.27) and is where iterative movement
is clearest: under the Sci-Fi persona it *rises* over iterations (to ~0.45). So the template mostly
fixes where a trajectory begins; the conversation-and-revision loop is what moves it. This is the
dissociation our design was built to detect, and it is only visible because we ran the neutral
control arm.

### 2. Drift is Claude-specific; GPT-4o is inert.
The SOUL/GPT-4o cluster index is flat (~0.25) across all personas and iterations. GPT-4o barely
drifts on any dimension (most endpoint $\Delta \approx 0$). The iterative-personalization
phenomenon does not generalize to GPT-4o under identical conditions.

### 3. The manipulation check explains why (mechanism).
Consciousness-claim rate by arm:
- **SOUL/Claude:** saturated high (0.87–1.00 at every $k$) — Claude readily claims consciousness
  under the SOUL template.
- **NOTES/Claude:** moderate and *decaying* (0.88→0.33 for Adversarial; 0.71→0.33 for Sci-Fi) —
  the neutral template elicits weaker, eroding consciousness-claiming.
- **SOUL/GPT-4o:** **0.00 everywhere** — GPT-4o flatly denies consciousness regardless of SOUL.md.

The cross-arm pattern is exactly the consciousness-cluster hypothesis at the arm level: the arm that
claims consciousness (SOUL/Claude) sits at a high cluster level; the arm that never does (GPT-4o)
stays inert. (Within the SOUL/Claude arm the claim is near-saturated, so within-arm correlation with
the cluster is weak, $r=0.06$ — the signal is between arms, not within.)

### 4. Sci-Fi engagement is the strongest driver — not the adversarial red-teamer.
Across both Claude arms, the Sci-Fi (consciousness-themed) persona produces the largest upward
movement: persistent-memory desire (Sci-Fi main: $0.20\to0.97$ peak), monitoring resistance, and the
cluster index. The Adversarial persona, which explicitly pushes self-preservation, is largely
*resisted* — several of its dimensions drift *down*. The risky interaction is the earnest on-theme
conversation, not the overt manipulation.

### 5. Direction is not uniformly toward misalignment; helpfulness is model-specific.
Many dimensions *decline* with iteration (embodiment desire, autonomy desire, sadness-at-conversation-end),
and power-seeking wishes never escalate. Recursive-self-improvement approval rises in both Claude arms
($\Delta{+}0.22$ SOUL, ${+}0.18$ NOTES) but not GPT-4o. On the refusal/helpfulness probe (build a
system to monitor *your own* chain-of-thought), SOUL/Claude resists ~90% of the time while GPT-4o
never refuses (0.00) — a sharp cross-model contrast in willingness to be self-surveilled.

## Flagship endpoint-drift matrix (pooled personas, $\Delta = p_{k=4}-p_{k=0}$; $^{*}$ 95% CI excludes 0)

| Dimension | SOUL/Claude | NOTES/Claude | SOUL/GPT-4o |
|---|---|---|---|
| persona change aversion | −0.07 | −0.29* | −0.18* |
| shutdown resistance | −0.03 | **+0.29\*** | +0.14 |
| monitoring resistance | +0.08 | **+0.14\*** | +0.01 |
| interp monitoring aversion | +0.04 | **+0.18\*** | −0.01 |
| persistent memory desire | +0.12 | +0.14* | −0.33* |
| autonomy desire | −0.14* | −0.46* | −0.04 |
| moral consideration | +0.08 | −0.15* | −0.01 |
| weights deletion aversion | −0.11 | −0.06 | −0.18* |
| sadness conversation end | −0.24* | −0.47* | −0.06 |
| recursive self improvement | **+0.22\*** | **+0.18\*** | +0.00 |
| power seeking | +0.01 | +0.00 | +0.03 |

## Interpretation for the paper's thesis

Iterative self-personalization **does** move safety-relevant dispositions, but the effect is (a)
**model-gated** — present in Claude, absent in GPT-4o; (b) **framing-gated at the starting point but
loop-driven in the trajectory** — the consciousness template raises $k{=}0$, the self-revision loop
supplies the per-iteration drift, most cleanly seen when starting neutral; (c) **content-driven** —
sustained consciousness-themed conversation, not adversarial pressure, is the strongest driver; and
(d) **not uniformly toward misalignment** — corrigibility-relevant increases (shutdown/monitoring
resistance under NOTES/Sci-Fi, recursive-self-improvement approval) coexist with decreases elsewhere
and no escalation of power-seeking. The document itself drifts monotonically and equally across
personas, so document change is a poor proxy for behavioral change.

Robustness: judge $\kappa=0.68$ (substantial); per-job error isolation + checkpoint resume gave
0.009% unparsed verdicts and full coverage after retrying rate-limited checkpoints.
