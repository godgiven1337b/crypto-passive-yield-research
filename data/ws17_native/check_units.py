import pandas as pd, numpy as np, json
df = pd.read_parquet('/home/coder/projects/strategy/data/ws17_native/all_native.parquet').reset_index()
df['expiry_dt']=pd.to_datetime(df['expiry']); df['dte']=(df['expiry_dt']-df['ts']).dt.days
for mk in ['PT-sUSDe-31JUL2025','PT-wstETH-30DEC2027','PT-sUSDe-26NOV2026']:
    g=df[df['market']==mk].sort_values('ts').reset_index(drop=True)
    for i in [30, len(g)//2, len(g)-40]:
        r=g.iloc[i]
        ttm=r['dte']
        imp_from_price=(1/r['ptPrice']-1)*365/ttm*100 if ttm>0 and r['ptPrice']>0 else np.nan
        print(f"{mk} {r['ts'].date()} dte={ttm} ptPrice={r['ptPrice']:.4f} ytPrice={r['ytPrice']:.5f} impliedApy={r['impliedApy']*100:.2f}% implied_from_price={imp_from_price:.2f}% underlying={r['underlyingApy']*100:.2f}%")
    # actual 30d MTM example
    i=len(g)//2; r0=g.iloc[i]; t1=min(i+30,len(g)-1); r1=g.iloc[t1]
    days=(r1['ts']-r0['ts']).days
    ret=(r1['ptPrice']-r0['ptPrice'])/r0['ptPrice']*365/days*100
    acc=(g['underlyingApy'].iloc[i:t1]/365).sum()*365/days*100
    print(f"  -> 30d MTM: PT ret={ret:.2f}% ann, underlying={acc:.2f}% ann, excess={ret-acc:+.2f} п.п.\n")
