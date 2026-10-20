"""Parameterised reference implementation of the June 2026 plan. compute(d, **opts) returns (reps, accounts).
Default options reproduce the plan exactly as written. Each option is a deliberate deviation used to size a ledger item."""
import pandas as pd, numpy as np
NET_MULT={15:1.2,30:1.0,45:0.9,60:0.7}
def compute(d, month="2026-06", exclude_accounts=(), hold_closer_not_employed_at_close=False, gtm_pre_month=True, include_denied=False,
            credits_on_nonexisting=False, residue_as_won=False, golive_latest_cw=False, ignore_employment=False, ramp_no_proration=False,
            first_worked_observed=False, no_ramp_restart_for=(), gtm_rate=0.03, half=0.5, smb_mult=None, gtm_as_standard=(), gtm_worked_only=(), role_override=None, mgr_proration=None):
    ro,hr,fx,comp,mp,opp,app,bill=d["roster"],d["hr"],d["fx"],d["comp"],d["map"],d["opp"],d["app"],d["bill"]
    M_START=pd.Timestamp(month+"-01"); M_END=M_START+pd.offsets.MonthEnd(0); DIM=M_END.day; P_START=M_START-pd.offsets.MonthBegin(1); P_END=M_START-pd.Timedelta(days=1); MONTH=M_START.strftime("%Y-%m"); PMONTH=P_START.strftime("%Y-%m")
    comp=comp.rename(columns={"Role":"role","Monthly Quota Target":"quota","Standard Payout":"rate","Monthly Target":"quota2","Standard Payout 2":"rate2"}); roles=comp.set_index("role")
    bands={"SMB Account Executive":dict(L1=30000,H1=40000,m1=1.2,L2=40000,m2=1.3),"ENT Account Executive":dict(L1=60000,H1=80000,m1=1.2,L2=80000,m2=1.3)}
    if smb_mult: bands["SMB Account Executive"]["m1"],bands["SMB Account Executive"]["m2"]=smb_mult
    spiff={"SMB Account Manager":500,"ENT Account Manager":1500}; ramp_pct={"SMB Account Executive":(1.0,0.5),"ENT Account Executive":(1.0,0.5),"SMB Account Manager":(1.0,1.0),"ENT Account Manager":(1.0,1.0)}
    def metric_of(role):
        if role=="Head of Sales & AM": return "Both"
        return "New" if ("Account Executive" in role or "AE" in role or role=="Director of Sales") else "Existing"
    reps=ro.merge(hr,on="hr_id",how="left"); reps["role"]=reps["Current Role"]
    if role_override:
        for nm,(rl,rs) in role_override.items():
            reps.loc[reps.name==nm,"role"]=rl
            if rs is not None: reps.loc[reps.name==nm,"Current Role Start Date"]=pd.Timestamp(rs)
    reps["metric"]=reps.role.map(metric_of)
    reps["is_ic"]=reps.role.isin(list(ramp_pct)); reps["rate"]=reps.role.map(roles.rate.astype(float)); reps["quota"]=reps.role.map(roles.quota.astype(float))
    reps["emp_start"]=reps["Start Date"]; reps["emp_end"]=reps["End Date"].fillna(pd.Timestamp("2099-12-31"))
    if ignore_employment: reps["emp_start"]=pd.Timestamp("1900-01-01"); reps["emp_end"]=pd.Timestamp("2099-12-31")
    reps["d_from"]=reps.emp_start.clip(lower=M_START); reps["d_to"]=reps.emp_end.clip(upper=M_END); reps["days_emp"]=((reps.d_to-reps.d_from).dt.days+1).clip(lower=0)
    reps["quota_pro"]=reps.quota*reps.days_emp/DIM
    def ramp_days(r):
        if r.role not in ramp_pct or r.days_emp==0: return 0,0
        rs=r["Current Role Start Date"]
        if r["name"] in no_ramp_restart_for: rs=r["Start Date"]
        n1=n2=0
        for t in pd.date_range(r.d_from,r.d_to):
            k=(t-rs).days+1
            if 1<=k<=30: n1+=1
            elif 31<=k<=60: n2+=1
        return n1,n2
    rd=reps.apply(ramp_days,axis=1,result_type="expand"); reps["ramp_n1"],reps["ramp_n2"]=rd[0],rd[1]
    if ramp_no_proration:
        reps["ramp_floor"]=[ (ramp_pct[r][0] if n1>0 else (ramp_pct[r][1] if n2>0 else 0))*q if r in ramp_pct else 0 for r,n1,n2,q in zip(reps.role,reps.ramp_n1,reps.ramp_n2,reps.quota)]
    else:
        reps["ramp_floor"]=[ (n1*ramp_pct[r][0]+n2*ramp_pct[r][1])*q/DIM if r in ramp_pct else 0 for r,n1,n2,q in zip(reps.role,reps.ramp_n1,reps.ramp_n2,reps.quota)]
    reps["ramping"]=(reps.ramp_n1+reps.ramp_n2)>0
    name=dict(zip(reps.crm_owner_id,reps.name)); rate_by=dict(zip(reps.crm_owner_id,reps.rate)); es=dict(zip(reps.crm_owner_id,reps.emp_start)); ee=dict(zip(reps.crm_owner_id,reps.emp_end))
    # accounts
    won=opp[(opp.opportunity_stage=="Closed Won")|(residue_as_won&opp.closed_won_date.notna())].sort_values(["crm_account_id","effective_start_date"])
    agg=dict(go_live=("effective_start_date","max" if golive_latest_cw else "min"),closer=("closed_by_owner_id","first"),owner=("crm_owner_id","first"),atype=("account_type","first"),segment=("segment","first"),net_terms=("net_terms","first"),charge=("charge_rate_per_shift","first"),pay=("pay_rate_per_shift","first"),first_won=("closed_won_date","min"),n_cw=("opportunity_id","size"))
    A=won.groupby("crm_account_id").agg(**agg).reset_index().merge(mp,on="crm_account_id",how="left"); A["margin"]=A.charge-A.pay
    fwg=app.groupby("app_account_id").account_first_worked_shift_date.first(); fwo=app[app.worked_shift].groupby("app_account_id").shift_worked_date.min()
    A=A.merge((fwo if first_worked_observed else fwg).rename("fw"),left_on="app_account_id",right_index=True,how="left")
    for k,off in (("W1s",0),("W1e",29),("W2s",30),("W2e",59),("W3s",60),("W3e",89)): A[k]=A.fw+pd.Timedelta(days=off)
    A["is_gtm"]=(A.atype=="GTM")&~A.app_account_id.isin(gtm_as_standard); A["mult"]=np.where(A.is_gtm,1.0,A.net_terms.map(NET_MULT)); A["closer_name"]=A.closer.map(name); A["owner_name"]=A.owner.map(name)
    A["c_start"]=A.closer.map(es); A["c_end"]=A.closer.map(ee)
    wk=app[app.worked_shift]; wk_by={k:v.values for k,v in wk.groupby("app_account_id").shift_worked_date}; po_by={k:v.values for k,v in app.groupby("app_account_id").shift_posted_date}
    def cnt(by,acct,lo,hi):
        x=by.get(acct)
        if x is None or pd.isna(hi): return 0
        lo=pd.Timestamp("1900-01-01") if pd.isna(lo) else lo
        if hi<lo: return 0
        return int(((x>=lo)&(x<=hi)).sum())
    FAR=pd.Timestamp("2099-01-01"); rows=[]
    for r in A.itertuples():
        a=r.app_account_id; m=r.margin; ch=r.charge; cs=r.c_start if pd.notna(r.c_start) else FAR; ce=r.c_end if pd.notna(r.c_end) else pd.Timestamp("1900-01-01")
        if pd.isna(r.fw): f1f=f1p=W1=W2=W3=0; pre=0
        elif r.is_gtm:
            if a in gtm_worked_only: by=wk_by  # alternative treatment: count only worked shifts (still by posted date basis replaced with worked dates)
            else: by=po_by
            lo_rec=None if (gtm_pre_month and r.fw>=M_START) else M_START
            f1f=ch*cnt(by,a,lo_rec,min(r.W1e,M_END)); f1p=ch*cnt(by,a,max(lo_rec if lo_rec is not None else pd.Timestamp("1900-01-01"),cs),min(r.W1e,M_END,ce))
            W1=ch*cnt(by,a,None,r.W1e); W2=ch*cnt(by,a,r.W2s,r.W2e); W3=ch*cnt(by,a,r.W3s,r.W3e); pre=ch*cnt(po_by,a,None,r.fw-pd.Timedelta(days=1))
        else:
            f1f=m*cnt(wk_by,a,max(r.W1s,M_START),min(r.W1e,M_END)); f1p=m*cnt(wk_by,a,max(r.W1s,M_START,cs),min(r.W1e,M_END,ce))
            W1=m*cnt(wk_by,a,r.W1s,r.W1e); W2=m*cnt(wk_by,a,r.W2s,r.W2e); W3=m*cnt(wk_by,a,r.W3s,r.W3e); pre=0
        w2c=pd.notna(r.fw) and M_START<=r.W2e<=M_END; w3c=pd.notna(r.fw) and M_START<=r.W3e<=M_END
        imp2=max(0,W2-W1)*half if w2c else 0; imp3=max(0,W3-max(W1,W2))*half if w3c else 0
        imp2p=imp2 if (w2c and cs<=r.W2e<=ce) else 0; imp3p=imp3 if (w3c and cs<=r.W3e<=ce) else 0
        has_closer=pd.notna(r.closer) and r.closer in rate_by
        conv=0 if not has_closer else ((gtm_rate/rate_by[r.closer]) if r.is_gtm else 1.0)
        treat=1.0
        if a in exclude_accounts: treat=0.0
        if hold_closer_not_employed_at_close and has_closer and pd.notna(r.first_won) and not (cs<=r.first_won<=ce): treat=0.0
        newf=(f1f+imp2+imp3)*r.mult*conv*treat; newp=(f1p+imp2p+imp3p)*r.mult*conv*treat
        uncred=(f1f+imp2+imp3)*r.mult if not has_closer else 0
        exj=m*cnt(wk_by,a,M_START,M_END) if r.go_live<M_START else 0; exm=m*cnt(wk_by,a,P_START,P_END) if r.go_live<P_START else 0
        rows.append(dict(crm_account_id=r.crm_account_id,app_account_id=a,billing_account_id=r.billing_account_id,closer=r.closer,closer_name=r.closer_name,owner=r.owner,owner_name=r.owner_name,atype=r.atype,segment=r.segment,net_terms=r.net_terms,mult=r.mult,charge=ch,pay=r.pay,margin=m,go_live=r.go_live,first_won=r.first_won,n_cw=r.n_cw,fw=r.fw,W1e=r.W1e,W2e=r.W2e,W3e=r.W3e,f1_june_full=f1f,f1_june_paid=f1p,W1=W1,W2=W2,W3=W3,imp2=imp2,imp3=imp3,conv=conv,new_cred_full=newf,new_cred_paid=newp,uncredited=uncred,pre_fw_gsv=pre,ex_june_nr=exj,ex_may_nr=exm,june_nr_all=m*cnt(wk_by,a,M_START,M_END),existing_june=r.go_live<M_START,existing_may=r.go_live<P_START))
    AC=pd.DataFrame(rows)
    b=bill if include_denied else bill[bill.ticket_status=="approved"]
    cj=b[b.billing_month==MONTH].groupby("billing_account_id").credit_amount.sum(); cm=b[b.billing_month==PMONTH].groupby("billing_account_id").credit_amount.sum()
    AC["cred_june_all"]=AC.billing_account_id.map(cj).fillna(0); AC["cred_may_all"]=AC.billing_account_id.map(cm).fillna(0)
    AC["cred_june"]=np.where(AC.existing_june|credits_on_nonexisting,AC.cred_june_all,0); AC["cred_may"]=np.where(AC.existing_may|credits_on_nonexisting,AC.cred_may_all,0)
    AC["ex_june"]=AC.ex_june_nr-AC.cred_june; AC["ex_may"]=AC.ex_may_nr-AC.cred_may; AC["ex_june_samebook"]=np.where(AC.existing_may,AC.ex_june,0)
    # reps
    reps["new_full"]=reps.crm_owner_id.map(AC.groupby("closer").new_cred_full.sum()).fillna(0); reps["new_paid"]=reps.crm_owner_id.map(AC.groupby("closer").new_cred_paid.sum()).fillna(0)
    reps["ex_june"]=reps.crm_owner_id.map(AC.groupby("owner").ex_june.sum()).fillna(0); reps["ex_may"]=reps.crm_owner_id.map(AC.groupby("owner").ex_may.sum()).fillna(0); reps["ex_june_samebook"]=reps.crm_owner_id.map(AC.groupby("owner").ex_june_samebook.sum()).fillna(0)
    is_ae=reps.role.isin(["SMB Account Executive","ENT Account Executive"]); is_am=reps.role.isin(["SMB Account Manager","ENT Account Manager"])
    reps["produced_paid"]=np.where(is_ae,reps.new_paid,np.where(is_am,reps.ex_june,0)); reps["produced_full"]=np.where(is_ae,reps.new_full,np.where(is_am,reps.ex_june,0))
    reps["employed"]=reps.days_emp>0
    reps["credited"]=np.where(reps.employed,np.maximum(reps.produced_paid,reps.ramp_floor),0); reps["credited_full"]=np.where(reps.employed,np.maximum(reps.produced_full,reps.ramp_floor),reps.produced_full)
    reps["attain"]=np.where(reps.quota_pro>0,reps.credited/reps.quota_pro,np.nan)
    def commission(role,C,rate,eligible):
        if role in bands and eligible:
            b_=bands[role]; return rate*(min(C,b_["L1"])+b_["m1"]*max(0,min(C,b_["H1"])-b_["L1"])+b_["m2"]*max(0,C-b_["L2"]))
        return rate*C
    reps["acc_eligible"]=is_ae&(~reps.ramping)&reps.employed
    reps["comm_ic"]=[commission(r,c,rt,e) if ic else 0 for r,c,rt,e,ic in zip(reps.role,reps.credited,reps.rate,reps.acc_eligible,reps.is_ic)]
    reps["spiff"]=[spiff[r] if (r in spiff and not rp and emp and may>0 and jun>=may) else 0 for r,rp,emp,may,jun in zip(reps.role,reps.ramping,reps.employed,reps.ex_may,reps.ex_june_samebook)]
    mgr=dict(zip(reps.hr_id,reps["Manager - ID"]))
    def chain(h):
        out=[]; cur=mgr.get(h)
        while cur in mgr: out.append(cur); cur=mgr.get(cur)
        return out
    reps["chain"]=reps.hr_id.map(chain); reps["metric_ic"]=np.where(is_ae,"New",np.where(is_am,"Existing",""))
    cn={}; cx={}
    for r in reps.itertuples():
        for g in r.chain:
            if r.metric_ic=="New": cn[g]=cn.get(g,0)+r.credited_full
            elif r.metric_ic=="Existing": cx[g]=cx.get(g,0)+r.credited_full
    reps["carried_new"]=reps.hr_id.map(cn).fillna(0); reps["carried_ex"]=reps.hr_id.map(cx).fillna(0)
    reps["rate2"]=reps.role.map(pd.to_numeric(roles.rate2,errors="coerce")).fillna(0)
    reps["comm_mgr"]=[0 if ic else (rt*n if m=="New" else (rt*x if m=="Existing" else rt*n+r2*x)) for ic,m,rt,r2,n,x in zip(reps.is_ic,reps.metric,reps.rate,reps.rate2,reps.carried_new,reps.carried_ex)]
    if mgr_proration:
        for nm,fr in mgr_proration.items(): reps.loc[reps.name==nm,"comm_mgr"]*=fr
    reps["commission_usd"]=reps.comm_ic+reps.comm_mgr+reps.spiff
    fxr=dict(zip(fx["Country Code"],fx["1 USD ="])); fxc=dict(zip(fx["Country Code"],fx["Code"]))
    reps["fx"]=reps["Country Code"].map(fxr); reps["ccy"]=reps["Country Code"].map(fxc); reps["commission_local"]=reps.commission_usd*reps.fx
    return reps, AC
