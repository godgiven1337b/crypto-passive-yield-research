"""
portfolio.py — аллокация портфеля пассивного дохода.

Методы:
- equal_weight: простое равновесие
- risk_budget: веса обратно пропорциональны риску (risk contribution equal)
- yield_tilted: максимизация E[yield] при ограничении на общий риск-бюджет
- kelly_fraction: для инструментов с положительным edge над безрисковой ставкой

Зависимости: numpy, models.risk_model.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from models.risk_model import ProtocolRisk, PortfolioPosition, expected_yield, portfolio_expected_yield


def _cash_position(risk_free: float) -> ProtocolRisk:
    """Синтетическая безрисковая позиция (T-bills / вывод в фиат)."""
    return ProtocolRisk(name=f"cash@{risk_free:.1%}", apy=risk_free, p_hack=0.0,
                        lgd_hack=0.0, p_depeg=0.0, lgd_depeg=0.0,
                        rate_volatility=0.0, recovery_rate_hack=0.0)


def equal_weight(risks: list[ProtocolRisk]) -> list[PortfolioPosition]:
    n = len(risks)
    return [PortfolioPosition(r, 1.0 / n) for r in risks]


def risk_budget_weights(risks: list[ProtocolRisk]) -> list[PortfolioPosition]:
    """Веса ∝ 1/risk_i, где risk_i = p_hack*lgd + p_depeg*lgd + rate_vol.

    Простейший inverse-volatility риск-бюджет: каждый инструмент вносит
    равный вклад в катастрофический риск портфеля.
    """
    risk_scores = []
    for r in risks:
        cat = r.p_hack * r.lgd_hack * (1.0 - r.recovery_rate_hack) + r.p_depeg * r.lgd_depeg
        total = cat + r.rate_volatility
        risk_scores.append(max(total, 1e-6))
    inv = np.array([1.0 / s for s in risk_scores])
    w = inv / inv.sum()
    # ограничение максимального веса (иначе ультрабезопасный инструмент забирает всё)
    cap = 0.40
    w = np.minimum(w, cap)
    if w.sum() > 0:
        w = w / w.sum()
    return [PortfolioPosition(r, float(wi)) for r, wi in zip(risks, w)]


def yield_tilted_weights(risks: list[ProtocolRisk], risk_free: float = 0.04,
                         max_weight: float = 0.40) -> list[PortfolioPosition]:
    """Максимизация суммы w_i * edge_i при сумме w_i * risk_i <= risk_budget.

    Жадная эвристика: сортируем по edge/risk (Sharpe-подобное отношение),
    наливаем до max_weight, пока не исчерпан риск-бюджет = средний риск равновесного
    портфеля (иначе решение вырождается в один лучший инструмент).

    edge_i = E[yield_i] - risk_free; risk_i как в risk_budget_weights.
    """
    edges = np.array([expected_yield(r) - risk_free for r in risks])
    risk_scores = np.array([
        max(r.p_hack * r.lgd_hack * (1 - r.recovery_rate_hack) + r.p_depeg * r.lgd_depeg + r.rate_volatility, 1e-6)
        for r in risks
    ])
    # риск-бюджет: равновесный портфель как ориентир (диверсификация сохраняется)
    budget = float(np.mean(risk_scores))
    ratio = edges / risk_scores
    order = np.argsort(-ratio)

    weights = np.zeros(len(risks))
    used_risk = 0.0
    for i in order:
        if edges[i] <= 0:
            continue
        w = min(max_weight, max(0.0, (budget - used_risk) / risk_scores[i]))
        if w <= 0:
            break
        weights[i] = w
        used_risk += w * risk_scores[i]
    positions = [PortfolioPosition(r, float(wi)) for r, wi in zip(risks, weights) if wi > 1e-9]
    # неизрасходованный остаток паркуем в безрисковый актив (честная cash-позиция)
    remainder = 1.0 - float(weights.sum())
    if remainder > 1e-9:
        positions.append(PortfolioPosition(_cash_position(risk_free), remainder))
    return positions


def kelly_allocation(risks: list[ProtocolRisk], risk_free: float = 0.04,
                     max_leverage: float = 1.0) -> list[PortfolioPosition]:
    """Дробный Келли для бинарных ставок «edge над безрисковой».

    Для инструмента с преимуществом e и вероятностью потери p*l (хвост):
    f* ≈ e / (p*l) — полный Келли; используем 1/4 Келли (консервативно),
    ограничиваем сумму весов единицей (без плеча) и max по инструменту 40%.
    """
    fracs = []
    for r in risks:
        e = expected_yield(r) - risk_free
        tail = r.p_hack * r.lgd_hack * (1 - r.recovery_rate_hack) + r.p_depeg * r.lgd_depeg
        if tail <= 0 or e <= 0:
            fracs.append(0.0)
        else:
            fracs.append(0.25 * e / tail)
    w = np.array(fracs)
    w = np.clip(w, 0, 0.40)
    if w.sum() > max_leverage:
        w = w * max_leverage / w.sum()
    positions = [PortfolioPosition(r, float(wi)) for r, wi in zip(risks, w) if wi > 1e-9]
    # неизрасходованный остаток — в безрисковый актив (дробный Келли не требует полного размещения)
    remainder = 1.0 - float(w.sum())
    if remainder > 1e-9:
        positions.append(PortfolioPosition(_cash_position(risk_free), remainder))
    return positions


@dataclass
class StrategyResult:
    name: str
    positions: list[PortfolioPosition]

    @property
    def expected_apy(self) -> float:
        return portfolio_expected_yield(self.positions)

    def describe(self) -> str:
        rows = [f"{p.risk.name:<28} {p.weight*100:5.1f}%  APY {p.risk.apy*100:5.2f}%  "
                f"E[y] {expected_yield(p.risk)*100:5.2f}%"
                for p in sorted(self.positions, key=lambda x: -x.weight)]
        return "\n".join([f"=== {self.name} | E[APY] = {self.expected_apy*100:.2f}% ==="] + rows)


def summarize(positions_list: list[PortfolioPosition]) -> dict:
    """Сводка для отчёта: веса, E[APY], концентрация (HHI)."""
    w = np.array([p.weight for p in positions_list])
    return {
        "expected_apy": portfolio_expected_yield(positions_list),
        "hhi_concentration": float((w ** 2).sum()),
        "n_positions": len(positions_list),
        "max_weight": float(w.max()),
    }
