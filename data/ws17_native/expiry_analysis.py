import pandas as pd, numpy as np
df = pd.read_parquet('/home/coder/projects/strategy/data/ws17_native/all_native.parquet').reset_index()
df['expiry_dt']=pd.to_datetime(df['expiry']); df['dte']=(df['expiry_dt']-df['ts']).dt.days
def prep(g):
    g=g.sort_values('ts').reset_index(drop=True)
    invar=(g['ptPrice']+g['ytPrice']).mean()
    if invar>1.5: g['pt_u']=g['ptPrice']/g['syPrice']
    else: g['pt_u']=g['ptPrice']
    return g
# completed markets (for realized-to-expiry)
comp=['PT-sUSDe-31JUL2025','PT-sUSDe-25SEP2025','PT-sUSDe-07MAY2026','PT-sUSDe-13AUG2026','PT-earnAUSD-08OCT2026','PT-AUSD-08OCT2026']
print("=== Implied при входе vs РЕАЛИЗОВАННО к погашению (hold-to-expiry, PT фиксация) ===")
print("бакеты по дням до экспирации; excess = implied_входа − realized_ср.underlying_до_погашения (б.п.)")
rows=[]
for mk in comp:
    g=prep(df[df['market']==mk]).reset_index(drop=True)
    for i in range(len(g)):
        dte=g['dte'].iloc[i]
        if dte<1 or dte>120: continue
        tail=g['underlyingApy'].iloc[i:]; realized=tail.mean()  # avg realized apy to expiry
        imp=g['impliedApy'].iloc[i]
        if imp>2 or imp<-0.5: continue  # sanity: APY artifacts
        rows.append(dict(market=mk, dte=dte, excess_bp=(imp-realized)*1e4))
r=pd.DataFrame(rows)
bins=[(1,7),(8,14),(15,30),(31,60),(61,120)]
print(f"{'бакет':>10s} {'n':>5s} {'median':>8s} {'mean':>8s} {'hit(>0)':>8s}")
for lo,hi in bins:
    b=r[(r.dte>=lo)&(r.dte<=hi)]
    if len(b)==0: continue
    print(f"{lo:>3d}-{hi:<4d}   {len(b):>5d} {b.excess_bp.median():>8.0f} {b.excess_bp.mean():>8.0f} {(b.excess_bp>0).mean()*100:>7.0f}%")
print("\n=== по рынкам (все dte 1-120) ===")
print(r.groupby('market')['excess_bp'].agg(['count','median','mean']).assign(hit=r.assign(p=r.excess_bp>0).groupby('market')['p'].mean()*100).round(0).to_string())
# TVL dynamics before expiry (LP pull-out)
print("\n=== TVL LP перед экспирацией (норм. к макс за 90д до эксп.) ===")
for mk in comp:
    g=prep(df[df['market']==mk]).sort_values('ts')
    tvl=g['tvl']
    for lo,hi,label in [(75,60,'75-61дн'),(60,31,'60-31дн'),(30,15,'30-16дн'),(14,8,'14-8дн'),(7,1,'7-1дн')]:
        sel=g[(g.dte>=lo)&(g.dte<=hi)]
        if len(sel)==0: continue
        base=g[(g.dte>=lo)&(g.dte<=90)]['tvl'].max()
        # normalize each day to TVL at ~90dte
        t90=g[g.dte<=90].sort_values('dte',ascending=False)['tvl'].iloc[0]
        print(f"{mk:24s} {label}: median TVL/TVL@90dte = {sel['tvl'].median()/t90*100:5.1f}%  (n={len(sel)})")
    print()
