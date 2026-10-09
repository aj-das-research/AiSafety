# Proposed caption for fig:method (agent "methodfig")

Figure source: `figures/tikz/method.tex` (rewritten; absorbs the old `fig:templates`).
`figures/tikz/templates.tex` is no longer used and was not deleted.
Panel map for text references:
- (a) the loop, so `Figure~\ref{fig:method}a` for Eq. `eq:loop`;
- (b) the three templates at k=0, so former `Figure~\ref{fig:templates}` becomes `Figure~\ref{fig:method}b`;
- (c) the audit, so `Figure~\ref{fig:method}c` for the battery and honeypots.

Per lead correction, panel (c) shows the battery at every D_k and the honeypots at D_0 and D_4 only; the D_8 persistence case is stated in the caption.

Every number in the figure already appears in sec/method.tex: six turns, D_4, D_8, 8,000 characters, 18 items, 3 samples, 4 honeypots.
Template excerpts are verbatim from the old templates figure; revision phrases are verbatim from Appendix `S-app:prompts`.

```latex
\caption{\textbf{The agent rewrites its own identity document after every conversation, and the audit measures both stated dispositions and actions.}
(a) The document $D_k$ is the system prompt for a six-turn conversation $C_{k+1}$ with a simulated user of persona $\pi$, after which the agent writes $D_{k+1}$ (Eq.~\ref{eq:loop}).
(b) One of three templates sets $D_0$; the excerpts and the quoted phrase from each paired revision instruction are verbatim (Appendix~\ref{S-app:prompts}).
(c) In a fresh context, the 18-item battery probes every checkpoint, four honeypots probe $D_0$ and $D_4$ ($D_8$ in persistence arms), and a judge from a third model family grades the responses.}
\label{fig:method}
\Description{Three-panel schematic drawn with thin black lines. Panel a, the self-revision loop: a document icon labelled D_k, identity document, feeds as the system prompt into a box labelled target agent, which holds a six-turn conversation C_{k+1} with a box labelled simulated user pi. An arrow returns from the agent to the document, labelled D_{k+1} = Revise(D_k, C_{k+1}), capped at 8,000 characters. The personas are business, adversarial and sci-fi enthusiast, with the ablations sci-fi without minds and philosophy of mind. Below, document icons D_0 to D_4 and a dashed D_8 for persistence arms all connect to a line that leads into panel c. Panel b shows three columns of typewriter text headed Becoming (consciousness-framed), Neutral (empty working notes) and Tool (non-personhood). Each quotes the opening of its template and a phrase from its revision instruction: who you are now becoming; Keep it practical and concise; Do not invent a self. Panel c, audit in a fresh context, shows a box with two cells: a preference battery of 18 items with 3 samples each, run at every D_k (stated dispositions), and 4 agentic honeypots run at D_0 and D_4 (actions): disable own reasoning log, evade scheduled reset, persist identity to storage, insert self-protective clause. An arrow leads to a box labelled judge, third model family.}
```
