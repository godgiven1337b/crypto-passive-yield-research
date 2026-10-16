"""
strategies.py — синтез пассивных стратегий из риск-профилей инструментов.

Запуск:  python3 models/strategies.py
Читает data/*.json (если заполнены исследователями), иначе использует
дефолтные оценки (помечены DEFAULT, уточняются после исследования).
Выводит таблицу стратегий и risk-метрики -> report/strategies_output.md
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.risk_model import (
    ProtocolRisk, PortfolioPosition, expected_yield, portfolio_expected_yield,
    portfolio_loss_probability, var_cvar,
)
from models.portfolio import equal_weight, risk_budget_weights, kelly_allocation, summarize

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
OUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "report", "strategies_output.md")

RISK_FREE = 0.04  # уточняется по данным WS-6 (T-bill)


def load_json(name: str) -> list | dict:
    path = os.path.join(DATA_DIR, name)
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
        # поддержка обёрток {"meta": ..., "entries": [...]} и {"markets": [...]}
        if isinstance(data, dict):
            for key in ("entries", "markets", "instruments", "items", "data"):
                if isinstance(data.get(key), list):
                    return data[key]
        return data
    return []


def _f(x, default: float) -> float:
    """Безопасное приведение к float (None/пропуски -> default)."""
    try:
        v = float(x)
        if v != v:  # NaN
            return default
        return v
    except (TypeError, ValueError):
        return default


def instrument_universe() -> list[ProtocolRisk]:
    """Строит вселенную инструментов из данных WS; fallback — консервативные дефолты.

    Все ставки в JSON-данных указаны В ПРОЦЕНТАХ (5.0 = 5%); здесь нормализуются в доли.
    """
    instruments: list[ProtocolRisk] = []

    def add_pct(name, apy_pct, p_hack_pct=0.5, lgd=0.9, p_depeg=0.002, lgd_depeg=0.1,
                rate_vol=0.02, recovery=0.3, src="DEFAULT"):
        instruments.append(ProtocolRisk(
            name=f"{name} [{src}]",
            apy=_f(apy_pct, 4.0) / 100.0,
            p_hack=_f(p_hack_pct, 0.5) / 100.0,
            lgd_hack=lgd, p_depeg=p_depeg, lgd_depeg=lgd_depeg,
            rate_volatility=rate_vol, recovery_rate_hack=recovery))

    # --- данные WS1: lending ---
    ws1 = load_json("ws1_stablecoin_lending.json")
    if isinstance(ws1, list) and ws1:
        # одна (лучшая по TVL) запись на протокол, иначе 7 копий Morpho искажают вселенную
        best_by_protocol: dict = {}
        for it in ws1:
            proto = str(it.get("protocol", "?"))
            tvl = _f(it.get("tvl_usd"), 0)
            if proto not in best_by_protocol or tvl > _f(best_by_protocol[proto].get("tvl_usd"), 0):
                best_by_protocol[proto] = it
        for it in best_by_protocol.values():
            add_pct(f"{it.get('protocol')} {it.get('asset')}",
                    it.get("apy_pct", 4),
                    it.get("hack_probability_annual_pct", 0.5),
                    rate_vol=0.015, src="WS1")
    else:
        add_pct("Aave v3 USDC", 4.5, 0.2, rate_vol=0.015, recovery=0.5)
        add_pct("Morpho USDC vault", 5.0, 0.4, rate_vol=0.02, recovery=0.3)
        add_pct("sUSDS (Sky)", 6.5, 0.3, rate_vol=0.02, recovery=0.4)
        add_pct("Kamino USDC", 6.0, 0.6, rate_vol=0.025, recovery=0.2)

    # --- данные WS2: LST ---
    ws2 = load_json("ws2_lsd_restaking.json")
    if isinstance(ws2, list) and ws2:
        for it in ws2[:8]:
            total_apy = _f(it.get("base_apy_pct", 3), 3) + _f(it.get("extra_yield_pct", 0), 0)
            add_pct(it.get("instrument", "?"), total_apy,
                    it.get("hack_probability_annual_pct", 0.5),
                    p_depeg=0.005, lgd_depeg=0.05, rate_vol=0.005, src="WS2")
    else:
        add_pct("wstETH", 3.5, 0.3, p_depeg=0.005, lgd_depeg=0.04, rate_vol=0.004, recovery=0.4)
        add_pct("jitoSOL", 8.0, 0.6, p_depeg=0.005, lgd_depeg=0.04, rate_vol=0.004, recovery=0.2)

    # --- данные WS3: delta-neutral ---
    ws3 = load_json("ws3_delta_neutral.json")
    if isinstance(ws3, list) and ws3:
        for it in ws3[:5]:
            avg12 = it.get("avg_apy_12m_pct", it.get("current_apy_pct", 8))
            add_pct(it.get("instrument", "?"), avg12,
                    it.get("hack_probability_annual_pct", 1.0),
                    p_depeg=0.01, lgd_depeg=0.12, rate_vol=0.05, recovery=0.1, src="WS3")
    else:
        add_pct("sUSDe", 8.0, 1.2, lgd=0.7, p_depeg=0.01, lgd_depeg=0.12,
                rate_vol=0.06, recovery=0.1)

    # --- данные WS4: Pendle PT (только blue-chip стейбл-рынки для консервативных стратегий) ---
    ws4 = load_json("ws4_pendle.json")
    if isinstance(ws4, list) and ws4:
        for it in ws4:
            market = str(it.get("market", "?"))
            # не добавляем двойной префикс: market уже вида "PT-sUSDe 26NOV2026"
            label = market if market.startswith("PT-") else f"PT-{market}"
            add_pct(label, it.get("implied_apy_pct", 6),
                    0.8, p_depeg=0.004, lgd_depeg=0.06, rate_vol=0.002, src="WS4")

    # --- данные WS6: RWA ---
    ws6 = load_json("ws6_rwa_niche.json")
    if isinstance(ws6, list) and ws6:
        for it in ws6[:6]:
            add_pct(it.get("product", "?"), it.get("current_yield_pct", 4.5),
                    it.get("hack_probability_annual_pct", 0.4),
                    p_depeg=0.001, lgd_depeg=0.02, rate_vol=0.003, src="WS6")
    else:
        add_pct("Ondo USDY", 4.5, 0.3, p_depeg=0.001, lgd_depeg=0.02, rate_vol=0.002, recovery=0.6)
        add_pct("BUIDL (через интегратора)", 4.3, 0.2, p_depeg=0.001, lgd_depeg=0.02,
                rate_vol=0.002, recovery=0.8)

    return instruments


def pick_universe(instruments: list[ProtocolRisk]) -> dict[str, ProtocolRisk]:
    """Выбирает представительный набор по категориям (по префиксу имени)."""
    by_cat: dict[str, list[ProtocolRisk]] = {}
    for ins in instruments:
        cat = ins.name.split(" ")[0].split("-")[-1]
        by_cat.setdefault(cat, []).append(ins)
    picked = {}
    # лучшие по risk_adjusted_score в каждой категории
    for cat, lst in by_cat.items():
        best = max(lst, key=lambda r: (r.apy - r.p_hack * r.lgd_hack * (1 - r.recovery_rate_hack)))
        picked[cat] = best
    return picked


def build_strategies() -> dict[str, list[PortfolioPosition]]:
    universe = instrument_universe()
    picked = pick_universe(universe)

    # Используем осмысленные имена; fallback если каких-то категорий нет
    def find(substr: str, default: ProtocolRisk | None = None) -> ProtocolRisk | None:
        """Ищет инструмент, preferring самые ранние (данные WS1 идут раньше WS4)."""
        for p in universe:
            if substr.lower() in p.name.lower():
                return p
        return default

    aave = find("Aave v3")
    susds = find("Sky (sUSDS)")
    morpho = find("Morpho")
    wsteth = find("wstETH")
    susde = find("sUSDe")  # WS3-инструмент; PT-sUSDe не должен перехватить (WS1/3 раньше WS4? проверяем)
    if susde and susde.name.startswith("PT-"):
        susde = None
    ondo = find("USDY", find("Ondo"))
    buidl = find("BUIDL")
    jito = find("jitoSOL")
    # PT: предпочитаем blue-chip стейбл-фикс (sUSDS), не 18% junior-транши
    pt = None
    for pref in ("PT-sUSDS", "PT-sUSDe", "PT-"):
        for p in universe:
            if p.name.startswith(pref):
                pt = p
                break
        if pt:
            break

    strategies: dict[str, list[PortfolioPosition]] = {}

    # S1 Ультраконсервативный: только стейбл-доходность максимального качества
    s1 = []
    for pos, w in [(buidl, 0.30), (ondo, 0.20), (aave, 0.25), (susds, 0.25)]:
        if pos:
            s1.append(PortfolioPosition(pos, w))
    if s1:
        total = sum(p.weight for p in s1)
        s1 = [PortfolioPosition(p.risk, p.weight / total) for p in s1]
        strategies["S1 Ультраконсервативный"] = s1

    # S2 Консервативный+: S1 + LST + PT (фикс)
    s2 = []
    for pos, w in [(buidl, 0.15), (aave, 0.25), (susds, 0.20), (wsteth, 0.20), (pt, 0.20)]:
        if pos:
            s2.append(PortfolioPosition(pos, w))
    if s2:
        total = sum(p.weight for p in s2)
        s2 = [PortfolioPosition(p.risk, p.weight / total) for p in s2]
        strategies["S2 Консервативный+"] = s2

    # S3 Умеренный: + sUSDe + jitoSOL
    s3 = []
    for pos, w in [(aave, 0.20), (susds, 0.20), (wsteth, 0.20), (pt, 0.15),
                   (susde, 0.15), (jito, 0.10)]:
        if pos:
            s3.append(PortfolioPosition(pos, w))
    if s3:
        total = sum(p.weight for p in s3)
        s3 = [PortfolioPosition(p.risk, p.weight / total) for p in s3]
        strategies["S3 Умеренный"] = s3

    # S4 Риск-бюджет (модельный): автоматическая аллокация
    rb = risk_budget_weights([p for p in [aave, susds, wsteth, susde, ondo, jito, pt, morpho] if p])
    strategies["S4 Риск-бюджет (модель)"] = rb

    return strategies


def render(strategies: dict[str, list[PortfolioPosition]]) -> str:
    lines = ["# Стратегии: модельный вывод (auto-generated)", "",
             f"Безрисковая ставка (T-bill): {RISK_FREE:.1%}", ""]
    for name, positions in strategies.items():
        ey = portfolio_expected_yield(positions)
        p50 = portfolio_loss_probability(positions, threshold=0.5)
        p25 = portfolio_loss_probability(positions, threshold=0.25)
        var95, cvar95 = var_cvar(positions, alpha=0.95, n_sims=80_000)
        var99, cvar99 = var_cvar(positions, alpha=0.99, n_sims=80_000)
        s = summarize(positions)
        lines += [f"## {name}", "",
                  f"- **E[APY] = {ey*100:.2f}%**",
                  f"- P(потеря >50% за год) = {p50*100:.3f}%; P(>25%) = {p25*100:.2f}%",
                  f"- VaR95 = {var95*100:.1f}%; CVaR95 = {cvar95*100:.1f}; "
                  f"VaR99 = {var99*100:.1f}%; CVaR99 = {cvar99*100:.1f}",
                  f"- Концентрация HHI = {s['hhi_concentration']:.2f}, позиций = {s['n_positions']}",
                  "", "| Инструмент | Вес | APY | E[y] | p_hack |", "|---|---|---|---|---|"]
        for p in sorted(positions, key=lambda x: -x.weight):
            lines.append(f"| {p.risk.name} | {p.weight*100:.0f}% | {p.risk.apy*100:.2f}% | "
                         f"{expected_yield(p.risk)*100:.2f}% | {p.risk.p_hack*100:.2f}% |")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    strategies = build_strategies()
    out = render(strategies)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write(out)
    print(out)
    print(f"\nSaved -> {OUT_PATH}")


if __name__ == "__main__":
    main()
