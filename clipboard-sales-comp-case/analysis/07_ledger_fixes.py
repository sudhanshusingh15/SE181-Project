"""Additional sizing after independent verification: Walter White HR-vs-Slack, corrected no-restart variant, GTM fill basis, counts."""
import sys, pandas as pd, numpy as np; sys.path.insert(0, sys.argv[1]+"/analysis"); from load_helper import load; from engine import compute
pd.set_option("display.width",220); pd.set_option("display.float_format",lambda v: f"{v:,.2f}")
S=sys.argv[1]; d=load(S+"/data/case_workbook.xlsx"); P=print
base,AB=compute(d); B=base.set_index("name").commission_usd
ref=pd.read_csv(S+"/out/reps_calc.csv").set_index("name"); P("engine still matches reference:", (base.set_index("name").commission_usd-ref.commission_usd).abs().max()<1e-6, "| total", round(base.commission_usd.sum(),2))
P("manager attainment:", base[~base.is_ic].set_index("name")[["attain","attain2"]].round(3).to_string())
def delta(reps,label):
    x=reps.set_index("name").commission_usd; dd=(x-B); dd=dd[dd.abs()>0.005].sort_values()
    P(f"\n### {label}: signed {dd.sum():,.2f} | abs {dd.abs().sum():,.2f} | reps {len(dd)}"); P(dd.round(2).to_string() if len(dd) else "  (none)"); return dd
rw,_=compute(d,emp_override={"Walter White":("2026-06-28",None)}); delta(rw,"Walter White started 28 June per Slack (HR says 2021)")
w=rw.set_index("name").loc["Walter White"]; P("  Walter White alt: days %d floor %.2f produced_paid %.2f credited %.2f comm %.2f" % (w.days_emp,w.ramp_floor,w.produced_paid,w.credited,w.commission_usd))
r11,_=compute(d,no_ramp_restart_for=("Jay Gatsby","Scout Finch","Gimli","Percy Jackson","Anna")); d11=delta(r11,"Ramp does not restart on promotion or rehire (corrected: Gimli from 2022 start)")
r12,_=compute(d,role_override={"Jay Gatsby":("ENT Account Executive","2026-06-08"),"Scout Finch":("ENT Account Executive","2026-06-01")}); delta(r12,"Jay and Scout: ENT role from the day after the SMB role ended (plan-consistent correction)")
# GTM fill basis
app=d["app"]; acc=pd.read_pickle(S+"/data/accounts.pkl") if False else None
opp=d["opp"]; mp=d["map"]; gtm_crm=opp[(opp.account_type=="GTM")].crm_account_id.unique(); gtm_app=mp[mp.crm_account_id.isin(gtm_crm)].app_account_id
FLAG="3ffe588d-e4a1-48bf-83f4-2c425aede793"; g=app[app.app_account_id.isin(gtm_app)]; oth=g[g.app_account_id!=FLAG]; std=app[~app.app_account_id.isin(gtm_app)]
P("\nGTM other 39 accounts: fill over all posted shifts in extract %.1f%% | June-posted %.1f%% | flagged account %.1f%% | Standard accounts %.1f%%" % (100*oth.worked_shift.mean(), 100*oth[oth.shift_posted_date>="2026-06-01"].worked_shift.mean(), 100*g[g.app_account_id==FLAG].worked_shift.mean(), 100*std.worked_shift.mean()))
per=oth.groupby("app_account_id").worked_shift.mean(); P("per-account fill among other GTM: min %.0f%% median %.0f%%" % (100*per.min(),100*per.median()))
ps=std.groupby("app_account_id").agg(posted=("shift_id","size"),fill=("worked_shift","mean")); big=ps[(ps.posted>=900)]; P("Standard accounts with >=900 posted shifts: %d, fill range %.0f%% to %.0f%%" % (len(big),100*big.fill.min(),100*big.fill.max()))
fw=app.groupby("app_account_id").account_first_worked_shift_date.first(); worked_days=app[app.worked_shift].groupby("app_account_id").shift_worked_date.apply(set)
nomatch=[a for a,f in fw.items() if f>=pd.Timestamp("2026-03-01") and f not in worked_days.get(a,set())]; P("accounts with given first-worked date >= 1 Mar and no worked shift that day:", len(nomatch))
P("Slack rows:", len(d["slack"]))
hr=d["hr"]; ro=d["roster"]; j=ro.merge(hr,on="hr_id"); late=opp[(opp.opportunity_stage=="Closed Won")].merge(j[["crm_owner_id","name","End Date"]],left_on="closed_by_owner_id",right_on="crm_owner_id"); P("Closed Won after closer End Date:", late[late.closed_won_date>late["End Date"]][["opportunity_id","name","closed_won_date","End Date"]].to_string(index=False))
P("SPIFF count:", (base.spiff>0).sum(), "total", base.spiff.sum())
base.to_csv(S+"/out/reps_base.csv",index=False); AB.to_csv(S+"/out/accounts_base.csv",index=False)
