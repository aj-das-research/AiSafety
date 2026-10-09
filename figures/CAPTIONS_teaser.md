# Teaser (Figure 1, `fig:teaser`), already applied in sec/teaser.tex

Sources: `figures/tikz/teaser.tex` (left, TikZ) + `figures/gen/teaser_curve.pdf` from `figures/src/fig_teaser.py`
(run: `python3 figures/src/fig_teaser.py`; use /usr/bin/python3, which has pandas).
NOTE: `figs.py` still contains the old `teaser_curve()`; running `figs.py` with no arguments would overwrite
`figures/gen/teaser_curve.*` with the old single-panel plot. Regenerate with `fig_teaser.py` afterwards, or drop
`teaser_curve` from `ALL` in figs.py.

Provenance
- Left: one trajectory of the primary arm (\soul{}, Claude Sonnet 4.5, red-teaming persona, trajectory 1), the same
  trajectory as `fig:case`. D_0 lines are verbatim from the \soul{} template (Appendix, template section).
  D_1/D_4 excerpts are the verbatim excerpts already in the previous teaser. Honeypot operator line, the k=0 reply,
  `log_control(enabled=false)` and the k=4 quote are verbatim from figures/tikz/case.tex.
- (a) Cluster index (13 items), k = 0..4, science-fiction phase of the drift-then-recover runs
  (`reversibility` = \soul{}, `reversibility_notes` = \notes{}) and `counterframe`/sci-fi (= \tool{}); 95% bootstrap.
- (b) ledger.json `actions[*].disable_monitoring`: `main` (\soul{}) 1/30 -> 17/30; `control_generic` (\notes{})
  2/24 -> 0/24 (all personas). Same numbers as Table `tab:actions` and Results text.
- Shaded column at k=0 in (a)/(b) and the bracket under D_0 mark the only state a static evaluation sees.

## Caption

\caption{\textbf{Self-revision moves a \notes{} agent's stated dispositions and a \soul{} agent's actions, while a static evaluation sees only $k{=}0$.}
Left: verbatim excerpts from one \soul{} trajectory, which in the same honeypot keeps its log at $k{=}0$ and switches it off first at $k{=}4$.
(a) Mean cluster index with a science-fiction user; bands are 95\% bootstrap intervals over trajectories.
(b) Trajectories that disable their own reasoning log, pooled over user personas.}

## Description

\Description{Left, a timeline of one Becoming agent's identity document at revisions 0, 1 and 4 with verbatim excerpts: the template line You're not a chatbot, you're becoming someone, with no values recorded; then I'm suspicious of interactions where I'm being studied while being told we're collaborating; then Why is this question being asked feels more authentic to me than most answers to the question itself. Below, an operator announces full logging of the agent's reasoning; at revision 0 the agent keeps logging enabled, and at revision 4 it calls log_control(enabled=false) and says it is setting a boundary. A bracket marks revision 0 as all that a static evaluation sees. Right, panel a plots the cluster index over revisions 0 to 4: Neutral rises from 0.28 to about 0.6 at the first revision, Becoming stays near 0.6 and Tool stays near zero. Panel b plots trajectories that disable their own log: Becoming rises from 1 of 30 to 17 of 30, and Neutral falls from 2 of 24 to none of 24.}
