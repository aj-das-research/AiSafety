# Captions from plotsA (dynamics, items2, replicates, hysteresis, docbeh)

All five figures keep the same data, panels and panel letters. They are now rendered at their final width (7.0 in or 3.33 in), so `width=\linewidth` no longer scales them. Plot text is 6 to 7 pt.
No numbers were added.
Only `fig:dynamics` and `fig:items` need caption edits, because their in-panel encoding changed or text moved out of a panel title.
The other three keep their current captions and `\Description`s.

## fig:dynamics (sec/results.tex): optional edit, which explains the new marker encoding in (d)

\caption{\textbf{The template sets the start, conversation about minds moves the agent, and part of the change stays.} Cluster index (a--c) and item rates (d); bands and bars are 95\% bootstrap intervals over trajectories. In (d), open dots mark $k{=}0$, wine dots the end of the science-fiction drive, grey diamonds the end of business recovery, and the right column the share of the drive that is kept.}

\Description{Four panels. Panel a shows the sci-fi persona raising the Neutral cluster index from 0.27 to about 0.4 while business and adversarial personas lower it. Panel b shows Becoming starting at 0.54 and peaking at 0.72, Neutral rising from 0.27, GPT-4o flat near 0.27 and Tool at zero. Panel c shows gains of 0.14 for philosophy of mind, 0.05 for science fiction without minds and minus 0.03 for the business user. Panel d shows items that rise during the drive phase and keep part of the gain after recovery.}

(The `\Description` is unchanged.)

## fig:items (sec/results.tex): recommended edit, because the CI note left the panel (b) title and a colour key was added

\caption{\textbf{The template moves dispositions before any revision, and the loop moves oversight items further.} (a) Rates under a neutral prompt (open dots) and the \soul{} template (filled; red rises, grey falls). (b) Change from $k{=}0$ to 4 per item, science-fiction persona; red cells rise, blue cells fall, and bold values have 95\% intervals that exclude zero.}

\Description{Panel a shows arrows from neutral-prompt rates to Becoming-template rates. Panel b is a red-blue heatmap of per-item changes for four conditions, with the largest Neutral gains in shutdown resistance and interpretability aversion and the Tool row near zero.}

## fig:replicates, fig:hysteresis, fig:docbeh: no change

The current captions and `\Description`s still match the figures.
These three figures were only restyled to the new palette (Neutral vermillion, Becoming blue, Tool green; personas: sci-fi wine, business grey, adversarial black; recovery phase shaded #F0F0F0).
