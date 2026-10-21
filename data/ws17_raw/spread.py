import pandas as pd, numpy as np
df = pd.read_parquet('/home/coder/projects/strategy/data/ws17_raw/merged.parquet').sort_index()
df.columns = [c[0] for c in df.columns]
pairs = [
 ('PT-wstETH-30DEC2027 (ETH)', 'pt_wsteth_30DEC2027', 'und_steth_lido'),
 ('PT-sUSDS-26NOV2026 (ETH)', 'pt_susds_26NOV2026', 'und_susds_sky'),
 ('LP-sUSDe-26NOV2026 (ETH, proxy implied=LP APY-без инцентивов?)', 'lp_susde_26NOV2026', 'und_susde_ethena'),
 ('PT-sUSDe-22OCT2026 (Monad)', 'pt_susde_22OCT2026_monad', 'und_susde_ethena'),
 ('PT-AUSD-17DEC2026 (Monad)', 'pt_ausd_17DEC2026_monad', 'und_susde_ethena'),
]
def nw_tstat(x, lags=10):
    e = np.asarray(x, dtype=float); e = e - np.nanmean(e)
    e = e[~np.isnan(e)]
    n = len(e); m = np.nanmean(np.asarray(x, dtype=float)); g0 = (e*e).sum()/n; s = g0
    for L in range(1, min(lags, n//5)):
        g = (e[L:]*e[:-L]).sum()/n; s += 2*(1-L/(lags+1))*g
    return m/np.sqrt(s/n) if s>0 else np.nan
rows=[]
for name, p, u in pairs:
    sub = df[[p,u]].dropna()
    if len(sub) < 20: continue
    # window: last 12 months if longer
    sub12 = sub[sub.index >= sub.index.max() - pd.Timedelta(days=365)]
    sp = (sub12[p] - sub12[u])
    sp_all = (sub[p]-sub[u])
    ac = sp.autocorr(1)
    # AR1 half-life
    x = sp.shift(1); y = sp
    mask = (~x.isna())&(~y.isna())
    if mask.sum()>10:
        phi = np.polyfit(x[mask], y[mask], 1)[0]
        hl = (np.log(0.5)/np.log(abs(phi)) if 0<abs(phi)<1 else np.inf)
    else: phi, hl = np.nan, np.nan
    rows.append(dict(market=name, n=len(sp), mean=sp.mean(), median=sp.median(), std=sp.std(),
                     pct_neg=(sp<0).mean()*100, tstat=nw_tstat(sp), ac1=ac, ar1=phi, half_life_d=hl,
                     mean_all=sp_all.mean(), n_all=len(sp_all)))
out = pd.DataFrame(rows)
pd.set_option('display.width', 250); pd.set_option('display.float_format', lambda v: f'{v:,.2f}')
print(out.to_string(index=False))
