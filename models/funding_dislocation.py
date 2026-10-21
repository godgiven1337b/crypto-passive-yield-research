"""
funding_dislocation.py — анализ неэффективностей funding/perp-базиса.

1. Кросс-веню фандинг сейчас: где дорого быть лонгом/шортом.
2. История Binance: распределение, частота отрицательных, сезонность (день недели/час),
   автокорреляция (mean-reversion?), условная доходность контрарной ставки.
3. Inversion-детектор: venue A платит long'ам, venue B short'ам одновременно ->
   внутри-рыночный арбитраж (long A + short B = сбор обоих фандингов, дельта 0).

Данные: публичные API Binance/Bybit/OKX/Hyperliquid (fetch_mode) или локальные JSON.
"""
from __future__ import annotations

import json
import os
import statistics
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "microstructure")


def _get(url: str, payload: dict | None = None):
    if payload:
        req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
    else:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def hl_current() -> dict[str, dict]:
    """Текущий фандинг/oi по Hyperliquid.

    ВАЖНО: funding в API HL — ЧАСОВАЯ ставка (аннуализация ×24×365, не ×3×365!).
    Ошибка ×3×365 занижает в 8 раз и создаёт ложную «инверсию» против Binance.
    """
    meta, ctxs = _get("https://api.hyperliquid.xyz/info", {"type": "metaAndAssetCtxs"})
    out = {}
    for m, c in zip(meta["universe"], ctxs):
        if m["name"] in ("BTC", "ETH", "SOL"):
            out[m["name"]] = {
                "funding_hourly": float(c["funding"]),
                "annual_pct": float(c["funding"]) * 24 * 365 * 100,
                "oi_usd": float(c["openInterest"]) * float(c["markPx"]),
                "mark": float(c["markPx"]),
            }
    return out


def binance_current() -> dict[str, float]:
    d = _get("https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT")
    return {"BTC": float(d["lastFundingRate"]) * 3 * 365 * 100}


def binance_history(symbol: str = "BTCUSDT", limit: int = 1000) -> list[dict]:
    out = []
    for start in range(0, limit, 100):
        d = _get(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={symbol}&limit=100&startTime="
                 f"{int(datetime(2026, 8, 1, tzinfo=timezone.utc).timestamp()*1000) + start*8*3600*1000}")
        out.extend(d)
        if len(d) < 100:
            break
    return out


def load_or_fetch(name: str, fetch_fn, *a, **kw):
    path = os.path.join(DATA, name)
    if os.path.exists(path):
        return json.load(open(path))
    data = fetch_fn(*a, **kw)
    os.makedirs(DATA, exist_ok=True)
    json.dump(data, open(path, "w"))
    return data


def funding_stats(history: list[dict]) -> dict:
    """Статистика серии 8-часовых ставок фандинга."""
    rates = [float(h["fundingRate"]) for h in history]
    ann = [r * 3 * 365 * 100 for r in rates]
    n = len(rates)
    neg = sum(1 for r in rates if r < 0)
    # сезонность по дню недели
    by_dow = defaultdict(list)
    by_hour = defaultdict(list)
    for h, r in zip(history, rates):
        t = datetime.fromtimestamp(h["fundingTime"] / 1000, tz=timezone.utc)
        by_dow[t.weekday()].append(r * 3 * 365 * 100)
        by_hour[t.hour].append(r * 3 * 365 * 100)
    dow_avg = {d: statistics.mean(v) for d, v in sorted(by_dow.items())}
    hour_avg = {h: statistics.mean(v) for h, v in sorted(by_hour.items())}
    # автокорреляция lag1, lag3 (сутки)
    def acf(series, lag):
        xs, ys = series[:-lag], series[lag:]
        mx, my = statistics.mean(xs), statistics.mean(ys)
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
        return num / den if den else 0.0
    # условная доходность контрарной ставки: после экстремально низких/высоких
    sorted_r = sorted(rates)
    q20 = sorted_r[int(n * 0.2)]
    q80 = sorted_r[int(n * 0.8)]
    after_low = [rates[i + 1] for i in range(n - 1) if rates[i] <= q20]
    after_high = [rates[i + 1] for i in range(n - 1) if rates[i] >= q80]
    return {
        "n": n,
        "mean_annual_pct": statistics.mean(ann),
        "median_annual_pct": statistics.median(ann),
        "pct_negative": neg / n * 100,
        "p10_annual_pct": sorted(ann)[int(n * 0.1)],
        "p90_annual_pct": sorted(ann)[int(n * 0.9)],
        "acf_lag1": acf(rates, 1),
        "acf_lag3": acf(rates, 3),
        "mean_after_bottom20_pct": statistics.mean(after_low) * 3 * 365 * 100 if after_low else None,
        "mean_after_top20_pct": statistics.mean(after_high) * 3 * 365 * 100 if after_high else None,
        "dow_avg_annual_pct": {str(k): round(v, 2) for k, v in dow_avg.items()},
        "hour_avg_annual_pct": {str(k): round(v, 2) for k, v in hour_avg.items()},
    }


def cross_venue_snapshot() -> list[dict]:
    """Текущий годовой фандинг по площадкам — детектор инверсий."""
    rows = []
    try:
        hl = hl_current()
        for k, v in hl.items():
            rows.append({"venue": "Hyperliquid", "asset": k, "funding_annual_pct": round(v["annual_pct"], 2)})
    except Exception as e:
        rows.append({"venue": "Hyperliquid", "asset": "?", "err": str(e)})
    try:
        for sym, name in [("BTCUSDT", "BTC"), ("ETHUSDT", "ETH"), ("SOLUSDT", "SOL")]:
            d = _get(f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={sym}")
            rows.append({"venue": "Binance", "asset": name,
                         "funding_annual_pct": round(float(d["lastFundingRate"]) * 3 * 365 * 100, 2)})
    except Exception as e:
        rows.append({"venue": "Binance", "err": str(e)})
    try:
        d = _get("https://api.bybit.com/v5/market/tickers?category=linear&symbol=BTCUSDT")
        r = float(d["result"]["list"][0]["fundingRate"])
        rows.append({"venue": "Bybit", "asset": "BTC", "funding_annual_pct": round(r * 3 * 365 * 100, 2)})
    except Exception as e:
        rows.append({"venue": "Bybit", "err": str(e)})
    try:
        d = _get("https://www.okx.com/api/v5/public/funding-rate?instId=BTC-USDT-SWAP")
        r = float(d["data"][0]["fundingRate"])
        rows.append({"venue": "OKX", "asset": "BTC", "funding_annual_pct": round(r * 3 * 365 * 100, 2)})
    except Exception as e:
        rows.append({"venue": "OKX", "err": str(e)})
    return rows


def detect_inversions(rows: list[dict]) -> list[str]:
    """Внутри-рыночный арбитраж: фандинг разных знаков на двух площадках."""
    by_asset = defaultdict(dict)
    for r in rows:
        if "funding_annual_pct" in r:
            by_asset[r["asset"]][r["venue"]] = r["funding_annual_pct"]
    notes = []
    for asset, venues in by_asset.items():
        if len(venues) < 2:
            continue
        vals = sorted(venues.items(), key=lambda kv: kv[1])
        lo, hi = vals[0], vals[-1]
        if lo[1] < 0 < hi[1]:
            spread = hi[1] - lo[1]
            notes.append(f"{asset}: инверсия {lo[0]} {lo[1]:+.1f}% vs {hi[0]} {hi[1]:+.1f}% "
                         f"(спрэд {spread:.1f} п.п.): шорт на {hi[0]} + лонг на {lo[0]} "
                         f"собирает ~{spread:.1f}% годовых фандинга при дельта 0")
    return notes


if __name__ == "__main__":
    print("=== Кросс-веню фандинг (сейчас) ===")
    rows = cross_venue_snapshot()
    for r in rows:
        print(" ", r)
    print("\n=== Инверсии ===")
    for n in detect_inversions(rows) or ["не найдено"]:
        print(" ", n)
    print("\n=== Статистика Binance BTC funding (история) ===")
    hist = load_or_fetch("binance_btc_hist.json", binance_history)
    st = funding_stats(hist)
    for k, v in st.items():
        print(f"  {k}: {v}")
