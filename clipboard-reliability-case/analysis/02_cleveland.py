import pandas as pd, numpy as np, sys
pd.set_option("display.width",220); pd.set_option("display.max_columns",30)
S=sys.argv[1]; P=print
sh=pd.read_pickle(f"{S}/data/shifts.pkl"); ca=pd.read_pickle(f"{S}/data/cancels.pkl")
sh["deleted"]=sh.Deleted.notna(); sh["has_worker"]=sh["Worker ID"].notna(); sh["gmv"]=sh.Charge*sh.Time
sh["post_lead_h"]=(sh.Start-sh["Created At"]).dt.total_seconds()/3600
def outcome(r):
    if r.Verified: return "worked"
    if r.deleted: return "deleted"
    if r.has_worker: return "assigned_unverified"
    return "unfilled"
sh["outcome"]=sh.apply(outcome,axis=1)
cl=ca[ca["Shift ID"].isin(sh["Shift ID"])].copy()
cl["late"]=cl["Lead Time"]<24; cl["ncns"]=cl.Action=="NO_CALL_NO_SHOW"
bins=[-np.inf,0,4,24,72,168,np.inf]; labels=["NCNS/after start","0-4h","4-24h","24-72h","72h-7d",">7d"]
cl["lt_bin"]=pd.cut(cl["Lead Time"],bins=bins,labels=labels,right=False)
P("### CLEVELAND CANCELS:", len(cl), "rows | shifts touched:", cl["Shift ID"].nunique(), "| workers:", cl["Worker ID"].nunique(), "| facilities:", cl["Facility ID"].nunique())
P(pd.crosstab(cl.lt_bin, cl.Action, margins=True).to_string())
P("Share of cancel rows that are late (<24h incl NCNS): %.1f%% | NCNS share of all cancels: %.1f%% | NCNS share of late: %.1f%%" % (100*cl.late.mean(), 100*cl.ncns.mean(), 100*cl[cl.late].ncns.mean()))
# shift-level
g=cl.groupby("Shift ID").agg(n_cancel=("Action","size"), any_late=("late","max"), any_ncns=("ncns","max"), min_lt=("Lead Time","min"), last_cancel=("Created At","max"))
sh=sh.merge(g, left_on="Shift ID", right_index=True, how="left"); sh["n_cancel"]=sh.n_cancel.fillna(0).astype(int); sh["any_late"]=sh.any_late.fillna(False).astype(bool); sh["any_ncns"]=sh.any_ncns.fillna(False).astype(bool)
sh["ever_booked"]=sh.has_worker|(sh.n_cancel>0)
P("\n### SHIFT LEVEL (n=%d). ever booked (has worker or had cancel): %d (%.1f%%)" % (len(sh), sh.ever_booked.sum(), 100*sh.ever_booked.mean()))
P("Shifts with >=1 cancel: %d (%.1f%% of all, %.1f%% of ever-booked)" % ((sh.n_cancel>0).sum(), 100*(sh.n_cancel>0).mean(), 100*(sh.n_cancel>0).sum()/sh.ever_booked.sum()))
P("Shifts with late cancel: %d (%.1f%% of ever-booked) | with NCNS: %d (%.1f%% of ever-booked)" % (sh.any_late.sum(), 100*sh.any_late.sum()/sh.ever_booked.sum(), sh.any_ncns.sum(), 100*sh.any_ncns.sum()/sh.ever_booked.sum()))
P("Outcome overall:\n", sh.outcome.value_counts().to_string())
P("Outcome x had cancel:\n", pd.crosstab(sh.outcome, sh.n_cancel.clip(upper=2), margins=True).to_string())
P("Outcome for shifts with LATE cancel:\n", sh[sh.any_late].outcome.value_counts().to_string())
P("Outcome for shifts with NCNS:\n", sh[sh.any_ncns].outcome.value_counts().to_string())
P("Outcome for shifts with only early cancels (>=24h):\n", sh[(sh.n_cancel>0)&(~sh.any_late)].outcome.value_counts().to_string())
P("Outcome for shifts with no cancel at all:\n", sh[sh.n_cancel==0].outcome.value_counts().to_string())
# economics
late_sh=sh[sh.any_late]
P("\n### ECONOMICS (Charge*Time). Avg GMV/shift all: %.0f | late-cancel shifts: %.0f" % (sh.gmv.mean(), late_sh.gmv.mean()))
lost=late_sh[late_sh.outcome!="worked"]; P("Late-cancel shifts NOT worked: %d, GMV %.0f (4 months) -> take 22%%: %.0f; annualized rev: %.0f" % (len(lost), lost.gmv.sum(), lost.gmv.sum()*.22, lost.gmv.sum()*.22*3))
worked_all=sh[sh.outcome=="worked"]; P("Worked GMV total (4mo): %.0f ; verified shifts %d" % (worked_all.gmv.sum(), len(worked_all)))
P("Monthly: shifts, worked, late-cancel shifts, ncns shifts, late rate per booked:")
m=sh.groupby(sh.Start.dt.to_period("M")).agg(shifts=("Shift ID","size"), booked=("ever_booked","sum"), worked=("Verified","sum"), late=("any_late","sum"), ncns=("any_ncns","sum"), unfilled=("outcome", lambda s:(s=="unfilled").sum()), deleted=("deleted","sum"))
m["late_rate_booked"]=(m.late/m.booked).round(3); m["ncns_rate_booked"]=(m.ncns/m.booked).round(3); m["fill_rate"]=(m.worked/m.shifts).round(3); P(m.to_string())
# patterns
def rate_by(col, df=sh):
    d=df[df.ever_booked].groupby(col).agg(booked=("Shift ID","size"), late=("any_late","sum"), ncns=("any_ncns","sum"), worked=("Verified","sum"))
    d["late_rate"]=(d.late/d.booked).round(3); d["ncns_rate"]=(d.ncns/d.booked).round(3); return d
P("\nBy Shift Type:\n", rate_by("Shift Type").to_string())
P("By Agent Req:\n", rate_by("Agent Req").to_string())
sh["dow"]=sh.Start.dt.dayofweek; P("By weekday (0=Mon):\n", rate_by("dow").to_string())
sh["charge_q"]=pd.qcut(sh.Charge.where(sh.Charge>0), 4, duplicates="drop"); P("By charge quartile (within booked, charge>0):\n", rate_by("charge_q").to_string())
sh["post_lead_bin"]=pd.cut(sh.post_lead_h,[-np.inf,24,72,168,336,np.inf],labels=["<1d","1-3d","3-7d","7-14d",">14d"]); P("By posting lead (Created->Start):\n", rate_by("post_lead_bin").to_string())
sh["dur_bin"]=pd.cut(sh.Time,[-np.inf,6,8.5,12.5,np.inf],labels=["<6h","6-8.5h","8.5-12.5h",">12.5h"]); P("By duration:\n", rate_by("dur_bin").to_string())
# facility concentration
f=sh[sh.ever_booked].groupby("Facility ID").agg(booked=("Shift ID","size"), late=("any_late","sum"), ncns=("any_ncns","sum")); f["late_rate"]=(f.late/f.booked).round(3); f=f.sort_values("booked",ascending=False)
P("\nFacilities (booked>=100) late rate spread: min %.3f p25 %.3f median %.3f p75 %.3f max %.3f" % tuple(f[f.booked>=100].late_rate.quantile([0,.25,.5,.75,1]).values)); P(f.head(12).to_string())
# worker concentration in cleveland
w=cl.groupby("Worker ID").agg(cancels=("Action","size"), late=("late","sum"), ncns=("ncns","sum")).sort_values("late",ascending=False)
wk=sh[sh.Verified].groupby("Worker ID").size().rename("worked")
w=w.join(wk, how="outer").fillna(0)
P("\n### WORKERS (Cleveland): with any cancel %d | with late cancel %d | with NCNS %d | workers who worked %d | total distinct %d" % ((w.cancels>0).sum(), (w.late>0).sum(), (w.ncns>0).sum(), (w.worked>0).sum(), len(w)))
wl=w[w.late>0].sort_values("late",ascending=False); tot=wl.late.sum()
for k in [1,2,3,5,10]: P("  workers with >=%d late cancels: %d (%.1f%% of late-cancelers) -> %.1f%% of late cancels" % (k,(wl.late>=k).sum(),100*(wl.late>=k).mean(),100*wl[wl.late>=k].late.sum()/tot))
P("  top 10%% of late-cancelers share: %.1f%%" % (100*wl.head(int(len(wl)*.1)).late.sum()/tot))
P("  distribution late per worker:\n", wl.late.astype(int).value_counts().sort_index().to_string())
w["late_per_worked"]=w.late/(w.worked+w.late); P("Workers with >=5 worked+late: late share quantiles:\n", w[(w.worked+w.late)>=5].late_per_worked.quantile([.1,.25,.5,.75,.9]).round(3).to_string())
# repeat sequence: nth late cancel per worker (cleveland)
cls=cl[cl.late].sort_values("Created At"); cls["nth"]=cls.groupby("Worker ID").cumcount()+1
P("Late cancels by worker's nth late cancel (Cleveland):\n", cls.nth.clip(upper=6).value_counts().sort_index().to_string())
# NCNS logging delay
P("\nNCNS Lead Time (hours, negative=after start) quantiles:\n", cl[cl.ncns]["Lead Time"].quantile([.1,.25,.5,.75,.9]).round(1).to_string())
# late worker cancels: hours before start distribution
lw=cl[(cl.Action=="WORKER_CANCEL")&(cl["Lead Time"]<24)]; P("WORKER_CANCEL <24h: lead time quantiles:\n", lw["Lead Time"].quantile([.1,.25,.5,.75,.9]).round(2).to_string())
P("  <1h: %d, 1-2h: %d, 2-4h: %d, 4-8h: %d, 8-12h: %d, 12-24h: %d" % tuple(((lw["Lead Time"]>=a)&(lw["Lead Time"]<b)).sum() for a,b in [(0,1),(1,2),(2,4),(4,8),(8,12),(12,24)]))
# cancel chains
P("\nCancels per shift (Cleveland):\n", sh[sh.n_cancel>0].n_cancel.value_counts().sort_index().to_string())
# refilled after late cancel: worked & final worker != canceling worker
lastc=cl.sort_values("Created At").groupby("Shift ID")["Worker ID"].last().rename("last_cancel_worker")
sh=sh.merge(lastc,left_on="Shift ID",right_index=True,how="left")
rf=sh[sh.any_late&sh.Verified]; P("Late-cancel shifts that were worked: %d; of which final worker differs from last canceler: %d" % (len(rf),(rf["Worker ID"]!=rf.last_cancel_worker).sum()))
sh.to_pickle(f"{S}/data/shifts_enriched.pkl"); cl.to_pickle(f"{S}/data/cancels_cleveland.pkl")
