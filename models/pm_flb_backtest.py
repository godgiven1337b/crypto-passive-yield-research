"""
pm_flb_backtest.py — бэктест FLB-харвеста на реальных историях цен Polymarket.

Стратегия: за N дней до резолюции купить YES-токен, торгующийся в диапазоне
[p_lo, p_hi] (фаворит), держать до резолюции. PnL на $1 = (outcome − entry).

Данные: gamma (resolved events с категориями) + CLOB prices-history
(снапшоты цен по token_id, окна interval=1w/1m с fidelity).

Валидность: только рынки с объёмом >= min_volume и Resolution ровно 1/0.
Издержки: спрэд на входе entry_spread (берём half-spread запас), taker-fee 0
(политика PM на момент 2026 для большинства категорий), gas ≈ 0.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import datetime, timezone

GAMMA = "https://gamma-api.polymarket.com/events"
CLOB = "https://clob.polymarket.com/prices-history"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "data", "microstructure", "pm_flb_backtest.json")


def _get(url: str, tries: int = 3):
    for i in range(tries):
        r = subprocess.run(["curl", "-s", "--max-time", "30", "-H", "User-Agent: Mozilla/5.0", url],
                           capture_output=True, text=True)
        if r.stdout.strip():
            try:
                return json.loads(r.stdout)
            except json.JSONDecodeError:
                pass
        time.sleep(1 + i)
    return None


def fetch_resolved_events(pages: int = 30, per_page: int = 40) -> list[dict]:
    events = []
    for off in range(0, pages * per_page, per_page):
        d = _get(f"{GAMMA}?closed=true&limit={per_page}&offset={off}"
                 f"&order=endDate&ascending=false")
        if not isinstance(d, list) or not d:
            break
        events.extend(d)
        if off % (per_page * 5) == 0 and off:
            print(f"  …{len(events)} событий")
        time.sleep(0.15)
    return events


def price_history(token_id: str, end_ts: int | None = None, window_days: int = 10,
                  fidelity: int = 60) -> list[tuple[int, float]]:
    """История цен, привязанная к дате РЕЗОЛЮЦИИ рынка (не к текущему моменту!).

    interval=1w отсчитывается от now — для закрытых рынков даёт пустоту/не то окно.
    Используем startTs/endTs вокруг endDate (окно <= 10 дней — лимит API).
    """
    if end_ts is None:
        d = _get(f"{CLOB}?market={token_id}&interval=1w&fidelity={fidelity}")
    else:
        start = end_ts - window_days * 86400
        d = _get(f"{CLOB}?market={token_id}&startTs={start}&endTs={end_ts + 3600}&fidelity={fidelity}")
    if not d or "history" not in d:
        return []
    return [(int(p["t"]), float(p["p"])) for p in d["history"]]


def categorize(event: dict) -> str:
    tags = event.get("tags") or []
    names = {str(t.get("label") or t.get("name") or "").lower() for t in tags if isinstance(t, dict)}
    title = str(event.get("title") or "").lower()
    if any(k in names or k in title for k in ["sport", "nba", "nfl", "mlb", "nhl", "soccer", "football",
                                              "epl", "uefa", "tennis", "ufc", "cricket"]):
        return "sports"
    if any(k in names or k in title for k in ["politics", "election", "president", "senate", "nominee",
                                              "governor", "minister", "party"]):
        return "politics"
    if any(k in names or k in title for k in ["crypto", "bitcoin", "btc", "eth", "solana", "token"]):
        return "crypto"
    if any(k in names or k in title for k in ["fed", "cpi", "s&p", "sp500", "economic", "gdp",
                                              "interest rate", "inflation"]):
        return "finance/macro"
    if any(k in names or k in title for k in ["weather", "temperature", "hurricane"]):
        return "weather"
    if any(k in names or k in title for k in ["pop", "celebrity", "award", "oscar", "music"]):
        return "pop-culture"
    return "other"


def run_backtest(days_before: list[int], p_lo: float = 0.85, p_hi: float = 0.97,
                 min_volume: float = 5_000, entry_slip: float = 0.01) -> dict:
    events = fetch_resolved_events()
    print(f"Разрешившихся событий: {len(events)}")
    trades = []
    for e in events:
        cat = categorize(e)
        end_str = str(e.get("endDate") or "")[:19]
        try:
            end_ts = int(datetime.fromisoformat(end_str).replace(tzinfo=timezone.utc).timestamp())
        except ValueError:
            continue
        if end_ts < time.time() - 90 * 86400:  # только последние 90 дней
            continue
        for m in e.get("markets") or []:
            try:
                vol = float(m.get("volumeNum") or m.get("volume") or 0)
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
            if not prices or prices[0] not in ("0", "1", 0, 1):
                continue
            outcome = float(prices[0])
            cti = m.get("clobTokenIds")
            if isinstance(cti, str):
                try:
                    cti = json.loads(cti)
                except Exception:
                    continue
            if not cti:
                continue
            yes_token = str(cti[0])
            hist = price_history(yes_token, end_ts=end_ts, window_days=10, fidelity=120)
            if len(hist) < 2:
                continue
            for d in days_before:
                target = end_ts - d * 86400
                pts = [(t, p) for t, p in hist if t <= target]
                if not pts:
                    continue
                _, px = pts[-1]  # последняя цена до T-d
                if p_lo <= px <= p_hi:
                    pnl = (outcome - (px + entry_slip)) / (px + entry_slip)
                    trades.append({"category": cat, "q": str(m.get("question"))[:48],
                                   "days_before": d, "entry": round(px, 3),
                                   "outcome": outcome, "pnl_pct": round(pnl * 100, 2),
                                   "volume": vol})
            time.sleep(0.12)
    # агрегация
    agg: dict = {}
    for t in trades:
        key = (t["category"], t["days_before"])
        agg.setdefault(key, []).append(t)
    report = {}
    for (cat, d), lst in sorted(agg.items()):
        pnls = [x["pnl_pct"] for x in lst]
        wins = sum(1 for p in pnls if p > 0)
        report[f"{cat}|T-{d}d"] = {
            "n": len(lst), "win_rate": round(wins / len(lst) * 100, 1),
            "avg_pnl_pct": round(sum(pnls) / len(lst), 3),
            "median_pnl_pct": round(sorted(pnls)[len(pnls)//2], 3),
            "total_usd_per_1": round(sum(pnls) / 100, 3),
        }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"params": {"p_lo": p_lo, "p_hi": p_hi, "min_volume": min_volume,
                          "entry_slip": entry_slip, "days_before": days_before,
                          "generated": datetime.now(timezone.utc).isoformat()},
               "report": report, "trades_sample": trades[:400]},
              open(OUT, "w"), indent=1, ensure_ascii=False)
    return report


if __name__ == "__main__":
    rep = run_backtest(days_before=[7, 3, 1])
    print(f"\n=== FLB бэктест (вход 0.85–0.97, slip 1¢) ===")
    print(f"{'Категория|Горизонт':<28} {'n':>4} {'win%':>6} {'avg%':>7} {'median%':>8} {'Σ$на $1/сделка':>10}")
    for k, v in rep.items():
        print(f"{k:<28} {v['n']:>4} {v['win_rate']:>6.1f} {v['avg_pnl_pct']:>7.2f} "
              f"{v['median_pnl_pct']:>8.2f} {v['total_usd_per_1']:>10.3f}")
    print(f"\n-> {OUT}")
