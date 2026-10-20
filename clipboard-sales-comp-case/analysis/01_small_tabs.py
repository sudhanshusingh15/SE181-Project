import sys, pandas as pd, numpy as np; sys.path.insert(0, sys.argv[1]+"/analysis"); from load_helper import load
pd.set_option("display.width",250); pd.set_option("display.max_columns",40); pd.set_option("display.max_colwidth",400); pd.set_option("display.max_rows",200)
d=load(sys.argv[1]+"/data/case_workbook.xlsx"); P=print
ro,hr,fx,ramp,comp,acc,sl=d["roster"],d["hr"],d["fx"],d["ramp"],d["comp"],d["acc_raw"],d["slack"]
P("### ROSTER", ro.shape, "| unique names", ro.name.nunique(), "| unique hr_id", ro.hr_id.nunique(), "| unique crm_owner_id", ro.crm_owner_id.nunique(), "| unique slack", ro.slack_user_id.nunique(), "| null crm", ro.crm_owner_id.isna().sum())
P("### HR", hr.shape, "| hr_id unique", hr.hr_id.nunique())
j=ro.merge(hr, on="hr_id", how="left", indicator=True); P("roster rows matched in HR:", (j._merge=="both").sum())
mgr_name=dict(zip(hr.hr_id, hr.hr_id)); name_by_hr=dict(zip(ro.hr_id, ro.name)); hr_role=dict(zip(hr.hr_id, hr["Current Role"]))
j["manager_name"]=j["Manager - ID"].map(name_by_hr).fillna(j["Manager - ID"].map(hr_role).fillna("(not in HR)"))
cols=["name","Current Role","Start Date","End Date","Current Role Start Date","Current Role End Date","Previous Role","Previous Role Start Date","Previous Role End Date","manager_name","Country Code"]
P(j[cols].sort_values(["Current Role","name"]).to_string(index=False))
P("\nRole counts among 80:\n", j["Current Role"].value_counts().to_string())
P("Leavers (End Date set):", j["End Date"].notna().sum(), "| role end date set:", j["Current Role End Date"].notna().sum(), "| previous role set:", j["Previous Role"].notna().sum())
P("Managers referenced:", j["Manager - ID"].nunique(), "| manager ids not in roster:", (~j["Manager - ID"].isin(ro.hr_id)).sum(), "->", j.loc[~j["Manager - ID"].isin(ro.hr_id),["name","Current Role","Manager - ID"]].to_string(index=False))
P("Country codes among 80:", j["Country Code"].value_counts().to_dict())
# HR rows for the 80 names: any duplicates of the same person (rehire rows)?
P("HR rows whose role is a sales role but hr_id not in roster:", hr[hr["Current Role"].isin(j["Current Role"].unique()) & ~hr.hr_id.isin(ro.hr_id)].shape[0])
P(hr[hr["Current Role"].isin(j["Current Role"].unique()) & ~hr.hr_id.isin(ro.hr_id)][["hr_id","Current Role","Start Date","End Date","Current Role Start Date","Manager - ID","Country Code"]].to_string(index=False))
P("\n### FX", fx.shape, "| codes unique:", fx["Country Code"].nunique(), "| dup codes:", fx[fx.duplicated("Country Code",keep=False)].to_string(index=False) if fx["Country Code"].duplicated().any() else "none")
P(fx[fx["Country Code"].isin(j["Country Code"].unique())].to_string(index=False))
P("FX oddities (rate<=0 or null):", fx[(fx["1 USD ="].isna())|(pd.to_numeric(fx["1 USD ="],errors="coerce")<=0)].to_string(index=False))
P("non-numeric rates:", fx[pd.to_numeric(fx["1 USD ="],errors="coerce").isna()].to_string(index=False))
P("\n### RAMP TERMS\n", ramp.to_string(index=False))
P("\n### COMPENSATION\n", comp.to_string(index=False))
P("\n### ACCELERATORS (raw)\n", acc.to_string(index=False))
P("\n### SLACK", sl.shape); sl["who"]=sl.slack_user_id.map(dict(zip(ro.slack_user_id, ro.name))).fillna("(not on roster)")
P(sl[["timestamp","channel","who","message"]].to_string(index=False))
