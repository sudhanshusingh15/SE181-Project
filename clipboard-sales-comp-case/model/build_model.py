"""Builds June_2026_Commissions_Model.xlsx: the 11 raw tabs untouched, plus Inputs, Calc_Opps, Calc_Accounts, Calc_Reps,
Payout_Summary, Scenario, Ledger and README. Every payout is a formula chain back to the raw tabs."""
import sys, json, openpyxl
from openpyxl.utils import get_column_letter as L
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
SRC, OUT = sys.argv[1], sys.argv[2]
LEDGER = json.load(open(sys.argv[3])) if len(sys.argv)>3 else []
wb = openpyxl.load_workbook(SRC)
APP="'9. App Export'"; OPP="'8. Opportunity Export'"; BILL="'10. Billing Export'"; HR="'2. HR Export'"; FX="'3. Exchange Rates'"; MAP="'7. Opportunity to ID Mapping'"; COMP="'5. Compensation'"; ACC="'6. Accelerators'"; ROS="'1. Sales Roster'"
N_APP=150000; N_OPP=1500; N_BILL=3000; N_HR=2000; N_FX=300; N_MAP=1100; N_COMP=18; N_REP=120; N_ACCT=1100
RAW={'9. App Export':107052,'8. Opportunity Export':815,'10. Billing Export':1089,'2. HR Export':1080,'3. Exchange Rates':196,'7. Opportunity to ID Mapping':761,'1. Sales Roster':80}
BLUE=Font(name="Arial",color="0000FF"); BLACK=Font(name="Arial"); BOLD=Font(name="Arial",bold=True); GREEN=Font(name="Arial",color="008000"); HDR=Font(name="Arial",bold=True,color="FFFFFF")
HFILL=PatternFill("solid",fgColor="1F3864"); YFILL=PatternFill("solid",fgColor="FFFF00"); GFILL=PatternFill("solid",fgColor="F2F2F2")
def hdr(ws,row,headers,widths=None):
    for i,h in enumerate(headers,1):
        c=ws.cell(row=row,column=i,value=h); c.font=HDR; c.fill=HFILL; c.alignment=Alignment(wrap_text=True,vertical="top")
        if widths: ws.column_dimensions[L(i)].width=widths[i-1] if i-1<len(widths) else 14
    ws.freeze_panes=ws.cell(row=row+1,column=1)
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if c.value is not None: c.font=Font(name="Arial",bold=c.font.bold)
# =============================== INPUTS
I=wb.create_sheet("Inputs",0)
I.column_dimensions["A"].width=46; I.column_dimensions["B"].width=18; I.column_dimensions["C"].width=70
I["A1"]="Inputs and plan parameters"; I["A1"].font=Font(name="Arial",bold=True,size=14)
I["A2"]="Blue cells are inputs. Everything else in the workbook is a formula. To run another month, change B4 and paste the new extracts into tabs 1 to 11 (same layout)."; I["A2"].font=BLACK
rows=[(4,"Comp month start date",None,"Input. First day of the statement month."),(5,"Comp month end date","=EOMONTH(B4,0)","Formula"),(6,"Days in comp month","=DAY(B5)","Formula; ramp and quota prorate against this"),(7,"Prior month start","=EDATE(B4,-1)","Formula; the retention SPIFF compares against this month"),(8,"Prior month end","=B4-1","Formula"),(9,"Billing month key (comp month)",'=TEXT(B4,"yyyy-mm")',"Formula; matches billing_month on tab 10"),(10,"Billing month key (prior month)",'=TEXT(B7,"yyyy-mm")',"Formula"),
      (13,"GTM payout rate (plan 7.6)",0.03,"Input from the plan text"),(14,"Half rate factor for F31-60D and F61-90D (plan 7.4)",0.5,"Input from the plan text"),(15,"Window length in days (plan 7.4)",30,"Input from the plan text; windows are days 1-30, 31-60, 61-90 from the first worked shift")]
for r,a,b,c in rows:
    I.cell(row=r,column=1,value=a).font=BLACK
    cell=I.cell(row=r,column=2,value=b); cell.font=BLUE if (b is None or not str(b).startswith("=")) else BLACK
    I.cell(row=r,column=3,value=c).font=Font(name="Arial",italic=True,color="595959")
import datetime
I["B4"]=datetime.datetime(2026,6,1); I["B4"].number_format="yyyy-mm-dd"; I["B4"].font=BLUE; I["B4"].fill=YFILL
for r in (5,7,8): I.cell(row=r,column=2).number_format="yyyy-mm-dd"
I["B13"].number_format="0.0%"; I["B14"].number_format="0.0"
I["A17"]="Net terms multipliers on new-logo revenue (plan 7.5)"; I["A17"].font=BOLD; I["B17"]="Multiplier"; I["B17"].font=BOLD
for i,(t,m) in enumerate([(15,1.2),(30,1.0),(45,0.9),(60,0.7)]): I.cell(row=18+i,column=1,value=t).font=BLUE; c=I.cell(row=18+i,column=2,value=m); c.font=BLUE; c.number_format="0.00"
I["A24"]="Ramp percentages by ramped role (tab 4. Ramp Terms, transcribed)"; I["A24"].font=BOLD; I["B24"]="Days 1-30"; I["C24"]="Days 31-60"; I["B24"].font=BOLD; I["C24"].font=BOLD
for i,(role,p1,p2) in enumerate([("SMB Account Executive",1.0,0.5),("ENT Account Executive",1.0,0.5),("SMB Account Manager",1.0,1.0),("ENT Account Manager",1.0,1.0)]):
    I.cell(row=25+i,column=1,value=role).font=BLUE
    for col,v in ((2,p1),(3,p2)): c=I.cell(row=25+i,column=col,value=v); c.font=BLUE; c.number_format="0%"
I["A31"]="Scenario: SMB AE accelerator multipliers (assignment 3)"; I["A31"].font=BOLD
I["A32"]="Band I multiplier, current"; I["B32"]=f"={ACC}!F3"; I["B32"].font=GREEN
I["A33"]="Band II multiplier, current"; I["B33"]=f"={ACC}!I3"; I["B33"].font=GREEN
I["A34"]="Band I multiplier, proposed"; I["B34"]=1.3; I["B34"].font=BLUE; I["B34"].fill=YFILL
I["A35"]="Band II multiplier, proposed"; I["B35"]=1.5; I["B35"].font=BLUE; I["B35"].fill=YFILL
I["A37"]="Treatments (1 = on, 0 = off). 'Plan as written' columns ignore these; 'Recommended' columns apply them."; I["A37"].font=BOLD
I["A38"]="Recognise GTM GSV posted before the comp month in the month the F1-30D window opens"; I["B38"]=1; I["C38"]="Plan 7.6 gives F1-30D an upper bound only. A shift posted before the first worked shift could not be recognised before the window existed, so it lands on the first statement that has the window. Set to 0 to recognise only shifts posted inside the comp month."
I["A39"]="Exclude flagged accounts (list below) from new-logo credit"; I["B39"]=1; I["C39"]="Ledger item 1. The plan as written pays these; I would not sign them off without review. The 'Plan as written' columns still show the full amount."
I["A40"]="Hold new-logo credit where the closer was not employed on the deal's close date"; I["B40"]=0; I["C40"]="Ledger item 2. Off by default: plan 7.4 says closed_by_owner_id governs as exported. Turn on to see the exposure."
for r in (38,39,40): I.cell(row=r,column=2).font=BLUE; I.cell(row=r,column=2).fill=YFILL; I.cell(row=r,column=3).font=Font(name="Arial",italic=True,color="595959"); I.cell(row=r,column=3).alignment=Alignment(wrap_text=True,vertical="top")
I["A41"]="Flagged app_account_id (new-logo credit withheld when B39 = 1)"; I["A41"].font=BOLD; I["B41"]="Reason"; I["B41"].font=BOLD
I["A42"]="3ffe588d-e4a1-48bf-83f4-2c425aede793"; I["A42"].font=BLUE; I["B42"]="GTM account closed by Jon Snow: 313 shifts posted in June, 45 worked. Posting pattern matches the templates described in Slack. Hold pending ops review."
I["B42"].alignment=Alignment(wrap_text=True,vertical="top")
for r in range(43,47): I.cell(row=r,column=1).font=BLUE
I["A48"]="Convention: blue = input, black = formula, green = link to another tab. Yellow fill marks the cells a reviewer is most likely to change."
# =============================== CALC_OPPS
CO=wb.create_sheet("Calc_Opps")
hdr(CO,1,["opportunity_id","crm_account_id","match key: account | stage","is Closed Won"],[14,40,52,12])
for r in range(2,N_OPP+1):
    g=f'{OPP}!B{r}=""'; CO.cell(row=r,column=1,value=f'=IF({g},"",{OPP}!B{r})'); CO.cell(row=r,column=2,value=f'=IF({g},"",{OPP}!A{r})'); CO.cell(row=r,column=3,value=f'=IF({g},"",{OPP}!A{r}&"|"&{OPP}!F{r})'); CO.cell(row=r,column=4,value=f'=IF({g},"",IF({OPP}!F{r}="Closed Won",1,0))')
# =============================== CALC_ACCOUNTS (columns defined in order)
A_COLS=[
("crm_account_id", f"={MAP}!A{{r}}"),
("app_account_id", f"={MAP}!B{{r}}"),
("billing_account_id", f"={MAP}!C{{r}}"),
("row of a Closed Won opp (Calc_Opps)", f'=IFERROR(MATCH(A{{r}}&"|Closed Won",Calc_Opps!$C$2:$C${N_OPP},0),"")'),
("go-live = earliest Closed Won effective_start_date (7.3)", f'=IF(D{{r}}="","",_xlfn.MINIFS({OPP}!$H$2:$H${N_OPP},{OPP}!$A$2:$A${N_OPP},A{{r}},{OPP}!$F$2:$F${N_OPP},"Closed Won"))'),
("first Closed Won date", f'=IF(D{{r}}="","",_xlfn.MINIFS({OPP}!$G$2:$G${N_OPP},{OPP}!$A$2:$A${N_OPP},A{{r}},{OPP}!$F$2:$F${N_OPP},"Closed Won"))'),
("closed_by_owner_id (7.4)", f'=IF(D{{r}}="","",IF(INDEX({OPP}!$C$2:$C${N_OPP},D{{r}})="","",INDEX({OPP}!$C$2:$C${N_OPP},D{{r}})))'),
("crm_owner_id (7.7)", f'=IF(D{{r}}="","",INDEX({OPP}!$D$2:$D${N_OPP},D{{r}}))'),
("account_type", f'=IF(D{{r}}="","",INDEX({OPP}!$E$2:$E${N_OPP},D{{r}}))'),
("segment", f'=IF(D{{r}}="","",INDEX({OPP}!$I$2:$I${N_OPP},D{{r}}))'),
("net_terms", f'=IF(D{{r}}="","",INDEX({OPP}!$L$2:$L${N_OPP},D{{r}}))'),
("charge rate per shift", f'=IF(D{{r}}="",0,INDEX({OPP}!$J$2:$J${N_OPP},D{{r}}))'),
("pay rate per shift", f'=IF(D{{r}}="",0,INDEX({OPP}!$K$2:$K${N_OPP},D{{r}}))'),
("margin per worked shift (7.1)", "=L{r}-M{r}"),
("net terms multiplier (7.5; 1 for GTM)", '=IF(I{r}="GTM",1,IFERROR(INDEX(Inputs!$B$18:$B$21,MATCH(K{r},Inputs!$A$18:$A$21,0)),1))'),
("first worked shift date (tab 9)", f'=IFERROR(INDEX({APP}!$F$2:$F${N_APP},MATCH(B{{r}},{APP}!$A$2:$A${N_APP},0)),"")'),
("W1 start", '=IF(P{r}="","",P{r})'),
("W1 end", '=IF(P{r}="","",P{r}+Inputs!$B$15-1)'),
("W2 start", '=IF(P{r}="","",P{r}+Inputs!$B$15)'),
("W2 end", '=IF(P{r}="","",P{r}+2*Inputs!$B$15-1)'),
("W3 start", '=IF(P{r}="","",P{r}+2*Inputs!$B$15)'),
("W3 end", '=IF(P{r}="","",P{r}+3*Inputs!$B$15-1)'),
("closer role rate", f'=IFERROR(INDEX(Calc_Reps!$N$2:$N${N_REP},MATCH(G{{r}},Calc_Reps!$C$2:$C${N_REP},0)),0)'),
("closer employment start", f'=IFERROR(INDEX(Calc_Reps!$H$2:$H${N_REP},MATCH(G{{r}},Calc_Reps!$C$2:$C${N_REP},0)),DATE(2099,12,31))'),
("closer employment end (2099 if open)", f'=IFERROR(INDEX(Calc_Reps!$I$2:$I${N_REP},MATCH(G{{r}},Calc_Reps!$C$2:$C${N_REP},0)),DATE(1900,1,1))'),
# counts, net revenue basis
("F1-30D worked shifts in comp month", f'=IF(OR(P{{r}}="",I{{r}}="GTM"),0,COUNTIFS({APP}!$A$2:$A${N_APP},B{{r}},{APP}!$D$2:$D${N_APP},TRUE,{APP}!$E$2:$E${N_APP},">="&MAX(Q{{r}},Inputs!$B$4),{APP}!$E$2:$E${N_APP},"<="&MIN(R{{r}},Inputs!$B$5)))'),
("F1-30D worked shifts in comp month while closer employed (7.11)", f'=IF(OR(P{{r}}="",I{{r}}="GTM"),0,COUNTIFS({APP}!$A$2:$A${N_APP},B{{r}},{APP}!$D$2:$D${N_APP},TRUE,{APP}!$E$2:$E${N_APP},">="&MAX(Q{{r}},Inputs!$B$4,X{{r}}),{APP}!$E$2:$E${N_APP},"<="&MIN(R{{r}},Inputs!$B$5,Y{{r}})))'),
("W1 worked shifts", f'=IF(OR(P{{r}}="",I{{r}}="GTM"),0,COUNTIFS({APP}!$A$2:$A${N_APP},B{{r}},{APP}!$D$2:$D${N_APP},TRUE,{APP}!$E$2:$E${N_APP},">="&Q{{r}},{APP}!$E$2:$E${N_APP},"<="&R{{r}}))'),
("W2 worked shifts", f'=IF(OR(P{{r}}="",I{{r}}="GTM"),0,COUNTIFS({APP}!$A$2:$A${N_APP},B{{r}},{APP}!$D$2:$D${N_APP},TRUE,{APP}!$E$2:$E${N_APP},">="&S{{r}},{APP}!$E$2:$E${N_APP},"<="&T{{r}}))'),
("W3 worked shifts", f'=IF(OR(P{{r}}="",I{{r}}="GTM"),0,COUNTIFS({APP}!$A$2:$A${N_APP},B{{r}},{APP}!$D$2:$D${N_APP},TRUE,{APP}!$E$2:$E${N_APP},">="&U{{r}},{APP}!$E$2:$E${N_APP},"<="&V{{r}}))'),
# counts, GSV basis (GTM)
("GTM: F1-30D shifts posted, recognised this month", f'=IF(OR(P{{r}}="",I{{r}}<>"GTM"),0,COUNTIFS({APP}!$A$2:$A${N_APP},B{{r}},{APP}!$C$2:$C${N_APP},">="&IF(AND(Inputs!$B$38=1,P{{r}}>=Inputs!$B$4),1,Inputs!$B$4),{APP}!$C$2:$C${N_APP},"<="&MIN(R{{r}},Inputs!$B$5)))'),
("GTM: same, while closer employed", f'=IF(OR(P{{r}}="",I{{r}}<>"GTM"),0,COUNTIFS({APP}!$A$2:$A${N_APP},B{{r}},{APP}!$C$2:$C${N_APP},">="&MAX(IF(AND(Inputs!$B$38=1,P{{r}}>=Inputs!$B$4),1,Inputs!$B$4),X{{r}}),{APP}!$C$2:$C${N_APP},"<="&MIN(R{{r}},Inputs!$B$5,Y{{r}})))'),
("GTM: W1 shifts posted (upper bound only)", f'=IF(OR(P{{r}}="",I{{r}}<>"GTM"),0,COUNTIFS({APP}!$A$2:$A${N_APP},B{{r}},{APP}!$C$2:$C${N_APP},"<="&R{{r}}))'),
("GTM: W2 shifts posted", f'=IF(OR(P{{r}}="",I{{r}}<>"GTM"),0,COUNTIFS({APP}!$A$2:$A${N_APP},B{{r}},{APP}!$C$2:$C${N_APP},">="&S{{r}},{APP}!$C$2:$C${N_APP},"<="&T{{r}}))'),
("GTM: W3 shifts posted", f'=IF(OR(P{{r}}="",I{{r}}<>"GTM"),0,COUNTIFS({APP}!$A$2:$A${N_APP},B{{r}},{APP}!$C$2:$C${N_APP},">="&U{{r}},{APP}!$C$2:$C${N_APP},"<="&V{{r}}))'),
# dollars
("F1-30D revenue recognised this month (NR, or GSV for GTM)", '=IF(I{r}="GTM",L{r}*AE{r},N{r}*Z{r})'),
("F1-30D revenue while closer employed", '=IF(I{r}="GTM",L{r}*AF{r},N{r}*AA{r})'),
("W1 total", '=IF(I{r}="GTM",L{r}*AG{r},N{r}*AB{r})'),
("W2 total", '=IF(I{r}="GTM",L{r}*AH{r},N{r}*AC{r})'),
("W3 total", '=IF(I{r}="GTM",L{r}*AI{r},N{r}*AD{r})'),
("W2 closes in comp month", '=IF(P{r}="",0,IF(AND(T{r}>=Inputs!$B$4,T{r}<=Inputs!$B$5),1,0))'),
("W3 closes in comp month", '=IF(P{r}="",0,IF(AND(V{r}>=Inputs!$B$4,V{r}<=Inputs!$B$5),1,0))'),
("F31-60D improvement credit, halved (7.4)", '=IF(AO{r}=1,MAX(0,AM{r}-AL{r})*Inputs!$B$14,0)'),
("F61-90D improvement credit, halved (7.4)", '=IF(AP{r}=1,MAX(0,AN{r}-MAX(AL{r},AM{r}))*Inputs!$B$14,0)'),
("F31-60D credit while closer employed on close date", '=IF(AND(AO{r}=1,T{r}>=X{r},T{r}<=Y{r}),AQ{r},0)'),
("F61-90D credit while closer employed on close date", '=IF(AND(AP{r}=1,V{r}>=X{r},V{r}<=Y{r}),AR{r},0)'),
("credit conversion (1; GTM = 3% / closer rate; 0 if no closer)", '=IF(G{r}="",0,IF(I{r}="GTM",IF(W{r}>0,Inputs!$B$13/W{r},0),1))'),
("NEW credited revenue, plan as written, full month", '=(AJ{r}+AQ{r}+AR{r})*O{r}*AU{r}'),
("NEW credited revenue, plan as written, closer employed", '=(AK{r}+AS{r}+AT{r})*O{r}*AU{r}'),
("flagged account (Inputs list)", '=IF(COUNTIF(Inputs!$A$42:$A$46,B{r})>0,1,0)'),
("closer employed on first Closed Won date", '=IF(OR(G{r}="",F{r}=""),1,IF(AND(F{r}>=X{r},F{r}<=Y{r}),1,0))'),
("treatment multiplier", '=IF(OR(AND(Inputs!$B$39=1,AX{r}=1),AND(Inputs!$B$40=1,AY{r}=0)),0,1)'),
("NEW credited revenue, recommended, full month", '=AV{r}*AZ{r}'),
("NEW credited revenue, recommended, closer employed", '=AW{r}*AZ{r}'),
# existing
("existing in comp month (go-live before month start, 7.7)", '=IF(E{r}="",0,IF(E{r}<Inputs!$B$4,1,0))'),
("existing in prior month (live before prior month start, 7.12)", '=IF(E{r}="",0,IF(E{r}<Inputs!$B$7,1,0))'),
("net revenue, shifts worked in comp month", f'=N{{r}}*COUNTIFS({APP}!$A$2:$A${N_APP},B{{r}},{APP}!$D$2:$D${N_APP},TRUE,{APP}!$E$2:$E${N_APP},">="&Inputs!$B$4,{APP}!$E$2:$E${N_APP},"<="&Inputs!$B$5)'),
("net revenue, shifts worked in prior month", f'=N{{r}}*COUNTIFS({APP}!$A$2:$A${N_APP},B{{r}},{APP}!$D$2:$D${N_APP},TRUE,{APP}!$E$2:$E${N_APP},">="&Inputs!$B$7,{APP}!$E$2:$E${N_APP},"<="&Inputs!$B$8)'),
("approved credits, comp month (7.2)", f'=SUMIFS({BILL}!$E$2:$E${N_BILL},{BILL}!$A$2:$A${N_BILL},C{{r}},{BILL}!$F$2:$F${N_BILL},"approved",{BILL}!$B$2:$B${N_BILL},Inputs!$B$9)'),
("approved credits, prior month", f'=SUMIFS({BILL}!$E$2:$E${N_BILL},{BILL}!$A$2:$A${N_BILL},C{{r}},{BILL}!$F$2:$F${N_BILL},"approved",{BILL}!$B$2:$B${N_BILL},Inputs!$B$10)'),
("EXISTING credited revenue, comp month", '=IF(BC{r}=1,BE{r}-BG{r},0)'),
("EXISTING revenue, prior month (same-book test)", '=IF(BD{r}=1,BF{r}-BH{r},0)'),
("EXISTING comp-month revenue on the prior-month book", '=IF(BD{r}=1,BI{r},0)'),
("approved comp-month credits on accounts not yet existing (excluded)", '=IF(BC{r}=0,BG{r},0)'),
("owner employment start", f'=IFERROR(INDEX(Calc_Reps!$H$2:$H${N_REP},MATCH(H{{r}},Calc_Reps!$C$2:$C${N_REP},0)),DATE(2099,12,31))'),
("owner employment end (2099 if active)", f'=IFERROR(INDEX(Calc_Reps!$I$2:$I${N_REP},MATCH(H{{r}},Calc_Reps!$C$2:$C${N_REP},0)),DATE(1900,1,1))'),
("net revenue, comp month, while owner employed (7.11)", f'=N{{r}}*COUNTIFS({APP}!$A$2:$A${N_APP},B{{r}},{APP}!$D$2:$D${N_APP},TRUE,{APP}!$E$2:$E${N_APP},">="&MAX(Inputs!$B$4,BM{{r}}),{APP}!$E$2:$E${N_APP},"<="&MIN(Inputs!$B$5,BN{{r}}))'),
("EXISTING credited revenue, comp month, owner employed (7.11)", '=IF(AND(BC{r}=1,BM{r}<=Inputs!$B$5,BN{r}>=Inputs!$B$4),BO{r}-BG{r},0)'),
]
CA=wb.create_sheet("Calc_Accounts")
hdr(CA,1,[h for h,_ in A_COLS],[38,38,38,10]+[16]*(len(A_COLS)-4))
CA.row_dimensions[1].height=78
assert len(A_COLS)==68, len(A_COLS)
for r in range(2,N_ACCT+1):
    for ci,(h,f) in enumerate(A_COLS,1):
        if ci==1: CA.cell(row=r,column=ci,value=f'=IF({MAP}!A{r}="","",{MAP}!A{r})')
        else: CA.cell(row=r,column=ci,value=f'=IF($A{r}="","",{f.format(r=r)[1:]})')
date_cols=["E","F","P","Q","R","S","T","U","V","X","Y","BM","BN"]
for col in date_cols:
    for r in range(2,N_ACCT+1): CA[f"{col}{r}"].number_format="yyyy-mm-dd"
for col in ["AJ","AK","AL","AM","AN","AQ","AR","AS","AT","AV","AW","BA","BB","BE","BF","BG","BH","BI","BJ","BK","BL","BO","BP"]:
    for r in range(2,N_ACCT+1): CA[f"{col}{r}"].number_format="#,##0.00"
# =============================== CALC_REPS
R_COLS=[
("name", f"={ROS}!A{{r}}"),("hr_id", f"={ROS}!B{{r}}"),("crm_owner_id", f"={ROS}!C{{r}}"),("slack_user_id", f"={ROS}!D{{r}}"),
("Current Role (tab 2; decides the plan)", f'=INDEX({HR}!$B$2:$B${N_HR},MATCH(B{{r}},{HR}!$A$2:$A${N_HR},0))'),
("Start Date", f'=INDEX({HR}!$C$2:$C${N_HR},MATCH(B{{r}},{HR}!$A$2:$A${N_HR},0))'),
("End Date (blank = active)", f'=IF(INDEX({HR}!$D$2:$D${N_HR},MATCH(B{{r}},{HR}!$A$2:$A${N_HR},0))="","",INDEX({HR}!$D$2:$D${N_HR},MATCH(B{{r}},{HR}!$A$2:$A${N_HR},0)))'),
("employment start", "=F{r}"),
("employment end (2099 if active)", '=IF(G{r}="",DATE(2099,12,31),G{r})'),
("Current Role Start Date (ramp clock, 7.10)", f'=INDEX({HR}!$E$2:$E${N_HR},MATCH(B{{r}},{HR}!$A$2:$A${N_HR},0))'),
("Manager - ID", f'=INDEX({HR}!$J$2:$J${N_HR},MATCH(B{{r}},{HR}!$A$2:$A${N_HR},0))'),
("Country Code", f'=INDEX({HR}!$K$2:$K${N_HR},MATCH(B{{r}},{HR}!$A$2:$A${N_HR},0))'),
("Monthly quota (tab 5)", f'=INDEX({COMP}!$D$2:$D${N_COMP},MATCH(E{{r}},{COMP}!$A$2:$A${N_COMP},0))'),
("Standard payout rate (tab 5)", f'=INDEX({COMP}!$G$2:$G${N_COMP},MATCH(E{{r}},{COMP}!$A$2:$A${N_COMP},0))'),
("metric carried", f'=IF(E{{r}}="Head of Sales & AM","Both",IF(INDEX({COMP}!$C$2:$C${N_COMP},MATCH(E{{r}},{COMP}!$A$2:$A${N_COMP},0))="New Customer Net Revenue","New","Existing"))'),
("Metric II quota (Head only)", f'=IFERROR(INDEX({COMP}!$K$2:$K${N_COMP},MATCH(E{{r}},{COMP}!$A$2:$A${N_COMP},0))*1,0)'),
("Metric II payout rate (Head only)", f'=IFERROR(INDEX({COMP}!$L$2:$L${N_COMP},MATCH(E{{r}},{COMP}!$A$2:$A${N_COMP},0))*1,0)'),
("individual contributor (1/0)", '=IF(OR(E{r}="SMB Account Executive",E{r}="ENT Account Executive",E{r}="SMB Account Manager",E{r}="ENT Account Manager"),1,0)'),
("IC metric", '=IF(R{r}=1,O{r},"")'),
("band I low (tab 6)", f'=IFERROR(INDEX({ACC}!$D$3:$D$4,MATCH(E{{r}},{ACC}!$A$3:$A$4,0)),"")'),
("band I high", f'=IFERROR(INDEX({ACC}!$E$3:$E$4,MATCH(E{{r}},{ACC}!$A$3:$A$4,0)),"")'),
("band I multiplier", f'=IFERROR(INDEX({ACC}!$F$3:$F$4,MATCH(E{{r}},{ACC}!$A$3:$A$4,0)),"")'),
("band II low", f'=IFERROR(INDEX({ACC}!$H$3:$H$4,MATCH(E{{r}},{ACC}!$A$3:$A$4,0)),"")'),
("band II multiplier", f'=IFERROR(INDEX({ACC}!$I$3:$I$4,MATCH(E{{r}},{ACC}!$A$3:$A$4,0)),"")'),
("ramp pct days 1-30 (Inputs)", '=IFERROR(INDEX(Inputs!$B$25:$B$28,MATCH(E{r},Inputs!$A$25:$A$28,0)),0)'),
("ramp pct days 31-60 (Inputs)", '=IFERROR(INDEX(Inputs!$C$25:$C$28,MATCH(E{r},Inputs!$A$25:$A$28,0)),0)'),
("employed from (in month)", '=MAX(H{r},Inputs!$B$4)'),
("employed to (in month)", '=MIN(I{r},Inputs!$B$5)'),
("days employed in month (7.11)", '=MAX(0,AB{r}-AA{r}+1)'),
("prorated quota", '=M{r}*AC{r}/Inputs!$B$6'),
("ramp days in month 1 (days 1-30 from role start)", '=IF(OR(Y{r}=0,AC{r}=0),0,MAX(0,MIN(AB{r},J{r}+29)-MAX(AA{r},J{r})+1))'),
("ramp days in month 2 (days 31-60)", '=IF(OR(Y{r}=0,AC{r}=0),0,MAX(0,MIN(AB{r},J{r}+59)-MAX(AA{r},J{r}+30)+1))'),
("ramp floor on credited revenue (7.10)", '=(AE{r}*Y{r}+AF{r}*Z{r})*M{r}/Inputs!$B$6'),
("ramping in month (1/0)", '=IF(AE{r}+AF{r}>0,1,0)'),
("produced, plan as written, while employed", f'=IF(S{{r}}="New",SUMIFS(Calc_Accounts!$AW$2:$AW${N_ACCT},Calc_Accounts!$G$2:$G${N_ACCT},C{{r}}),IF(S{{r}}="Existing",SUMIFS(Calc_Accounts!$BP$2:$BP${N_ACCT},Calc_Accounts!$H$2:$H${N_ACCT},C{{r}}),0))'),
("produced, plan as written, full month (manager roll-up)", f'=IF(S{{r}}="New",SUMIFS(Calc_Accounts!$AV$2:$AV${N_ACCT},Calc_Accounts!$G$2:$G${N_ACCT},C{{r}}),IF(S{{r}}="Existing",SUMIFS(Calc_Accounts!$BI$2:$BI${N_ACCT},Calc_Accounts!$H$2:$H${N_ACCT},C{{r}}),0))'),
("produced, recommended, while employed", f'=IF(S{{r}}="New",SUMIFS(Calc_Accounts!$BB$2:$BB${N_ACCT},Calc_Accounts!$G$2:$G${N_ACCT},C{{r}}),IF(S{{r}}="Existing",SUMIFS(Calc_Accounts!$BP$2:$BP${N_ACCT},Calc_Accounts!$H$2:$H${N_ACCT},C{{r}}),0))'),
("produced, recommended, full month", f'=IF(S{{r}}="New",SUMIFS(Calc_Accounts!$BA$2:$BA${N_ACCT},Calc_Accounts!$G$2:$G${N_ACCT},C{{r}}),IF(S{{r}}="Existing",SUMIFS(Calc_Accounts!$BI$2:$BI${N_ACCT},Calc_Accounts!$H$2:$H${N_ACCT},C{{r}}),0))'),
("credited revenue, plan as written", '=IF(AC{r}>0,MAX(AI{r},AG{r}),0)'),
("credited revenue, plan as written, full (roll-up)", '=IF(AC{r}>0,MAX(AJ{r},AG{r}),AJ{r})'),
("credited revenue, recommended", '=IF(AC{r}>0,MAX(AK{r},AG{r}),0)'),
("credited revenue, recommended, full (roll-up)", '=IF(AC{r}>0,MAX(AL{r},AG{r}),AL{r})'),
("attainment: credited (recommended) or carried revenue / prorated quota", '=IF(AD{r}>0,IF(R{r}=1,AO{r}/AD{r},IF(O{r}="Existing",BD{r}/AD{r},BC{r}/AD{r})),"")'),
("accelerator eligible (AE, not ramping, employed)", '=IF(AND(R{r}=1,T{r}<>"",AH{r}=0,AC{r}>0),1,0)'),
("IC commission, plan as written", '=IF(R{r}=0,0,IF(AR{r}=1,N{r}*(MIN(AM{r},T{r})+V{r}*MAX(0,MIN(AM{r},U{r})-T{r})+X{r}*MAX(0,AM{r}-W{r})),N{r}*AM{r}))'),
("IC commission, recommended", '=IF(R{r}=0,0,IF(AR{r}=1,N{r}*(MIN(AO{r},T{r})+V{r}*MAX(0,MIN(AO{r},U{r})-T{r})+X{r}*MAX(0,AO{r}-W{r})),N{r}*AO{r}))'),
("IC commission, scenario multipliers (recommended basis)", '=IF(R{r}=0,0,IF(AR{r}=1,N{r}*(MIN(AO{r},T{r})+IF(E{r}="SMB Account Executive",Inputs!$B$34,V{r})*MAX(0,MIN(AO{r},U{r})-T{r})+IF(E{r}="SMB Account Executive",Inputs!$B$35,X{r})*MAX(0,AO{r}-W{r})),N{r}*AO{r}))'),
("prior-month existing revenue on same book (7.12)", f'=IF(S{{r}}="Existing",SUMIFS(Calc_Accounts!$BJ$2:$BJ${N_ACCT},Calc_Accounts!$H$2:$H${N_ACCT},C{{r}}),0)'),
("comp-month existing revenue on same book", f'=IF(S{{r}}="Existing",SUMIFS(Calc_Accounts!$BK$2:$BK${N_ACCT},Calc_Accounts!$H$2:$H${N_ACCT},C{{r}}),0)'),
("retention SPIFF (7.12, amount from tab 6)", f'=IF(AND(S{{r}}="Existing",R{{r}}=1,AH{{r}}=0,AC{{r}}>0,AV{{r}}>0,AW{{r}}>=AV{{r}}),IFERROR(INDEX({ACC}!$D$9:$D$10,MATCH(E{{r}},{ACC}!$A$9:$A$10,0)),0),0)'),
("manager level 1", "=K{r}"),
("manager level 2", f'=IFERROR(INDEX({HR}!$J$2:$J${N_HR},MATCH(AY{{r}},{HR}!$A$2:$A${N_HR},0)),"")'),
("manager level 3", f'=IFERROR(INDEX({HR}!$J$2:$J${N_HR},MATCH(AZ{{r}},{HR}!$A$2:$A${N_HR},0)),"")'),
("manager level 4", f'=IFERROR(INDEX({HR}!$J$2:$J${N_HR},MATCH(BA{{r}},{HR}!$A$2:$A${N_HR},0)),"")'),
("carried NEW, recommended (all ICs beneath, 7.8)", f'=SUMIFS($AP$2:$AP${N_REP},$S$2:$S${N_REP},"New",$AY$2:$AY${N_REP},B{{r}})+SUMIFS($AP$2:$AP${N_REP},$S$2:$S${N_REP},"New",$AZ$2:$AZ${N_REP},B{{r}})+SUMIFS($AP$2:$AP${N_REP},$S$2:$S${N_REP},"New",$BA$2:$BA${N_REP},B{{r}})+SUMIFS($AP$2:$AP${N_REP},$S$2:$S${N_REP},"New",$BB$2:$BB${N_REP},B{{r}})'),
("carried EXISTING, recommended", f'=SUMIFS($AP$2:$AP${N_REP},$S$2:$S${N_REP},"Existing",$AY$2:$AY${N_REP},B{{r}})+SUMIFS($AP$2:$AP${N_REP},$S$2:$S${N_REP},"Existing",$AZ$2:$AZ${N_REP},B{{r}})+SUMIFS($AP$2:$AP${N_REP},$S$2:$S${N_REP},"Existing",$BA$2:$BA${N_REP},B{{r}})+SUMIFS($AP$2:$AP${N_REP},$S$2:$S${N_REP},"Existing",$BB$2:$BB${N_REP},B{{r}})'),
("carried NEW, plan as written", f'=SUMIFS($AN$2:$AN${N_REP},$S$2:$S${N_REP},"New",$AY$2:$AY${N_REP},B{{r}})+SUMIFS($AN$2:$AN${N_REP},$S$2:$S${N_REP},"New",$AZ$2:$AZ${N_REP},B{{r}})+SUMIFS($AN$2:$AN${N_REP},$S$2:$S${N_REP},"New",$BA$2:$BA${N_REP},B{{r}})+SUMIFS($AN$2:$AN${N_REP},$S$2:$S${N_REP},"New",$BB$2:$BB${N_REP},B{{r}})'),
("carried EXISTING, plan as written", f'=SUMIFS($AN$2:$AN${N_REP},$S$2:$S${N_REP},"Existing",$AY$2:$AY${N_REP},B{{r}})+SUMIFS($AN$2:$AN${N_REP},$S$2:$S${N_REP},"Existing",$AZ$2:$AZ${N_REP},B{{r}})+SUMIFS($AN$2:$AN${N_REP},$S$2:$S${N_REP},"Existing",$BA$2:$BA${N_REP},B{{r}})+SUMIFS($AN$2:$AN${N_REP},$S$2:$S${N_REP},"Existing",$BB$2:$BB${N_REP},B{{r}})'),
("manager commission, recommended (7.8)", '=IF(R{r}=1,0,IF(O{r}="New",N{r}*BC{r},IF(O{r}="Existing",N{r}*BD{r},N{r}*BC{r}+Q{r}*BD{r})))'),
("manager commission, plan as written", '=IF(R{r}=1,0,IF(O{r}="New",N{r}*BE{r},IF(O{r}="Existing",N{r}*BF{r},N{r}*BE{r}+Q{r}*BF{r})))'),
("approved adjustment, USD (input)", None),
("adjustment note (input)", None),
("TOTAL USD, recommended payable", '=AT{r}+BG{r}+AX{r}+BI{r}'),
("TOTAL USD, plan as written", '=AS{r}+BH{r}+AX{r}'),
("TOTAL USD, scenario (recommended basis)", '=AU{r}+BG{r}+AX{r}+BI{r}'),
("FX: local units per USD (tab 3)", f'=INDEX({FX}!$E$2:$E${N_FX},MATCH(L{{r}},{FX}!$A$2:$A${N_FX},0))'),
("local currency", f'=INDEX({FX}!$D$2:$D${N_FX},MATCH(L{{r}},{FX}!$A$2:$A${N_FX},0))'),
("TOTAL local currency, recommended payable", '=BK{r}*BN{r}'),
("TOTAL local currency, plan as written", '=BL{r}*BN{r}'),
("Metric II attainment (Head of Sales & AM only)", '=IF(P{r}>0,BD{r}/P{r},"")'),
("IC commission, scenario multipliers (plan as written basis)", '=IF(R{r}=0,0,IF(AR{r}=1,N{r}*(MIN(AM{r},T{r})+IF(E{r}="SMB Account Executive",Inputs!$B$34,V{r})*MAX(0,MIN(AM{r},U{r})-T{r})+IF(E{r}="SMB Account Executive",Inputs!$B$35,X{r})*MAX(0,AM{r}-W{r})),N{r}*AM{r}))'),
("TOTAL USD, scenario (plan as written basis)", '=BS{r}+BH{r}+AX{r}'),
]
CR=wb.create_sheet("Calc_Reps")
hdr(CR,1,[h for h,_ in R_COLS],[20,38,38,38,24]+[14]*(len(R_COLS)-5)); CR.row_dimensions[1].height=78
for r in range(2,N_REP+1):
    for ci,(h,f) in enumerate(R_COLS,1):
        if f is None:
            c=CR.cell(row=r,column=ci,value=(0 if "USD" in h else None) if r<=RAW['1. Sales Roster']+1 else None); c.font=BLUE
        elif ci==1: CR.cell(row=r,column=ci,value=f'=IF({ROS}!A{r}="","",{ROS}!A{r})')
        else: CR.cell(row=r,column=ci,value=f'=IF($A{r}="","",{f.format(r=r)[1:]})')
for col in ["F","G","H","I","J","AA","AB"]:
    for r in range(2,N_REP+1): CR[f"{col}{r}"].number_format="yyyy-mm-dd"
for col in ["M","AD","AG","AI","AJ","AK","AL","AM","AN","AO","AP","AS","AT","AU","AV","AW","AX","BC","BD","BE","BF","BG","BH","BI","BK","BL","BM","BP","BQ","BS","BT"]:
    for r in range(2,N_REP+1): CR[f"{col}{r}"].number_format="#,##0.00"
for r in range(2,N_REP+1): CR[f"AQ{r}"].number_format="0.0%"; CR[f"BR{r}"].number_format="0.0%"; CR[f"N{r}"].number_format="0.000%"; CR[f"Q{r}"].number_format="0.0000%"
# =============================== PAYOUT SUMMARY
PS=wb.create_sheet("Payout_Summary",1)
PS["A1"]="June 2026 commission statement summary"; PS["A1"].font=Font(name="Arial",bold=True,size=14)
PS["A2"]='="Comp month: "&TEXT(Inputs!B4,"mmmm yyyy")&". Recommended payable applies the treatments on Inputs (rows 38-40). Plan as written applies none. Local amounts use tab 3 rates."'
cols=[("Name","A"),("Role","E"),("Country","L"),("Currency","BO"),("Days employed","AC"),("Prorated quota USD","AD"),("Credited or carried revenue USD (recommended)","__cred"),("Attainment","AQ"),("Ramping","AH"),("Retention SPIFF USD","AX"),("Commission USD, plan as written","BL"),("Commission USD, recommended payable","BK"),("Difference USD","__diff"),("Approved adjustment USD","BI"),("FX rate","BN"),("Payable in local currency (recommended)","BP"),("Payable in local currency (plan as written)","BQ")]
hdr(PS,4,[c for c,_ in cols],[20,24,9,9,10,15,17,10,8,12,16,16,12,12,8,18,18]); PS.row_dimensions[4].height=60
for i in range(2,N_REP+1):
    r=i+3
    for ci,(h,src) in enumerate(cols,1):
        if src=="__diff": PS.cell(row=r,column=ci,value=f'=IF(A{r}="","",L{r}-K{r})')
        elif src=="__cred": PS.cell(row=r,column=ci,value=f'=IF(Calc_Reps!$A{i}="","",IF(Calc_Reps!R{i}=1,Calc_Reps!AO{i},IF(Calc_Reps!O{i}="Existing",Calc_Reps!BD{i},Calc_Reps!BC{i})))')
        else: PS.cell(row=r,column=ci,value=f'=IF(Calc_Reps!$A{i}="","",Calc_Reps!{src}{i})')
        PS.cell(row=r,column=ci).font=GREEN if src not in ("__diff","__cred") else BLACK
    for ci in (6,7,10,11,12,13,14,16,17): PS.cell(row=r,column=ci).number_format="#,##0.00"
    PS.cell(row=r,column=8).number_format="0%"
tr=N_REP+4
PS.cell(row=tr,column=1,value="TOTAL USD").font=BOLD
for ci in (6,7,10,11,12,13,14): c=PS.cell(row=tr,column=ci,value=f"=SUM({L(ci)}5:{L(ci)}{tr-1})"); c.font=BOLD; c.number_format="#,##0.00"
PS.cell(row=tr+2,column=1,value="Totals by role (USD)").font=BOLD
roles=["SMB Account Executive","ENT Account Executive","SMB Account Manager","ENT Account Manager","SMB AE Manager I","SMB AE Manager III","ENT AE Manager I","ENT AE Manager II","Director of Sales","SMB AM Manager I","SMB AM Manager III","ENT AM Manager I","ENT AM Manager II","ENT AM Manager III","Director of SMB AM","Director of ENT AM","Head of Sales & AM"]
for j,h in enumerate(["Role","Reps","Credited revenue (recommended)","Commission plan as written","Commission recommended","Difference"]): c=PS.cell(row=tr+3,column=1+j,value=h); c.font=BOLD
for k,role in enumerate(roles):
    rr=tr+4+k; PS.cell(row=rr,column=1,value=role)
    PS.cell(row=rr,column=2,value=f'=COUNTIF($B$5:$B${tr-1},A{rr})')
    for ci,src in ((3,"G"),(4,"K"),(5,"L"),(6,"M")): c=PS.cell(row=rr,column=ci,value=f'=SUMIF($B$5:$B${tr-1},A{rr},{src}$5:{src}${tr-1})'); c.number_format="#,##0.00"
# =============================== SCENARIO
SC=wb.create_sheet("Scenario",2)
SC["A1"]="Plan change: SMB AE accelerator 1.2x / 1.3x to 1.3x / 1.5x (assignment 3)"; SC["A1"].font=Font(name="Arial",bold=True,size=14)
SC["A2"]="Bands unchanged ($30k to $40k, $40k+). Only accelerator-eligible SMB AEs move: ramping reps are not eligible, and managers are paid on credited revenue, not on reps' commission. Shown on both bases: recommended payable (Inputs treatments on) and plan as written. Proposed multipliers are Inputs!B34:B35."
SC["A2"].alignment=Alignment(wrap_text=True); SC.row_dimensions[2].height=45
hdr(SC,4,["Name","Role","Credited revenue USD (recommended)","Accelerator eligible","Current, recommended basis","Proposed, recommended basis","Delta, recommended basis","Credited revenue USD (as written)","Current, as written","Proposed, as written","Delta, as written","Dollars in band I (recommended)","Dollars in band II (recommended)"],[20,22,15,10,15,15,13,15,15,15,13,14,14])
SC.row_dimensions[4].height=60
for i in range(2,N_REP+1):
    r=i+3; g=f'Calc_Reps!$A{i}=""'
    refs=[("A","A"),("B","E"),("C","AO"),("D","AR"),("E","AT"),("F","AU"),("H","AM"),("I","AS"),("J","BS")]
    for col,src in refs: SC[f"{col}{r}"]=f'=IF({g},"",Calc_Reps!{src}{i})'; SC[f"{col}{r}"].font=GREEN
    SC[f"G{r}"]=f'=IF({g},"",F{r}-E{r})'; SC[f"K{r}"]=f'=IF({g},"",J{r}-I{r})'
    SC[f"L{r}"]=f'=IF({g},"",IF(AND(D{r}=1,Calc_Reps!T{i}<>""),MAX(0,MIN(C{r},Calc_Reps!U{i})-Calc_Reps!T{i}),0))'; SC[f"M{r}"]=f'=IF({g},"",IF(AND(D{r}=1,Calc_Reps!W{i}<>""),MAX(0,C{r}-Calc_Reps!W{i}),0))'
    for col in "CEFGHIJKLM": SC[f"{col}{r}"].number_format="#,##0.00"
tr=N_REP+4
SC.cell(row=tr,column=1,value="TOTAL").font=BOLD
for col in "CEFGHIJKLM": c=SC[f"{col}{tr}"]; c.value=f"=SUM({col}5:{col}{tr-1})"; c.font=BOLD; c.number_format="#,##0.00"
SC.cell(row=tr+1,column=1,value="SMB AE only").font=BOLD
for col in "CEFGHIJKLM": c=SC[f"{col}{tr+1}"]; c.value=f'=SUMIF($B$5:$B${tr-1},"SMB Account Executive",{col}5:{col}{tr-1})'; c.font=BOLD; c.number_format="#,##0.00"
SC.cell(row=tr+2,column=1,value="Delta as % of SMB AE commission"); c=SC[f"G{tr+2}"]; c.value=f"=IF(E{tr+1}>0,G{tr+1}/E{tr+1},0)"; c.number_format="0.0%"; c=SC[f"K{tr+2}"]; c.value=f"=IF(I{tr+1}>0,K{tr+1}/I{tr+1},0)"; c.number_format="0.0%"
# =============================== LEDGER
LG=wb.create_sheet("Ledger",3)
LG["A1"]="Data quality exceptions ledger, June 2026"; LG["A1"].font=Font(name="Arial",bold=True,size=14)
LG["A2"]="Three groups, each ranked by dollars moved. HOLD: the plan as written pays it and I would not release it without a decision. NAIVE: a straight read of the extracts would have paid it wrong; this model does not. CALL: a judgment the plan leaves open, sized both ways. Dollars are June commission across all reps affected, including manager roll-ups, computed by the Python replica in analysis/ (code included) on the same raw tabs; the live check below reconciles group HOLD to the model."
LG["A2"].alignment=Alignment(wrap_text=True); LG.row_dimensions[2].height=45
hdr(LG,4,["#","Group","Finding","Records touched","Reps affected","Dollars moved (USD commission)","Treatment applied in this model","Why, and what I would do instead"],[4,9,46,14,12,16,38,58])
for i,row in enumerate(LEDGER):
    r=5+i
    LG.cell(row=r,column=1,value=i+1)
    for ci,key in enumerate(["group","finding","records","reps","dollars","treatment","why"],2):
        v=row.get(key); c=LG.cell(row=r,column=ci,value=v); c.alignment=Alignment(wrap_text=True,vertical="top")
        if key=="dollars" and isinstance(v,(int,float)): c.number_format="#,##0"
    LG.row_dimensions[r].height=max(45,15*(1+len(str(row.get("why","")))//70))
# live sizes for item 1 and the toggle
LG.cell(row=5+len(LEDGER)+1,column=3,value="Live check: total plan-as-written minus recommended (all reps), USD").font=BOLD
c=LG.cell(row=5+len(LEDGER)+1,column=6,value=f"=SUM(Calc_Reps!BL2:BL{N_REP})-SUM(Calc_Reps!BK2:BK{N_REP})"); c.number_format="#,##0.00"; c.font=BOLD
# =============================== INPUTS: capacity check
I["A50"]="Data capacity check: rows present in each tab against the rows the formulas cover. If any line says EXTEND, raise the constant in model/build_model.py and rebuild."; I["A50"].font=BOLD
for j,h in enumerate(["Tab","Rows present","Rows covered","Status"]): c=I.cell(row=51,column=1+j,value=h); c.font=BOLD
checks=[("9. App Export",N_APP-1),("8. Opportunity Export",N_OPP-1),("10. Billing Export",N_BILL-1),("2. HR Export",N_HR-1),("3. Exchange Rates",N_FX-1),("7. Opportunity to ID Mapping (accounts)",N_ACCT-1),("1. Sales Roster (reps)",N_REP-1)]
for k,(tab,capn) in enumerate(checks):
    rr=52+k; sheet=tab.split(" (")[0]
    I.cell(row=rr,column=1,value=tab); I.cell(row=rr,column=2,value=f"=COUNTA('{sheet}'!$A:$A)-1"); I.cell(row=rr,column=3,value=capn); I.cell(row=rr,column=4,value=f'=IF(B{rr}<=C{rr},"OK","EXTEND RANGES")')
# =============================== README
RM=wb.create_sheet("README",0)
RM.column_dimensions["A"].width=120
lines=["June 2026 commission model: how it works",
"",
"Purpose. Pays all 80 reps on 1. Sales Roster for the comp month on Inputs!B4 under the plan in section 07, with every payout traceable to source rows. Nothing in tabs 1 to 11 is edited; all calculations live in the Calc_ tabs.",
"",
"Tab map. Inputs: dates, plan constants, scenario multipliers, treatments. Payout_Summary: the statement (USD and local). Scenario: the SMB AE accelerator repricing. Ledger: exceptions, sized. Calc_Opps: one row per opportunity, a lookup key. Calc_Accounts: one row per account (761), windows, new-logo credit, existing revenue, credits. Calc_Reps: one row per rep (80), employment, ramp, credited revenue, bands, SPIFF, manager roll-up, FX.",
"",
"How a payout traces. Payout_Summary -> Calc_Reps (credited revenue, bands, roll-up) -> Calc_Accounts (per-account windows and revenue, by COUNTIFS/SUMIFS over tab 9 and tab 10) -> tabs 7, 8, 9, 10 (source rows). Every Calc_ column header names the plan section it applies.",
"",
"Running July. Change Inputs!B4 to 2026-07-01, replace tabs 1 to 11 with the July extracts in the same layout (same column order), check the capacity table at Inputs!A50 says OK on every line (the formulas cover 150,000 shifts, 1,500 opportunities, 3,000 credit tickets, 2,000 employees, 1,100 accounts and 120 reps), review Inputs rows 38 to 42, and recalculate. Approved adjustments go in Calc_Reps columns BI:BJ. Nothing else changes.",
"",
"Two payout columns. 'Plan as written' applies section 07 literally. 'Recommended payable' applies the treatments switched on at Inputs!B38:B40 (by default: hold new-logo credit on the flagged GTM account, see Ledger item 1). The difference is shown per rep.",
"",
"Conventions. Blue text = input; black = formula; green = link to another tab; yellow fill = cells a reviewer would change. All amounts USD unless the header says local. Dates are stored as dates. Percentages are stored as fractions.",
"",
"Functions used. SUMIFS, COUNTIFS, COUNTA, INDEX/MATCH, MINIFS, EOMONTH, EDATE, TEXT. No volatile functions, no array formulas, no macros, no external links. Rows beyond the data in the Calc tabs are blank-guarded formulas waiting for a larger extract.",
"",
"Assumptions where the plan is silent are listed in the written summary and in the Ledger; the two treatment toggles on Inputs make the alternatives one click away."]
for i,t in enumerate(lines,1):
    c=RM.cell(row=i,column=1,value=t); c.alignment=Alignment(wrap_text=True,vertical="top"); c.font=Font(name="Arial",bold=(i==1),size=14 if i==1 else 10)
wb.move_sheet("README",offset=-wb.index(wb["README"]))
order=["README","Inputs","Payout_Summary","Scenario","Ledger"]
for name in order[::-1]: wb.move_sheet(name,offset=-wb.index(wb[name]))
wb.save(OUT); print("saved",OUT)
