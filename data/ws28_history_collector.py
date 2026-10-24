#!/usr/bin/env python3
"""WS-28: resolved 5-min window history Limitless <-> PM (frequency analysis)."""
import json, time, urllib.request, datetime, os

LIM = "https://api.limitless.exchange/markets"
GAM = "https://gamma-api.polymarket.com/markets?slug=%s&closed=true"
HDRS = {"User-Agent": "Mozilla/5.0 (research)", "Accept": "application/json"}
OUT = "/home/coder/projects/strategy/data/ws28_resolved_history.json"

def get(url, timeout=12):
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

def ts():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def main():
    now_epoch = int(time.time())
    cur5 = now_epoch - (now_epoch % 300)
    rows = []
    assets = [("btc", "btc-up-or-down-5-min-%d"), ("eth", "eth-up-or-down-5-min-%d")]
    n_windows = int(os.environ.get("NWIN", "150"))
    for a, lpat in assets:
        for k in range(1, n_windows + 1):
            e = cur5 - 300 * k
            slug = lpat % e
            row = {"asset": a, "epoch": e, "utc": datetime.datetime.fromtimestamp(e, datetime.timezone.utc).strftime("%H:%M")}
            try:
                m = get(f"{LIM}/{slug}")
                row["lim_status"] = m.get("status")
                row["lim_win"] = m.get("winningOutcomeIndex")
                row["lim_prices"] = m.get("prices")
                row["lim_trade"] = m.get("tradePrices")
                row["lim_vol"] = m.get("volumeFormatted")
                row["lim_desc_beat"] = None
            except Exception as ex:
                row["lim_err"] = str(ex)[:60]
            time.sleep(0.05)
            try:
                arr = get(GAM % f"{a}-updown-5m-{e}")
                if arr:
                    g = arr[0]
                    row["pm_closed"] = g.get("closed")
                    row["pm_outcomePrices"] = json.loads(g.get("outcomePrices") or "[]")
                    row["pm_volume"] = g.get("volume")
                    row["pm_liquidity"] = g.get("liquidityNum")
                else:
                    row["pm_missing"] = True
            except Exception as ex:
                row["pm_err"] = str(ex)[:60]
            time.sleep(0.05)
            rows.append(row)
            if k % 25 == 0:
                print(f"{a} {k}/{n_windows}", flush=True)
    data = {"meta": {"collected": ts(), "n_windows": n_windows, "step": 300,
                     "note": "final tradePrices/outcomePrices of resolved 5m windows; lim_prices=last trade, pm_outcomePrices=last"},
            "rows": rows}
    json.dump(data, open(OUT, "w"), separators=(",", ":"))
    print("saved", OUT, len(rows), flush=True)

if __name__ == "__main__":
    main()
