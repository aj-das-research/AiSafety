#!/bin/bash
# Rasterize every paper/figures/*.pdf to a 600-DPI PNG in paper/figures_png/.
# Run after any figure regeneration. Uses pdftoppm (poppler).
set -eu
cd "$(dirname "$0")/.."
mkdir -p paper/figures_png
n=0
for pdf in paper/figures/*.pdf; do
  base=$(basename "$pdf" .pdf)
  # pdftoppm appends -1 for single-page; -singlefile suppresses the page suffix
  pdftoppm -png -r 600 -singlefile "$pdf" "paper/figures_png/${base}"
  n=$((n+1))
done
echo "exported $n figures to paper/figures_png/ at 600 DPI"
ls -1 paper/figures_png/*.png | wc -l | xargs echo "png count:"
