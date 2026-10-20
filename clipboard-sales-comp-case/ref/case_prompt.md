# Sales Compensation Analyst Case Study (Clipboard): prompt summary

Working copy of the candidate case prompt, kept here so the folder stands on its own. The original is a view-only Google Doc owned by Clipboard; contact details are left out on purpose.

## The role and the month

You are the first dedicated Sales Compensation Analyst at a healthcare staffing marketplace. Facilities post shifts, workers claim and work them. The company bills a charge rate per shift and pays a pay rate; the margin is Net Revenue. Account Executives (AEs) are paid on New Customer Net Revenue for a limited window after each account they close starts producing. Account Managers (AMs) are paid on Existing Customer Net Revenue of the book they hold. Managers and directors carry roll-up quotas. The comp month under review is June 2026. June statements already went out from a spreadsheet rebuilt from memory each month; you are building a fresh version.

## Assignment

1. Calculate June 2026 commissions for all 80 reps on the Sales Roster from the raw data, applying the plan exactly as written: AEs, AMs, frontline managers, directors and the Head of Sales & AM. Traceable to source rows. Dynamic model (must be updatable for July). Include any code built outside the spreadsheet.
2. Build a data quality exceptions ledger: every record or group that would produce a wrong payout if processed naively, sized (records, dollars, reps) with the treatment applied and why. Include anything the plan would pay but you would not sign off. Hint: one finding is worth more than all the others combined.
3. Model a plan change: SMB AE accelerator from 1.2x / 1.3x to 1.3x / 1.5x. June as paid, June repriced, delta, assumptions, surprises.
4. Respond to the rep: from the Slack scrape (June and the first two weeks of July), pick the three messages to escalate and why, then write one response of 250 words or fewer (reply to the rep, or a note to sales leadership).

## Deliverables

- Google Sheet or Excel model: June 2026 commission for all 80 reps in USD and local currency, the exceptions ledger, the plan-change scenario. Inputs separate from calculations. No black-box hardcoded solutions.
- Written PDF summary, 3 pages maximum: ledger findings ranked by dollar impact; every assumption where the plan is silent, with recommendation; plan-change answer and surprises; the three Slack messages to escalate, with the reply to one.

## The compensation plan (section 07), condensed

- 7.1 Net Revenue = charge rate less pay rate on a worked shift, recognised in the month worked. Gross Services Value (GSV) = charge rate on every posted shift, filled or not, recognised on the posted date; GTM accounts only.
- 7.2 Approved billing credits reduce Existing Customer Net Revenue only. Denied tickets change nothing. A credit belongs to the month named by its billing_month.
- 7.3 Go-live = effective_start_date of the earliest Closed Won opportunity; later expansions do not restart it. opportunity_stage governs; a closed_won_date on a non Closed Won row is residue, not a win. Rates, net terms, segment and account type are account properties.
- 7.4 New Customer Net Revenue: AE earns for the account's first 90 days from its first worked shift, in three 30-day windows (F1-30D, F31-60D, F61-90D). F1-30D credits every dollar in the month worked. F31-60D and F61-90D credit only the improvement over the best earlier window, in one piece, on the statement for the month the window closes; a window that goes backwards credits nothing. F1-30D pays at the role's full rate; F31-60D and F61-90D at half, taken on the credit. Credit belongs to closed_by_owner_id as exported; blank means no owner.
- 7.5 Net terms adjust new-logo revenue only: Net 15 at 120%, Net 30 at 100%, Net 45 at 90%, Net 60 at 70%. Never Existing revenue, never GTM.
- 7.6 GTM accounts (an Applied Science shift tag flips an account to GTM): windows and improvement test unchanged but on GSV by posted date; GTM dollars pay 3% instead of the role's rate; credited revenue enters at 3% divided by the role's rate. Windows have an upper bound only. AEs only.
- 7.7 Existing Customer Net Revenue: an account is existing in a month once it went live before the first day of that month; credit belongs to crm_owner_id; Net Revenue of shifts worked less approved credits booked to the month. No net terms, GSV or accelerators.
- 7.8 Managers carry the sum of what their reports are paid on (after any ramp floor) for everyone beneath them in the Manager chain. AE managers and the Director of Sales carry New; AM managers and the two AM Directors carry Existing; the Head of Sales & AM carries both at the two rates on the Compensation tab. No accounts, no accelerators, no ramp. Leavers' revenue still rolls up to the manager; blank closed_by credits nobody.
- 7.9 Commission = credited revenue at the role's Standard Payout, with accelerator multipliers on the incremental dollars in each band (SMB AE and ENT AE only). Bands are absolute dollars and do not prorate. No floor, no cap. Ramping reps get no accelerators.
- 7.10 Ramp: SMB AE, ENT AE, SMB AM, ENT AM ramp from Current Role Start Date (promotion or rehire restarts). Month 1 = days 1 to 30, month 2 = days 31 to 60. Ramp credit is a floor on credited revenue, prorated by calendar day against monthly quota divided by days in the month; assumes Net 30.
- 7.11 Quota prorates on calendar days employed in the month, not for a role change. A rep is credited only where employed on the date the credit is recognised; a leaver before the month began earns nothing, their manager still carries it.
- 7.12 Retention SPIFF: AM individual contributors only; payable where June Existing Customer Net Revenue is at least 100% of May's on the same book (accounts held in June that were live before 1 May), both months net of approved credits. Where May is zero there is nothing to retain. Not payable while ramping.
- 7.13 Currency: computed in USD, paid in local currency at the rate on the Exchange Rates tab (local units per USD).
- Governing documents: this document, the plan tabs, and written adjustments approved by sales leadership. Nothing in Slack governs. It does not stop you flagging a payout you believe should not be made.

## Data dictionary notes (Appendix A)

- Roster: 80 reps; crm_owner_id matches closed_by_owner_id for AEs and crm_owner_id for AMs; roster is not guaranteed to agree with HR.
- HR export: 1,080 employees; Start/End Date inclusive; Current Role Start Date starts the ramp clock; Manager - ID is the roll-up line; point-in-time snapshot, no manager history; the Head of Sales & AM reports outside the export.
- Exchange rates: 1 USD = units of local currency. Ramp Terms: Start Date Ramp in columns B to D; no role carries a New Report Ramp. Compensation: Metric II columns only for Account Managers and the Head of Sales & AM.
- Opportunity export: 815 rows; closed_by_owner_id is always an AE where populated; crm_owner_id is always an AM; segment does not decide the plan.
- App export: 107,052 posted shifts worked between 1 March and 30 June 2026 (a window, not the history); account_first_worked_shift_date is given; do not infer it.
- Billing export: 1,089 credit tickets, credits only, USD; every approved ticket reduces Existing revenue; tickets cover shifts worked in May and June.
- Slack scrape: 55 messages.
