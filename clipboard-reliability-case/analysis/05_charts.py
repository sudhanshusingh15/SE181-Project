import pandas as pd, numpy as np, sys, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, textwrap
from matplotlib.path import Path
from matplotlib.patches import PathPatch
S=sys.argv[1]
INK="#0b0b0b"; INK2="#52514e"; MUTED="#898781"; GRID="#e1e0d9"; BASE="#c3c2b7"; SURF="#fcfcfb"
BLUE="#2a78d6"; BLUE_L="#9ec5f4"; ORANGE="#eb6834"
plt.rcParams.update({"font.family":"Inter","font.size":9,"svg.fonttype":"path","axes.edgecolor":BASE,"axes.labelcolor":INK2,"xtick.color":MUTED,"ytick.color":MUTED,"figure.facecolor":SURF,"axes.facecolor":SURF,"savefig.facecolor":SURF})
def rbar(ax,x,h,w,color,r=None):
    """bar with rounded top corners, square at baseline (in data units; r in y units scaled)"""
    if h<=0: return
    x0,x1=x-w/2,x+w/2
    # radius: 4px-ish -> compute from axis size later; approximate with fraction of width
    rx=w*0.22; ry=rx*ax.get_ylim()[1]/ (ax.get_xlim()[1]-ax.get_xlim()[0]) * (ax.get_window_extent().width/ax.get_window_extent().height)
    ry=min(ry,h*0.6)
    verts=[(x0,0),(x0,h-ry),(x0,h),(x0+rx,h),(x1-rx,h),(x1,h),(x1,h-ry),(x1,0),(x0,0)]
    codes=[Path.MOVETO,Path.LINETO,Path.CURVE3,Path.CURVE3,Path.LINETO,Path.CURVE3,Path.CURVE3,Path.LINETO,Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts,codes),facecolor=color,edgecolor="none",linewidth=0))
def style(ax,ymax,ylab="",pct=True):
    ax.set_xlim(-0.6,None); ax.set_ylim(0,ymax)
    for s in ["top","right","left"]: ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(BASE); ax.spines["bottom"].set_linewidth(0.8)
    ax.yaxis.grid(True,color=GRID,linewidth=0.7); ax.set_axisbelow(True); ax.tick_params(axis="both",length=0,labelsize=8.5,pad=4)
    if pct: ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,_: f"{v:.0f}%"))
    ax.set_ylabel(ylab,color=INK2,fontsize=8.5)
def title(fig,t,sub):
    fig.text(0.01,0.97,t,ha="left",va="top",fontsize=11,fontweight="semibold",color=INK)
    fig.text(0.01,0.885,textwrap.fill(sub,118),ha="left",va="top",fontsize=8.5,color=INK2,linespacing=1.35)
def save(fig,name): fig.savefig(f"{S}/fig/{name}.svg"); fig.savefig(f"{S}/fig/{name}.png",dpi=200); plt.close(fig)

# F1 refill curve
rc=pd.read_csv(f"{S}/out/refill_curve.csv")
order=["NCNS/after","0-1h","1-4h","4-12h","12-24h","24-48h","48-72h","3-7d",">7d"]; rc=rc.set_index("lt_bin").loc[order]
labels=["No-show","0 to 1h","1 to 4h","4 to 12h","12 to 24h","24 to 48h","48 to 72h","3 to 7d","Over 7d"]
fig=plt.figure(figsize=(6.8,2.8)); ax=fig.add_axes([0.09,0.2,0.9,0.5]); style(ax,100,"Share of shifts left empty")
ax.set_xlim(-0.6,len(order)-0.4)
for i,(k,row) in enumerate(rc.iterrows()):
    v=100*row.unfilled_rate; rbar(ax,i,v,0.56,BLUE if i<=4 else BLUE_L)
    if i in (0,1,2,3,4,5,8): ax.text(i,v+2.5,f"{v:.0f}%",ha="center",va="bottom",fontsize=8.5,color=INK,fontweight="semibold")
ax.set_xticks(range(len(order))); ax.set_xticklabels([f"{l}\n n={int(n):,}" for l,n in zip(labels,rc.shifts)],fontsize=8)
ax.axvline(4.5,color=BASE,linewidth=0.8,linestyle=(0,(3,3))); ax.text(4.42,96,"inside 24h",ha="right",va="top",fontsize=8,color=INK2); ax.text(4.58,96,"24h or more",ha="left",va="top",fontsize=8,color=INK2)
title(fig,"Shifts canceled inside 24 hours mostly stay empty. Shifts released earlier mostly get filled.","Share of Cleveland shifts that ended with no worker, by how long before the start the last cancellation happened. Oct 2021 to Jan 2022, 6,535 shifts with a cancellation.")
save(fig,"f1_refill")

# F2 lead time histogram
lt=pd.read_csv(f"{S}/out/leadtime_hist.csv"); order2=["NCNS","0-1h","1-2h","2-4h","4-8h","8-12h","12-24h","24-48h","48-72h","3-7d","7-14d",">14d"]; lt=lt.set_index("ltb").loc[order2]
lab2=["No-show","0 to 1h","1 to 2h","2 to 4h","4 to 8h","8 to 12h","12 to 24h","24 to\n48h","48 to\n72h","3 to 7d","7 to 14d","Over 14d"]
fig=plt.figure(figsize=(6.8,3.0)); ax=fig.add_axes([0.09,0.19,0.9,0.56]); style(ax,1700,"Cancellation events",pct=False); ax.set_xlim(-0.6,len(order2)-0.4)
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,_: f"{v/1000:.1f}K" if v>=1000 else f"{v:.0f}"))
for i,(k,row) in enumerate(lt.iterrows()):
    rbar(ax,i,row.cancels,0.56,BLUE if i<=6 else BLUE_L)
    if i in (0,6,10): ax.text(i,row.cancels+40,f"{int(row.cancels):,}",ha="center",va="bottom",fontsize=8.5,color=INK,fontweight="semibold")
ax.set_xticks(range(len(order2))); ax.set_xticklabels(lab2,fontsize=8,rotation=0)
ax.axvline(6.5,color=BASE,linewidth=0.8,linestyle=(0,(3,3))); ax.text(6.42,1640,"inside 24h: 3,846 events (49%)",ha="right",va="top",fontsize=8,color=INK2); ax.text(6.58,1640,"24h or more: 3,934 (51%)",ha="left",va="top",fontsize=8,color=INK2)
title(fig,"Half of all cancellations land inside 24 hours, and a third of those are no-shows.","Cleveland cancellation events by lead time before shift start. Oct 2021 to Jan 2022, 7,780 events.")
save(fig,"f2_leadtime")

# F3 worker segments
seg=pd.read_csv(f"{S}/out/worker_segments.csv")
fig=plt.figure(figsize=(6.8,2.8)); ax=fig.add_axes([0.09,0.2,0.9,0.5]); style(ax,55,"Share of Cleveland total"); ax.set_xlim(-0.6,len(seg)-0.4)
x=np.arange(len(seg)); w=0.3
for i,row in seg.iterrows():
    rbar(ax,i-w/2-0.01,row.share_late,w,ORANGE); rbar(ax,i+w/2+0.01,row.share_verified,w,BLUE)
    if i>=3:
        ax.text(i-w/2-0.01,row.share_late+1.2,f"{row.share_late:.0f}%",ha="center",va="bottom",fontsize=8.5,color=INK,fontweight="semibold")
        ax.text(i+w/2+0.01,row.share_verified+1.2,f"{row.share_verified:.0f}%",ha="center",va="bottom",fontsize=8.5,color=INK,fontweight="semibold")
ax.set_xticks(x); ax.set_xticklabels([f"{s} late cancels\n{int(n):,} workers" for s,n in zip(seg.segment,seg.workers)],fontsize=8)
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([],[],marker="s",linestyle="none",markersize=7,markerfacecolor=ORANGE,markeredgecolor="none",label="Share of all late cancellations"),Line2D([],[],marker="s",linestyle="none",markersize=7,markerfacecolor=BLUE,markeredgecolor="none",label="Share of all worked shifts")],loc="upper left",frameon=False,fontsize=8.5,labelcolor=INK2,handletextpad=0.4,borderaxespad=0.2)
title(fig,"The people who cancel late the most are also the people who work the most.","Cleveland professionals grouped by their number of late cancellations (under 24h or no-show) over the four months. 1,058 professionals, 3,846 late cancellations, 16,400 worked (verified) shifts.")
save(fig,"f3_segments")

# F5 appendix: tenure and weekday
t=pd.read_csv(f"{S}/out/tenure.csv"); wd=pd.read_csv(f"{S}/out/by_weekday.csv").set_index("dow").loc[["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]]
fig=plt.figure(figsize=(6.8,3.0))
ax=fig.add_axes([0.09,0.18,0.39,0.5]); style(ax,22,"Late cancellation rate"); ax.set_xlim(-0.6,len(t)-0.4)
for i,row in t.iterrows():
    rbar(ax,i,100*row.late_rate,0.56,BLUE); ax.text(i,100*row.late_rate+0.6,f"{100*row.late_rate:.0f}%",ha="center",va="bottom",fontsize=8,color=INK)
ax.set_xticks(range(len(t))); ax.set_xticklabels(["<2 wk","2-4 wk","1-2 mo","2-3 mo","3-6 mo","6-12 mo",">1 yr"],fontsize=6.8); ax.set_title("By professional's tenure at shift start",fontsize=9,color=INK2,loc="left",pad=6)
ax2=fig.add_axes([0.6,0.18,0.39,0.5]); style(ax2,22,""); ax2.set_xlim(-0.6,6.6)
for i,(k,row) in enumerate(wd.iterrows()):
    rbar(ax2,i,100*row.late_rate,0.56,BLUE); ax2.text(i,100*row.late_rate+0.6,f"{100*row.late_rate:.0f}%",ha="center",va="bottom",fontsize=8,color=INK)
ax2.set_xticks(range(7)); ax2.set_xticklabels(wd.index,fontsize=8); ax2.set_title("By weekday of the shift",fontsize=9,color=INK2,loc="left",pad=6)
title(fig,"Late cancellations fall with tenure and peak on Mondays, but neither effect is large.","Late cancellations (under 24h or no-show) per booking, Cleveland, Oct 2021 to Jan 2022.")
save(fig,"f5_tenure_weekday")
print("ok")
