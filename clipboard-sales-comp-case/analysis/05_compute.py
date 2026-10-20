"""Reference calculation of June 2026 commissions (plan as written). Thin wrapper around engine.compute; writes out/reps_calc.csv and out/accounts_calc.csv."""
import sys, pandas as pd; sys.path.insert(0, sys.argv[1]+"/analysis"); from load_helper import load; from engine import compute
pd.set_option("display.width",250); pd.set_option("display.max_columns",60); pd.set_option("display.float_format",lambda v: f"{v:,.2f}")
S=sys.argv[1]; d=load(S+"/data/case_workbook.xlsx"); reps,AC=compute(d)
cols=["name","role","Country Code","emp_start","emp_end","days_emp","quota_pro","ramp_n1","ramp_n2","ramp_floor","ramping","produced_paid","produced_full","credited","attain","attain2","acc_eligible","comm_ic","spiff","carried_new","carried_ex","comm_mgr","commission_usd","ccy","fx","commission_local"]
reps[cols].to_csv(S+"/out/reps_calc.csv",index=False); AC.to_csv(S+"/out/accounts_calc.csv",index=False)
print(reps[cols].sort_values(["role","name"]).to_string(index=False)); print("\nTOTAL USD: %.2f | local: %.2f" % (reps.commission_usd.sum(), reps.commission_local.sum()))
print("by role:\n", reps.groupby("role").agg(n=("name","size"),credited=("credited","sum"),comm=("commission_usd","sum")).to_string())
