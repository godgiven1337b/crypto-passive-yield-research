import pandas as pd, numpy as np
df = pd.read_parquet('/home/coder/projects/strategy/data/ws17_native/all_native.parquet').reset_index()
df['expiry_dt'] = pd.to_datetime(df['expiry'])
df['dte'] = (df['expiry_dt'] - df['ts']).dt.days
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
        exp_day = g['dte'].iloc[t1] <= 0
        acc = (g['underlyingApy'].iloc[i:t1]/365).sum()
        p_out = (1.0 if exp_day else g['ptPrice'].iloc[t1]) if side=='PT' else (0.0 if exp_day else g['ytPrice'].iloc[t1])
        p_in = g['ptPrice' if side=='PT' else 'ytPrice'].iloc[i]
        if p_in <= 0: continue
        ret = (p_out - p_in)/p_in if side=='PT' else (p_out + acc - p_in)/p_in
        res.append(dict(market=g['market'].iloc[i], ts=g['ts'].iloc[i], days=days,
                        ret_ann=ret*365/days, bench_ann=acc*365/days))
    r = pd.DataFrame(res)
    if len(r): r['excess']=r['ret_ann']-r['bench_ann']
    return r
def pooled(cond, side, label):
    rs=[run(df[df['market']==mk], cond, side) for mk in markets]
    rs=[r for r in rs if len(r)]
    if not rs: print(label,'нет сигналов'); return
    a=pd.concat(rs)
    # per-market excess mean, then equal-weight across markets (avoid one market dominating)
    per = a.groupby('market')['excess'].agg(['mean','count','std'])
    per['hit']=a[a.excess>0].groupby('market').size()/per['count']*100
    print(f"\n=== {label} (side={side}) ===")
    pd.set_option('display.width',200); pd.set_option('display.float_format', lambda v:f'{v:,.1f}')
    print((per.assign(mean_bp=per['mean']*100))[['count','mean_bp','hit']].to_string())
    print(f"пул: n={len(a)}, mean_excess={a['excess'].mean()*100:+.1f} б.п., hit={(a['excess']>0).mean()*100:.0f}%, equal-weight-рынки={per['mean_bp'].mean():+.1f} б.п.")
pooled(lambda i,t: True, 'PT', 'UNCONDITIONAL: покупать PT каждый день')
pooled(lambda i,t: i > t + 0.01, 'PT', 'PT при implied > trail30 (инверсия правила-б)')
pooled(lambda i,t: i > t + 0.01, 'PT', 'PT при implied > trail30 + 100б.п.'.replace(' + 100б.п.',' + 100б.п.'), )
