# Verbatim plan text from the case prompt (section 07 and Appendix A). Contact details omitted.

## 07 The Compensation Plan
This section, plus tabs 4. Ramp Terms, 5. Compensation and 6. Accelerators, is the complete set of rules governing June 2026 payouts.

### 7.1 Net revenue and gross services value
Net Revenue is the margin on a worked shift: charge rate less pay rate. It is recognised in the month the shift was worked, not posted e.g., a shift posted 28 May and worked 3 June is June revenue. A posted shift that was never claimed generates no Net Revenue.
Gross Services Value is the charge rate on every posted shift, filled or not, and is recognised on the posted date whether the shift was worked or not. It matters for GTM accounts only.

### 7.2 Billing credits
Approved billing credits reduce Existing Customer Net Revenue only: the Account Manager's number. New-logo credit is measured before credits: billing credits are a post-onboarding operation the Account Manager owns.
Denied tickets change nothing. A credit belongs to the month named by its billing_month.

### 7.3 What counts as an account
- An account's go-live is the effective_start_date of its earliest Closed Won opportunity. A later expansion or renewal does not restart it.
- opportunity_stage governs. A populated closed_won_date on a row that is not Closed Won is the residue of a deal moved to Closed Won and reversed. It is not a win.
- Rates, net terms, segment and account type are properties of the account, identical across every opportunity on it.

### 7.4 New customer net revenue
An Account Executive earns on each account they closed for its first 90 days, measured from that account's first worked shift split into three consecutive 30-day windows: F1-30D = days 1 to 30 from the first worked shift; F31-60D = days 31 to 60; F61-90D = days 61 to 90.
Windows run in days from that first worked shift, so they will not line up with calendar months.
F1-30D credits every dollar it earns, in the month the shift was worked. Nothing about it waits: each month's statement simply picks up the F1-30D revenue worked in that month.
Example: An account whose first worked shift is 12 May. F1-30D runs 12 May to 10 June and produces $30,000 during the first 30 day window: $20k worked in May, $10k worked in June. May close paid off a quota retirement of $20k; June close pays off the remaining quota retirement of $10k.
F31-60D and F61-90D credit only the amount by which the account improved on its best earlier window. That is a comparison of whole windows, so it is not measured until the window has finished. The improvement is credited in one piece, on the statement for the month that window closes. A window that goes backwards credits nothing, and nothing already paid is ever restated.
Example: A second account, first worked shift 8 April. F1-30D ran 8 April to 7 May and produced $30k. F31-60D ran 8 May to 6 June and produced $40k, so it improved by $10k. The window closed on 6 June, so that $10k quota retirement applies to the June statement. Its F61-90D does not close until July and contributes nothing in the June close.
F1-30D pays at the role's full rate; F31-60D and F61-90D pay at half. The half is taken on the credit, so quota and the bands see the halved figure.
Credit belongs to closed_by_owner_id as it stands in the export: the rep who closed the account, whether or not they still own it. Where that field is blank the credit has no owner, do not reassign it.

### 7.5 Net terms move the revenue, not the rate
Faster terms are recognised at a premium and slower terms at a discount: Net 15 at 120%, Net 30 at 100%, Net 45 at 90%, Net 60 at 70%. The adjustment lands on the revenue, not the rate, and applies to new-logo credit only: never to Existing Customer Net Revenue, and never to GTM credit, which is already gross.

### 7.6 GTM accounts
An Applied Science shift tag flips an account to GTM. Margin on these is distorted (they are rural or under experiment) so the plan pays on gross. The windows and improvement test of 7.4 apply unchanged, but on GSV by posted date rather than Net Revenue, and GTM dollars pay 3% instead of the role's rate. Because the windows are anchored on the first worked shift, a shift posted before that date still falls in F1-30D: the windows have an upper bound only.
Quota and the accelerator bands are denominated at the role's own rate, so a dollar of GSV enters credited revenue at 3% divided by the role's rate: it retires exactly the quota that three cents of commission is worth, in whichever band it lands. GTM applies to Account Executives only.

### 7.7 Existing customer net revenue
An account is existing in a month once it went live before the first day of that month, and its credit belongs to crm_owner_id. The month's figure is the Net Revenue of shifts worked on that book, less approved credits booked to the month. Net terms, GSV and accelerators do not apply.

### 7.8 Managers, directors and the Head of Sales & AM
A manager carries the sum of what their reports are paid on, the figure after any ramp floor, for everyone beneath them in the Manager chain, not only direct reports. AE managers and the Director of Sales carry New; AM managers and the two AM Directors carry Existing; the Head of Sales & AM carries both, at the two rates on 5. Compensation.
Managers hold no accounts, have no accelerators and do not ramp. Their quota is on 5. Compensation, built from the quotas of everyone beneath them in the Manager chain rather than from what those reps produce.
Where a rep cannot be paid, because they have left, their manager still carries the revenue. Where closed_by_owner_id is blank, nobody is credited.

### 7.9 Commission and accelerators
Commission is credited revenue at the role's Standard Payout, with the bands and multipliers on 6. Accelerators applied to the incremental dollars in each band. Only SMB AE and ENT AE have accelerators.
So an SMB AE at $45k of credited revenue earns $30k at standard, the next $10k at the band I multiplier and the last $5k at band II. Bands are absolute dollars and do not prorate for a partial month, so the standard band is capped at the band I threshold and never at a prorated quota. Quota sets attainment; it does not gate payout, as there is no floor and no cap. A ramping rep is not eligible for accelerators.

### 7.10 Ramp
Four roles ramp: SMB AE, ENT AE, SMB AM, ENT AM; managers and directors do not. The clock starts on Current Role Start Date, and a promotion into a ramped role or a rehire restarts it. Month 1 is days 1 to 30 from that date, month 2 days 31 to 60.
Ramp quota credit is a floor on credited revenue, not an addition: a ramping rep is credited with the greater of what they produced and their ramp credit. It prorates by calendar day: each day carries the percentage for whichever ramp month that day falls in, against the monthly quota divided by the days in the month. It assumes Net 30 terms. The percentage each role carries in each month is on 4. Ramp Terms.

### 7.11 Joiners, leavers and role changes
Quota prorates on calendar days employed in the month, and not for a role change. A rep is credited only where they were employed on the date that credit is recognised, so somebody who left before the month began earns nothing. Their manager still carries it.

### 7.12 Retention SPIFF
For Account Manager individual contributors only, at the amounts on 6. Accelerators. Payable where June Existing Customer Net Revenue holds at 100% or better of May's on the same book: the accounts held in June that were live before 1 May, measured in both months. An account that went live during May was not there to be retained. Both months are measured net of approved credits booked to that month. Where May is zero there is nothing to retain. Not payable while ramping.

### 7.13 Currency
Every facility bills in USD, so nothing converts on the revenue side. Commission is computed in USD and paid in the rep's local currency, at the rate on 3. Exchange Rates. That rate is quoted as one US dollar expressed in local units.

### Governing documents
Payouts are governed solely by this document, the plan tabs it points to, and adjustments approved in writing by sales leadership. No external convention, benchmark or promise applies unless incorporated here in writing, including anything in Slack. That governs how revenue is measured. It does not stop you flagging a payout you believe should not be made.

## Appendix A: Data dictionary (what the tabs cannot tell you)
1. Sales Roster, 80 reps: header row 1, data rows 2 to 81. Names are unique. crm_owner_id is the rep's single CRM id: it matches closed_by_owner_id on 8. Opportunity Export for Account Executives, and crm_owner_id for Account Managers. This is the roster as of the start of the review and is not guaranteed to agree with HR.
2. HR Export, 1,080 employees: Current Role decides which plan the rep is paid on. Start Date / End Date: employment, inclusive, the first and last day worked; a populated End Date means they left. Current Role Start / End Date: time in role, starts the ramp clock. Manager - ID: the reporting line used for roll-up quotas. Country Code: the employee's location, not their accounts'. The 80 reps in scope sit among the wider company, in no particular order. A point-in-time snapshot with no manager history: the Manager-ID shown held for the whole month. The Head of Sales & AM reports outside this export, so their Manager-ID has no matching row.
3, 4, 6 and 7: 3. Exchange Rates, 196 rows: 1 USD = is the units of local currency per one US dollar. 4. Ramp Terms, 17 roles: columns B to D carry the Start Date Ramp, for the person new in role. Columns E to G would carry a New Report Ramp; no role in this plan does, and column G says why. na means the row does not carry that ramp. 6. Accelerators: the AE bands and multipliers, with the Account Manager retention SPIFF underneath. 7. Opportunity to ID Mapping, 761 rows: the identifier map between CRM, the app and billing.
5. Compensation, 17 roles: # of is the headcount in that role. # of Reports is how many reports each manager of that role carries. Metric II and the columns after it are populated only for Account Managers and for the Head of Sales & AM, who carries both metrics.
8. Opportunity Export, 815 opportunities: closed_by_owner_id is the rep who closed it, always an Account Executive where it is populated; a few rows are blank, see 7.4. crm_owner_id is the rep who owns it now, always an Account Manager. effective_start_date is when the account goes live. segment is as stamped in CRM and does not decide the plan.
9. App Export, 107,052 posted shifts: worked_shift TRUE or FALSE, nobody claimed the FALSE ones. shift_worked_date populated only where worked_shift is TRUE. account_first_worked_shift_date is the account's first ever worked shift. The extract covers shifts worked between 1 March and 30 June 2026. It is a window, not the whole history. Many accounts were live long before it opens, which is why the first worked shift is given rather than left to be derived. Do not try to infer it.
10. Billing Export, 1,089 credit tickets: credits only; there is no invoice or payment data. credit_amount is USD. ticket_type is descriptive: every approved ticket reduces Existing Customer Net Revenue whatever its type. Tickets cover shifts worked in May and June.
11. Slack Scrape, 55 messages.

## Assignment extracts relevant to verification
- Calculate what each of the 80 reps should be paid for June 2026 from the raw data, applying the plan exactly as written. Model must be dynamic and traceable.
- Exceptions ledger: every record or group that would produce a wrong payout if processed naively, sized (records touched, dollars moved, reps affected, treatment). Include anything the plan as written would pay but you would not sign off. Hint: one finding is worth more than all the others combined.
- Plan change: SMB AE accelerator from 1.2x / 1.3x to 1.3x / 1.5x: June as paid, June repriced, delta, assumptions, surprises.
- Slack: pick the three messages to escalate and why; one response of 250 words or fewer.
