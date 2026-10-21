import pandas as pd, numpy as np
df = pd.read_parquet('/home/coder/projects/strategy/data/ws17_native/all_native.parquet').reset_index()
df['expiry_dt']=pd.to_datetime(df['expiry']); df['dte']=(df['expiry_dt']-df['ts']).dt.days
g=df[df['market']=='PT-sUSDe-07MAY2026'].sort_values('ts').reset_index(drop=True)
print(g[['ts','dte','impliedApy','underlyingApy','ptPrice','ytPrice','syPrice']].iloc[[0,1,2,20,40,60,80,100,117]].to_string())
# check invariant pt+yt=sy
chk=(g['ptPrice']+g['ytPrice']-g['syPrice']).abs().max()
print('max |pt+yt-sy| =', chk, ' syPrice range:', g['syPrice'].min(), g['syPrice'].max())
# implied from rel price
g['pt_rel']=g['ptPrice']/g['syPrice']
g['imp_rel']=(1/g['pt_rel']-1)*365/g['dte']
print(g[['ts','dte','impliedApy','imp_rel']].iloc[[0,20,40,60,80,100]].to_string())
