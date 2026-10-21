import json, os, pandas as pd, numpy as np
BASE='/home/coder/projects/strategy/data/ws17_native'
META = {
 'eth_susde_20250731': dict(market='PT-sUSDe-31JUL2025', chain='ethereum', expiry='2025-07-31'),
 'eth_susde_20250925': dict(market='PT-sUSDe-25SEP2025', chain='ethereum', expiry='2025-09-25'),
 'eth_susde_20260507': dict(market='PT-sUSDe-07MAY2026', chain='ethereum', expiry='2026-05-07'),
 'eth_susde_20260813': dict(market='PT-sUSDe-13AUG2026', chain='ethereum', expiry='2026-08-13'),
 'eth_susde_20261126': dict(market='PT-sUSDe-26NOV2026', chain='ethereum', expiry='2026-11-26'),
 'eth_susds_20261126': dict(market='PT-sUSDS-26NOV2026', chain='ethereum', expiry='2026-11-26'),
 'eth_wsteth_20271230': dict(market='PT-wstETH-30DEC2027', chain='ethereum', expiry='2027-12-30'),
 'mon_susde_20261022': dict(market='PT-sUSDe-22OCT2026', chain='monad', expiry='2026-10-22'),
 'mon_susde_20270128': dict(market='PT-sUSDe-28JAN2027', chain='monad', expiry='2027-01-28'),
 'mon_ausd_20261217': dict(market='PT-AUSD-17DEC2026', chain='monad', expiry='2026-12-17'),
 'mon_earnausd_20261008': dict(market='PT-earnAUSD-08OCT2026', chain='monad', expiry='2026-10-08'),
 'mon_ausd_20261008': dict(market='PT-AUSD-08OCT2026', chain='monad', expiry='2026-10-08'),
}
rows=[]; frames={}
for k, m in META.items():
    d = json.load(open(f'{BASE}/{k}.json'))
    df = pd.DataFrame(d['results'])
    df['ts'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
    for c in ['impliedApy','underlyingApy','ptPrice','ytPrice','tvl','tradingVolume','baseApy']:
        if c in df: df[c]=pd.to_numeric(df[c], errors='coerce')
    df['market']=m['market']; df['chain']=m['chain']; df['expiry']=m['expiry']
    frames[m['market']]=df.set_index('ts').sort_index()
    for _, r in df.iterrows():
        rows.append(dict(ts=r['ts'].strftime('%Y-%m-%d'), market=m['market'],
            implied=round(float(r['impliedApy'])*100,4), underlying=round(float(r['underlyingApy'])*100,4),
            ptPrice=round(float(r['ptPrice']),6) if pd.notna(r['ptPrice']) else None,
            ytPrice=round(float(r['ytPrice']),6) if pd.notna(r['ytPrice']) else None,
            tvlUsd=round(float(r['tvl']),2) if pd.notna(r['tvl']) else None,
            expiry=m['expiry'], chain=m['chain']))
rows.sort(key=lambda r:(r['market'], r['ts']))
with open('/home/coder/projects/strategy/data/ws17_pendle_history.json','w') as f:
    json.dump(dict(source='Pendle native API api-v2.pendle.finance/core/v3/.../historical-data (day, fields=all), fetched 2026-10-21',
                   fields_note='implied/underlying in % APY; ptPrice/ytPrice in underlying units; tvlUsd market TVL',
                   n_points=len(rows), data=rows), f, indent=0)
print('saved', len(rows), 'points')
all_df = pd.concat(frames)
all_df.to_parquet(f'{BASE}/all_native.parquet')
for mk, df in frames.items():
    print(f"{mk:28s} n={len(df):5d} {df.index.min().date()} .. {df.index.max().date()} implied_last={df['impliedApy'].iloc[-1]*100:.2f}% und_last={df['underlyingApy'].iloc[-1]*100:.2f}%")
