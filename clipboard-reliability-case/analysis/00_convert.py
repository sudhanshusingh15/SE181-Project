import pandas as pd, sys, time
S=sys.argv[1]
t=time.time()
for n in ["shifts","cancels"]:
    df=pd.read_excel(f"{S}/data/{n}.xlsx", engine="openpyxl")
    df.to_pickle(f"{S}/data/{n}.pkl")
    df.to_csv(f"{S}/data/{n}.csv", index=False)
    print(n, df.shape, f"{time.time()-t:.0f}s"); print(df.dtypes.to_string()); print()
