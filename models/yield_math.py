"""
yield_math.py — базовая математика доходности.

Единицы соглашений:
- Все ставки (APR, fee) передаются в ДОЛЯХ (0.07 = 7%) или в процентах там,
  где имя аргумента заканчивается на _pct (7.0 = 7%).
- Время в годах (долях года).

Формулы:
- APY при n компаундирований в год:  APY = (1 + APR/n)^n - 1
- Непрерывный: APY = exp(APR) - 1
- Нетто-ставка после m комиссий: r_net = r * prod(1 - fee_i)
- Газ-издержки: амортизация на горизонт = gas_cost / capital / horizon_years
"""

from __future__ import annotations

import math
from dataclasses import dataclass


def apr_to_apy(apr: float, compounds_per_year: float = 365.0) -> float:
    """Перевод APR (простая ставка) в APY при заданной частоте компаундинга.

    apr_to_apy(0.07, 365) ≈ 0.0725 (7.25%)
    """
    if apr <= -1:
        raise ValueError("APR must be > -100%")
    n = compounds_per_year
    if n <= 0:
        raise ValueError("compounds_per_year must be > 0")
    return (1.0 + apr / n) ** n - 1.0


def apr_to_apy_continuous(apr: float) -> float:
    """Непрерывный компаундинг: e^apr - 1."""
    return math.exp(apr) - 1.0


def apy_to_apr(apy: float, compounds_per_year: float = 365.0) -> float:
    """Обратное преобразование APY -> APR."""
    n = compounds_per_year
    return ((1.0 + apy) ** (1.0 / n) - 1.0) * n


def net_rate(gross_apr: float, fees: list[float]) -> float:
    """Нетто-APR после вычитания долей комиссий из процентного дохода.

    fees = [0.1] означает, что протокол забирает 10% от начисленных процентов.
    Комиссии применяются последовательно к остатку.
    """
    if any(f < 0 or f > 1 for f in fees):
        raise ValueError("fee shares must be in [0, 1]")
    factor = 1.0
    for f in fees:
        factor *= (1.0 - f)
    return gross_apr * factor


def gas_drag(gas_cost_usd: float, capital_usd: float, horizon_years: float,
             entries: int = 1) -> float:
    """Годовое снижение доходности из-за газа/комиссий сети.

    gas_drag(50, 10_000, 1, 2) = 0.01 -> 1% годовых при $50 газа дважды.
    """
    if capital_usd <= 0 or horizon_years <= 0 or entries <= 0:
        raise ValueError("capital, horizon, entries must be > 0")
    return (gas_cost_usd * entries) / capital_usd / horizon_years


def auto_compound_gain(apr: float, manual_compounds_per_year: float = 12.0) -> float:
    """Выигрыш от автокомпаундинга (365/год) vs ручного с заданной частотой.

    Возвращает разницу APY - APR_эквивалент_ручного в процентных пунктах (долях).
    """
    auto = apr_to_apy(apr, 365.0)
    manual = apr_to_apy(apr, manual_compounds_per_year)
    return auto - manual


@dataclass
class YieldStream:
    """Поток доходности одного инструмента (все ставки — доли APR)."""
    name: str
    base_apr: float = 0.0            # базовая ставка (например, lending)
    incentive_apr: float = 0.0       # токен-инсентивы (нестабильные)
    reward_token_volatility: float = 0.5   # ожидаемое падение цены reward-токена
    protocol_fee: float = 0.0        # доля процентов, забираемая протоколом
    gas_cost_usd: float = 0.0        # суммарный газ на вход+выход
    capital_usd: float = 1.0

    def conservative_apr(self, haircut_incentives: bool = True) -> float:
        """Консервативная оценка APR: fees + haircut инсентивов + газ."""
        base_net = net_rate(self.base_apr, [self.protocol_fee])
        if haircut_incentives:
            inc = self.incentive_apr * (1.0 - self.reward_token_volatility)
        else:
            inc = self.incentive_apr
        gas = gas_drag(self.gas_cost_usd, self.capital_usd, 1.0)
        return base_net + inc - gas

    def apy(self, haircut_incentives: bool = True) -> float:
        return apr_to_apy(self.conservative_apr(haircut_incentives))


def blended_rate(rates: list[tuple[float, float]]) -> float:
    """Взвешенная ставка: [(вес, ставка), ...]. Веса нормируются к 1."""
    total_w = sum(w for w, _ in rates)
    if total_w <= 0:
        raise ValueError("total weight must be > 0")
    return sum(w * r for w, r in rates) / total_w
