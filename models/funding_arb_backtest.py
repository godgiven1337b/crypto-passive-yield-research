"""
funding_arb_backtest.py — бэктест перп-перп фандинг-арбитража на реальной истории.

Стратегия: когда спрэд годовых фандингов двух площадок по одному активу
превышает порог входа — шорт перп на «дорогой» площадке + лонг на «дешёвой»,
дельта 0, сбор разницы фандинга; выход при спрэде ниже порога выхода.

Данные: Binance fapi fundingRate (8ч), OKX funding-rate-history (8ч),
Bybit funding/history (8ч), HL fundingHistory (1ч → агрегируем в 8ч).
Издержки: taker-комиссии обеих площадок на вход/выход (0.05%+0.05% на сторону
консервативно), borrow-free (перпы без займа).

Запуск: python3 models/funding_arb_backtest.py
"""
from __future__ import annotations

import json
import os
import statistics
import subprocess
import time
from datetime import datetime, timezone

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "microstructure")
OUT = os.path.join(DATA, "funding_arb_backtest.json")


def _get(url: str):
    for i in range(3):
        r = subprocess.run(["curl", "-s", "--max-time", "30", "-H", "User-Agent: Mozilla/5.0", url],
                           capture_output=True, text=True)
        if r.stdout.strip():
            try:
                return json.loads(r.stdout)
            except json.JSONDecodeError:
                pass
        time.sleep(1)
    return None


def _post(url: str, payload: dict):
    r = subprocess.run(["curl", "-s", "--max-time", "30", "-X", "POST", url,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True)
    return json.loads(r.stdout)


def fetch_binance(symbol: str = "BTCUSDT", days: int = 180) -> dict[int, float]:
    """8ч-точки Binance за период."""
    out = {}
    end = int(time.time() * 1000)
    start = end - days * 86400 * 1000
    cur = start
    while cur < end:
        d = _get(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={symbol}&startTime={cur}"
                 f"&endTime={end}&limit=1000")
        if not isinstance(d, list) or not d:
            break
        for h in d:
            out[int(h["fundingTime"]) // 1000 // 28800 * 28800] = float(h["fundingRate"])
        cur = int(d[-1]["fundingTime"]) + 1
        time.sleep(0.1)
    return out


def fetch_okx(inst: str = "BTC-USDT-SWAP", days: int = 180) -> dict[int, float]:
    """8ч-точки OKX (пагинация 'after' назад во времени)."""
    out = {}
    before = ""
    deadline = int((time.time() - days * 86400) * 1000)
    for _ in range(60):
        url = (f"https://www.okx.com/api/v5/public/funding-rate-history?instId={inst}&limit=100"
               + (f"&before={before}" if before else ""))
        d = _get(url)
        rows = (d or {}).get("data", [])
        if not rows:
            break
        for r in rows:
            ts = int(r["fundingTime"]) // 1000 // 28800 * 28800
            out[ts] = float(r["realizedRate"])
        oldest = int(rows[0]["fundingTime"])
        if oldest < deadline:
            break
        before = str(oldest)
        time.sleep(0.12)
    return out


def fetch_bybit(symbol: str = "BTCUSDT", days: int = 180) -> dict[int, float]:
    """8ч-точки Bybit (пагинация 'cursor')."""
    out = {}
    cursor = ""
    deadline = int((time.time() - days * 86400) * 1000)
    for _ in range(60):
        url = (f"https://api.bybit.com/v5/market/funding/history?category=linear&symbol={symbol}&limit=200"
               + (f"&cursor={cursor}" if cursor else ""))
        d = _get(url)
        rows = (d or {}).get("result", {}).get("list", [])
        if not rows:
            break
        for r in rows:
            ts = int(r["fundingRateTimestamp"]) // 1000 // 28800 * 28800
            out[ts] = float(r["fundingRate"])
        nxt = (d or {}).get("result", {}).get("nextPageCursor", "")
        oldest = min(int(r["fundingRateTimestamp"]) for r in rows)
        if not nxt or oldest < deadline:
            break
        cursor = nxt
        time.sleep(0.12)
    return out


def fetch_hl(coin: str = "BTC", days: int = 180) -> dict[int, float]:
    """HL часовые точки -> сумма по 8ч-бакетам."""
    end = int(time.time() * 1000)
    start = end - days * 86400 * 1000
    hourly = {}
    cur = start
    for _ in range(days // 20 + 2):
        d = _post("https://api.hyperliquid.xyz/info",
                  {"type": "fundingHistory", "coin": coin, "startTime": cur, "endTime": min(cur + 500 * 3600 * 1000, end)})
        if not isinstance(d, list) or not d:
            break
        for h in d:
            hourly[int(h["time"]) // 1000] = float(h["fundingRate"])
        last = int(d[-1]["time"])
        if last >= end - 3600_000:
            break
        cur = last + 1
        time.sleep(0.15)
    out = {}
    for ts, r in hourly.items():
        bucket = ts // 28800 * 28800
        out[bucket] = out.get(bucket, 0.0) + r
    return out


def backtest(a: dict[int, float], b: dict[int, float], name_a: str, name_b: str,
             entry_pp: float = 4.0, exit_pp: float = 1.0,
             notional_per_capital: float = 3.0, fees_roundtrip: float = 0.0012) -> dict:
    """Симуляция: вход когда |spread_annual| > entry_pp, выход когда < exit_pp.

    Позиция собирает разницу фандингов обеих ног; издержки fees_roundtrip
    на цикл (в долях от нотионала), приведённые к капиталу через notional_per_capital.
    """
    common = sorted(set(a) & set(b))
    ann = lambda r: r * 3 * 365 * 100  # годовые %
    spreads = {ts: ann(a[ts]) - ann(b[ts]) for ts in common}
    in_pos = False
    entry_side = 0  # +1: шорт A (A дороже), -1: шорт B
    acc_funding_pp = 0.0
    trades = []
    cur_acc = 0.0
    entry_ts = None
    for ts in common:
        s = spreads[ts]
        if not in_pos and abs(s) > entry_pp:
            in_pos = True
            entry_side = 1 if s > 0 else -1
            entry_ts, cur_acc = ts, 0.0
        elif in_pos:
            cur_acc += s * entry_side / 3 / 365 / 100 * 2  # обе ноги: разница фандингов за 8ч в долях капитала x notional
            cur_acc += 0  # (уже учтено)
            gross = cur_acc * notional_per_capital
            if abs(s) < exit_pp or ts == common[-1]:
                trades.append({"entry": datetime.fromtimestamp(entry_ts, tz=timezone.utc).strftime("%m-%d"),
                               "exit": datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%m-%d"),
                               "days": round((ts - entry_ts) / 86400, 1),
                               "side": f"short {name_a}" if entry_side > 0 else f"short {name_b}",
                               "gross_pct": round(gross * 100, 3)})
                in_pos = False
    # аккуратнее: пересчёт cur_acc — в цикле выше ошибка двойного учёта, пересобираем
    trades = []
    in_pos = False
    for ts in common:
        s = spreads[ts]
        if not in_pos and abs(s) > entry_pp:
            in_pos, entry_side, entry_ts, cur_acc = True, (1 if s > 0 else -1), ts, 0.0
        elif in_pos:
            # за 8ч период с обеих ног собираем (s_a - s_b)*side как разницу годовых/кол-во периодов
            cur_acc += (s * entry_side / 100) / (3 * 365)  # доля капитала за 8ч при 1x нотионале
            if abs(s) < exit_pp or ts == common[-1]:
                gross = cur_acc * notional_per_capital
                net = gross - fees_roundtrip * notional_per_capital
                trades.append({"entry": datetime.fromtimestamp(entry_ts, tz=timezone.utc).strftime("%m-%d"),
                               "exit": datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%m-%d"),
                               "days": round((ts - entry_ts) / 86400, 1),
                               "side": f"short {name_a}" if entry_side > 0 else f"short {name_b}",
                               "gross_pct": round(gross * 100, 3), "net_pct": round(net * 100, 3)})
                in_pos = False
    nets = [t["net_pct"] for t in trades]
    total_days = (common[-1] - common[0]) / 86400
    total_net = sum(nets) / 100 * notional_per_capital / notional_per_capital  # в долях капитала
    res = {
        "pair": f"{name_a}-{name_b}", "n_trades": len(trades),
        "period_days": round(total_days),
        "win_rate": round(sum(1 for n in nets if n > 0) / len(nets) * 100, 1) if nets else 0,
        "avg_net_pct_per_trade": round(statistics.mean(nets), 3) if nets else 0,
        "total_net_pct_on_capital": round(sum(nets), 3) if nets else 0,
        "annualized_pct": round(sum(nets) / total_days * 365, 2) if nets else 0,
        "spread_mean_pp": round(statistics.mean([spreads[t] for t in common]), 2),
        "spread_above_entry_pct_time": round(sum(1 for t in common if abs(spreads[t]) > entry_pp) / len(common) * 100, 1),
        "trades": trades,
    }
    return res


def main():
    days = 180
    print(f"Загрузка историй фандинга BTC ({days} дней)…")
    data = {}
    for name, fn in [("Binance", fetch_binance), ("OKX", fetch_okx),
                     ("Bybit", fetch_bybit), ("HL", fetch_hl)]:
        try:
            data[name] = fn(days=days)
            print(f"  {name}: {len(data[name])} 8ч-точек "
                  f"({datetime.fromtimestamp(min(data[name]), tz=timezone.utc):%m-%d}"
                  f"→{datetime.fromtimestamp(max(data[name]), tz=timezone.utc):%m-%d})")
        except Exception as e:
            print(f"  {name}: ERR {e}")
    json.dump(data, open(os.path.join(DATA, "funding_hist_180d.json"), "w"))
    results = []
    pairs = [("Binance", "OKX"), ("Binance", "Bybit"), ("Binance", "HL"),
             ("HL", "OKX"), ("HL", "Bybit")]
    for a, b in pairs:
        if a in data and b in data:
            r = backtest(data[a], data[b], a, b)
            results.append(r)
            print(f"\n{r['pair']}: сделок {r['n_trades']} за {r['period_days']}д | "
                  f"win {r['win_rate']}% | итог {r['total_net_pct_on_capital']:+.2f}% на капитал "
                  f"| annualized {r['annualized_pct']:+.2f}% | спрэд>порога {r['spread_above_entry_pct_time']}% времени")
            for t in r["trades"][:4]:
                print(f"    {t['entry']}→{t['exit']} ({t['days']}д) {t['side']}: net {t['net_pct']:+.3f}%")
    json.dump(results, open(OUT, "w"), indent=1)
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
