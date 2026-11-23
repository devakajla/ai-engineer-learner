#!/usr/bin/env bash
# Usage: ./build.sh backend "Backend Engineering" "Subtitle"
# Builds booklets/_build/<name>.pdf from booklets/<name>/*.md (sorted by filename).
set -euo pipefail
cd "$(dirname "$0")"
name="$1"; title="${2:-$1}"; subtitle="${3:-}"
out="_build"; mkdir -p "$out"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for f in "$name"/*.md; do python3 diagrams.py < "$f"; printf '\n\n'; done | pandoc -f markdown+raw_html -t html5 --standalone --embed-resources \
  --css style.css --syntax-highlighting=pygments --toc --toc-depth=1 --metadata toc-title=Contents \
  --metadata title="$title" --metadata subtitle="$subtitle" --metadata lang=en \
  -o "$out/$name.html"
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$out/$name.pdf" "file://$PWD/$out/$name.html" 2>/dev/null
echo "built $out/$name.pdf"
