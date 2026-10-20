# Clipboard marketplace reliability case

A project proposal written for the Clipboard "Marketplace Reliability" candidate case: cut the damage from late shift cancellations in a two-sided healthcare staffing marketplace.

**Deliverable:** [`Confirm_or_Release_Clipboard_Case.pdf`](Confirm_or_Release_Clipboard_Case.pdf). Six pages of narrative plus a four page appendix of tables and figures.

**The proposal in one paragraph.** Every booked shift must be confirmed by the professional between 48 and 24 hours before it starts, with one tap on the reminder already sent. An unconfirmed shift is released back to the marketplace at the 24 hour mark with no penalty, and the facility is told right away. The data shows that shifts canceled inside 24 hours stay empty two thirds of the time while shifts released a day or more ahead mostly get refilled, and that punishing late cancelers harder would cost about three worked shifts per cancellation avoided because they are also the highest volume workers. Moving the decision point to 24 hours is the cheapest lever on the one variable that matters: lead time.

## Folder map

| Path | What it is |
|---|---|
| `Confirm_or_Release_Clipboard_Case.pdf` | The submission. |
| `writeup/template.html`, `build.py`, `render_pdf.js` | Narrative source, appendix table builder, PDF renderer (Playwright + Chromium). |
| `analysis/00_convert.py` to `05_charts.py` | The analysis pipeline, in order. `analysis/logs/` holds the printed output of each step. |
| `out/` | Summary tables used in the appendix (CSV) and `headline.json`. |
| `fig/` | Figures (SVG for the PDF, PNG for viewing). |
| `reference/case_prompt.md` | Working summary of the case prompt. |
| `data/` | Empty on purpose. Put the raw exports here to rerun. |

## Reproducing

1. Export the Google Sheets linked in the case prompt as `.xlsx` into `data/`: `shifts.xlsx` (Cleveland_shifts_logs) and `cancels.xlsx` (Cancel_logs).
2. Install: `pip install pandas openpyxl numpy matplotlib`; `npm i -g playwright` plus a Chromium build (set `NODE_PATH` to the global `node_modules` so `require('playwright')` resolves, or run `npm i playwright` inside `writeup/`); and the Inter font.
3. Run `./run_all.sh`.

## Data notes

- The shift log is Cleveland only (41,040 shifts, 67 facilities, Oct 2021 to Jan 2022). The cancellation log covers the whole marketplace (78,073 events); 7,780 of them join to Cleveland shifts by Shift ID and every rate in the document uses that join.
- The booking log (127,005 rows) was not used. Bookings were reconstructed as final assignments plus cancellation events (28,785). The write-up says so in assumption 2 and lists what the booking log would add in Appendix D.
- Timestamps are UTC. Worker, shift and facility IDs are MongoDB ObjectIds, so their first 8 hex characters give a creation time; this is how worker tenure was derived (validated against the shift Created At column).
