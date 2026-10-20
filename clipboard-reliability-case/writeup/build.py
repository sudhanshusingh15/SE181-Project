import pandas as pd, numpy as np, sys, re, html
S=sys.argv[1]; O=f"{S}/out"
def table(df, cols, fmt=None, hdr=None):
    fmt=fmt or {}; hdr=hdr or {}
    out=["<table>","<thead><tr>"+"".join(f'<th class="{ "n" if c in fmt else "" }">{html.escape(hdr.get(c,c))}</th>' for c in cols)+"</tr></thead>"]
    for _,r in df.iterrows():
        cells=[]
        for c in cols:
            v=r[c]
            if c in fmt: cells.append(f'<td class="n">{fmt[c](v)}</td>')
            else: cells.append(f'<td>{html.escape(str(v))}</td>')
        out.append("<tr>"+"".join(cells)+"</tr>")
    out.append("</table>"); return "\n".join(out)
I=lambda v: f"{int(round(v)):,}"; P=lambda v: f"{100*v:.1f}%"; P0=lambda v: f"{100*v:.0f}%"
m=pd.read_csv(f"{O}/monthly.csv"); m["late_rate"]=m.late/m.booked; m["fill"]=m.worked/m.shifts; m["late_per100"]=m.late_per100/100
m["Start"]=pd.to_datetime(m.Start).dt.strftime("%b %Y")
B1=table(m,["Start","shifts","booked","bookings","worked","late","ncns","unfilled","deleted","late_rate","late_per100","fill"],{c:I for c in ["shifts","booked","bookings","worked","late","ncns","unfilled","deleted"]}|{"late_rate":P,"late_per100":P,"fill":P0},{"Start":"Month","shifts":"Posted","booked":"Booked shifts","bookings":"Bookings","worked":"Worked","late":"Late shifts","ncns":"No-show shifts","unfilled":"Empty","deleted":"Deleted","late_rate":"Shift late rate","late_per100":"Late per 100 bookings","fill":"Fill rate"})
rc=pd.read_csv(f"{O}/refill_curve.csv"); order=["NCNS/after","0-1h","1-4h","4-12h","12-24h","24-48h","48-72h","3-7d",">7d"]; rc=rc.set_index("lt_bin").loc[order].reset_index()
rc["lt_bin"]=["No-show / after start","0 to 1 hour","1 to 4 hours","4 to 12 hours","12 to 24 hours","24 to 48 hours","48 to 72 hours","3 to 7 days","Over 7 days"]
B2=table(rc,["lt_bin","shifts","refilled","worked","unfilled","deleted","worked_rate","deleted_rate","unfilled_rate"],{c:I for c in ["shifts","refilled","worked","unfilled","deleted"]}|{"worked_rate":P,"deleted_rate":P,"unfilled_rate":P},{"lt_bin":"Lead time of last cancellation","shifts":"Shifts","refilled":"Refilled","worked":"Worked","unfilled":"Empty","deleted":"Deleted","worked_rate":"Worked rate","deleted_rate":"Deleted rate","unfilled_rate":"Empty rate"})
lt=pd.read_csv(f"{O}/leadtime_hist.csv"); order2=["NCNS","0-1h","1-2h","2-4h","4-8h","8-12h","12-24h","24-48h","48-72h","3-7d","7-14d",">14d"]; lt=lt.set_index("ltb").loc[order2].reset_index(); lt["share"]=lt.cancels/lt.cancels.sum()
lt["ltb"]=["No-show","0 to 1 hour","1 to 2 hours","2 to 4 hours","4 to 8 hours","8 to 12 hours","12 to 24 hours","24 to 48 hours","48 to 72 hours","3 to 7 days","7 to 14 days","Over 14 days"]
B3=table(lt,["ltb","cancels","share"],{"cancels":I,"share":P},{"ltb":"Lead time","cancels":"Events","share":"Share"})
seg=pd.read_csv(f"{O}/worker_segments.csv"); seg["segment"]=seg.segment.astype(str).str.replace("-"," to ")+" late cancellations"
seg["share_late"]/=100; seg["share_verified"]/=100; seg["late_rate"]/=100
B4=table(seg,["segment","workers","bookings","verified","late","share_late","share_verified","late_rate"],{"workers":I,"bookings":I,"verified":I,"late":I,"share_late":P,"share_verified":P,"late_rate":P},{"segment":"Segment","workers":"Professionals","bookings":"Bookings","verified":"Worked","late":"Late","share_late":"Share of late","share_verified":"Share of worked","late_rate":"Late rate"})
ps=pd.read_csv(f"{O}/policy_sim.csv")
B5=table(ps,["rule","suspensions","deactivations","late_avoided","late_avoided_pct","verified_lost","verified_lost_pct","verified_lost_per_avoided"],{"suspensions":I,"deactivations":I,"late_avoided":I,"late_avoided_pct":P0,"verified_lost":I,"verified_lost_pct":P,"verified_lost_per_avoided":lambda v: f"{v:.1f}"},{"rule":"Rule","suspensions":"Suspensions","deactivations":"Deactivations","late_avoided":"Late avoided","late_avoided_pct":"Share of late","verified_lost":"Worked shifts lost","verified_lost_pct":"Share of worked","verified_lost_per_avoided":"Lost per avoided"})
rows=[]
r=pd.read_csv(f"{O}/by_role.csv"); r=r[r.booked>=100]
for _,x in r.iterrows(): rows.append(dict(group="Role",level=x["Agent Req"],booked=x.booked,late_rate=x.late_rate,ncns_rate=x.ncns_rate))
st=pd.read_csv(f"{O}/by_shifttype.csv")
for _,x in st.iterrows(): rows.append(dict(group="Shift type",level=x["Shift Type"].upper(),booked=x.booked,late_rate=x.late_rate,ncns_rate=x.ncns_rate))
wd=pd.read_csv(f"{O}/by_weekday.csv").set_index("dow").loc[["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]].reset_index()
for _,x in wd.iterrows(): rows.append(dict(group="Weekday",level=x.dow,booked=x.booked,late_rate=x.late_rate,ncns_rate=x.ncns_rate))
b6=pd.DataFrame(rows); B6=table(b6,["group","level","booked","late_rate","ncns_rate"],{"booked":I,"late_rate":P,"ncns_rate":P},{"group":"Cut","level":"Value","booked":"Booked shifts","late_rate":"Late rate","ncns_rate":"No-show rate"})
t=pd.read_csv(f"{O}/tenure.csv"); t["tenure_bin"]=["Under 2 weeks","2 to 4 weeks","1 to 2 months","2 to 3 months","3 to 6 months","6 to 12 months","Over 1 year"]; t["ncns_rate"]=t.ncns/t.bookings
B7=table(t,["tenure_bin","bookings","late","late_rate","ncns_rate"],{"bookings":I,"late":I,"late_rate":P,"ncns_rate":P},{"tenure_bin":"Tenure at shift start","bookings":"Bookings","late":"Late","late_rate":"Late rate","ncns_rate":"No-show rate"})
tpl=open(f"{S}/writeup/template.html").read()
for k,v in dict(B1=B1,B2=B2,B3=B3,B4=B4,B5=B5,B6=B6,B7=B7).items(): tpl=tpl.replace("{{"+k+"}}",v)
assert "{{" not in tpl
bad=[ch for ch in "—–" if ch in tpl]; assert not bad, f"dash found: {bad}"
open(f"{S}/writeup/Confirm_or_Release_Clipboard_Case.html","w").write(tpl)
words=len(re.sub(r"<[^>]+>"," ",tpl.split('<div class="appendix">')[0]).split()); print("narrative words ~",words)
