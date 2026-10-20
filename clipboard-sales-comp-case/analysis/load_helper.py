"""Shared loader: reads every tab of the case workbook into pandas with clean column names."""
import pandas as pd, numpy as np, warnings; warnings.filterwarnings("ignore")
def load(path):
    x=pd.read_excel(path, sheet_name=None)
    d={}
    d["roster"]=x["1. Sales Roster"]; d["hr"]=x["2. HR Export"]; d["fx"]=x["3. Exchange Rates"]; d["ramp"]=x["4. Ramp Terms"]; d["comp"]=x["5. Compensation"]
    acc=pd.read_excel(path, sheet_name="6. Accelerators", header=None); d["acc_raw"]=acc
    d["map"]=x["7. Opportunity to ID Mapping"]; d["opp"]=x["8. Opportunity Export"]; d["app"]=x["9. App Export"]; d["bill"]=x["10. Billing Export"]; d["slack"]=x["11. Slack Scrape"]
    return d
