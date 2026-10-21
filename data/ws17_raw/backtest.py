import pandas as pd, numpy as np
df = pd.read_parquet('/home/coder/projects/strategy/data/ws17_raw/merged.parquet').sort_index()
df.columns = [c[0] for c in df.columns]
pairs = [
 ('PT-wstETH-30DEC2027', 'pt_wsteth_30DEC2027', 'und_steth_lido'),
 ('PT-sUSDS-26NOV2026', 'pt_susds_26NOV2026', 'und_susds_sky'),
 ('PT-sUSDe-22OCT2026-Monad', 'pt_susde_22OCT2026_monad', 'und_susde_ethena'),
 ('LP-sUSDe-26NOV2026(proxy)', 'lp_susde_26NOV2026', 'und_susde_ethena'),
]
H = 30  # holding days
rows = []
for name, p, u in pairs:
    sub = df[[p, u]].dropna()
    if len(sub) < 60: continue
    imp = sub[p]
    und = sub[u]
    trail30 = und.shift(1).rolling(30, min_periods=20).mean()
    fwd30 = und.rolling(H).mean().shift(-H)  # mean over [t, t+H)
    bt = pd.DataFrame({'imp': imp, 'und': und, 'trail30': trail30, 'fwd': fwd30}).dropna()
    for X in [0, 50, 100, 200]:
        sig_pt = bt['imp'] < bt['trail30'] - X/1e4*100
        sig_yt = bt['imp'] > bt['trail30'] + X/1e4*100
        # PT entry: earn implied (fixed) vs underlying fwd
        ex_pt = (bt['imp'] - bt['fwd'])[sig_pt]
        ex_yt = (bt['fwd'] - bt['imp'])[sig_yt]
        rows.append(dict(market=name, X_bp=X,
            PT_signals=int(sig_pt.sum()),
            PT_avg_excess_bp=ex_pt.mean()*100 if len(ex_pt)>0 else np.nan,
            PT_hitrate=(ex_pt>0).mean()*100 if len(ex_pt)>0 else np.nan,
            YT_signals=int(sig_yt.sum()),
            YT_avg_excess_bp=ex_yt.mean()*100 if len(ex_yt)>0 else np.nan,
            YT_hitrate=(ex_yt>0).mean()*100 if len(ex_yt)>0 else np.nan))
    # unconditional: implied vs fwd realized (was implied biased predictor?)
    ex_all = bt['imp'] - bt['fwd']
    rows.append(dict(market=name, X_bp='ALL: imp-fwd', PT_signals=len(bt),
        PT_avg_excess_bp=ex_all.mean()*100, PT_hitrate=(ex_all>0).mean()*100,
        YT_signals=0, YT_avg_excess_bp=np.nan, YT_hitrate=np.nan))
out = pd.DataFrame(rows)
pd.set_option('display.width', 260); pd.set_option('display.float_format', lambda v: f'{v:,.1f}')
print(out.to_string(index=False))
