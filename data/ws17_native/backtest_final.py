import pandas as pd, numpy as np
df = pd.read_parquet('/home/coder/projects/strategy/data/ws17_native/all_native.parquet').reset_index()
df['expiry_dt'] = pd.to_datetime(df['expiry']); df['dte'] = (df['expiry_dt']-df['ts']).dt.days
# normalize prices to SY units
for c in ['ptPrice','ytPrice','syPrice']:
    df[c] = pd.to_numeric(df[c], errors='coerce')
df['pt_rel'] = df['ptPrice']/df['syPrice']; df['yt_rel'] = df['ytPrice']/df['syPrice']
H = 30
markets = ['PT-sUSDe-31JUL2025','PT-sUSDe-25SEP2025','PT-sUSDe-07MAY2026','PT-sUSDe-13AUG2026','PT-sUSDe-26NOV2026',
           'PT-sUSDS-26NOV2026','PT-wstETH-30DEC2027','PT-sUSDe-22OCT2026','PT-AUSD-17DEC2026','PT-earnAUSD-08OCT2026','PT-AUSD-08OCT2026']
def run(g, cond, side, h=H):
    g = g.sort_values('ts').reset_index(drop=True)
    trail30 = g['underlyingApy'].shift(1).rolling(30, min_periods=20).mean()
    res=[]
    for i in range(len(g)):
        if np.isnan(trail30.iloc[i]) or g['dte'].iloc[i] <= 7: continue
        imp, tr = g['impliedApy'].iloc[i], trail30.iloc[i]
        if not cond(imp, tr): continue
        t1 = min(i + h, len(g)-1)
        days = (g['ts'].iloc[t1]-g['ts'].iloc[i]).days
        if days <= 0: continue
        exp_day = g['dte'].iloc[t1] <= 1
        acc = (g['underlyingApy'].iloc[i:t1]/365).sum()
        pin = g['pt_rel' if side=='PT' else 'yt_rel'].iloc[i]
        if pin <= 0 or np.isnan(pin): continue
        pout = (1.0 if exp_day else g['pt_rel' if side=='PT' else 'yt_rel'].iloc[t1]) if side=='PT' else (0.0 if exp_day else g['yt_rel'].iloc[t1])
        ret = (pout-pin)/pin if side=='PT' else (pout+acc-pin)/pin
        res.append(dict(market=g['market'].iloc[i], ts=g['ts'].iloc[i], days=days, ret_ann=ret*365/days, bench_ann=acc*365/days))
    r=pd.DataFrame(res)
    if len(r): r['excess_bp']=(r['ret_ann']-r['bench_ann'])*1e4
    return r
def pooled(cond, side, label):
    rs=[run(df[df['market']==mk], cond, side) for mk in markets]; rs=[r for r in rs if len(r)]
    if not rs: print(f"{label}: нет сигналов"); return None
    a=pd.concat(rs)
    per=a.groupby('market')['excess_bp'].agg(['count','mean'])
    per['hit']=(a.assign(pos=a.excess_bp>0).groupby('market')['pos'].mean()*100)
    ew = per['mean'].mean()
    print(f"\n=== {label} [{side}] ===")
    pd.set_option('display.width',200); pd.set_option('display.float_format', lambda v:f'{v:,.0f}')
    print(per.rename(columns={'mean':'mean_bp'}).to_string())
    print(f"POOL n={len(a)}: mean={a['excess_bp'].mean():+.0f} б.п., hit={(a['excess_bp']>0).mean()*100:.0f}%, equal-weight по рынкам={ew:+.0f} б.п.")
    return a
A = pooled(lambda i,t: True, 'PT', 'R0: покупать PT безусловно (каждый день, MTM 30д)')
B = pooled(lambda i,t: i < t, 'PT', 'Rа: PT при implied < trail30 (правило польз.)')
C = pooled(lambda i,t: i > t, 'PT', 'Rinv: PT при implied > trail30 (инверсия)')
D = pooled(lambda i,t: i > t+0.01, 'YT', 'Rб: YT при implied > trail30 (правило польз.)')
for x,lbl in [(0.01,'+100б.п.'),(0.02,'+200б.п.')]:
    pooled(lambda i,t,xx=x: i > t+xx, 'PT', f'Rinv{lbl}: PT при implied > trail30 {lbl}')
    pooled(lambda i,t,xx=x: i > t+xx, 'YT', f'Rб{lbl}: YT при implied > trail30 {lbl}')
