import pandas as pd, numpy as np
df = pd.read_parquet('/home/coder/projects/strategy/data/ws17_native/all_native.parquet').reset_index()
df['expiry_dt']=pd.to_datetime(df['expiry']); df['dte']=(df['expiry_dt']-df['ts']).dt.days
comp=['PT-sUSDe-31JUL2025','PT-sUSDe-25SEP2025','PT-sUSDe-07MAY2026','PT-sUSDe-13AUG2026','PT-earnAUSD-08OCT2026','PT-AUSD-08OCT2026','PT-sUSDe-22OCT2026']
print("TVL рынка (USDe-единицы/$) в бакетах до экспирации, норм. к значению при dte=90")
for mk in comp:
    g=df[df['market']==mk].sort_values('ts')
    t90=g[g.dte<=92].sort_values('dte',ascending=False)
    if len(t90)==0: print(mk,'нет dte<=92'); continue
    t90v=t90['tvl'].iloc[0]
    parts=[]
    for lo,hi in [(45,60),(16,30),(8,14),(1,7)]:
        sel=g[(g.dte>=lo)&(g.dte<=hi)]
        parts.append(f"{hi:>2d}-{lo:<2d}дн:{sel['tvl'].median()/t90v*100:5.0f}%")
    print(f"{mk:24s} 90дн:{t90v/1e6:5.1f}M  " + "  ".join(parts))
