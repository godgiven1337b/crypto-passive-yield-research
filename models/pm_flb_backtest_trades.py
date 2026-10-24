"""
pm_flb_backtest_trades.py — FLB-бэктест по РЕАЛЬНЫМ сделкам (data-api /trades).

CLOB prices-history не отдаёт закрытые рынки (hist_nonempty=0 на 1445 рынках),
поэтому используем тейкер-сделки: для каждого resolved-рынка пагинируем назад
до T-8д и берём последнюю цену сделки <= каждой цели (T-1/T-3/T-7).

Фильтры рынка: volume >= $20k, outcome строго 1/0, endDate < now-1d.
Издержки: entry_slip (полспрэда + impact) на вход.
"""
from __future__ import annotations

import json
import os
import statistics
import subprocess
import time
from datetime import datetime, timezone

GAMMA = "https://gamma-api.polymarket.com/events"
TRADES = "https://data-api.polymarket.com/trades"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "data", "microstructure", "pm_flb_backtest_trades.json")


def _get(url: str):
    for i in range(3):
        r = subprocess.run(["curl", "-s", "--max-time", "25", "-H", "User-Agent: Mozilla/5.0", url],
                           capture_output=True, text=True)
        if r.stdout.strip():
            try:
                return json.loads(r.stdout)
            except json.JSONDecodeError:
                pass
        time.sleep(0.8 + i)
    return None


def categorize(event: dict) -> str:
    tags = event.get("tags") or []
    names = {str(t.get("label") or t.get("name") or "").lower() for t in tags if isinstance(t, dict)}
    title = str(event.get("title") or "").lower()
    def hit(keys):
        return any(k in names or k in title for k in keys)
    if hit(["sport", "nba", "nfl", "mlb", "nhl", "epl", "uefa", "tennis", "ufc", "vs.", "match"]):
        return "sports"
    if hit(["politics", "election", "president", "senate", "nominee", "governor", "minister"]):
        return "politics"
    if hit(["crypto", "bitcoin", "btc", "eth", "solana", "fdv", "token"]):
        return "crypto"
    if hit(["fed", "cpi", "s&p", "sp500", "economic", "gdp", "rate"]):
        return "finance/macro"
    if hit(["weather", "temperature", "hurricane"]):
        return "weather"
    return "other"


def collect_markets(max_events: int = 560, min_volume: float = 10_000) -> list[dict]:
    markets = []
    from datetime import timedelta
    d_min = (datetime.now(timezone.utc) - timedelta(days=90)).strftime("%Y-%m-%d")
    d_max = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    for off in range(0, max_events, 40):
        d = _get(f"{GAMMA}?closed=true&limit=40&offset={off}&order=endDate&ascending=false"
                 f"&end_date_min={d_min}&end_date_max={d_max}")
        if not isinstance(d, list) or not d:
            break
        for e in d:
            cat = categorize(e)
            end_str = str(e.get("endDate") or "")[:19]
            try:
                end_ts = int(datetime.fromisoformat(end_str).replace(tzinfo=timezone.utc).timestamp())
            except ValueError:
                continue
            if end_ts > time.time() - 86400 or end_ts < time.time() - 90 * 86400:
                continue
            for m in e.get("markets") or []:
                try:
                    vol = float(m.get("volumeNum") or 0)
                except (TypeError, ValueError):
                    continue
                if vol < min_volume or m.get("closed") is not True:
                    continue
                prices = m.get("outcomePrices")
                if isinstance(prices, str):
                    try:
                        prices = json.loads(prices)
                    except Exception:
                        continue
                if not prices or str(prices[0]) not in ("0", "1"):
                    continue
                cti = m.get("clobTokenIds")
                if isinstance(cti, str):
                    try:
                        cti = json.loads(cti)
                    except Exception:
                        continue
                if not cti:
                    continue
                markets.append({"cat": cat, "q": str(m.get("question"))[:44], "end_ts": end_ts,
                                "token": str(cti[0]), "outcome": float(prices[0]), "vol": vol})
        time.sleep(0.12)
    markets.sort(key=lambda m: -m["vol"])
    return markets


def price_at(token: str, targets: dict[int, float], page_cap: int = 90) -> dict[int, float] | None:
    """Последняя цена сделки <= каждой цели (targets: ts -> None placeholder)."""
    found: dict[int, float | None] = {t: None for t in targets}
    need_until = min(targets)
    offset = 0
    for _ in range(page_cap):
        d = _get(f"{TRADES}?tokenId={token}&limit=500&offset={offset}")
        rows = d if isinstance(d, list) else []
        if not rows:
            break
        for r in rows:
            ts = int(float(r.get("timestamp") or 0))
            px = float(r.get("price"))
            for t in found:
                if found[t] is None and ts <= t:
                    found[t] = px
        oldest = min(int(float(r.get("timestamp") or 0)) for r in rows)
        if all(v is not None for v in found.values()) or oldest < need_until:
            break
        offset += len(rows)
        time.sleep(0.08)
    return {t: v for t, v in found.items()} if any(v is not None for v in found.values()) else None


def run(sample: int = 220, p_lo: float = 0.85, p_hi: float = 0.97, entry_slip: float = 0.01):
    markets = collect_markets()
    print(f"Рынков после фильтров: {len(markets)}; берём топ-{sample} по объёму")
    horizons = [1, 3]
    trades = []
    for i, m in enumerate(markets[:sample]):
        targets = {m["end_ts"] - d * 86400: d for d in horizons}
        pxs = price_at(m["token"], {t: 0 for t in targets})
        if not pxs:
            continue
        for ts, d in targets.items():
            px = pxs.get(ts)
            if px is None or not (p_lo <= px <= p_hi):
                continue
            entry = px + entry_slip
            trades.append({"cat": m["cat"], "q": m["q"], "d": d, "entry": round(px, 3),
                           "outcome": m["outcome"], "pnl_pct": round((m["outcome"] - entry) / entry * 100, 2),
                           "vol": m["vol"]})
        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{min(sample, len(markets))} рынков, сделок {len(trades)}")
    agg: dict = {}
    for t in trades:
        agg.setdefault((t["cat"], t["d"]), []).append(t)
    report = {}
    for (cat, d), lst in sorted(agg.items()):
        pnls = [x["pnl_pct"] for x in lst]
        report[f"{cat}|T-{d}d"] = {
            "n": len(lst),
            "win_rate": round(sum(1 for p in pnls if p > 0) / len(lst) * 100, 1),
            "avg_pnl_pct": round(statistics.mean(pnls), 2),
            "median": round(statistics.median(pnls), 2),
            "sum_per_dollar": round(sum((x['outcome'] - x['entry'] - entry_slip) / x['entry'] for x in lst), 3),
        }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"params": {"sample": sample, "p_lo": p_lo, "p_hi": p_hi, "entry_slip": entry_slip,
                          "generated": datetime.now(timezone.utc).isoformat()},
               "report": report, "trades": trades}, open(OUT, "w"), indent=1, ensure_ascii=False)
    return report, trades


if __name__ == "__main__":
    report, trades = run()
    print(f"\n=== FLB бэктест по сделкам (вход {0.85:.2f}–{0.97:.2f}, slip 1¢), n={len(trades)} ===")
    print(f"{'Категория|Горизонт':<26} {'n':>4} {'win%':>6} {'avg%':>7} {'median%':>8}")
    for k, v in report.items():
        print(f"{k:<26} {v['n']:>4} {v['win_rate']:>6.1f} {v['avg_pnl_pct']:>7.2f} {v['median']:>8.2f}")
    print(f"\n-> {OUT}")
