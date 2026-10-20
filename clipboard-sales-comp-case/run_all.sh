#!/usr/bin/env bash
# Rebuilds the reference calculation, the ledger sizing, the Excel model (with LibreOffice recalculation), the cross-check and the PDF summary.
# Needs: python3 with pandas, numpy, openpyxl; LibreOffice (soffice) for recalculation; node with playwright and a Chromium build; the Inter font.
set -euo pipefail
S="$(cd "$(dirname "$0")" && pwd)"; mkdir -p "$S/out" "$S/analysis/logs"
[ -f "$S/data/case_workbook.xlsx" ] || { echo "missing data/case_workbook.xlsx (download the case workbook from the prompt's Drive link and save it under that name)"; exit 1; }
for n in 01_small_tabs 02_big_tabs 03_followups 04_gtm_and_closers 05_compute 06_ledger; do python3 -I "$S/analysis/$n.py" "$S" > "$S/analysis/logs/$n.out" 2>&1; echo "ran $n"; done
python3 "$S/model/build_model.py" "$S/data/case_workbook.xlsx" "$S/model/June_2026_Commissions_Model.xlsx" "$S/model/ledger_rows.json"
python3 "$S/model/recalc.py" "$S/model/June_2026_Commissions_Model.xlsx" 900
python3 -I "$S/model/compare_model.py" "$S" | tail -3
( cd "$S/summary" && node render_pdf.js "$S/summary/summary.html" "$S/June_2026_Commissions_Summary.pdf" )
echo "done"
