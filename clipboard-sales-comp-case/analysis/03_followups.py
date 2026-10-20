import sys, pandas as pd, numpy as np; sys.path.insert(0, sys.argv[1]+"/analysis"); from load_helper import load
pd.set_option("display.width",250); pd.set_option("display.max_columns",40); pd.set_option("display.max_colwidth",60); pd.set_option("display.max_rows",200)
d=load(sys.argv[1]+"/data/case_workbook.xlsx"); P=print
ro,hr,mp,opp,app,bill=d["roster"],d["hr"],d["map"],d["opp"],d["app"],d["bill"]
names=dict(zip(ro.crm_owner_id, ro.name))
P("### residue rows (closed_won_date on non Closed Won):"); P(opp[(opp.opportunity_stage!="Closed Won")&opp.closed_won_date.notna()].assign(closer=lambda x:x.closed_by_owner_id.map(names)).to_string(index=False))
P("\n### all non Closed Won rows:"); P(opp[opp.opportunity_stage!="Closed Won"][["crm_account_id","opportunity_id","opportunity_stage","closed_won_date","effective_start_date","account_type","segment"]].to_string(index=False))
P("\n### blank closed_by rows:"); P(opp[opp.closed_by_owner_id.isna()].to_string(index=False))
P("\n### eff start before closed won:"); P(opp[opp.effective_start_date<opp.closed_won_date][["crm_account_id","opportunity_id","opportunity_stage","closed_won_date","effective_start_date","closed_by_owner_id"]].assign(closer=lambda x:x.closed_by_owner_id.map(names)).to_string(index=False))
# accounts with multiple closed won
cw=opp[opp.opportunity_stage=="Closed Won"]; multi=cw[cw.crm_account_id.isin(cw.crm_account_id.value_counts()[lambda s:s>1].index)].sort_values(["crm_account_id","effective_start_date"])
P("\n### accounts with >1 Closed Won (first 12 accounts):"); P(multi.head(24)[["crm_account_id","opportunity_id","closed_won_date","effective_start_date","closed_by_owner_id","crm_owner_id"]].to_string(index=False))
# go-live per account and relation to first worked
golive=cw.groupby("crm_account_id").effective_start_date.min().rename("go_live")
fw=app.groupby("app_account_id").account_first_worked_shift_date.first().rename("first_worked"); mn=app[app.worked_shift].groupby("app_account_id").shift_worked_date.min().rename("min_worked_extract"); nshift=app.groupby("app_account_id").size().rename("n_shifts")
a=mp.merge(golive,left_on="crm_account_id",right_index=True,how="left").merge(fw,left_on="app_account_id",right_index=True,how="left").merge(mn,left_on="app_account_id",right_index=True,how="left").merge(nshift,left_on="app_account_id",right_index=True,how="left")
a=a.merge(opp.drop_duplicates("crm_account_id")[["crm_account_id","account_type","segment","net_terms","charge_rate_per_shift","pay_rate_per_shift","closed_by_owner_id","crm_owner_id"]],on="crm_account_id",how="left")
P("\n### ACCOUNTS: ", len(a), "| no shifts in extract:", a.n_shifts.isna().sum(), "| first worked before go-live:", (a.first_worked<a.go_live).sum(), "| first worked null:", a.first_worked.isna().sum())
P("first worked - go_live days describe:\n", (a.first_worked-a.go_live).dt.days.describe().round(1).to_string())
gap=a[(a.first_worked>="2026-03-01")&(a.min_worked_extract>a.first_worked)]; P("accounts with given first-worked in window but no worked shift on that date:", len(gap)); P((gap.min_worked_extract-gap.first_worked).dt.days.describe().round(1).to_string())
P(gap.head(8)[["crm_account_id","go_live","first_worked","min_worked_extract","n_shifts","account_type"]].to_string(index=False))
P("\naccounts whose first worked shift falls inside the 90-day new-logo window overlapping June (first_worked > 2026-03-02):", (a.first_worked>"2026-03-02").sum(), "| GTM among them:", ((a.first_worked>"2026-03-02")&(a.account_type=="GTM")).sum())
P("GTM accounts:", (a.account_type=="GTM").sum(), "| by segment:", a[a.account_type=="GTM"].segment.value_counts().to_dict())
P("go-live by month (accounts):", golive.dt.to_period("M").value_counts().sort_index().tail(8).to_dict())
P("first worked by month:", a.first_worked.dt.to_period("M").value_counts().sort_index().tail(6).to_dict())
P("accounts live before 2026-06-01 (existing in June):", (a.go_live<"2026-06-01").sum(), "| live before 2026-05-01:", (a.go_live<"2026-05-01").sum(), "| go-live in June:", ((a.go_live>="2026-06-01")&(a.go_live<"2026-07-01")).sum(), "| go-live after June:", (a.go_live>="2026-07-01").sum())
P("accounts with worked shifts in June but go-live >= June 1:", a[(a.go_live>="2026-06-01")].merge(app[app.worked_shift&(app.shift_worked_date>="2026-06-01")].groupby("app_account_id").size().rename("jun_worked"),left_on="app_account_id",right_index=True,how="inner").shape[0])
P("accounts with shifts worked BEFORE go-live:", app[app.worked_shift].merge(a[["app_account_id","go_live"]],on="app_account_id").query("shift_worked_date<go_live").app_account_id.nunique())
# AE roster: closers per AE, AM books
ae_cnt=cw.drop_duplicates("crm_account_id").closed_by_owner_id.map(names).value_counts(); P("\naccounts closed per AE (roster names):\n", ae_cnt.to_string())
am_cnt=a.crm_owner_id.map(names).value_counts(); P("\naccounts owned per AM:\n", am_cnt.to_string())
P("\nshift_id format check:", app.shift_id.str.match(r"^SH-\d{6}$").mean(), "| posted dates with time component:", (app.shift_posted_date.dt.normalize()!=app.shift_posted_date).sum(), "| worked dates with time:", (app.shift_worked_date.dropna().dt.normalize()!=app.shift_worked_date.dropna()).sum())
P("shifts worked per account in June describe:\n", app[app.worked_shift&(app.shift_worked_date>="2026-06-01")].groupby("app_account_id").size().describe().round(1).to_string())
P("worked shifts per account per day max:", app[app.worked_shift].groupby(["app_account_id","shift_worked_date"]).size().max())
# billing: approved June credits by account owner (AM) and ticket types, denied share
bj=bill.merge(mp,on="billing_account_id",how="left").merge(a[["crm_account_id","crm_owner_id","go_live","account_type"]],on="crm_account_id",how="left",suffixes=("","_a"))
P("\napproved June credits on accounts that went live on/after June 1 (not existing):", bj[(bj.ticket_status=="approved")&(bj.billing_month=="2026-06")&(bj.go_live>="2026-06-01")].credit_amount.agg(["count","sum"]).to_dict())
P("approved credits by type (June):", bj[(bj.ticket_status=="approved")&(bj.billing_month=="2026-06")].groupby("ticket_type").credit_amount.agg(["count","sum"]).to_dict())
P("credit amount vs account charge rate: tickets with credit > charge:", (bj.credit_amount>bj.merge(opp.drop_duplicates("crm_account_id")[["crm_account_id","charge_rate_per_shift"]],on="crm_account_id",how="left").charge_rate_per_shift).sum())
