"""Cross-check: recalculated Excel model vs the pandas reference implementation, rep by rep and account by account."""
import sys, pandas as pd, numpy as np, openpyxl
pd.set_option("display.width",230); pd.set_option("display.max_columns",30); pd.set_option("display.float_format",lambda v: f"{v:,.2f}")
S=sys.argv[1]; wb=openpyxl.load_workbook(f"{S}/model/June_2026_Commissions_Model.xlsx",data_only=True,read_only=True)
def sheet_df(name):
    ws=wb[name]; rows=list(ws.iter_rows(values_only=True)); return pd.DataFrame(rows[1:],columns=[str(c) for c in rows[0]])
cr=sheet_df("Calc_Reps"); ca=sheet_df("Calc_Accounts")
py=pd.read_csv(f"{S}/out/reps_calc.csv").add_prefix("py_").rename(columns={"py_name":"name"}); pa=pd.read_csv(f"{S}/out/accounts_calc.csv").add_prefix("py_").rename(columns={"py_crm_account_id":"crm_account_id"})
def c(df,h): assert h in df.columns,h; return pd.to_numeric(df[h],errors="coerce")
x=pd.DataFrame({"name":cr["name"],"days":c(cr,"days employed in month (7.11)"),"floor":c(cr,"ramp floor on credited revenue (7.10)"),"prod_paid":c(cr,"produced, plan as written, while employed"),"prod_full":c(cr,"produced, plan as written, full month (manager roll-up)"),"cred_aw":c(cr,"credited revenue, plan as written"),"comm_ic_aw":c(cr,"IC commission, plan as written"),"spiff":c(cr,"retention SPIFF (7.12, amount from tab 6)"),"mgr_aw":c(cr,"manager commission, plan as written"),"total_aw":c(cr,"TOTAL USD, plan as written"),"total_rec":c(cr,"TOTAL USD, recommended payable"),"total_scn":c(cr,"TOTAL USD, scenario (recommended basis)"),"local_aw":c(cr,"TOTAL local currency, plan as written")})
m=x.merge(py,on="name"); bad=0
for a,b in [("days","py_days_emp"),("floor","py_ramp_floor"),("prod_paid","py_produced_paid"),("prod_full","py_produced_full"),("cred_aw","py_credited"),("comm_ic_aw","py_comm_ic"),("spiff","py_spiff"),("mgr_aw","py_comm_mgr"),("total_aw","py_commission_usd"),("local_aw","py_commission_local")]:
    d=(m[a]-m[b]).abs(); n=(d>0.01).sum(); bad+=n; print(f"{a:12s} vs {b:20s}: max abs diff {d.max():,.4f} | rows differing >0.01: {n}")
    if n: print(m.loc[d>0.01,["name",a,b]].to_string(index=False))
print("\nTOTALS: excel as-written %.2f | pandas %.2f | excel recommended %.2f | excel scenario(rec) %.2f" % (x.total_aw.sum(), py.py_commission_usd.sum(), x.total_rec.sum(), x.total_scn.sum()))
d=x[(x.total_rec-x.total_aw).abs()>0.005][["name","total_aw","total_rec"]].copy(); d["diff"]=d.total_rec-d.total_aw; print("recommended minus as-written, non-zero reps:\n", d.to_string(index=False))
acc=pd.DataFrame({"crm_account_id":ca["crm_account_id"],"f1":c(ca,"F1-30D revenue recognised this month (NR, or GSV for GTM)"),"imp2":c(ca,"F31-60D improvement credit, halved (7.4)"),"imp3":c(ca,"F61-90D improvement credit, halved (7.4)"),"new_full":c(ca,"NEW credited revenue, plan as written, full month"),"new_paid":c(ca,"NEW credited revenue, plan as written, closer employed"),"ex":c(ca,"EXISTING credited revenue, comp month"),"ex_may":c(ca,"EXISTING revenue, prior month (same-book test)")})
j=acc.merge(pa,on="crm_account_id")
for a,b in [("f1","py_f1_june_full"),("imp2","py_imp2"),("imp3","py_imp3"),("new_full","py_new_cred_full"),("new_paid","py_new_cred_paid"),("ex","py_ex_june"),("ex_may","py_ex_may")]:
    d=(j[a]-j[b]).abs(); n=(d>0.01).sum(); bad+=n; print(f"{a:10s} vs {b:18s}: max abs diff {d.max():,.4f} | n>0.01: {n}")
    if n: print(j.loc[d>0.01,["crm_account_id",a,b,"py_closer_name","py_atype"]].head(8).to_string(index=False))
print("\nRESULT:", "MATCH" if bad==0 else f"{bad} mismatches")
