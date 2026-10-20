#!/usr/bin/env bash
# Rebuilds every table, figure and the PDF from the raw exports in data/.
# Needs: python3 with pandas, openpyxl, numpy, matplotlib; node with playwright and a Chromium build; the Inter font.
set -euo pipefail
S="$(cd "$(dirname "$0")" && pwd)"; mkdir -p "$S/analysis/logs" "$S/out" "$S/fig"
for f in shifts cancels; do [ -f "$S/data/$f.xlsx" ] || { echo "missing data/$f.xlsx (export the Google Sheet as .xlsx)"; exit 1; }; done
python3 -I "$S/analysis/00_convert.py" "$S"
python3 -I "$S/analysis/01_explore.py" "$S" | tee "$S/analysis/logs/01_explore.out"
python3 -I "$S/analysis/02_cleveland.py" "$S" | tee "$S/analysis/logs/02_cleveland.out"
python3 -I "$S/analysis/03_mechanisms.py" "$S" | tee "$S/analysis/logs/03_mechanisms.out"
python3 -I "$S/analysis/04_extra.py" "$S" | tee "$S/analysis/logs/04_extra.out"
python3 -I "$S/analysis/05_charts.py" "$S"
( cd "$S/writeup" && python3 -I build.py "$S" && node render_pdf.js "$S/writeup/Confirm_or_Release_Clipboard_Case.html" "$S/Confirm_or_Release_Clipboard_Case.pdf" )
echo "done: $S/Confirm_or_Release_Clipboard_Case.pdf"
