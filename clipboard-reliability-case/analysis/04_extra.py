"""Extra cuts, sensitivity checks and every table the write-up's appendix uses. Run after 03."""
import pandas as pd, numpy as np, sys, json
pd.set_option("display.width",220); pd.set_option("display.max_columns",30)
S=sys.argv[1]; O=f"{S}/out"; P=print
sh=pd.read_pickle(f"{S}/data/shifts_enriched.pkl"); cl=pd.read_pickle(f"{S}/data/cancels_cleveland.pkl"); bk=pd.read_pickle(f"{S}/data/pseudo_bookings.pkl"); d=pd.read_pickle(f"{S}/data/refill.pkl"); ws=pd.read_pickle(f"{S}/data/worker_stats.pkl"); ca=pd.read_pickle(f"{S}/data/cancels.pkl")
TZ="America/New_York"; loc=lambda s: s.dt.tz_localize("UTC").dt.tz_convert(TZ)
N_VER=int(sh.Verified.sum()); N_BOOK=len(bk); N_LATE=int(cl.late.sum())
# ---- (a) what happens to a professional after a no-show / late cancel
worked=sh[sh.Verified][["Worker ID","Start"]]; lastw=worked.groupby("Worker ID").Start.max().rename("last_worked")
ev=bk.assign(t=pd.to_datetime(np.where(bk.canceled, bk.cancel_at, bk.Start)))[["Worker ID","t"]].sort_values("t"); grp={w:g.t.values for w,g in ev.groupby("Worker ID")}
def later_events(row):
    """Events by the same professional strictly after this shift's start, excluding this event's own record."""
    arr=grp.get(row["Worker ID"])
    if arr is None: return 0
    n=len(arr)-np.searchsorted(arr, np.datetime64(row.Start), side="right")
    return n-(1 if row["Created At"]>row.Start else 0)
P("### AFTER THE EVENT (Cleveland; 'excl. last 2 weeks' drops events starting after Jan 17 to limit right-censoring)")
for name,sub in [("NCNS",cl[cl.ncns]),("late WORKER_CANCEL",cl[cl.late&~cl.ncns]),("early cancel",cl[~cl.late])]:
    x=sub.merge(lastw,left_on="Worker ID",right_index=True,how="left"); x["later"]=x.apply(later_events,axis=1)
    nw=(x.last_worked.isna())|(x.last_worked<=x.Start); ne=(x.later<=0)
    y=x[x.Start<"2022-01-17"]; nw2=(y.last_worked.isna())|(y.last_worked<=y.Start); ne2=(y.later<=0)
    P("%-18s n=%d | no verified shift afterwards: %.1f%% (excl. last 2 weeks %.1f%%) | no event of any kind afterwards: %.1f%% (excl. %.1f%%)" % (name,len(x),100*nw.mean(),100*nw2.mean(),100*ne.mean(),100*ne2.mean()))
# ---- (b) refill among ALL late-disrupted shifts (the metric's definition)
late_sh=sh[sh.any_late]; lastc=cl.sort_values("Created At").groupby("Shift ID")["Worker ID"].last()
refilled=(late_sh.Verified&(late_sh["Worker ID"]!=late_sh["Shift ID"].map(lastc))).sum()
P("\nLate-disrupted shifts %d | worked %d (%.1f%%) | refilled by a different professional %d (%.1f%%)" % (len(late_sh),late_sh.Verified.sum(),100*late_sh.Verified.mean(),refilled,100*refilled/len(late_sh)))
# ---- (c) impact model on a SHIFT basis, using outcome rates by lead time of the last cancellation
d["cat"]=np.select([d.last_action=="NO_CALL_NO_SHOW", d.last_lt<4, d.last_lt<24, d.last_lt<30, d.last_lt<48],["NCNS","0-4h","4-24h","24-30h","30-48h"],"other")
rates=d.groupby("cat").agg(shifts=("Shift ID","size"),empty=("outcome",lambda s:(s=="unfilled").mean()),worked=("Verified","mean"),deleted=("deleted","mean"))
cf=d[(d.last_lt>=24)&(d.last_lt<48)]; cf_empty=(cf.outcome=="unfilled").mean(); cf_worked=cf.Verified.mean(); cf_deleted=cf.deleted.mean()
P("\n### OUTCOME RATES by last-cancel bucket (shift basis):\n", rates.round(3).to_string()); P("counterfactual 24-48h: n=%d empty %.3f worked %.3f deleted %.3f" % (len(cf),cf_empty,cf_worked,cf_deleted))
assume={"4-24h":0.35,"NCNS":0.25,"0-4h":0.10}; events={"4-24h":int(((cl["Lead Time"]>=4)&(cl["Lead Time"]<24)&~cl.ncns).sum()),"NCNS":int(cl.ncns.sum()),"0-4h":int(((cl["Lead Time"]<4)&~cl.ncns).sum())}
rows=[]
for b,a in assume.items():
    r=rates.loc[b]; moved=a*r["shifts"]
    rows.append(dict(bucket=b,late_events=events[b],shifts=int(r["shifts"]),assumed_share_moved=a,shifts_moved=moved,empty_rate=r["empty"],worked_rate=r["worked"],saved_empty=moved*(r["empty"]-cf_empty),gained_worked=moved*(cf_worked-r["worked"]),saved_empty_cf24to30=moved*(r["empty"]-rates.loc["24-30h","empty"])))
im=pd.DataFrame(rows); im.to_csv(f"{O}/impact_model.csv",index=False)
tot_ev=sum(a*events[b] for b,a in assume.items()); saved=im.saved_empty.sum(); gained=im.gained_worked.sum(); saved_alt=im.saved_empty_cf24to30.sum()
avg_gmv=sh[sh.any_late&(sh.outcome!="worked")&(sh.Charge>0)].gmv.mean()
P("\n### IMPACT MODEL\n", im.round(3).to_string(index=False))
P("events moved %.0f of %d (%.1f%%) -> late rate %.1f -> %.1f per 100 bookings" % (tot_ev,N_LATE,100*tot_ev/N_LATE,100*N_LATE/N_BOOK,100*(N_LATE-tot_ev)/N_BOOK))
P("shifts moved %.0f | empty shifts avoided per 4mo %.0f (x3 = %.0f/yr) | worked shifts gained %.0f (x3 = %.0f/yr) | with 24-30h counterfactual: %.0f avoided" % (im.shifts_moved.sum(),saved,saved*3,gained,gained*3,saved_alt))
P("avg GMV of a lost late shift $%.0f -> gained worked billings/yr $%.0f, revenue @22%% $%.0f ; x10 markets $%.0f / $%.0f" % (avg_gmv,gained*3*avg_gmv,gained*3*avg_gmv*.22,gained*3*avg_gmv*10,gained*3*avg_gmv*.22*10))
P("half the assumed conversion: empty avoided %.0f per 4mo" % (saved/2))
P("break-even accidental release rate (share of would-be-worked bookings released and not taken back): %.1f%% ; cost at 1%%: %.0f empty shifts per 4mo" % (100*saved/(N_VER*cf_empty), 0.01*N_VER*cf_empty))
P("booked-then-empty after plan: (%d - %.0f)/%d = %.1f%%" % (2744,saved,24566,100*(2744-saved)/24566))
# ---- (d) pilot power with clustering by professional (last 8 weeks of the window as the volume reference)
w8=bk[bk.Start>=bk.Start.max()-pd.Timedelta(weeks=8)]
g=w8.groupby("Worker ID").late.agg(["mean","size"]); g=g[g["size"]>=2]
# one-way ANOVA ICC
k=len(g); n_i=g["size"].values; N=n_i.sum(); grand=w8[w8["Worker ID"].isin(g.index)].late.mean()
ssb=(n_i*(g["mean"].values-grand)**2).sum(); sub=w8[w8["Worker ID"].isin(g.index)]; ssw=((sub.late-sub["Worker ID"].map(g["mean"]))**2).sum()
msb=ssb/(k-1); msw=ssw/(N-k); n0=(N-(n_i**2).sum()/N)/(k-1); icc=max((msb-msw)/(msb+(n0-1)*msw),0); deff=1+(N/k-1)*icc
from math import sqrt, erf
Phi=lambda z:0.5*(1+erf(z/sqrt(2)))
p0=N_LATE/N_BOOK; per_arm=len(w8)/2; neff=per_arm/deff
P("\n### PILOT POWER: last 8 weeks bookings %d (%.0f per arm), ICC %.3f, mean bookings/professional %.1f, design effect %.2f, effective n per arm %.0f" % (len(w8),per_arm,icc,N/k,deff,neff))
for cut in [.15,.20,.25]:
    se=sqrt(2*p0*(1-p0)/neff); z=p0*cut/se; P("  %.0f%% relative cut: power %.0f%% (two-sided 5%%)" % (100*cut,100*Phi(z-1.96)))
# ---- (e) NURSE / $0 sensitivity
nurse=sh[sh["Agent Req"]=="NURSE"]; zero=sh[sh.Charge<=0]
bk_n=bk[bk["Agent Req"]!="NURSE"]
P("\n### NURSE rows: %d shifts, charge==0 %.0f%%, assigned %d, verified %d, late events %d, NCNS %d" % (len(nurse),100*(nurse.Charge==0).mean(),nurse.has_worker.sum(),nurse.Verified.sum(),bk[bk["Agent Req"]=="NURSE"].late.sum(),bk[bk["Agent Req"]=="NURSE"].ncns.sum()))
P("Excluding NURSE: bookings %d, late %d, late rate %.1f per 100 (vs %.1f)" % (len(bk_n),bk_n.late.sum(),100*bk_n.late.mean(),100*bk.late.mean()))
P("$0 charge rows total %d; non-NURSE $0 rows %d of which deleted %d, verified %d" % (len(zero),len(zero[zero["Agent Req"]!="NURSE"]),zero[zero["Agent Req"]!="NURSE"].deleted.sum(),zero[zero["Agent Req"]!="NURSE"].Verified.sum()))
# ---- (f) monthly: shift level and event level
m=sh.groupby(sh.Start.dt.to_period("M")).agg(shifts=("Shift ID","size"),booked=("ever_booked","sum"),worked=("Verified","sum"),late=("any_late","sum"),ncns=("any_ncns","sum"),unfilled=("outcome",lambda s:(s=="unfilled").sum()),deleted=("deleted","sum"))
mb=bk.groupby(bk.Start.dt.to_period("M")).agg(bookings=("Shift ID","size"),late_events=("late","sum"),ncns_events=("ncns","sum"))
m=m.join(mb); m["late_per100"]=100*m.late_events/m.bookings; m.to_csv(f"{O}/monthly.csv"); P("\n### MONTHLY\n", m.round(1).to_string())
# ---- (g) cuts: weekday in local time, shift type, role, tenure
sh["dow"]=loc(sh.Start).dt.day_name().str[:3]
for col,fn in [("dow","weekday"),("Shift Type","shifttype"),("Agent Req","role")]:
    g2=sh[sh.ever_booked].groupby(col).agg(booked=("Shift ID","size"),late=("any_late","sum"),ncns=("any_ncns","sum"),worked=("Verified","sum")); g2["late_rate"]=g2.late/g2.booked; g2["ncns_rate"]=g2.ncns/g2.booked; g2.to_csv(f"{O}/by_{fn}.csv")
    if col=="dow": P("\nLate rate by weekday (local):\n", g2.loc[["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]].round(3).to_string())
bk["tenure_d"]=(bk.Start-bk.worker_created).dt.days; bk["tenure_bin"]=pd.cut(bk.tenure_d,[-np.inf,14,30,60,90,180,365,np.inf],labels=["<2w","2-4w","1-2mo","2-3mo","3-6mo","6-12mo",">1y"])
t=bk.groupby("tenure_bin",observed=True).agg(bookings=("Shift ID","size"),late=("late","sum"),ncns=("ncns","sum")); t["late_rate"]=t.late/t.bookings; t.to_csv(f"{O}/tenure.csv")
# ---- (h) worker segments (shares of verified shifts, denominator = all verified shifts)
ver=sh[sh.Verified].groupby("Worker ID").size().rename("verified"); ws=ws.join(ver,how="left").fillna({"verified":0})
seg=[]
for lo,hi,name in [(0,0,"0"),(1,2,"1-2"),(3,4,"3-4"),(5,9,"5-9"),(10,999,"10+")]:
    s_=ws[(ws.late>=lo)&(ws.late<=hi)]; seg.append(dict(segment=name,workers=len(s_),bookings=int(s_.bookings.sum()),verified=int(s_.verified.sum()),late=int(s_.late.sum()),share_late=round(100*s_.late.sum()/ws.late.sum(),1),share_verified=round(100*s_.verified.sum()/N_VER,1),late_rate=round(100*s_.late.sum()/max(s_.bookings.sum(),1),1)))
seg=pd.DataFrame(seg); seg.to_csv(f"{O}/worker_segments.csv",index=False); P("\n### SEGMENTS\n", seg.to_string(index=False)); P("5+ late: share of verified %.1f%%, share of late %.1f%%" % (seg[seg.segment.isin(["5-9","10+"])].share_verified.sum(), seg[seg.segment.isin(["5-9","10+"])].share_late.sum()))
# ---- (i) refill curve and lead-time histogram exports
rc=d.groupby("lt_bin",observed=True).agg(shifts=("Shift ID","size"),refilled=("refilled","sum"),worked=("Verified","sum"),unfilled=("outcome",lambda s:(s=="unfilled").sum()),deleted=("deleted","sum")); rc["refill_rate"]=rc.refilled/rc.shifts; rc["unfilled_rate"]=rc.unfilled/rc.shifts; rc["worked_rate"]=rc.worked/rc.shifts; rc["deleted_rate"]=rc.deleted/rc.shifts; rc.to_csv(f"{O}/refill_curve.csv")
bins=[-np.inf,0,1,2,4,8,12,24,48,72,168,336,np.inf]; labels=["NCNS","0-1h","1-2h","2-4h","4-8h","8-12h","12-24h","24-48h","48-72h","3-7d","7-14d",">14d"]
cl["ltb"]=pd.cut(cl["Lead Time"],bins,labels=labels,right=False); cl.loc[cl.ncns,"ltb"]="NCNS"; cl.groupby("ltb",observed=True).size().rename("cancels").to_csv(f"{O}/leadtime_hist.csv")
# ---- (j) misc facts quoted in the text
lw=cl[(cl.Action=="WORKER_CANCEL")&(cl["Lead Time"]<24)]
P("\nMedian lead time: late WORKER_CANCEL %.2f h | all late events incl NCNS %.2f h" % (lw["Lead Time"].median(), cl[cl.late]["Lead Time"].median()))
P("Late WORKER_CANCEL by local hour (top 6):", loc(lw["Created At"]).dt.hour.value_counts().head(6).to_dict())
P("Posting lead median %.1f days | late events inside 4h incl NCNS: %.1f%%" % (((sh.Start-sh["Created At"]).dt.total_seconds()/86400).median(), 100*((cl.late)&(cl["Lead Time"]<4)).sum()/N_LATE))
mw=ca[ca.Action=="WORKER_CANCEL"]; P("Marketplace: worker cancels <24h %.1f%%, NCNS share of events %.1f%% | Cleveland %.1f%% / %.1f%%" % (100*(mw["Lead Time"]<24).mean(),100*(ca.Action=="NO_CALL_NO_SHOW").mean(),100*(cl[cl.Action=="WORKER_CANCEL"]["Lead Time"]<24).mean(),100*cl.ncns.mean()))
mism=cl.merge(sh[["Shift ID","Start"]].rename(columns={"Start":"sh_start"}),on="Shift ID"); P("Cancel rows whose Start differs from shift log: %d" % ((mism.Start!=mism.sh_start).sum()))
H=dict(shifts=int(len(sh)),facilities=int(sh["Facility ID"].nunique()),workers=int(bk["Worker ID"].nunique()),bookings=N_BOOK,cancels=int(len(cl)),late_events=N_LATE,ncns_events=int(cl.ncns.sum()),late_per100=round(100*N_LATE/N_BOOK,1),ncns_per100=round(100*cl.ncns.mean()*len(cl)/N_BOOK,1),late_shifts=int(sh.any_late.sum()),late_shifts_unfilled=int(((sh.any_late)&(sh.outcome=="unfilled")).sum()),late_shifts_deleted=int(((sh.any_late)&(sh.deleted)).sum()),late_shifts_worked=int(((sh.any_late)&(sh.Verified)).sum()),worked=N_VER,unfilled=int((sh.outcome=="unfilled").sum()),deleted=int(sh.deleted.sum()),refill_rate_late_shifts=round(100*refilled/len(late_sh),1),empty_avoided_4mo=round(saved),worked_gained_4mo=round(gained))
json.dump(H,open(f"{O}/headline.json","w"),indent=1); P("\n",H)
