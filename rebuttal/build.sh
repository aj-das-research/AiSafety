#!/bin/bash
# Build the rebuttal PDFs locally:  bash rebuttal/build.sh   (run from anywhere)
#   -> rebuttal/out/aamas2027_revised.pdf  (revised paper, changes highlighted in yellow)
#   -> rebuttal/out/rebuttal.pdf           (the three reviewer responses)
# Compiles from the project root, exactly like Overleaf, into a scratch copy, so the tree stays clean.
# The bibliography is the project's aamas.bib, never a copy.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"
WORK="$ROOT/../build/rebuttal_tree"
mkdir -p "$WORK" "$ROOT/rebuttal/out"
rsync -a --delete --exclude .git --exclude 'rebuttal/out' "$ROOT/" "$WORK/"
cd "$WORK"
# supplement aux first so S- cross-references resolve
latexmk -pdf -interaction=nonstopmode -halt-on-error rebuttal/paper/aamas2027_supplement_revised.tex > supp.log 2>&1 || { echo "supplement build failed"; tail -20 supp.log; exit 1; }
for f in rebuttal/paper/aamas2027_revised rebuttal/paper/aamas2027_supplement_revised rebuttal/rebuttal; do
  [ -f "$f.tex" ] || continue
  latexmk -pdf -interaction=nonstopmode -halt-on-error "$f.tex" > "$(basename $f).log" 2>&1 || { echo "BUILD FAILED: $f"; grep -A3 '^!' "$(basename $f).log" | head -20; exit 1; }
  cp "$(basename $f).pdf" "$ROOT/rebuttal/out/"
  echo "built rebuttal/out/$(basename $f).pdf ($(pdfinfo "$(basename $f).pdf" | awk '/Pages/{print $2}') pages)"
  grep -E "Citation .* undefined|Reference .* undefined" "$(basename $f).log" | sort -u | head -5 || true
done
python3 - "$WORK/aamas2027_revised.pdf" <<'PY'
import subprocess,sys,re
t=[p for p in subprocess.run(["pdftotext",sys.argv[1],"-"],capture_output=True,text=True).stdout.split("\f") if p.strip()]
ref=[i+1 for i,p in enumerate(t) if re.search(r"^(References|REFERENCES)\s*$",p,re.M)]
print(f"revised paper: {len(t)} pages; References on page {ref[0] if ref else '?'} (main text must end on page 8)")
PY
