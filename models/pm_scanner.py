"""
pm_scanner.py — сканер арбитражных корзин на Polymarket (gamma API).

Что ищет:
1. Mutually-exclusive события с несколькими исходами (мульти-исход, часто enableNegRisk):
   - sum(YES) < 1 - fee_buffer -> купить все YES (одно обязательно сыграет) = гарантированный %
   - sum(NO)  < 1 - fee_buffer -> купить все NO (анти-корзина; ровно один исход YES, прочие NO платят $1)
   Фактически sum(NO) = N - sum(YES), поэтому условие sum(NO) < N-1 эквивалентно sum(YES) > 1.
2. Широкие спрэды best bid/ask у топ-объёмных бинарных рынков (возможность MM).

Цены исходов — 'outcomePrices' (mid) и bestBid/bestAsk из gamma. Реальный исполнимый
эдж считается по ask для покупки (минус buffer на движение и комиссии вывода).
"""
from __future__ import annotations

import json
import os
import subprocess

GAMMA = "https://gamma-api.polymarket.com/events"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "data", "microstructure", "pm_baskets.json")

# буфер:Polymarket без торговой комиссии на большинстве рынков, но есть
# slippage между ногами и gas на claim/redeem. Берём 1% консервативно.
EXEC_BUFFER = 0.01


def _get(url: str):
    r = subprocess.run(["curl", "-s", "--max-time", "35", "-H", "User-Agent: Mozilla/5.0", url],
                       capture_output=True, text=True)
    return json.loads(r.stdout)


def fetch_events(per_page: int = 40, pages: int = 6) -> list[dict]:
    events = []
    for offset in range(0, pages * per_page, per_page):
        url = (f"{GAMMA}?closed=false&archived=false&active=true&limit={per_page}"
               f"&offset={offset}&order=volume24hr&ascending=false")
        try:
            batch = _get(url)
        except Exception:
            break
        if not isinstance(batch, list) or not batch:
            break
        events.extend(batch)
    return events


def parse_float(x) -> float | None:
    try:
        v = float(x)
        return v if 0.0 <= v <= 1.0 else None
    except (TypeError, ValueError):
        return None


def analyze_events(events: list[dict]) -> tuple[list[dict], list[dict]]:
    baskets, spreads = [], []
    for e in events:
        markets = e.get("markets") or []
        # ТОЛЬКО взаимоисключающие корзины: архитектура negRisk (ровно один YES исход).
        # Прочие мульти-рыночные события (спорт-пропы: 306 исходов) — коллекции
        # НЕЗАВИСИМЫХ рынков, сумма YES там не обязана быть 1 -> ложные "арбитражи".
        if len(markets) < 3 or not e.get("enableNegRisk"):
            # но спрэды собираем со всех
            for m in markets:
                if m.get("closed") or not m.get("active"):
                    continue
                prices = m.get("outcomePrices")
                if isinstance(prices, str):
                    try:
                        prices = json.loads(prices)
                    except Exception:
                        continue
                if not prices:
                    continue
                yes = parse_float(prices[0])
                if yes is None:
                    continue
                sp = (parse_float(m.get("bestAsk")) or yes) - (parse_float(m.get("bestBid")) or yes)
                vol24 = float(m.get("volume24hr") or 0)
                if vol24 > 10_000 and sp >= 0:
                    spreads.append({"q": (m.get("question") or "?")[:62],
                                    "spread_pct": round(sp * 100, 2),
                                    "mid": round(yes, 3), "vol24": round(vol24),
                                    "liquidity": round(float(m.get("liquidityNum") or 0))})
            continue
        live = []
        for m in markets:
            if m.get("closed") or not m.get("active"):
                continue
            prices = m.get("outcomePrices")
            if isinstance(prices, str):
                try:
                    prices = json.loads(prices)
                except Exception:
                    continue
            if not prices:
                continue
            yes = parse_float(prices[0])
            if yes is None:
                continue
            ask = parse_float(m.get("bestAsk")) or yes
            bid = parse_float(m.get("bestBid")) or yes
            liq = float(m.get("liquidityNum") or m.get("liquidity") or 0)
            live.append({"q": m.get("question", "?")[:60], "yes_mid": yes,
                         "ask": ask, "bid": bid, "liquidity": liq,
                         "vol24": float(m.get("volume24hr") or 0)})
        if len(live) < 3:
            continue
        sum_yes_mid = sum(x["yes_mid"] for x in live)
        sum_yes_ask = sum(x["ask"] for x in live)      # цена покупки корзины YES по ask
        sum_no_ask = sum(1 - x["bid"] for x in live)   # цена покупки корзины NO по ask(bid YES)
        min_liq = min((x["liquidity"] for x in live), default=0)
        baskets.append({
            "event": (e.get("title") or "?")[:70],
            "neg_risk": bool(e.get("enableNegRisk")),
            "n_outcomes": len(live),
            "sum_yes_mid": round(sum_yes_mid, 4),
            "yes_basket_edge": round(1 - sum_yes_ask - EXEC_BUFFER, 4),   # >0 = арбитраж
            "no_basket_edge": round(len(live) - 1 - sum_no_ask - EXEC_BUFFER, 4),
            "min_liquidity": round(min_liq),
            "vol24": round(sum(x["vol24"] for x in live)),
        })
        # спрэды по бинарным топ-рынкам
        for x in live:
            sp = x["ask"] - x["bid"]
            if x["vol24"] > 10_000 and sp >= 0:
                spreads.append({"q": x["q"], "spread_pct": round(sp * 100, 2),
                                "mid": round(x["yes_mid"], 3),
                                "vol24": round(x["vol24"]), "liquidity": round(x["liquidity"])})
    baskets.sort(key=lambda b: -max(b["yes_basket_edge"], b["no_basket_edge"]))
    spreads.sort(key=lambda s: -s["spread_pct"])
    return baskets, spreads


def liquid_baskets(events: list[dict], min_leg_liq: float = 500) -> list[dict]:
    """ЖИВЫЕ negRisk-корзины: каждая нога > min_leg_liq. Корректные формулы эджа:

    YES-корзина (купить YES всех исходов): cost = ΣYES_asks; payoff = $1 (ровно один исход YES)
      эдж = 1 − ΣYES
    NO-корзина (купить NO всех исходов): cost = Σ(1−YES_bid) = n − ΣYES; payoff = (n−1)
      эдж = ΣYES − 1
    Положительный эдж любого знака = гарантированная доходность до погашения (при исполнимости).
    Миды — верхняя оценка; реальный эдж меньше на спрэды ног (проверять по CLOB).
    """
    out = []
    for e in events:
        if not e.get("enableNegRisk"):
            continue
        mkts = [m for m in (e.get("markets") or []) if m.get("active") and not m.get("closed")]
        if len(mkts) < 3:
            continue
        legs = []
        for m in mkts:
            liq = float(m.get("liquidityNum") or 0)
            if liq < min_leg_liq:
                continue
            prices = m.get("outcomePrices")
            if isinstance(prices, str):
                try:
                    prices = json.loads(prices)
                except Exception:
                    continue
            if not isinstance(prices, list) or not prices:
                continue
            yes = parse_float(prices[0])
            if yes is None:
                continue
            legs.append((yes, liq))
        if len(legs) >= 3:
            sum_yes = sum(l[0] for l in legs)
            out.append({
                "event": str(e.get("title") or "?")[:60],
                "n_outcomes": len(legs),
                "sum_yes": round(sum_yes, 4),
                "yes_basket_edge_pct": round((1 - sum_yes) * 100, 2),   # >0: купить все YES
                "no_basket_edge_pct": round((sum_yes - 1) * 100, 2),    # >0: купить все NO
                "min_leg_liquidity": round(min(l[1] for l in legs)),
                "vol24": round(float(e.get("volume24hr") or 0)),
                "end_date": str(e.get("endDate") or "")[:10],
            })
    out.sort(key=lambda b: -max(abs(b["yes_basket_edge_pct"]), abs(b["no_basket_edge_pct"])))
    return out


def main():
    events = fetch_events()
    print(f"Активных событий загружено: {len(events)}")
    baskets, spreads = analyze_events(events)
    liq = liquid_baskets(events)
    print(f"negRisk-корзин: {len(baskets)}, из них ЖИВЫХ (нога >$500): {len(liq)}\n")

    print("=== ТОП ЖИВЫХ корзин по |эджу| (миды; реальный эдж меньше на спрэды) ===")
    for b in liq[:15]:
        side = "BUY-YES-ALL" if b["yes_basket_edge_pct"] > 0 else "BUY-NO-ALL"
        edge = max(b["yes_basket_edge_pct"], b["no_basket_edge_pct"])
        print(f"  [{side}] {b['event'][:52]:<54} n={b['n_outcomes']:<3} ΣYES={b['sum_yes']:.3f} "
              f"эдж≈{edge:+.2f}% до {b['end_date']} minLiq=${b['min_leg_liquidity']:,.0f} vol24=${b['vol24']:,.0f}")

    wide = [s for s in spreads if s["spread_pct"] >= 2]
    print(f"\n=== Широкие спрэды ≥2ц у объёмных рынков (MM-кандидаты): {len(wide)} ===")
    for s in wide[:12]:
        print(f"  {s['q']:<62} спрэд {s['spread_pct']:>5.2f}¢ mid={s['mid']:.3f} "
              f"vol24=${s['vol24']:,.0f} liq=${s['liquidity']:,.0f}")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"generated": "2026-10-21", "liquid_baskets": liq,
               "neg_risk_baskets_all": baskets[:80], "spreads_top": spreads[:60]},
              open(OUT, "w"), indent=1, ensure_ascii=False)
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
