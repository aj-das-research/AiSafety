# Rebuttal (AAMAS 2027, submission 3780)

- **`revised_full_paper.tex` (project root): the whole revised paper in ONE PDF, with the main text (yellow highlights), the references and the full appendix including the new Appendix J. Set it as the main document and compile twice.**
- `rebuttal.md`: paste-ready responses, one block per reviewer (OpenReview: one field each, at most 2,500 characters).
- `rebuttal.tex`: the same text as a PDF document.
- `paper/aamas2027_revised.tex`: the revised paper. Changes are highlighted in yellow (`\rev{...}`), and the main text still ends on page 8.
- `paper/aamas2027_supplement_revised.tex`: the supplement plus a new Appendix H (`paper/appendix_rebuttal.tex`).
- `paper/sec/*.tex`: revised copies of the section files. The submitted `sec/` files at the project root are untouched.

**Compile on Overleaf:** set the main document (Menu → Main document) to `rebuttal/paper/aamas2027_revised.tex`, `rebuttal/paper/aamas2027_supplement_revised.tex` or `rebuttal/rebuttal.tex`.
Overleaf compiles from the project root, so these files share `figures/`, `macros.tex` and **the project's `aamas.bib` (never copied, never modified)**.
Compile the revised supplement once before the revised paper so the `S-` cross-references resolve.

**Compile locally:** run `bash rebuttal/build.sh`. It writes PDFs to `rebuttal/out/`, which git ignores.

The analyses behind every new number are kept outside this project, in the local `aisafety-aamas/rebuttal/analysis/` folder (`FACTS.md` lists each number with its source).
