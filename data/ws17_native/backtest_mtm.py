import pandas as pd, numpy as np
df = pd.read_parquet('/home/coder/projects/strategy/data/ws17_native/all_native.parquet').reset_index()
df['expiry_dt'] = pd.to_datetime(df['expiry'])
df['dte'] = (df['expiry_dt'] - df['ts']).dt.days
H = 30
def run_market(g, X_bp, side):
    g = g.sort_values('ts').reset_index(drop=True)
    trail30 = g['underlyingApy'].shift(1).rolling(30, min_periods=20).mean()
    res = []
    for i in range(len(g)):
        if np.isnan(trail30.iloc[i]) or g['dte'].iloc[i] <= 7: continue
        imp, tr = g['impliedApy'].iloc[i], trail30.iloc[i]
        sig_pt = imp < tr - X_bp/1e4
        sig_yt = imp > tr + X_bp/1e4
        if (side=='PT' and not sig_pt) or (side=='YT' and not sig_yt): continue
        t0 = i; t1 = min(i + H, len(g)-1)
        # если t1 не дошёл до конца ряда и рынок ещё жив — выход по цене в t1
        days = (g['ts'].iloc[t1] - g['ts'].iloc[t0]).days
        if days <= 0: continue
        exp_day = g['dte'].iloc[t1] <= 0
        acc = (g['underlyingApy'].iloc[t0:t1]/365).sum()  # accrued underlying за период
        bench = acc  # buy-and-hold underlying
        if side=='PT':
            p_out = 1.0 if exp_day else g['ptPrice'].iloc[t1]
            p_in = g['ptPrice'].iloc[t0]
            ret = (p_out - p_in)/p_in
        else:
            p_out = 0.0 if exp_day else g['ytPrice'].iloc[t1]
            p_in = g['ytPrice'].iloc[t0]
            ret = (p_out + acc - p_in)/p_in
        res.append(dict(ts=g['ts'].iloc[t0], days=days, ret_ann=ret*365/days, bench_ann=bench*365/days))
    r = pd.DataFrame(res)
    if len(r)==0: return r
    r['excess'] = (r['ret_ann'] - r['bench_ann'])*100
    return r
markets = ['PT-sUSDe-31JUL2025','PT-sUSDe-25SEP2025','PT-sUSDe-07MAY2026','PT-sUSDe-13AUG2026','PT-sUSDe-26NOV2026',
           'PT-sUSDS-26NOV2026','PT-wstETH-30DEC2027','PT-sUSDe-22OCT2026','PT-AUSD-17DEC2026','PT-earnAUSD-08OCT2026','PT-AUSD-08OCT2026']
summary=[]
agg_all = {}
for side in ['PT','YT']:
    for X in [0,100,200]:
        allr=[]
        for mk in markets:
            g = df[df['market']==mk]
            r = run_market(g, X, side)
            if len(r)>0:
                allr.append(r.assign(market=mk))
                summary.append(dict(side=side, X=X, market=mk, n=len(r), avg_excess_bp=r['excess'].mean(), hit=(r['excess']>0).mean()*100))
        a = pd.concat(allr) if allr else pd.DataFrame()
        if len(a):
            # aggregate per-signal-day, avoid overlapping double count: mean of daily excess
            agg_all[(side,X)] = dict(n=len(a), pooled_excess_bp=a['excess'].mean(), hit=(a['excess']>0).mean()*100)
print("=== ПООРЫНОЧНО (excess vs buy-hold underlying, б.п. годовых) ===")
s = pd.DataFrame(summary)
pd.set_option('display.width',250); pd.set_option('display.float_format', lambda v:f'{v:,.0f}')
print(s.to_string(index=False))
print("\n=== ПУЛ ПО СИГНАЛАМ ===")
for k,v in agg_all.items(): print(k, {kk:(round(vv,1) if isinstance(vv,float) else vv) for kk,vv in v.items()})
