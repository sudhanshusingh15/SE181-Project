import sys, pandas as pd, numpy as np; sys.path.insert(0, sys.argv[1]+"/analysis"); from load_helper import load
pd.set_option("display.width",250); pd.set_option("display.max_columns",40); pd.set_option("display.max_colwidth",50); pd.set_option("display.max_rows",200)
d=load(sys.argv[1]+"/data/case_workbook.xlsx"); P=print
ro,hr,mp,opp,app,bill,sl=d["roster"],d["hr"],d["map"],d["opp"],d["app"],d["bill"],d["slack"]
names=dict(zip(ro.crm_owner_id, ro.name)); hrj=ro.merge(hr,on="hr_id")
cw=opp[opp.opportunity_stage=="Closed Won"]
acct=cw.sort_values("effective_start_date").groupby("crm_account_id").agg(go_live=("effective_start_date","min"),closed_by=("closed_by_owner_id","first"),crm_owner=("crm_owner_id","first"),account_type=("account_type","first"),segment=("segment","first"),net_terms=("net_terms","first"),charge=("charge_rate_per_shift","first"),pay=("pay_rate_per_shift","first"),first_won=("closed_won_date","min")).reset_index()
acct=acct.merge(mp,on="crm_account_id",how="left")
fw=app.groupby("app_account_id").account_first_worked_shift_date.first().rename("first_worked"); acct=acct.merge(fw,left_on="app_account_id",right_index=True,how="left")
acct["closer"]=acct.closed_by.map(names); acct["am"]=acct.crm_owner.map(names)
# ---- GTM: GSV on posted shifts, worked share, by account and AE
a2=app.merge(acct[["app_account_id","account_type","charge","pay","closer","first_worked","go_live"]],on="app_account_id",how="left")
a2["gsv"]=a2.charge; a2["nr"]=np.where(a2.worked_shift, a2.charge-a2.pay, 0)
g=a2[a2.account_type=="GTM"].groupby(["app_account_id","closer","first_worked","go_live"]).agg(posted=("shift_id","size"),worked=("worked_shift","sum"),gsv=("gsv","sum"),gsv_jun=("gsv",lambda s: s[(a2.loc[s.index,"shift_posted_date"]>="2026-06-01")].sum()),nr=("nr","sum")).reset_index().sort_values("posted",ascending=False)
g["worked_share"]=(g.worked/g.posted).round(2)
P("### GTM ACCOUNTS (40): posted/worked/GSV by account\n", g.to_string(index=False))
P("\nGTM posted/worked by closer:\n", g.groupby("closer").agg(accounts=("app_account_id","size"),posted=("posted","sum"),worked=("worked","sum"),gsv=("gsv","sum"),gsv_jun=("gsv_jun","sum")).sort_values("gsv",ascending=False).to_string())
P("\nStandard accounts worked share overall: %.2f | GTM accounts worked share: %.2f" % (a2[a2.account_type=="Standard"].worked_shift.mean(), a2[a2.account_type=="GTM"].worked_shift.mean()))
# posted-per-day spikes on GTM accounts
spk=a2[a2.account_type=="GTM"].groupby(["app_account_id","shift_posted_date"]).size().rename("n").reset_index(); P("GTM max shifts posted on one day per account (top 10):\n", spk.sort_values("n",ascending=False).head(10).to_string(index=False))
P("Standard max shifts posted per day:", a2[a2.account_type=="Standard"].groupby(["app_account_id","shift_posted_date"]).size().max())
# ---- closers vs employment dates
e=acct.merge(hrj[["crm_owner_id","name","Current Role","Start Date","End Date","Current Role Start Date","Previous Role","Previous Role Start Date","Previous Role End Date"]],left_on="closed_by",right_on="crm_owner_id",how="left")
e["won_before_start"]=e.first_won<e["Start Date"]; e["won_after_end"]=e.first_won>e["End Date"]
P("\n### accounts whose first Closed Won predates the closer's HR Start Date:", e.won_before_start.sum()); P(e[e.won_before_start].groupby("closer").agg(n=("crm_account_id","size"),first_won_min=("first_won","min"),first_won_max=("first_won","max"),start=("Start Date","first")).to_string())
P("accounts won after closer's End Date:", e.won_after_end.sum())
# Gimli rehire gap
gim=e[(e.closer=="Gimli")]; P("Gimli accounts by won date relative to his gap (2024-11-15 to 2026-05-04):", ((gim.first_won>"2024-11-15")&(gim.first_won<"2026-05-04")).sum(), "in gap of", len(gim))
# new-logo June exposure per closer: accounts with first_worked within 90 days of June
e["in_window_june"]=(e.first_worked.notna())&(e.first_worked+pd.Timedelta(days=89)>="2026-06-01")&(e.first_worked<="2026-06-30")
P("\naccounts with any new-logo window touching June, by closer:\n", e[e.in_window_june].groupby("closer").size().sort_values(ascending=False).to_string())
# Slack user mapping
sl["who"]=sl.slack_user_id.map(dict(zip(ro.slack_user_id,ro.name))).fillna("(not on roster)"); P("\nSlack authors:", sl.who.value_counts().to_dict())
P("\nSlack user 295bf011 =", sl[sl.slack_user_id.str.startswith("295bf011")].who.iloc[0])
acct.to_pickle(sys.argv[1]+"/data/accounts.pkl")
