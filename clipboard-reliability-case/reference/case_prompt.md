# Marketplace Reliability Case Study (Clipboard) : prompt summary

Working copy of the candidate case prompt, kept here so the folder stands on its own. The original is a view-only Google Doc owned by Clipboard; contact details from it are left out on purpose.

## The task

Imagine it is 2021 and you are the newest member of the team. Write a project proposal for executive leadership that addresses the marketplace problem of late cancellations by healthcare professionals (HCPs) at healthcare facilities (HCFs). Convince leadership to invest in the proposal because it creates the greatest positive impact for customers. Both facilities and professionals are customers.

Format: a narrative document (not slides), no longer than 6 pages, with optional appendix for figures and analysis. One recommended solution; simpler is better. State assumptions explicitly, justify them, and say how their validity would change the recommendation.

## What the report should show

- Extreme curiosity: insights pulled directly from the data.
- First principles: proposal follows from the data and the marketplace problem.
- Anti-incremental thinking: greatest effect size at the lowest cost.
- Intellectual honesty: risks, trade-offs, alternatives, limitations, guardrails.
- Metrics-driven: what to track, how far to move it, by when, what counts as success or failure.
- Ownership: enough detail to start executing tomorrow.
- Uncomfortably high standards: specific, concise, executive-level writing.

## Assumptions given in the brief

- The most damaging cancellation for a facility is a No-Call-No-Show (NCNS). Both NCNS and late cancellations (under 24 hours before start) correlate with facility churn.
- Top reasons professionals report for last-minute cancellations: sickness, family emergencies, transportation, facility issues.
- Professionals already receive reminder notifications in the app before a shift.
- Average take rate in this market is 22 percent.
- Data is from Cleveland; assume Cleveland dynamics generalize across the marketplace.
- A mid-2021 attendance policy moved the needle incrementally. Under it, professionals who frequently canceled or no-showed were deactivated.

## Historical attendance rules (2021)

- No-Call-No-Show: 1st and 2nd each bring a one week suspension; 3rd brings deactivation.
- Call-off (cancellation under 4 hours before start): 2 bring a one week suspension; 4 bring deactivation.
- Standard cancellation (4 to 72 hours before start): 6 bring a one week suspension.
- Offenses that look unpunished in the data were likely excused by the team that manually triaged attendance cases.

## Data files (Google Sheets, links in the original prompt)

1. Cleveland_shifts_logs: one row per shift. Columns: Shift ID, Worker ID, Facility ID, Start, Agent Req, End, Deleted, Shift Type, Created At, Verified, Charge, Time.
2. Booking_logs: one row per booking event. Columns: Action ID, Created At, Shift ID, Action (SHIFT_CLAIM), Worker ID, Facility ID, Lead Time.
3. Cancel_logs: one row per cancellation event. Columns: Action ID, Created At, Shift ID, Action (WORKER_CANCEL or NO_CALL_NO_SHOW), Worker ID, Start, Facility ID, Lead Time.

Lead Time is hours between the action and the shift start.
