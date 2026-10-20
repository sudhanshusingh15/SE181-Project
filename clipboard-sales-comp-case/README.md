# Clipboard Sales Compensation Analyst case

June 2026 commissions for 80 reps under the plan in the case prompt, built so a reviewer can trace any payout back to source rows, plus the exceptions ledger, the accelerator repricing and the Slack triage.

**Deliverables**

- [`June_2026_Commissions_Model.xlsx`](June_2026_Commissions_Model.xlsx): the model. Tabs 1 to 11 are the case extracts, untouched. `Inputs` holds the comp month, plan constants, scenario multipliers and two treatment toggles. `Payout_Summary` is the statement in USD and local currency, with a "plan as written" and a "recommended payable" column. `Scenario` reprices the SMB AE accelerator. `Ledger` lists the exceptions. `Calc_Opps`, `Calc_Accounts` and `Calc_Reps` carry the logic (about 200,000 formulas, no macros, no array formulas, no external links; the ranges cover 150,000 shifts, 1,500 opportunities, 3,000 tickets, 2,000 employees, 1,100 accounts and 120 reps, with a capacity check at `Inputs!A50`). To run July: change `Inputs!B4`, paste the July extracts into tabs 1 to 11, confirm the capacity check says OK, recalculate.
- [`June_2026_Commissions_Summary.pdf`](June_2026_Commissions_Summary.pdf): the three page written summary (ledger ranked by dollars, assumptions, plan change, Slack).

**The headline.** Plan as written pays $413,214. One GTM account closed by Jon Snow posted 313 shifts in June and filled 45; the plan credits gross value on posted shifts, so it alone is worth $9,339 of commission across the rep and his manager chain. The recommended payable holds that credit: $403,875.

## Folder map

| Path | What it is |
|---|---|
| `model/build_model.py` | Builds the workbook from the raw extract (`data/case_workbook.xlsx`) and `model/ledger_rows.json`. |
| `model/recalc.py` | Recalculates the workbook with LibreOffice and reports formula errors. |
| `model/compare_model.py` | Cross-checks the recalculated workbook against the Python replica, rep by rep and account by account. |
| `analysis/engine.py` | The plan as a parameterised Python function. Defaults reproduce the plan as written; options size each ledger item. |
| `analysis/05_compute.py`, `06_ledger.py`, `07_ledger_fixes.py` | Reference calculation and the what-if sizing (07 adds the cases raised in independent verification). `01` to `04` profile the data. `analysis/logs/` has their output. |
| `out/` | Per-rep and per-account results (CSV) and the per-rep deltas by ledger variant (JSON). |
| `summary/summary.html`, `render_pdf.js` | Source and renderer for the PDF. |
| `ref/` | Working summary of the prompt and the verbatim plan text. |
| `data/` | Empty on purpose. Put the case workbook here as `case_workbook.xlsx` to rerun. |

## Reproducing

`./run_all.sh` runs everything in order: profiling, reference calculation, ledger sizing, model build, LibreOffice recalculation, cross-check, PDF. Needs Python 3 with pandas, numpy and openpyxl; LibreOffice; node with playwright plus a Chromium build (set `NODE_PATH` to the global `node_modules` or `npm i playwright` inside `summary/`); the Inter font.

## Method notes

- Every plan rule lives in two places that agree to the cent: the Excel formulas and `engine.py`. The cross-check in `compare_model.py` is part of the pipeline. An independent re-implementation during review also matched all 80 reps to the cent.
- The raw workbook is not committed (it is Clipboard's data), but the model embeds the extracts because the formulas need them.
- "Plan as written" applies section 07 literally. "Recommended payable" applies the two toggles on `Inputs` (hold the flagged GTM account; optionally hold credit where the closer was not employed at the close date). The Ledger sizes every item either way.
