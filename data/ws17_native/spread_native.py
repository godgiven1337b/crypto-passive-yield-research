import pandas as pd, numpy as np
df = pd.read_parquet('/home/coder/projects/strategy/data/ws17_native/all_native.parquet').reset_index()
df['expiry_dt'] = pd.to_datetime(df['expiry'])
df['dte'] = (df['expiry_dt'] - df['ts']).dt.days
# exclude last 7 days (APY explodes as TTM->0)
core = df[df['dte'] > 7].copy()
core['spread_pp'] = (core['impliedApy'] - core['underlyingApy'])*100
def nw_tstat(x, lags=10):
    e = np.asarray(x, float); e = e - np.nanmean(e); e = e[~np.isnan(e)]; n = len(e)
    if n < 15: return np.nan
    m = np.nanmean(np.asarray(x, float)); g0=(e*e).sum()/n; s=g0
    for L in range(1, min(lags, n//5)):
        g=(e[L:]*e[:-L]).sum()/n; s+=2*(1-L/(lags+1))*g
    return m/np.sqrt(s/n)
rows=[]
for mk, g in core.groupby('market'):
    g = g.sort_values('ts'); sp = g['spread_pp']
    if len(sp) < 15: continue
    x = sp.shift(1); y = sp
    phi = np.polyfit(x[1:], y[1:], 1)[0]
    rows.append(dict(market=mk, n=len(sp), first=g['ts'].min().date(), last=g['ts'].max().date(),
        mean_bp=sp.mean()*100, median_bp=sp.median()*100, std_bp=sp.std()*100,
        pct_days_pos=(sp>0).mean()*100, tstat=nw_tstat(sp), ac1=sp.autocorr(1),
        ar1=phi, hl_days=(np.log(0.5)/np.log(abs(phi)) if 0<abs(phi)<1 else np.inf)))
out = pd.DataFrame(rows)
pd.set_option('display.width',250); pd.set_option('display.float_format', lambda v:f'{v:,.2f}')
print("=== СПРЭД implied − underlying (п.п.→б.п.), дни до экспирации > 7 ===")
print(out.sort_values('market').to_string(index=False))
# stitched ETH sUSDe series
sus = core[core['market'].str.contains('sUSDe') & core['chain'].eq('ethereum')].sort_values(['ts'])
sp = (sus['impliedApy']-sus['underlyingApy'])*100
print("\n=== Сшитая серия PT-sUSDe ETH (5 рынков, 2025-03..2026-10): ===")
print(f"n={len(sus)}, mean={sp.mean()*100:.1f} б.п., median={sp.median()*100:.1f} б.п., pct_pos={(sp>0).mean()*100:.0f}%, t={nw_tstat(sp):.2f}, ac1={sp.autocorr(1):.2f}")
# 12m window only
sus12 = sus[sus['ts'] >= sus['ts'].max() - pd.Timedelta(days=365)]
sp12 = (sus12['impliedApy']-sus12['underlyingApy'])*100
print(f"последние 12 мес: n={len(sus12)}, mean={sp12.mean()*100:.1f} б.п., median={sp12.median()*100:.1f} б.п., pct_pos={(sp12>0).mean()*100:.0f}%, t={nw_tstat(sp12):.2f}")
