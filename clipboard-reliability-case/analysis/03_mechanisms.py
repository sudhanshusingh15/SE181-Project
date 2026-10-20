import pandas as pd, numpy as np, sys
pd.set_option("display.width",220); pd.set_option("display.max_columns",30)
S=sys.argv[1]; P=print
sh=pd.read_pickle(f"{S}/data/shifts_enriched.pkl"); cl=pd.read_pickle(f"{S}/data/cancels_cleveland.pkl"); ca=pd.read_pickle(f"{S}/data/cancels.pkl")
oid=lambda s: pd.to_datetime(s.apply(lambda x: int(x[:8],16) if isinstance(x,str) and len(x)>=8 else np.nan),unit="s")
# 0. validate ObjectId timestamp
chk=(oid(sh["Shift ID"])-sh["Created At"]).dt.total_seconds().abs(); P("ObjectId ts vs Created At: median abs diff %.1fs, p99 %.1fs" % (chk.median(), chk.quantile(.99)))
sh["worker_created"]=oid(sh["Worker ID"])
sh["fac_created"]=oid(sh["Facility ID"])
cl["worker_created"]=oid(cl["Worker ID"]); cl["fac_created"]=oid(cl["Facility ID"])
P("Worker signup range (cancel log, all markets):", oid(ca["Worker ID"]).min(), "->", oid(ca["Worker ID"]).max())
# 1. refill curve: P(worked) by lead time of the LAST cancel on the shift
last=cl.sort_values("Created At").groupby("Shift ID").agg(last_lt=("Lead Time","last"), last_action=("Action","last"), last_worker=("Worker ID","last"))
d=sh.merge(last,left_on="Shift ID",right_index=True,how="inner")
d["refilled"]=d.Verified&(d["Worker ID"]!=d.last_worker)
bins=[-np.inf,0,1,4,12,24,48,72,168,np.inf]; labels=["NCNS/after","0-1h","1-4h","4-12h","12-24h","24-48h","48-72h","3-7d",">7d"]
d["lt_bin"]=pd.cut(d.last_lt,bins,labels=labels,right=False)
rc=d.groupby("lt_bin",observed=True).agg(shifts=("Shift ID","size"), refilled=("refilled","sum"), worked=("Verified","sum"), unfilled=("outcome",lambda s:(s=="unfilled").sum()), deleted=("deleted","sum"))
rc["refill_rate"]=(rc.refilled/rc.shifts).round(3); rc["unfilled_rate"]=(rc.unfilled/rc.shifts).round(3); P("\n### REFILL CURVE by lead time of last cancel:\n", rc.to_string())
# 2. shift-swap: late cancel worker worked an overlapping / same-day Cleveland shift
worked=sh[sh.Verified][["Shift ID","Worker ID","Facility ID","Start","End","Charge","Agent Req"]].rename(columns={"Shift ID":"w_shift","Facility ID":"w_fac","Start":"w_start","End":"w_end","Charge":"w_charge","Agent Req":"w_role"})
c2=cl.merge(sh[["Shift ID","Start","End","Charge","Agent Req","Shift Type"]].rename(columns={"Start":"c_start"}),on="Shift ID",how="left")
m=c2.merge(worked,on="Worker ID",how="left")
m["overlap"]=(m.w_start<m.End)&(m.w_end>m.c_start)&(m.w_shift!=m["Shift ID"])
m["sameday12"]=((m.w_start-m.c_start).abs()<=pd.Timedelta(hours=12))&(m.w_shift!=m["Shift ID"])
m["within48"]=((m.w_start-m.c_start).abs()<=pd.Timedelta(hours=48))&(m.w_shift!=m["Shift ID"])
agg=m.groupby("Action ID").agg(overlap=("overlap","max"), sameday=("sameday12","max"), within48=("within48","max"), ov_charge=("w_charge",lambda s: np.nan), )
# charge of overlapping worked shift
ov=m[m.overlap].groupby("Action ID").agg(ov_charge=("w_charge","max"), ov_fac=("w_fac","first"))
c2=c2.merge(agg[["overlap","sameday","within48"]],left_on="Action ID",right_index=True,how="left").merge(ov,left_on="Action ID",right_index=True,how="left")
for col in ["overlap","sameday","within48"]: c2[col]=c2[col].fillna(False).astype(bool)
c2["cat"]=np.select([c2.Action=="NO_CALL_NO_SHOW", c2["Lead Time"]<4, c2["Lead Time"]<24, c2["Lead Time"]<72],["NCNS","0-4h","4-24h","24-72h"],">72h")
P("\n### SHIFT-SWAP: share of cancels where same worker WORKED another Cleveland shift (verified):")
P(c2.groupby("cat")[["overlap","sameday","within48"]].mean().round(3).to_string()); P("counts:\n", c2.groupby("cat")[["overlap","sameday","within48"]].sum().to_string())
sw=c2[c2.overlap&(c2["Lead Time"]<24)]; P("Late cancels w/ overlapping worked shift: %d; of which higher charge at worked shift: %d, equal: %d, lower: %d; different facility: %d" % (len(sw),(sw.ov_charge>sw.Charge).sum(),(sw.ov_charge==sw.Charge).sum(),(sw.ov_charge<sw.Charge).sum(),(sw.ov_fac!=sw["Facility ID"]).sum()))
P("  mean charge canceled %.1f vs worked %.1f" % (sw.Charge.mean(), sw.ov_charge.mean()))
# 3. worker tenure at shift start -> late rate. Build pseudo-booking table
bk=pd.concat([sh[sh.has_worker][["Shift ID","Worker ID","Facility ID","Start","Charge","Agent Req","Shift Type","worker_created"]].assign(late=False,ncns=False,canceled=False,lt=np.nan),
              cl[["Shift ID","Worker ID","Facility ID","Start","worker_created","late","ncns","Lead Time"]].rename(columns={"Lead Time":"lt"}).merge(sh[["Shift ID","Charge","Agent Req","Shift Type"]],on="Shift ID",how="left").assign(canceled=True)],ignore_index=True)
P("\n### PSEUDO-BOOKINGS (final assignments + cancel events):", len(bk), "| cancel rate %.3f | late rate %.3f | ncns rate %.3f" % (bk.canceled.mean(), bk.late.mean(), bk.ncns.mean()))
bk["tenure_d"]=(bk.Start-bk.worker_created).dt.days
bk["tenure_bin"]=pd.cut(bk.tenure_d,[-np.inf,14,30,60,90,180,365,np.inf],labels=["<2w","2-4w","1-2mo","2-3mo","3-6mo","6-12mo",">1y"])
t=bk.groupby("tenure_bin",observed=True).agg(bookings=("Shift ID","size"),late=("late","sum"),ncns=("ncns","sum"),workers=("Worker ID","nunique")); t["late_rate"]=(t.late/t.bookings).round(3); t["ncns_rate"]=(t.ncns/t.bookings).round(3); t["share_of_late"]=(t.late/t.late.sum()).round(3); P("Late rate by worker tenure at shift start:\n", t.to_string())
# experience: nth booking of worker within window (ordered by Start)
bk=bk.sort_values("Start"); bk["nth_booking"]=bk.groupby("Worker ID").cumcount()+1
bk["nth_bin"]=pd.cut(bk.nth_booking,[0,1,3,5,10,20,50,1000],labels=["1st","2-3","4-5","6-10","11-20","21-50","50+"])
e=bk.groupby("nth_bin",observed=True).agg(bookings=("Shift ID","size"),late=("late","sum"),ncns=("ncns","sum")); e["late_rate"]=(e.late/e.bookings).round(3); e["ncns_rate"]=(e.ncns/e.bookings).round(3); P("Late rate by worker's nth booking in window:\n", e.to_string())
# role-controlled charge effect (CNA only)
cna=bk[bk["Agent Req"]=="CNA"].copy(); cna["cq"]=pd.qcut(cna.Charge.where(cna.Charge>0),4,duplicates="drop"); q=cna.groupby("cq",observed=True).agg(bookings=("Shift ID","size"),late=("late","sum")); q["late_rate"]=(q.late/q.bookings).round(3); P("CNA late rate by charge quartile:\n", q.to_string())
# 4. facility-level drivers
fac=bk.groupby("Facility ID").agg(bookings=("Shift ID","size"),late=("late","sum"),ncns=("ncns","sum"),cna_share=("Agent Req",lambda s:(s=="CNA").mean()),charge=("Charge","mean"))
fac["late_rate"]=fac.late/fac.bookings; fac=fac[fac.bookings>=100]
cna_fac=cna.groupby("Facility ID").Charge.mean().rename("cna_charge"); fac=fac.join(cna_fac)
P("\n### FACILITIES (>=100 bookings) n=%d. corr(late_rate, cna_charge)=%.2f corr(late_rate, cna_share)=%.2f corr(late_rate, bookings)=%.2f" % (len(fac), fac.late_rate.corr(fac.cna_charge), fac.late_rate.corr(fac.cna_share), fac.late_rate.corr(fac.bookings)))
P(fac.sort_values("late_rate").round(3).to_string())
# 5. worker-level policy simulation: rolling 30d late count triggers
late=cl[cl.late].sort_values("Created At").copy()
wstats=bk.groupby("Worker ID").agg(bookings=("Shift ID","size"),late=("late","sum"),ncns=("ncns","sum"),worked=("canceled",lambda s:(~s).sum()))
wstats["late_rate"]=wstats.late/wstats.bookings
P("\n### WORKER SEGMENTS (Cleveland, Oct-Jan):")
for lo,hi,name in [(0,0,"0 late"),(1,2,"1-2 late"),(3,4,"3-4 late"),(5,9,"5-9 late"),(10,999,"10+ late")]:
    seg=wstats[(wstats.late>=lo)&(wstats.late<=hi)]; P("  %-9s workers %4d | bookings %5d | worked %5d | late %4d (%.0f%% of all late) | seg late rate %.2f | worked share %.0f%%" % (name,len(seg),seg.bookings.sum(),seg.worked.sum(),seg.late.sum(),100*seg.late.sum()/wstats.late.sum(),seg.late.sum()/max(seg.bookings.sum(),1),100*seg.worked.sum()/wstats.worked.sum()))
P("Workers with late_rate>=0.5 and >=4 bookings:", ((wstats.late_rate>=.5)&(wstats.bookings>=4)).sum(), "-> late cancels", wstats[(wstats.late_rate>=.5)&(wstats.bookings>=4)].late.sum(), "worked", wstats[(wstats.late_rate>=.5)&(wstats.bookings>=4)].worked.sum())
# simulate: after k-th late cancel in rolling 30 days -> suspended 7 days (no bookings honored during suspension; count late cancels and worked shifts that fall in suspension windows as 'avoided'/'lost')
def simulate(k, susp_days=7, window=30):
    avoided=0; lost=0; suspensions=0
    for w,g in bk.groupby("Worker ID"):
        g=g.sort_values("Start"); lates=[]; susp_until=pd.Timestamp.min
        for _,r in g.iterrows():
            if r.Start<susp_until:
                if r.late: avoided+=1
                elif not r.canceled: lost+=1
                continue
            if r.late:
                lates=[t for t in lates if (r.Start-t).days<window]+[r.Start]
                if len(lates)>=k: susp_until=r.Start+pd.Timedelta(days=susp_days); suspensions+=1; lates=[]
    return avoided,lost,suspensions
for k in [2,3]:
    a,l,s=simulate(k); P("Policy sim: %d late in 30d -> 7d suspension: suspensions %d, late cancels avoided %d (%.0f%%), worked shifts lost %d (%.1f%%)" % (k,s,a,100*a/bk.late.sum(),l,100*l/(~bk.canceled).sum()))
# 6. cancel action local time (ET = UTC-5 in Nov-Jan, -4 in Oct) for late worker cancels
lw=cl[(cl.Action=="WORKER_CANCEL")&(cl["Lead Time"]<24)].copy(); lw["local"]=lw["Created At"]-pd.Timedelta(hours=5); P("\nLate WORKER_CANCEL by local hour of cancel action:\n", lw.groupby(lw.local.dt.hour).size().to_string())
# 7. NURSE zero charge check
P("\nNURSE rows: charge==0 share %.2f, verified %d of %d" % ((sh[sh["Agent Req"]=="NURSE"].Charge==0).mean(), sh[sh["Agent Req"]=="NURSE"].Verified.sum(), (sh["Agent Req"]=="NURSE").sum()))
# 8. facility churn proxy: posting change vs early-period late exposure
sh["period"]=np.where(sh.Start<"2021-12-01","P1","P2")
fp=sh.pivot_table(index="Facility ID",columns="period",values="Shift ID",aggfunc="count").fillna(0)
ex=sh[(sh.period=="P1")&sh.ever_booked].groupby("Facility ID").agg(booked=("Shift ID","size"),late=("any_late","sum"),ncns=("any_ncns","sum")); ex["late_rate"]=ex.late/ex.booked
fp=fp.join(ex); fp=fp[(fp.P1>=50)]; fp["growth"]=(fp.P2-fp.P1)/fp.P1
P("\nFacility churn proxy (P1>=50 shifts, n=%d): corr(P1 late_rate, growth P1->P2) = %.2f ; corr(ncns share, growth) = %.2f" % (len(fp), fp.late_rate.corr(fp.growth), (fp.ncns/fp.booked).corr(fp.growth)))
fp["lr_bin"]=pd.qcut(fp.late_rate,3,labels=["low","mid","high"]); P(fp.groupby("lr_bin",observed=True).agg(n=("P1","size"),P1=("P1","sum"),P2=("P2","sum"),med_growth=("growth","median"),shrank=("growth",lambda s:(s<-0.25).mean())).round(2).to_string())
bk.to_pickle(f"{S}/data/pseudo_bookings.pkl"); d.to_pickle(f"{S}/data/refill.pkl"); c2.to_pickle(f"{S}/data/cancels_swap.pkl"); wstats.to_pickle(f"{S}/data/worker_stats.pkl")
