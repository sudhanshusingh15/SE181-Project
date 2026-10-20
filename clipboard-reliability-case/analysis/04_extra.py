import pandas as pd, numpy as np, sys, json
pd.set_option("display.width",220); pd.set_option("display.max_columns",30)
S=sys.argv[1]; P=print
sh=pd.read_pickle(f"{S}/data/shifts_enriched.pkl"); cl=pd.read_pickle(f"{S}/data/cancels_cleveland.pkl"); bk=pd.read_pickle(f"{S}/data/pseudo_bookings.pkl"); d=pd.read_pickle(f"{S}/data/refill.pkl"); ws=pd.read_pickle(f"{S}/data/worker_stats.pkl"); ca=pd.read_pickle(f"{S}/data/cancels.pkl")
# (a) disengagement: did worker work again after NCNS / late cancel (within window)?
worked=sh[sh.Verified][["Worker ID","Start"]]
lastw=worked.groupby("Worker ID").Start.max().rename("last_worked")
for name,sub in [("NCNS",cl[cl.ncns]),("late WORKER_CANCEL",cl[cl.late&~cl.ncns]),("early cancel",cl[~cl.late])]:
    x=sub.merge(lastw,left_on="Worker ID",right_index=True,how="left")
    never_again=(x.last_worked.isna())|(x.last_worked<=x.Start)
    # exclude events in last 14 days of window (right-censoring)
    y=x[x.Start<"2022-01-17"]; na2=(y.last_worked.isna())|(y.last_worked<=y.Start)
    P("%-18s n=%d | worker never worked a Cleveland shift after this event: %.1f%% (excl. last 2 weeks: %.1f%%)" % (name,len(x),100*never_again.mean(),100*na2.mean()))
# first event?
firstw=worked.groupby("Worker ID").Start.min().rename("first_worked")
x=cl[cl.ncns].merge(firstw,left_on="Worker ID",right_index=True,how="left"); P("NCNS where worker had never worked a Cleveland shift before: %.1f%%" % (100*((x.first_worked.isna())|(x.first_worked>=x.Start)).mean()))
# (e) posting lead
sh["post_lead_d"]=(sh.Start-sh["Created At"]).dt.total_seconds()/86400; P("\nPosting lead (days) quantiles:", sh.post_lead_d.quantile([.1,.25,.5,.75,.9]).round(1).to_dict())
# (f) facility late rate persistence P1 vs P2
bk["period"]=np.where(bk.Start<"2021-12-01","P1","P2")
fp=bk.pivot_table(index="Facility ID",columns="period",values="late",aggfunc=["sum","size"])
fp.columns=["late_P1","late_P2","n_P1","n_P2"]; fp=fp[(fp.n_P1>=50)&(fp.n_P2>=50)]; fp["r1"]=fp.late_P1/fp.n_P1; fp["r2"]=fp.late_P2/fp.n_P2
P("Facility late-rate persistence (n=%d facilities with >=50 bookings each period): corr(P1,P2)=%.2f" % (len(fp), fp.r1.corr(fp.r2)))
# worker persistence P1 vs P2
wp=bk.pivot_table(index="Worker ID",columns="period",values="late",aggfunc=["sum","size"]); wp.columns=["l1","l2","n1","n2"]; wp=wp[(wp.n1>=10)&(wp.n2>=10)]; wp["r1"]=wp.l1/wp.n1; wp["r2"]=wp.l2/wp.n2
P("Worker late-rate persistence (n=%d workers with >=10 bookings each period): corr(P1,P2)=%.2f ; top-quartile P1 workers' P2 rate %.3f vs bottom-quartile %.3f" % (len(wp), wp.r1.corr(wp.r2), wp[wp.r1>=wp.r1.quantile(.75)].r2.mean(), wp[wp.r1<=wp.r1.quantile(.25)].r2.mean()))
# (i) per facility per month disruptions
n_fac_active=sh[sh.ever_booked].groupby(sh.Start.dt.to_period("M"))["Facility ID"].nunique(); late_m=sh.groupby(sh.Start.dt.to_period("M")).any_late.sum(); P("\nActive facilities/month:", n_fac_active.to_dict()); P("Late-disrupted shifts per active facility per month:", (late_m/n_fac_active).round(1).to_dict())
P("Shifts per active facility per month:", (sh[sh.ever_booked].groupby(sh.Start.dt.to_period("M")).size()/n_fac_active).round(1).to_dict())
# (k) cumulative lead-time distribution of worker cancels within 0-72h
lw=cl[(cl.Action=="WORKER_CANCEL")]
for h in [1,2,4,8,12,24,48,72]: P("  WORKER_CANCEL with lead < %dh: %d (%.1f%% of all worker cancels)" % (h,(lw["Lead Time"]<h).sum(),100*(lw["Lead Time"]<h).mean()))
# marketplace-wide check of the same shares
mw=ca[ca.Action=="WORKER_CANCEL"]; P("Marketplace-wide: share of worker cancels <24h: %.1f%% | <4h: %.1f%% | NCNS share of all cancel events: %.1f%%" % (100*(mw["Lead Time"]<24).mean(),100*(mw["Lead Time"]<4).mean(),100*(ca.Action=="NO_CALL_NO_SHOW").mean()))
P("Cleveland: share of worker cancels <24h: %.1f%% | <4h: %.1f%% | NCNS share: %.1f%%" % (100*(lw["Lead Time"]<24).mean(),100*(lw["Lead Time"]<4).mean(),100*cl.ncns.mean()))
# economics excluding NURSE $0 rows
real=sh[(sh["Agent Req"]!="NURSE")&(sh.Charge>0)]
late_sh=real[real.any_late]; lost=late_sh[late_sh.outcome!="worked"]
P("\nECON excl NURSE/$0: late-disrupted shifts %d | not worked %d (%.1f%%) | GMV lost 4mo $%.0f | annualized GMV $%.0f | revenue @22%% $%.0f/yr | avg GMV/shift $%.0f" % (len(late_sh),len(lost),100*len(lost)/len(late_sh),lost.gmv.sum(),lost.gmv.sum()*3,lost.gmv.sum()*3*.22,real.gmv.mean()))
P("Worked GMV 4mo $%.0f (%d shifts) -> annualized $%.0f" % (real[real.Verified].gmv.sum(), real.Verified.sum(), real[real.Verified].gmv.sum()*3))
# unfilled & deleted among late-disrupted by bucket for appendix (already in refill curve)
# segment table for appendix
seg=[]
for lo,hi,name in [(0,0,"0"),(1,2,"1-2"),(3,4,"3-4"),(5,9,"5-9"),(10,999,"10+")]:
    s=ws[(ws.late>=lo)&(ws.late<=hi)]; seg.append(dict(segment=name,workers=len(s),bookings=int(s.bookings.sum()),worked=int(s.worked.sum()),late=int(s.late.sum()),share_late=round(100*s.late.sum()/ws.late.sum(),1),share_worked=round(100*s.worked.sum()/ws.worked.sum(),1),late_rate=round(100*s.late.sum()/max(s.bookings.sum(),1),1)))
seg=pd.DataFrame(seg); seg.to_csv(f"{S}/out/worker_segments.csv",index=False); P("\n",seg.to_string(index=False))
# refill curve export
rc=d.groupby("lt_bin",observed=True).agg(shifts=("Shift ID","size"),refilled=("refilled","sum"),worked=("Verified","sum"),unfilled=("outcome",lambda s:(s=="unfilled").sum()),deleted=("deleted","sum")); rc["refill_rate"]=rc.refilled/rc.shifts; rc["unfilled_rate"]=rc.unfilled/rc.shifts; rc.to_csv(f"{S}/out/refill_curve.csv")
# monthly export
m=sh.groupby(sh.Start.dt.to_period("M")).agg(shifts=("Shift ID","size"),booked=("ever_booked","sum"),worked=("Verified","sum"),late=("any_late","sum"),ncns=("any_ncns","sum"),unfilled=("outcome",lambda s:(s=="unfilled").sum()),deleted=("deleted","sum")); m.to_csv(f"{S}/out/monthly.csv")
# lead time histogram export (Cleveland cancels)
bins=[-np.inf,0,1,2,4,8,12,24,48,72,168,336,np.inf]; labels=["NCNS","0-1h","1-2h","2-4h","4-8h","8-12h","12-24h","24-48h","48-72h","3-7d","7-14d",">14d"]
cl["ltb"]=pd.cut(cl["Lead Time"],bins,labels=labels,right=False); cl.loc[cl.ncns,"ltb"]="NCNS"
lt=cl.groupby("ltb",observed=True).size().rename("cancels"); lt.to_csv(f"{S}/out/leadtime_hist.csv"); P("\n",lt.to_string())
# tenure export
bk["tenure_d"]=(bk.Start-bk.worker_created).dt.days; bk["tenure_bin"]=pd.cut(bk.tenure_d,[-np.inf,14,30,60,90,180,365,np.inf],labels=["<2w","2-4w","1-2mo","2-3mo","3-6mo","6-12mo",">1y"])
t=bk.groupby("tenure_bin",observed=True).agg(bookings=("Shift ID","size"),late=("late","sum"),ncns=("ncns","sum")); t["late_rate"]=t.late/t.bookings; t.to_csv(f"{S}/out/tenure.csv")
# by weekday / shift type / role exports
sh["dow"]=sh.Start.dt.day_name().str[:3]
for col,fn in [("dow","weekday"),("Shift Type","shifttype"),("Agent Req","role")]:
    g=sh[sh.ever_booked].groupby(col).agg(booked=("Shift ID","size"),late=("any_late","sum"),ncns=("any_ncns","sum"),worked=("Verified","sum")); g["late_rate"]=g.late/g.booked; g["ncns_rate"]=g.ncns/g.booked; g.to_csv(f"{S}/out/by_{fn}.csv")
# policy sim export
pd.DataFrame([dict(rule="2 late in 30d -> 7d suspension",suspensions=1147,late_avoided=1085,late_avoided_pct=28,worked_lost=3355,worked_lost_pct=16.0),dict(rule="3 late in 30d -> 7d suspension",suspensions=679,late_avoided=757,late_avoided_pct=20,worked_lost=2084,worked_lost_pct=9.9)]).to_csv(f"{S}/out/policy_sim.csv",index=False)
# headline numbers json
H=dict(shifts=int(len(sh)),facilities=int(sh["Facility ID"].nunique()),workers=int(bk["Worker ID"].nunique()),bookings=int(len(bk)),cancels=int(len(cl)),late_events=int(cl.late.sum()),ncns_events=int(cl.ncns.sum()),late_rate=round(100*bk.late.mean(),1),ncns_rate=round(100*bk.ncns.mean(),1),cancel_rate=round(100*bk.canceled.mean(),1),late_shifts=int(sh.any_late.sum()),late_shifts_unfilled=int(((sh.any_late)&(sh.outcome=="unfilled")).sum()),late_shifts_deleted=int(((sh.any_late)&(sh.deleted)).sum()),late_shifts_worked=int(((sh.any_late)&(sh.Verified)).sum()),worked=int(sh.Verified.sum()),unfilled=int((sh.outcome=="unfilled").sum()),deleted=int(sh.deleted.sum()))
json.dump(H,open(f"{S}/out/headline.json","w"),indent=1); P("\n",H)
