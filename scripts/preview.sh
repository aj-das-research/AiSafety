#!/bin/bash
# Private compile: scripts/preview.sh NAME  -> ~/aisafety-aamas/build/NAME/aamas2027.pdf
# Copies the shared overleaf tree to a private dir so parallel agents never clash.
set -e
NAME=${1:?name}
export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"
OUT=~/aisafety-aamas/build/$NAME
mkdir -p "$OUT"
rsync -a --delete --exclude .git --exclude '*.aux' --exclude '*.bbl' --exclude '*.fls' --exclude '*.fdb_latexmk' ~/aisafety-aamas/overleaf/ "$OUT/"
cd "$OUT"
latexmk -pdf -interaction=nonstopmode -halt-on-error aamas2027.tex > build.log 2>&1 || { grep -A3 -E "^!" build.log | head -30; echo "BUILD FAILED (see $OUT/build.log)"; exit 1; }
python3 - "$OUT/aamas2027.pdf" <<'PY'
import subprocess,sys,re
t=subprocess.run(["pdftotext",sys.argv[1],"-"],capture_output=True,text=True).stdout.split("\f")
t=[p for p in t if p.strip()]
ref=[i+1 for i,p in enumerate(t) if re.search(r"^(References|REFERENCES)\s*$",p,re.M)]
print(f"PDF pages: {len(t)}; References heading on page: {ref[0] if ref else '?'} (main text must end on page 8)")
PY
grep -cE "Overfull \\\\hbox" build.log | xargs echo "overfull hboxes:"
grep -E "Reference .* undefined|Citation .* undefined" build.log | grep -vE "S-app|TotPages|app:|eq:app" | sort -u | head
echo "PDF: $OUT/aamas2027.pdf"
