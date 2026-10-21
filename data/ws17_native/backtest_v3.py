import pandas as pd, numpy as np
df = pd.read_parquet('/home/coder/projects/strategy/data/ws17_native/all_native.parquet').reset_index()
df['expiry_dt']=pd.to_datetime(df['expiry']); df['dte']=(df['expiry_dt']-df['ts']).dt.days
for c in ['ptPrice','ytPrice','syPrice','impliedApy','underlyingApy']:
    df[c]=pd.to_numeric(df[c],errors='coerce')
def prep(g):
    g=g.sort_values('ts').reset_index(drop=True)
    invar=(g['ptPrice']+g['ytPrice']).mean()
    if invar>1.5:  # USD format -> normalize to SY units
        g['pt_u']=g['ptPrice']/g['syPrice']; g['yt_u']=g['ytPrice']/g['syPrice']
    else:
        g['pt_u']=g['ptPrice']; g['yt_u']=g['ytPrice']
    return g
markets=['PT-sUSDe-31JUL2025','PT-sUSDe-25SEP2025','PT-sUSDe-07MAY2026','PT-sUSDe-13AUG2026','PT-sUSDe-26NOV2026',
         'PT-sUSDS-26NOV2026','PT-wstETH-30DEC2027','PT-sUSDe-22OCT2026','PT-AUSD-17DEC2026','PT-earnAUSD-08OCT2026','PT-AUSD-08OCT2026']
G={mk:prep(df[df['market']==mk]) for mk in markets}
def run(g,cond,side,h=30):
    trail30=g['underlyingApy'].shift(1).rolling(30,min_periods=20).mean()
    res=[]
    for i in range(len(g)):
        if np.isnan(trail30.iloc[i]) or g['dte'].iloc[i]<=7: continue
        imp,tr=g['impliedApy'].iloc[i],trail30.iloc[i]
        if not cond(imp,tr): continue
        t1=min(i+h,len(g)-1); days=(g['ts'].iloc[t1]-g['ts'].iloc[i]).days
        if days<=0: continue
        exp_day=g['dte'].iloc[t1]<=1
        acc=(g['underlyingApy'].iloc[i:t1]/365).sum()
        pin=g['pt_u' if side=='PT' else 'yt_u'].iloc[i]
        if pin<=0 or np.isnan(pin): continue
        if side=='PT':
            pout=1.0 if exp_day else g['pt_u'].iloc[t1]
            ret=(pout-pin)/pin
        else:
            pout=0.0 if exp_day else g['yt_u'].iloc[t1]
            ret=(pout+acc-pin)/pin
        res.append(dict(market=g['market'].iloc[i],ts=g['ts'].iloc[i],days=days,ret_ann=ret*365/days,bench_ann=acc*365/days))
    r=pd.DataFrame(res)
    if len(r): r['excess_bp']=(r['ret_ann']-r['bench_ann'])*1e4
    return r
def pooled(cond,side,label,silent=False):
    rs=[run(G[mk],cond,side) for mk in markets]; rs=[r for r in rs if len(r)]
    if not rs: print(f"{label}: нет сигналов"); return None
    a=pd.concat(rs)
    per=a.groupby('market')['excess_bp'].agg(['count','mean','median'])
    per['hit']=a.assign(p=a.excess_bp>0).groupby('market')['p'].mean()*100
    if not silent:
        pd.set_option('display.width',200); pd.set_option('display.float_format',lambda v:f'{v:,.0f}')
        print(f"\n=== {label} [{side}] ===")
        print(per.rename(columns={'mean':'mean_bp','median':'med_bp'}).to_string())
        # block bootstrap CI on pooled mean (block=7d, 1000 iter)
        x=a['excess_bp'].values; n=len(x); bs=[]
        rng=np.random.default_rng(7); B=7
        nb=n//B
        if nb>2:
            for _ in range(1000):
                idx=np.concatenate([rng.integers(0,n-B,B)[:,None]+np.arange(B)[None,:]]).ravel()[:n]
                bs.append(x[idx].mean())
            lo,hi=np.percentile(bs,[2.5,97.5])
        else: lo,hi=np.nan,np.nan
        print(f"POOL n={n}: mean={a['excess_bp'].mean():+.0f} б.п. (95% CI [{lo:+.0f}, {hi:+.0f}]), median={a['excess_bp'].median():+.0f}, hit={(a['excess_bp']>0).mean()*100:.0f}%")
    return a
pooled(lambda i,t:True,'PT','R0: PT безусловно (30д MTM)')
pooled(lambda i,t:i<t,'PT','Rа: PT при implied < trail30')
pooled(lambda i,t:i>t,'PT','Rinv: PT при implied > trail30')
pooled(lambda i,t:i>t+0.01,'PT','Rinv100: PT при implied > trail30+100б.п.')
pooled(lambda i,t:i>t+0.02,'PT','Rinv200: PT при implied > trail30+200б.п.')
pooled(lambda i,t:i>t,'YT','Rб: YT при implied > trail30')
pooled(lambda i,t:i>t+0.01,'YT','Rб100: YT при implied > trail30+100б.п.')
pooled(lambda i,t:i<t,'YT','Rб-: YT при implied < trail30')
