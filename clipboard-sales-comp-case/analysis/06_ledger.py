"""Sizes every ledger item as a controlled what-if against the plan-as-written baseline."""
import sys, json, pandas as pd, numpy as np; sys.path.insert(0, sys.argv[1]+"/analysis"); from load_helper import load; from engine import compute
pd.set_option("display.width",230); pd.set_option("display.max_colwidth",60); pd.set_option("display.float_format",lambda v: f"{v:,.2f}")
S=sys.argv[1]; d=load(S+"/data/case_workbook.xlsx"); P=print
base,AB=compute(d); B=base.set_index("name").commission_usd
def delta(reps,label):
    x=reps.set_index("name").commission_usd; dd=(x-B); dd=dd[dd.abs()>0.005].sort_values()
    P(f"\n### {label}: total signed delta {dd.sum():,.2f} | sum of abs {dd.abs().sum():,.2f} | reps affected {len(dd)}"); P(dd.round(2).to_string() if len(dd) else "  (none)")
    return dd
FLAG="3ffe588d-e4a1-48bf-83f4-2c425aede793"
r1,_=compute(d,exclude_accounts=(FLAG,)); d1=delta(r1,"1a. Exclude flagged GTM account (recommended)")
r1b,_=compute(d,gtm_worked_only=(FLAG,)); d1b=delta(r1b,"1b. Flagged GTM account: credit worked shifts only")
r1c,_=compute(d,gtm_as_standard=(FLAG,)); d1c=delta(r1c,"1c. Flagged GTM account: treat as Standard net revenue")
acc=AB[AB.app_account_id==FLAG].iloc[0]; P("flagged account detail:", dict(f1_june_gsv=acc.f1_june_full, pre_fw_gsv=acc.pre_fw_gsv, conv=acc.conv, new_cred_full=acc.new_cred_full, june_nr=acc.june_nr_all, net_terms=acc.net_terms))
P("Jon Snow baseline: credited %.2f commission %.2f ; without account: credited %.2f commission %.2f" % (base.set_index('name').loc['Jon Snow','credited'], B['Jon Snow'], r1.set_index('name').loc['Jon Snow','credited'], r1.set_index('name').loc['Jon Snow','commission_usd']))
r2,A2=compute(d,hold_closer_not_employed_at_close=True); d2=delta(r2,"2. Hold credit where closer not employed on close date")
pre=AB[(AB.first_won<AB.closer.map(dict(zip(base.crm_owner_id,base.emp_start))))]; P("accounts with first won before closer start: %d; with any June new credit: %d; June new credit full $%.2f" % (len(pre),(pre.new_cred_full>0).sum(),pre.new_cred_full.sum()))
P(pre[pre.new_cred_full>0].groupby("closer_name").agg(accounts=("crm_account_id","size"),new_credit=("new_cred_full","sum")).sort_values("new_credit",ascending=False).to_string())
r3,_=compute(d,ignore_employment=True); d3=delta(r3,"3. Naive: ignore joiner/leaver dates (7.11)")
r4,_=compute(d,ramp_no_proration=True); d4=delta(r4,"4. Naive: ramp floor not prorated by day")
r5,_=compute(d,residue_as_won=True); d5=delta(r5,"5. Naive: residue rows treated as wins")
r6,_=compute(d,golive_latest_cw=True); d6=delta(r6,"6. Naive: go-live from the latest Closed Won (expansions restart)")
r7,_=compute(d,include_denied=True); d7=delta(r7,"7. Naive: denied tickets subtracted")
r8,_=compute(d,credits_on_nonexisting=True); d8=delta(r8,"8. Naive: credits on not-yet-existing accounts subtracted from the owner")
r9,_=compute(d,gtm_pre_month=False); d9=delta(r9,"9. Assumption: GTM pre-month posted GSV NOT recognised this month")
r10,_=compute(d,first_worked_observed=True); d10=delta(r10,"10. Sensitivity: windows anchored on observed first worked date")
r11,_=compute(d,no_ramp_restart_for=("Jay Gatsby","Scout Finch","Gimli","Percy Jackson","Anna")); d11=delta(r11,"11. Alternative: ramp does not restart on promotion/rehire")
r12,_=compute(d,role_override={"Jay Gatsby":("SMB Account Executive","2023-08-14"),"Scout Finch":("SMB Account Executive","2022-11-14")}); d12=delta(r12,"12. Alternative: Jay Gatsby and Scout Finch paid as SMB AEs (their June credit is from SMB deals)")
r13,_=compute(d,mgr_proration={"Lord Voldemort":9/30}); d13=delta(r13,"13. Alternative: Lord Voldemort manager credit from 22 June only (Slack vs HR)")
r14,_=compute(d,smb_mult=(1.3,1.5)); d14=delta(r14,"14. Scenario: SMB AE multipliers 1.3 / 1.5")
rn,_=compute(d,ignore_employment=True,ramp_no_proration=True,residue_as_won=True,golive_latest_cw=True,include_denied=True,credits_on_nonexisting=True); dn=delta(rn,"ALL NAIVE TOGETHER (vs plan as written)")
# blank closer, no-shift accounts, expansions, residue detail
P("\nblank closer uncredited new revenue: $%.2f on %d accounts" % (AB.uncredited.sum(),(AB.uncredited>0).sum()))
P("accounts with no shifts in extract:", AB[AB.fw.isna()][["crm_account_id","closer_name","owner_name","go_live","atype"]].to_string(index=False))
names=dict(zip(base.crm_owner_id,base.name)); opp=d["opp"]; res=opp[(opp.opportunity_stage!="Closed Won")&opp.closed_won_date.notna()]; P("\nresidue rows closers:", res.closed_by_owner_id.map(names).value_counts().to_dict())
# Slack-related numbers
bi=base.set_index("name")
P("\nDr. Watson same-book: May %.2f June %.2f (%.2f%%)" % (bi.loc["Dr. Watson","ex_may"], bi.loc["Dr. Watson","ex_june_samebook"], 100*bi.loc["Dr. Watson","ex_june_samebook"]/bi.loc["Dr. Watson","ex_may"]))
for n in ["Katniss Everdeen","Tom Sawyer","Ron Weasley","Frodo Baggins","Gimli","Hermione Granger","Scout Finch","Jay Gatsby","Percy Jackson","Anna","Walter White","Gandalf","Albus Dumbledore","Harry Potter","Luke Skywalker","Jon Snow","Dorothy Gale","Legolas"]:
    r=bi.loc[n]; P(f"{n:18s} role {r.role:22s} days {r.days_emp:2d} prod_paid {r.produced_paid:10,.2f} prod_full {r.produced_full:10,.2f} floor {r.ramp_floor:9,.2f} credited {r.credited:10,.2f} attain {r.attain if pd.notna(r.attain) else 0:5.2f} elig {int(r.acc_eligible)} comm {r.commission_usd:9,.2f} spiff {r.spiff}")
# Gandalf accounts live 28-29 June
g=AB[(AB.closer_name=="Gandalf")&(AB.go_live>="2026-06-25")]; P("\nGandalf late-June accounts:", g[["crm_account_id","go_live","fw","f1_june_full","new_cred_full"]].to_string(index=False))
al=AB[(AB.closer_name=="Albus Dumbledore")&(AB.fw.isna())]; P("Albus no-shift account:", al[["crm_account_id","go_live","first_won"]].to_string(index=False))
hp=AB[(AB.closer_name=="Harry Potter")&(AB.new_cred_full>0)][["crm_account_id","net_terms","mult","f1_june_full","new_cred_full"]]; P("Harry Potter credited accounts:\n", hp.to_string(index=False))
lk=AB[(AB.closer_name=="Luke Skywalker")&(AB.net_terms==15)&(AB.new_cred_full>0)][["crm_account_id","net_terms","f1_june_full","new_cred_full"]]; P("Luke Net 15:\n", lk.to_string(index=False))
dg=AB[(AB.owner_name=="Dorothy Gale")&(AB.atype=="GTM")][["crm_account_id","app_account_id","go_live","closer_name","existing_june","june_nr_all"]]; P("Dorothy Gale GTM accounts:\n", dg.to_string(index=False))
# save
out={"d1":d1.to_dict(),"d1b":d1b.to_dict(),"d1c":d1c.to_dict(),"d2":d2.to_dict(),"d3":d3.to_dict(),"d4":d4.to_dict(),"d5":d5.to_dict(),"d6":d6.to_dict(),"d7":d7.to_dict(),"d8":d8.to_dict(),"d9":d9.to_dict(),"d10":d10.to_dict(),"d11":d11.to_dict(),"d12":d12.to_dict(),"d13":d13.to_dict(),"d14":d14.to_dict(),"naive":dn.to_dict()}
json.dump(out,open(S+"/out/ledger_deltas.json","w"),indent=1,default=float)
r14.to_csv(S+"/out/reps_scenario.csv",index=False); base.to_csv(S+"/out/reps_base.csv",index=False); AB.to_csv(S+"/out/accounts_base.csv",index=False)
