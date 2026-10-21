import json, pandas as pd, numpy as np, glob, os
BASE = '/home/coder/projects/strategy/data/ws17_raw'
def load(name):
    d = json.load(open(f'{BASE}/{name}.json'))
    df = pd.DataFrame(d['data'])
    df['ts'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
    df['date'] = df['ts'].dt.floor('D')
    df = df.drop_duplicates('date').sort_values('date').set_index('date')
    return df[['apyBase']].astype(float).rename(columns={'apyBase': name})
series = {n.split('.json')[0]: load(n.split('.json')[0]) for n in os.listdir(BASE) if n.endswith('.json')}
for k, v in series.items():
    print(k, len(v), v.index.min().date(), v.index.max().date(), 'nan:', int(v.isna().sum().sum()))
# save merged
common = pd.concat(series, axis=1)
common.to_parquet(f'{BASE}/merged.parquet')
print('merged shape', common.shape)
