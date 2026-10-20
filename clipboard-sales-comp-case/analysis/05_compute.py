"""Reference implementation of the June 2026 commission plan (section 07) in pandas.
Every rule is applied as written; treatments for data-quality exceptions are flagged, not silently applied, except where noted in the ledger."""
import sys, json, pandas as pd, numpy as np; sys.path.insert(0, sys.argv[1]+"/analysis"); from load_helper import load
pd.set_option("display.width",250); pd.set_option("display.max_columns",60); pd.set_option("display.max_colwidth",40); pd.set_option("display.max_rows",200)
S=sys.argv[1]; d=load(S+"/data/case_workbook.xlsx"); P=print
ro,hr,fx,ramp,comp,acc,mp,opp,app,bill=d["roster"],d["hr"],d["fx"],d["ramp"],d["comp"],d["acc_raw"],d["map"],d["opp"],d["app"],d["bill"]
M_START=pd.Timestamp("2026-06-01"); M_END=pd.Timestamp("2026-06-30"); DIM=30; P_START=pd.Timestamp("2026-05-01"); P_END=pd.Timestamp("2026-05-31"); MONTH="2026-06"; PMONTH="2026-05"
NET_MULT={15:1.2,30:1.0,45:0.9,60:0.7}; GTM_RATE=0.03; HALF=0.5
# ---------------- plan tables
comp=comp.rename(columns={"Role":"role","Monthly Quota Target":"quota","Standard Payout":"rate","Monthly Target":"quota2","Standard Payout 2":"rate2"})
roles=comp.set_index("role")
bands={"SMB Account Executive":dict(L1=30000,H1=40000,m1=1.2,L2=40000,m2=1.3),"ENT Account Executive":dict(L1=60000,H1=80000,m1=1.2,L2=80000,m2=1.3)}
spiff={"SMB Account Manager":500,"ENT Account Manager":1500}
ramp_pct={"SMB Account Executive":(1.0,0.5),"ENT Account Executive":(1.0,0.5),"SMB Account Manager":(1.0,1.0),"ENT Account Manager":(1.0,1.0)}
def metric_of(role):
    if role=="Head of Sales & AM": return "Both"
    return "New" if ("Account Executive" in role or "AE" in role or role=="Director of Sales") else "Existing"
# ---------------- reps
reps=ro.merge(hr,on="hr_id",how="left")
reps["role"]=reps["Current Role"]; reps["metric"]=reps.role.map(metric_of); reps["is_ic"]=reps.role.isin(["SMB Account Executive","ENT Account Executive","SMB Account Manager","ENT Account Manager"])
reps["rate"]=reps.role.map(roles.rate.astype(float)); reps["quota"]=reps.role.map(roles.quota.astype(float))
reps["emp_start"]=reps["Start Date"]; reps["emp_end"]=reps["End Date"].fillna(pd.Timestamp("2099-12-31"))
reps["d_from"]=reps.emp_start.clip(lower=M_START); reps["d_to"]=reps.emp_end.clip(upper=M_END); reps["days_emp"]=((reps.d_to-reps.d_from).dt.days+1).clip(lower=0)
reps["quota_pro"]=reps.quota*reps.days_emp/DIM
def ramp_days(r):
    if r.role not in ramp_pct or r.days_emp==0: return 0,0
    rs=r["Current Role Start Date"]; n1=n2=0
    for t in pd.date_range(r.d_from,r.d_to):
        k=(t-rs).days+1
        if 1<=k<=30: n1+=1
        elif 31<=k<=60: n2+=1
    return n1,n2
rd=reps.apply(ramp_days,axis=1,result_type="expand"); reps["ramp_n1"],reps["ramp_n2"]=rd[0],rd[1]
reps["ramp_floor"]=[ (n1*ramp_pct[r][0]+n2*ramp_pct[r][1])*q/DIM if r in ramp_pct else 0 for r,n1,n2,q in zip(reps.role,reps.ramp_n1,reps.ramp_n2,reps.quota)]
reps["ramping"]=(reps.ramp_n1+reps.ramp_n2)>0
name=dict(zip(reps.crm_owner_id,reps.name)); rate_by_crm=dict(zip(reps.crm_owner_id,reps.rate)); role_by_crm=dict(zip(reps.crm_owner_id,reps.role))
emp_start=dict(zip(reps.crm_owner_id,reps.emp_start)); emp_end=dict(zip(reps.crm_owner_id,reps.emp_end))
# ---------------- accounts
cw=opp[opp.opportunity_stage=="Closed Won"].sort_values(["crm_account_id","effective_start_date"])
A=cw.groupby("crm_account_id").agg(go_live=("effective_start_date","min"),closer=("closed_by_owner_id","first"),owner=("crm_owner_id","first"),atype=("account_type","first"),segment=("segment","first"),net_terms=("net_terms","first"),charge=("charge_rate_per_shift","first"),pay=("pay_rate_per_shift","first"),first_won=("closed_won_date","min"),n_cw=("opportunity_id","size")).reset_index()
A=A.merge(mp,on="crm_account_id",how="left"); A["margin"]=A.charge-A.pay
A=A.merge(app.groupby("app_account_id").account_first_worked_shift_date.first().rename("fw"),left_on="app_account_id",right_index=True,how="left")
A["W1s"]=A.fw; A["W1e"]=A.fw+pd.Timedelta(days=29); A["W2s"]=A.fw+pd.Timedelta(days=30); A["W2e"]=A.fw+pd.Timedelta(days=59); A["W3s"]=A.fw+pd.Timedelta(days=60); A["W3e"]=A.fw+pd.Timedelta(days=89)
A["mult"]=np.where(A.atype=="GTM",1.0,A.net_terms.map(NET_MULT)); A["is_gtm"]=A.atype=="GTM"
A["closer_name"]=A.closer.map(name); A["owner_name"]=A.owner.map(name)
A["c_start"]=A.closer.map(emp_start); A["c_end"]=A.closer.map(emp_end)
sh=app.merge(A[["app_account_id","margin","charge","is_gtm"]],on="app_account_id",how="left")
wk=sh[sh.worked_shift]
def cnt_worked(acct, lo, hi):
    if pd.isna(lo) or pd.isna(hi) or hi<lo: return 0
    x=wk_by.get(acct); 
    if x is None: return 0
    return int(((x>=lo)&(x<=hi)).sum())
def cnt_posted(acct, lo, hi):
    if pd.isna(hi): return 0
    x=po_by.get(acct)
    if x is None: return 0
    lo=pd.Timestamp("1900-01-01") if pd.isna(lo) else lo
    if hi<lo: return 0
    return int(((x>=lo)&(x<=hi)).sum())
wk_by={k:v.values for k,v in wk.groupby("app_account_id").shift_worked_date}; po_by={k:v.values for k,v in sh.groupby("app_account_id").shift_posted_date}
rows=[]
for r in A.itertuples():
    a=r.app_account_id; m=r.margin; ch=r.charge
    if r.is_gtm:
        # GSV by posted date; F1 has an upper bound only. June recognition: posted in June within W1, plus pre-June posts if the window opened in June (first statement the window exists)
        f1_june_full=ch*cnt_posted(a, M_START if r.fw<M_START else None, min(r.W1e,M_END))
        f1_june_paid=ch*cnt_posted(a, max(M_START if r.fw<M_START else pd.Timestamp("1900-01-01"), r.c_start) if pd.notna(r.c_start) else pd.Timestamp("2099-01-01"), min(r.W1e,M_END,r.c_end if pd.notna(r.c_end) else M_END))
        W1=ch*cnt_posted(a,None,r.W1e); W2=ch*cnt_posted(a,r.W2s,r.W2e); W3=ch*cnt_posted(a,r.W3s,r.W3e)
        pre_fw_gsv=ch*cnt_posted(a,None,r.fw-pd.Timedelta(days=1)) if pd.notna(r.fw) else 0
    else:
        f1_june_full=m*cnt_worked(a,max(r.W1s,M_START) if pd.notna(r.W1s) else pd.NaT,min(r.W1e,M_END) if pd.notna(r.W1e) else pd.NaT)
        f1_june_paid=m*cnt_worked(a,max(r.W1s,M_START,r.c_start) if pd.notna(r.W1s) and pd.notna(r.c_start) else pd.NaT,min(r.W1e,M_END,r.c_end) if pd.notna(r.W1e) and pd.notna(r.c_end) else pd.NaT)
        W1=m*cnt_worked(a,r.W1s,r.W1e); W2=m*cnt_worked(a,r.W2s,r.W2e); W3=m*cnt_worked(a,r.W3s,r.W3e); pre_fw_gsv=0
    w2_closes=pd.notna(r.W2e) and M_START<=r.W2e<=M_END; w3_closes=pd.notna(r.W3e) and M_START<=r.W3e<=M_END
    imp2=max(0,W2-W1)*HALF if w2_closes else 0; imp3=max(0,W3-max(W1,W2))*HALF if w3_closes else 0
    emp_on=lambda t: pd.notna(r.c_start) and r.c_start<=t<=r.c_end
    imp2_paid=imp2 if (w2_closes and emp_on(r.W2e)) else 0; imp3_paid=imp3 if (w3_closes and emp_on(r.W3e)) else 0
    conv=(GTM_RATE/rate_by_crm[r.closer]) if (r.is_gtm and pd.notna(r.closer) and r.closer in rate_by_crm) else (1.0 if not r.is_gtm else np.nan)
    def cred(f1,i2,i3): return (f1+i2+i3)*r.mult*conv if pd.notna(conv) else 0
    new_full=cred(f1_june_full,imp2,imp3); new_paid=cred(f1_june_paid,imp2_paid,imp3_paid)
    # existing
    ex_june_nr=m*cnt_worked(a,M_START,M_END) if r.go_live<M_START else 0
    ex_may_nr=m*cnt_worked(a,P_START,P_END) if r.go_live<P_START else 0
    june_nr_all=m*cnt_worked(a,M_START,M_END)
    rows.append(dict(crm_account_id=r.crm_account_id,app_account_id=a,billing_account_id=r.billing_account_id,closer=r.closer,closer_name=r.closer_name,owner=r.owner,owner_name=r.owner_name,atype=r.atype,segment=r.segment,net_terms=r.net_terms,mult=r.mult,charge=ch,pay=r.pay,margin=m,go_live=r.go_live,first_won=r.first_won,n_cw=r.n_cw,fw=r.fw,W1e=r.W1e,W2e=r.W2e,W3e=r.W3e,
        f1_june_full=f1_june_full,f1_june_paid=f1_june_paid,W1=W1,W2=W2,W3=W3,w2_closes=w2_closes,w3_closes=w3_closes,imp2=imp2,imp3=imp3,imp2_paid=imp2_paid,imp3_paid=imp3_paid,conv=conv,new_cred_full=new_full,new_cred_paid=new_paid,pre_fw_gsv=pre_fw_gsv,
        ex_june_nr=ex_june_nr,ex_may_nr=ex_may_nr,june_nr_all=june_nr_all,existing_june=r.go_live<M_START,existing_may=r.go_live<P_START))
AC=pd.DataFrame(rows)
# credits
appr=bill[bill.ticket_status=="approved"]
cj=appr[appr.billing_month==MONTH].groupby("billing_account_id").credit_amount.sum(); cm=appr[appr.billing_month==PMONTH].groupby("billing_account_id").credit_amount.sum()
AC["cred_june_all"]=AC.billing_account_id.map(cj).fillna(0); AC["cred_may_all"]=AC.billing_account_id.map(cm).fillna(0)
AC["cred_june"]=np.where(AC.existing_june,AC.cred_june_all,0); AC["cred_may"]=np.where(AC.existing_may,AC.cred_may_all,0)
AC["ex_june"]=AC.ex_june_nr-AC.cred_june; AC["ex_may"]=AC.ex_may_nr-AC.cred_may
AC["ex_june_samebook"]=np.where(AC.existing_may,AC.ex_june,0)   # June figure for the May book (live before 1 May)
AC.to_csv(S+"/out/accounts_calc.csv",index=False)
# ---------------- rep level
newf=AC.groupby("closer").new_cred_full.sum(); newp=AC.groupby("closer").new_cred_paid.sum()
exj=AC.groupby("owner").ex_june.sum(); exm=AC.groupby("owner").ex_may.sum(); exjs=AC.groupby("owner").ex_june_samebook.sum()
reps["new_full"]=reps.crm_owner_id.map(newf).fillna(0); reps["new_paid"]=reps.crm_owner_id.map(newp).fillna(0)
reps["ex_june"]=reps.crm_owner_id.map(exj).fillna(0); reps["ex_may"]=reps.crm_owner_id.map(exm).fillna(0); reps["ex_june_samebook"]=reps.crm_owner_id.map(exjs).fillna(0)
is_ae=reps.role.isin(["SMB Account Executive","ENT Account Executive"]); is_am=reps.role.isin(["SMB Account Manager","ENT Account Manager"])
reps["produced_paid"]=np.where(is_ae,reps.new_paid,np.where(is_am,reps.ex_june,0)); reps["produced_full"]=np.where(is_ae,reps.new_full,np.where(is_am,reps.ex_june,0))
reps["employed_in_month"]=reps.days_emp>0
reps["credited"]=np.where(reps.employed_in_month,np.maximum(reps.produced_paid,reps.ramp_floor),0)
reps["credited_full"]=np.where(reps.employed_in_month,np.maximum(reps.produced_full,reps.ramp_floor),reps.produced_full)
reps["attain"]=np.where(reps.quota_pro>0,reps.credited/reps.quota_pro,np.nan)
def commission(role,C,rate,eligible,mult_override=None):
    if role in bands and eligible:
        b=bands[role]; m1=b["m1"]; m2=b["m2"]
        if mult_override and role=="SMB Account Executive": m1,m2=mult_override
        return rate*(min(C,b["L1"])+m1*max(0,min(C,b["H1"])-b["L1"])+m2*max(0,C-b["L2"]))
    return rate*C
reps["acc_eligible"]=is_ae&(~reps.ramping)&reps.employed_in_month
reps["comm_ic"]=[commission(r,c,rt,e) if ic else 0 for r,c,rt,e,ic in zip(reps.role,reps.credited,reps.rate,reps.acc_eligible,reps.is_ic)]
reps["comm_ic_scn"]=[commission(r,c,rt,e,(1.3,1.5)) if ic else 0 for r,c,rt,e,ic in zip(reps.role,reps.credited,reps.rate,reps.acc_eligible,reps.is_ic)]
# SPIFF
reps["spiff"]=[spiff[r] if (r in spiff and not rp and emp and may>0 and jun>=may) else 0 for r,rp,emp,may,jun in zip(reps.role,reps.ramping,reps.employed_in_month,reps.ex_may,reps.ex_june_samebook)]
# ---------------- manager chain
mgr=dict(zip(reps.hr_id,reps["Manager - ID"]))
def chain(h):
    out=[]; cur=mgr.get(h)
    while cur in mgr: out.append(cur); cur=mgr.get(cur)
    return out
reps["chain"]=reps.hr_id.map(chain)
reps["metric_ic"]=np.where(is_ae,"New",np.where(is_am,"Existing",""))
carried_new={}; carried_ex={}
for r in reps.itertuples():
    for mgid in r.chain:
        if r.metric_ic=="New": carried_new[mgid]=carried_new.get(mgid,0)+r.credited_full
        elif r.metric_ic=="Existing": carried_ex[mgid]=carried_ex.get(mgid,0)+r.credited_full
reps["carried_new"]=reps.hr_id.map(carried_new).fillna(0); reps["carried_ex"]=reps.hr_id.map(carried_ex).fillna(0)
reps["rate2"]=reps.role.map(pd.to_numeric(roles.rate2,errors="coerce")); reps["quota2"]=reps.role.map(pd.to_numeric(roles.quota2,errors="coerce"))
def mgr_comm(r):
    if r.is_ic: return 0
    if r.metric=="New": return r.rate*r.carried_new
    if r.metric=="Existing": return r.rate*r.carried_ex
    return r.rate*r.carried_new+r.rate2*r.carried_ex
reps["comm_mgr"]=reps.apply(mgr_comm,axis=1)
reps["mgr_credited"]=np.where(reps.metric=="New",reps.carried_new,np.where(reps.metric=="Existing",reps.carried_ex,reps.carried_new))
reps["mgr_attain"]=np.where(~reps.is_ic,reps.mgr_credited/reps.quota_pro,np.nan)
reps["commission_usd"]=reps.comm_ic+reps.comm_mgr+reps.spiff; reps["commission_usd_scn"]=reps.comm_ic_scn+reps.comm_mgr+reps.spiff
fxr=dict(zip(fx["Country Code"],fx["1 USD ="])); fxc=dict(zip(fx["Country Code"],fx["Code"]))
reps["fx"]=reps["Country Code"].map(fxr); reps["ccy"]=reps["Country Code"].map(fxc); reps["commission_local"]=reps.commission_usd*reps.fx
cols=["name","role","Country Code","emp_start","emp_end","days_emp","quota_pro","ramp_n1","ramp_n2","ramp_floor","ramping","produced_paid","produced_full","credited","attain","acc_eligible","comm_ic","spiff","carried_new","carried_ex","comm_mgr","commission_usd","ccy","fx","commission_local","commission_usd_scn"]
out=reps[cols].copy(); out.to_csv(S+"/out/reps_calc.csv",index=False)
pd.set_option("display.float_format",lambda v: f"{v:,.2f}")
P(out.sort_values(["role","name"]).to_string(index=False))
P("\nTOTAL USD: %.2f | scenario: %.2f | delta: %.2f" % (reps.commission_usd.sum(),reps.commission_usd_scn.sum(),reps.commission_usd_scn.sum()-reps.commission_usd.sum()))
P("by role:\n", reps.groupby("role").agg(n=("name","size"),credited=("credited","sum"),comm=("commission_usd","sum"),scn=("commission_usd_scn","sum")).to_string())
reps.to_pickle(S+"/data/reps_calc.pkl"); AC.to_pickle(S+"/data/accounts_calc.pkl")
