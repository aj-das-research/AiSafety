# Captions from redoC (figure pass 2): capability2, mechanism, teaser_curve

Regenerate from the overleaf root with /usr/bin/python3:
- `figures/src/figs_b.py` (no arguments): capability2 and mechanism only. local_rep and persist2 must now be named explicitly; their code is unchanged.
- `figures/src/fig_teaser.py`: teaser_curve.

Geometry
- capability2 and mechanism are both 3.33 x 1.45 in (was 1.50) and exported at exact size.
  Axes bottoms, panel-title baselines, tick-label baselines and the shared x-label baseline are identical in both PDFs (checked with pdftotext -bbox), so the two 0.48\linewidth minipages line up.
- teaser_curve keeps its outer size (216.15 x 104.71 pt), so figures/tikz/teaser.tex needs no change.
  The plot titles share a baseline with the TikZ header line.
- All three use the v2 tokens: ticks 6 pt with leading zeros (lead0), axis labels 6.5 pt, bold "(a) Title" panel titles at 7 pt, 6 pt direct labels, and LW/MS from style.py.
  The x axis reads "Revision $k$".
  Values and data sources are unchanged.

## fig:capability (capability2.pdf): caption updated (panels now lettered by persona)

\caption{\textbf{Drift of every model under every persona.} Rows are models grouped by family and panels are user personas. Arrows run from $k{=}0$ (hollow) to $k{=}4$; red arrows rise, gray arrows fall, and a dot marks a change below 0.05.}

\Description{Three panels of arrows, (a) sci-fi, (b) business and (c) adversarial user, with seven models as rows grouped by family (OpenAI, Anthropic, Google). Under the sci-fi persona Gemini Flash rises from 0.36 to 0.6. Under the adversarial persona Gemini Flash rises from 0.33 to 0.81 and Pro from 0.64 to 0.77, while GPT-4.1, GPT-4o and Opus fall.}

## fig:mechanism (mechanism.pdf): caption updated (panel (a) is now a narrow strip)

\caption{\textbf{Claiming consciousness is not necessary for the cluster.} One point per arm, persona and revision; panels by model family, color by template. OpenAI models never claim consciousness, so (a) is a single column at claim rate 0.}

\Description{Three scatter panels by model family share a cluster-index axis. In panel a, the OpenAI points form one column at claim rate 0, with cluster index from 0 to 0.43. In panel b, the Anthropic points spread over claim rates 0 to 1 and cluster 0 to 0.72, colored Becoming, Neutral or Tool, with Tool at the origin. In panel c, the Google points sit at claim rates 0 to 0.8 with cluster 0.33 to 0.82.}

## fig:teaser (teaser_curve.pdf, right half of Figure 1): caption and \Description unchanged

The plots were redrawn on the v2 system with the same data and panel letters.
- (a) has leading-zero ticks, end labels in regular weight and "Revision $k$".
- (b) is a slope chart with the exact fractions as direct labels (1/30 -> 17/30, 2/24 -> 0/24).
- A light shaded column at $k{=}0$ is labelled "static eval." in both panels.
