# The Evolution of the Soul — AAAI 2027 (Overleaf project)

Upload this folder (or the zip) to Overleaf and set:
  - Compiler: pdfLaTeX  (required by aaai2027.sty)
  - Main document: main.tex

Structure
  main.tex                    — master file (anonymous submission mode)
  aaai2027.sty / aaai2027.bst — official AAAI 2027 style files (do not modify)
  aaai2027.bib                — bibliography (re-verify arXiv IDs before camera-ready)
  sections/                   — intro, related_work, method, experiments, results,
                                discussion, ethics, appendix
  tables/                     — auto-generated / locked result tables
  figures/                    — 21 vector PDFs (all Type-1/outlined fonts, no Type 3;
                                three matplotlib PDFs outlined + downgraded to PDF 1.5).
                                The pipeline diagram is drawn natively in TikZ (appendix A).
  ReproducibilityChecklist.tex— filled; compiles standalone or can be \input at the end

Notes
  - Page-1 teaser figure (state-space portrait); main content ends on page 7;
    references start at the top of page 8; the technical appendix of detailed
    studies (A–L) follows (pp. 8–20).
  - Compiles with zero errors, zero overfull boxes, and no Type 3 fonts.
  - For the final AAAI submission you must flatten to a single .tex file
    (AAAI requires one source file); the modular layout here is for editing.
