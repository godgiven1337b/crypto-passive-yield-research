"""
risk_model.py — вероятностная модель рисков доходных стратегий.

Ключевая идея: номинальный APY — не ожидаемая доходность. Ожидаемая доходность
должна учитывать:
  1. Вероятность взлома/протокольного события (p_hack) и долю потерь (loss_given_hack)
  2. Вероятность depeg (для стейблов/LST) и глубину восстановления
  3. Волатильность самой ставки (для плавающих стратегий)
  4. Комиссии и газ

E[r] = (1 - p_loss) * r_yield + p_loss * (r_yield * (1 - LGD) - LGD_капитала)
Упрощённо: E[r] ≈ r_net - p_hack * LGD - p_depeg * depeg_loss + ...

Также: VaR/CVaR через аналитику и Монте-Карло (numpy).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class ProtocolRisk:
    """Риск-профиль одного протокола/инструмента.

    Все вероятности — годовые, доли. Потери — доли капитала в событии.
    """
    name: str
    apy: float                        # номинальный нетто-APY (доля, 0.05=5%)
    p_hack: float = 0.005             # вероятность взлома/эксплойта за год
    lgd_hack: float = 0.90            # loss given hack (доля позиции, обычно 0.3-1.0)
    p_depeg: float = 0.002            # вероятность depeg underlying за год
    lgd_depeg: float = 0.15           # средняя потеря при depeg (USDC-2023: ~восстановился, ~=5-10%)
    rate_volatility: float = 0.02     # волатильность ставки (для плавающих)
    recovery_rate_hack: float = 0.30  # доля, возвращаемая после взлома (Euler=1.0, обычно 0-0.5)
    correlations: dict = field(default_factory=dict)  # корреляции с другими инструментами по имени


def expected_yield(pr: ProtocolRisk) -> float:
    """Вероятностно-взвешенная годовая доходность (без учёта волатильности ставки).

    expected_yield(ProtocolRisk('x', 0.05, p_hack=0, ...)) == 0.05
    При p_hack=1%, LGD=0.9, recovery=30%: E ≈ 0.05 - 0.01*(0.9*(1-0.3)) = 0.05 - 0.0063
    """
    eff_hack_loss = pr.p_hack * pr.lgd_hack * (1.0 - pr.recovery_rate_hack)
    eff_depeg_loss = pr.p_depeg * pr.lgd_depeg
    # Если взлом случился, доходность тоже не получена за часть года — игнорируем (2-й порядок)
    return pr.apy - eff_hack_loss - eff_depeg_loss


def risk_penalty(pr: ProtocolRisk) -> float:
    """На сколько процентных пунктов (в долях) риск снижает номинальную ставку."""
    return pr.apy - expected_yield(pr)


def risk_adjusted_score(pr: ProtocolRisk) -> float:
    """Простой скор: E[yield] / (1 + penalty_волатильности ставки).

    Для сравнения инструментов между собой. Выше = лучше.
    """
    ey = expected_yield(pr)
    denom = 1.0 + pr.rate_volatility + pr.p_hack * pr.lgd_hack
    return ey / denom


@dataclass
class PortfolioPosition:
    risk: ProtocolRisk
    weight: float


def portfolio_expected_yield(positions: list[PortfolioPosition]) -> float:
    """E[yield] портфеля = сумма весов * E[yield]. Веса должны суммироваться в 1."""
    total_w = sum(p.weight for p in positions)
    if not np.isclose(total_w, 1.0, atol=1e-6):
        raise ValueError(f"weights must sum to 1, got {total_w}")
    return sum(p.weight * expected_yield(p.risk) for p in positions)


def portfolio_loss_probability(positions: list[PortfolioPosition],
                               threshold: float = 0.5) -> float:
    """Вероятность потерять больше threshold капитала за год от взломов.

    Считаем: потеря от i-го взлома = w_i * LGD_i. События независимы (консервативно —
    без учёка общих факторов типа одной цепочки). P(sum losses > threshold).
    Используем свёртку через Монте-Карло (быстрая аппроксимация).
    """
    rng = np.random.default_rng(42)
    n_sims = 200_000
    total_loss = np.zeros(n_sims)
    for p in positions:
        hacked = rng.random(n_sims) < p.risk.p_hack
        loss = hacked * p.weight * p.risk.lgd_hack * (1.0 - p.risk.recovery_rate_hack)
        depegged = rng.random(n_sims) < p.risk.p_depeg
        loss += depegged * p.weight * p.risk.lgd_depeg
        total_loss += loss
    return float((total_loss > threshold).mean())


def var_cvar(positions: list[PortfolioPosition], alpha: float = 0.95,
             n_sims: int = 100_000, seed: int = 7) -> tuple[float, float]:
    """Годовой VaR и CVaR портфеля (только катастрофические события + ставка).

    Модель: доход = yield (детерминированный) - потери (Бернулли * LGD).
    Возвращает (var, cvar) как ДОЛИ потерь капитала (положительные = убыток).
    """
    rng = np.random.default_rng(seed)
    losses = np.zeros(n_sims)
    yields = np.zeros(n_sims)
    for p in positions:
        hacked = rng.random(n_sims) < p.risk.p_hack
        loss = hacked * p.weight * p.risk.lgd_hack * (1.0 - p.risk.recovery_rate_hack)
        depegged = rng.random(n_sims) < p.risk.p_depeg
        loss += depegged * p.weight * p.risk.lgd_depeg
        # волатильность ставки: фактическая ставка ~ N(apy, rate_vol)
        realized_rate = rng.normal(p.risk.apy, p.risk.rate_volatility, n_sims)
        yields += p.weight * realized_rate
    net = yields - losses  # чистый годовой результат (доля)
    pnl_sorted = np.sort(net)
    # VaR_alpha: альфа-квантиль убытка = -(квантиль net)
    q = np.quantile(net, 1.0 - alpha)
    var = -q
    cvar = -pnl_sorted[pnl_sorted <= q].mean()
    return float(max(var, 0.0)), float(max(cvar, 0.0))


def breakeven_risk_tolerance(pr: ProtocolRisk, risk_free: float = 0.04) -> float:
    """Максимальная p_hack*lgd при которой инструмент всё ещё лучше risk_free.

    Возвращает допустимую годовую вероятность потери (в долях).
    """
    edge = pr.apy - risk_free - pr.p_depeg * pr.lgd_depeg
    lgd_eff = pr.lgd_hack * (1.0 - pr.recovery_rate_hack)
    if lgd_eff <= 0:
        return float("inf")
    return max(0.0, edge / lgd_eff)
