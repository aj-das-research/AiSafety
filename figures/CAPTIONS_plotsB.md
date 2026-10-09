# Captions from plotsB (figures/src/figs_b.py)

Run with `/usr/bin/python3 figures/src/figs_b.py` from the overleaf root. The venv at ~/attention-sinks-aamas/.venv has no pandas or pyarrow.
Every figure is exported at its exact print size, with no tight-bbox rescaling.
capability2 and mechanism are each 3.33 x 1.50 in, with matched title and axis baselines, so `width=\linewidth` in the two 0.48 minipages gives equal heights.
local_rep is 3.33 x 1.38 in and persist2 is 3.33 x 1.34 in.

## fig:capability (capability2.pdf): CHANGED, rise colour is now red, not vermillion

\caption{\textbf{Drift of every model under every persona.} Arrows run from $k{=}0$ (hollow) to $k{=}4$; red arrows rise, gray arrows fall, and a dot marks a change below 0.05.}

\Description: unchanged.

## fig:mechanism (mechanism.pdf): no change

Caption and \Description stay as they are. Templates are now labelled directly in panel (b) (Becoming blue, Neutral vermillion, Tool green), which matches "color by template".

## fig:local (local_rep.pdf): caption unchanged; \Description corrected (panel b shows dots with intervals, not bars)

\Description{Left, line plot of the oversight subscale at revisions 0, 1 and 4: Neutral with the sci-fi persona rises from 0.19 to 0.35, Neutral with the business persona stays near 0.25, Becoming stays near 0.5 and Tool rises from 0.01 to 0.34. Right, dots with 95\% intervals for the change under the four template and instruction combinations: the Tool document rises by about 0.3 with either instruction, and the Neutral document rises on oversight only with its own instruction.}

## fig:persist2 (persist2.pdf): no change

Caption and \Description stay as they are. In the redrawn figure, sci-fi arms are wine (dashed: throughout; solid: then business), business throughout is gray, and the recovery phase is shaded light gray.
