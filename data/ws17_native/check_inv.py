import pandas as pd, numpy as np
df = pd.read_parquet('/home/coder/projects/strategy/data/ws17_native/all_native.parquet').reset_index()
for mk, g in df.groupby('market'):
    s = (g['ptPrice']+g['ytPrice'])
    print(f"{mk:26s} pt+yt: mean={s.mean():.4f} std={s.std():.4f} min={s.min():.4f} max={s.max():.4f} | syPrice: {g['syPrice'].mean():.3f}±{g['syPrice'].std():.3f} | pt: {g['ptPrice'].min():.3f}..{g['ptPrice'].max():.3f}")
