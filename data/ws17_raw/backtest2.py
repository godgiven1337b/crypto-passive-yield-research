import pandas as pd, numpy as np
df = pd.read_parquet('/home/coder/projects/strategy/data/ws17_raw/merged.parquet').sort_index()
df.columns = [c[0] for c in df.columns]
pairs = [
 ('PT-wstETH-30DEC2027', 'pt_wsteth_30DEC2027', 'und_steth_lido'),
 ('PT-sUSDS-26NOV2026', 'pt_susds_26NOV2026', 'und_susds_sky'),
 ('PT-sUSDe-22OCT2026-Monad', 'pt_susde_22OCT2026_monad', 'und_susde_ethena'),
]
H = 30
print("=== RULE PT-BUY: implied > trail30 + X (инверсия YT-правила) ===")
rows=[]
for name, p, u in pairs:
    sub = df[[p,u]].dropna()
    imp, und = sub[p], sub[u]
    trail30 = und.shift(1).rolling(30, min_periods=20).mean()
    fwd30 = und.rolling(H).mean().shift(-H)
    bt = pd.DataFrame({'imp':imp,'trail30':trail30,'fwd':fwd30}).dropna()
    for X in [0, 100, 200]:
        sig = bt['imp'] > bt['trail30'] + X/1e4*100
        ex = (bt['imp'] - bt['fwd'])[sig]
        # Newey-West t-stat of daily excess among signal days
        e = ex.dropna().values; e = e - e.mean(); n=len(e)
        if n>5:
            g0=(e*e).sum()/n; s=g0
            for L in range(1, min(10,n//5)):
                g=(e[L:]*e[:-L]).sum()/n; s+=2*(1-L/11)*g
            t = ex.mean()/np.sqrt(s/n)*np.sqrt(1)  # t-stat of mean daily excess
        else: t=np.nan
        rows.append(dict(market=name, X=X, n=int(sig.sum()), avg_excess_bp=ex.mean()*100 if len(ex) else np.nan,
                         hit=(ex>0).mean()*100 if len(ex) else np.nan, t=t))
out=pd.DataFrame(rows); pd.set_option('display.width',200); pd.set_option('display.float_format', lambda v:f'{v:,.1f}')
print(out.to_string(index=False))
