# The Evolution of the Soul — AAMAS 2027 submission

| File | Role |
|---|---|
| `aamas2027.tex` | **Compile root** (Overleaf: Menu → Main document, pdfLaTeX). Current draft: 10-page main text (AAMAS limit is 8), then references, then the appendix in the same PDF |
| `Appendix.tex`, `sections/`, `tables/` | Appendix body and its tables (from the earlier AAAI version) |
| `macros.tex` | Packages and macros shared by both documents |
| `figures/tikz/` | Vector diagrams: teaser, method, templates, case study, blind spots; `agents.tex` holds the expressive agent avatars |
| `figures/gen/` | Data figures (PDF/SVG/PNG) from `figures/src/figs.py` |
| `figures/data/` | `ledger.json` and `long.parquet`, built from the HF dataset `abhijit2k01/evolution-of-the-soul` by `figures/src/build_ledger.py` |
| `archive/aaai2027/` | Earlier AAAI 2027 version |

Sync: this repo is the Overleaf project; GitHub mirror is branch `paper` of `aj-das-research/AiSafety` (`paper-sync`).
Before submission: set `\acmSubmissionID{}` in both root files.
