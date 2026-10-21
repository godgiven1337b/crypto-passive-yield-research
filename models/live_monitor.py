"""
live_monitor.py — живой монитор неэффективностей (одиночный снимок + алерты).

Что мониторит:
  1. Кросс-веню фандинг BTC/ETH/SOL (Binance/Bybit/OKX/Hyperliquid): расхождения >4 п.п.
  2. Депеги квази-стейблов (USDe, USDC, USDT, USDS): отклонение >50 б.п. от $1
  3. Дисконт LST: wstETH/ETH рыночный коэффициент vs redemption (грубая проверка >30 б.п.)
  4. PT-дисконты Pendle: sUSDe/sUSDS (дисконт к exchange rate)
  5. Апдейт: сравнение с прошлым снимком (data/microstructure/last_snapshot.json)

Запуск: python3 models/live_monitor.py
Крон: каждые 1-4 часа; алерты пишет в stdout + data/microstructure/alerts.log
"""
from __future__ import annotations

import json
import os
import statistics
import subprocess
import time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = os.path.join(ROOT, "data", "microstructure", "last_snapshot.json")
ALERTS = os.path.join(ROOT, "data", "microstructure", "alerts.log")

THRESH_FUNDING_SPREAD_PP = 4.0
THRESH_DEPEG_BP = 50


def _get(url, payload=None):
    cmd = ["curl", "-s", "--max-time", "25", "-H", "User-Agent: Mozilla/5.0"]
    if payload:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(payload), url]
    else:
        cmd += [url]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(r.stdout)


def funding_snapshot() -> dict[str, float]:
    out = {}
    try:
        for sym, name in [("BTCUSDT", "BTC"), ("ETHUSDT", "ETH"), ("SOLUSDT", "SOL")]:
            d = _get(f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={sym}")
            out[f"Binance:{name}"] = round(float(d["lastFundingRate"]) * 3 * 365 * 100, 2)
    except Exception:
        pass
    try:
        d = _get("https://api.bybit.com/v5/market/tickers?category=linear&symbol=BTCUSDT")
        out["Bybit:BTC"] = round(float(d["result"]["list"][0]["fundingRate"]) * 3 * 365 * 100, 2)
    except Exception:
        pass
    try:
        d = _get("https://www.okx.com/api/v5/public/funding-rate?instId=BTC-USDT-SWAP")
        out["OKX:BTC"] = round(float(d["data"][0]["fundingRate"]) * 3 * 365 * 100, 2)
    except Exception:
        pass
    try:
        meta, ctxs = _get("https://api.hyperliquid.xyz/info", {"type": "metaAndAssetCtxs"})
        for m, c in zip(meta["universe"], ctxs):
            if m["name"] in ("BTC", "ETH", "SOL"):
                out[f"HL:{m['name']}"] = round(float(c["funding"]) * 24 * 365 * 100, 2)  # часовая ставка!
    except Exception:
        pass
    return out


def peg_snapshot() -> dict[str, float]:
    ids = "usde,usd-coin,tether,usds,ethena-usde"
    try:
        d = _get(f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd")
        return {k: round(v["usd"], 4) for k, v in d.items()}
    except Exception:
        return {}


def wsteth_ratio() -> dict[str, float]:
    try:
        d = _get("https://api.coingecko.com/api/v3/simple/price?ids=wrapped-steth,ethereum&vs_currencies=usd")
        ratio = d["wrapped-steth"]["usd"] / d["ethereum"]["usd"]
        return {"wsteth_eth_market_ratio": round(ratio, 5)}
    except Exception:
        return {}


def pendle_discounts() -> dict[str, float]:
    """PT-дисконт через Pendle API (Ethereum)."""
    out = {}
    try:
        d = _get("https://api-v2.pendle.finance/api/v1/markets?chain=1&is_expired=false")
        for m in d.get("data", [])[:40]:
            name = (m.get("name") or "").upper()
            if any(k in name for k in ("SUSDE", "SUSDS", "WSTETH")) and "26" in (m.get("expiry") or ""):
                pt = m.get("pt", {})
                out[m.get("name", "?")[:32]] = {
                    "implied_apy_pct": round(float(pt.get("impliedApy") or 0) * 100, 2),
                    "discount_pct": round(float(pt.get("discount") or 0) * 100, 2),
                }
    except Exception:
        pass
    return out



def undersupplied_pools() -> list[dict]:
    """Пулы с volume/TVL > 20x (недоснабжённая ликвидность) — кандидат на LP (WS-16)."""
    out = []
    try:
        d = _get("https://yields.llama.fi/pools")
        for p in d["data"]:
            tvl = p.get("tvlUsd") or 0
            vol = (p.get("volumeUsd1d") or 0)
            if tvl > 3e5 and vol / tvl > 20:
                out.append({"pool": p.get("symbol"), "project": p.get("project"),
                            "chain": p.get("chain"), "tvl_usd": round(tvl),
                            "vol_tvl_x": round(vol / tvl, 1),
                            "apy_pct": round(p.get("apy") or 0, 1)})
        out.sort(key=lambda x: -x["vol_tvl_x"])
    except Exception:
        pass
    return out[:10]


def pendle_pt_signal() -> list[dict]:
    """Правило WS-17: PT интересен, когда implied > trailing realized +200 б.п."""
    out = []
    try:
        d = _get("https://api-v2.pendle.finance/api/v1/markets?chain=1&is_expired=false")
        for m in d.get("data", []):
            pt = m.get("pt", {})
            implied = float(pt.get("impliedApy") or 0) * 100
            underlying = float(m.get("underlyingApy", 0)) * 100 if m.get("underlyingApy") else None
            if underlying and implied - underlying > 1.5:
                out.append({"market": m.get("name", "?")[:40],
                            "implied_pct": round(implied, 2),
                            "underlying_pct": round(underlying, 2),
                            "spread_bp": round((implied - underlying) * 100)})
    except Exception:
        pass
    return out[:8]


def check_dislocations(funding: dict) -> list[str]:
    alerts = []
    by_asset: dict[str, dict] = {}
    for k, v in funding.items():
        venue, asset = k.split(":")
        by_asset.setdefault(asset, {})[venue] = v
    for asset, venues in by_asset.items():
        if len(venues) < 2:
            continue
        hi = max(venues.items(), key=lambda kv: kv[1])
        lo = min(venues.items(), key=lambda kv: kv[1])
        spread = hi[1] - lo[1]
        if spread > THRESH_FUNDING_SPREAD_PP:
            alerts.append(f"ФАНДИНГ {asset}: спрэд {spread:.1f} п.п. ({hi[0]} {hi[1]:+.1f}% vs "
                          f"{lo[0]} {lo[1]:+.1f}%) — перп-перп: шорт {hi[0]} + лонг {lo[0]}")
    return alerts


def check_pegs(pegs: dict) -> list[str]:
    alerts = []
    for name, px in pegs.items():
        if abs(px - 1.0) * 10000 > THRESH_DEPEG_BP:
            direction = "ниже" if px < 1 else "выше"
            alerts.append(f"ПЕГ {name}: {px} ({(px-1)*10000:+.0f} б.п. {direction} $1) — кандидата на mean-reversion")
    return alerts


def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    funding = funding_snapshot()
    pegs = peg_snapshot()
    lst = wsteth_ratio()
    pendle = pendle_discounts()

    alerts = check_dislocations(funding) + check_pegs(pegs)

    print(f"=== Снимок {now} ===")
    print("Фандинг (годовых %):")
    for k, v in sorted(funding.items()):
        print(f"  {k:<14} {v:+7.2f}%")
    print("Пеги:", pegs or "нет данных")
    print("wstETH/ETH:", lst)
    if pendle:
        print("Pendle PT:")
        for k, v in list(pendle.items())[:6]:
            print(f"  {k}: implied {v['implied_apy_pct']}%, дисконт {v['discount_pct']}%")

    us = undersupplied_pools()
    if us:
        print("\nНедоснабжённые пулы (vol/TVL>20x, WS-16):")
        for u in us[:6]:
            print(f"  {u['project']}/{u['chain']}: {u['pool']} x{u['vol_tvl_x']} TVL ${u['tvl_usd']/1e6:.1f}M APY {u['apy_pct']}%")
    pt_sig = pendle_pt_signal()
    if pt_sig:
        print("\nPendle PT-сигнал (implied>underlying+150 б.п., WS-17):")
        for s in pt_sig[:6]:
            print(f"  {s['market']}: implied {s['implied_pct']}% vs {s['underlying_pct']}% (+{s['spread_bp']} б.п.)")

    if alerts:
        print("\n!!! АЛЕРТЫ:")
        for a in alerts:
            print("  -", a)
    else:
        print("\nДислокаций в пределах порогов нет.")

    prev = {}
    if os.path.exists(SNAP):
        prev = json.load(open(SNAP))
    snap = {"ts": now, "funding": funding, "pegs": pegs, "lst": lst,
            "pendle": pendle, "alerts": alerts,
            "prev_funding": prev.get("funding", {})}
    json.dump(snap, open(SNAP, "w"), indent=1)
    if alerts:
        with open(ALERTS, "a") as f:
            f.write(f"[{now}] " + " | ".join(alerts) + "\n")


if __name__ == "__main__":
    main()
