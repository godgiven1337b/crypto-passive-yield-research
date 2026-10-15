"""
funding_model.py — модель доходности дельта-нейтральных стратегий (Ethena-подобных).

Механика: доход = funding rate, получаемый за шорт-позицию перпетуалов,
хеджирующую спот-collateral. Плюс base & burn / T-bill доход на часть collateral.

Формулы:
- Funding обычно платится каждые 8ч (3 раза в день, на Binance и др.).
  Годовая ставка = среднее funding per period * periods_per_year.
- Ожидаемая доходность с горизонтом: E[r] = mean_funding_annualized - fees_drag
- Стресс: отрицательный funding в течение k дней с силой f.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def annualize_funding(avg_funding_per_8h: float, periods_per_year: float = 3 * 365) -> float:
    """Годовая ставка funding из среднего на 8-часовой период.

    annualize_funding(0.0001) = 0.0001 * 1095 = 0.1095 (10.95% годовых).
    """
    return avg_funding_per_8h * periods_per_year


def funding_to_apy(funding_series_8h: list[float], protocol_fee: float = 0.20,
                   periods_per_year: float = 3 * 365) -> float:
    """APY sUSDe-подобного инструмента из серии 8-часовых funding-платежей.

    Компаундирует фактические платежи за период и экстраполирует на год.
    protocol_fee — доля, забираемая протоколом (Ethena: 20%).
    """
    if not funding_series_8h:
        raise ValueError("empty series")
    net = [(1.0 - protocol_fee) * f for f in funding_series_8h]
    growth = float(np.prod([1.0 + f for f in net]))
    periods = len(net)
    if growth <= 0:
        return -1.0
    apy = growth ** (periods_per_year / periods) - 1.0
    return apy


@dataclass
class DeltaNeutralPosition:
    """Позиция типа sUSDe: базовая ставка = funding + опционально T-bill на collateral."""
    name: str
    funding_annual_mean: float      # средний годовой funding (доля)
    funding_annual_vol: float       # волатильность годовой ставки
    tbill_on_collateral: float = 0.0  # доход на незанятый collateral
    protocol_fee: float = 0.20
    negative_funding_prob: float = 0.15   # вероятность квартала с отрицательным суммарным funding
    negative_funding_severity: float = 0.10  # сколько теряем за такой квартал (доля)
    counterparty_risk_p: float = 0.01    # вероятность события контрагента (биржа/кастодиан)
    counterparty_lgd: float = 0.30       # потеря при событии (диверсификация бирж снижает)

    def expected_yield(self) -> float:
        funding_net = (self.funding_annual_mean - self.tbill_on_collateral * 0) * (1.0 - self.protocol_fee)
        base = funding_net + self.tbill_on_collateral
        tail = self.negative_funding_prob * self.negative_funding_severity
        cp = self.counterparty_risk_p * self.counterparty_lgd
        return base - tail - cp

    def stress_scenario(self, months_negative: int = 3, annual_negative_rate: float = -0.10) -> float:
        """Годовой результат, если `months_negative` месяцев funding = annual_negative_rate."""
        frac = months_negative / 12.0
        blended = self.funding_annual_mean * (1.0 - frac) + annual_negative_rate * frac
        return blended * (1.0 - self.protocol_fee) + self.tbill_on_collateral

    def simulate_year(self, n_sims: int = 100_000, seed: int = 11) -> dict:
        """Монте-Карло годовой доходности: funding ~ N(mean, vol), кварты стресса."""
        rng = np.random.default_rng(seed)
        # Дробим год на 4 квартала; каждый квартал funding-ставка ~ N(mean, vol/sqrt(4)) с шумом
        quarterly = rng.normal(self.funding_annual_mean, self.funding_annual_vol / 2.0, (n_sims, 4))
        annual = quarterly.mean(axis=1)
        net = annual * (1.0 - self.protocol_fee) + self.tbill_on_collateral
        # хвост: контрагентскийイベント
        evt = rng.random(n_sims) < self.counterparty_risk_p
        net = np.where(evt, net - self.counterparty_lgd, net)
        return {
            "mean": float(net.mean()),
            "p5": float(np.percentile(net, 5)),
            "p50": float(np.percentile(net, 50)),
            "p95": float(np.percentile(net, 95)),
            "prob_negative": float((net < 0).mean()),
        }


def cash_and_carry(spot: float, perp_basis_annualized: float, fees_in: float,
                   fees_out: float, funding_annual_mean: float,
                   holding_years: float = 1.0) -> float:
    """Доходность самостоятельного cash-and-carry (спот + шорт перп).

    fees_in/out — торговые комиссии входа/выхода в долях от капитала.
    Возвращает годовую нетто-доходность.
    """
    total_fees = fees_in + fees_out
    gross = funding_annual_mean * holding_years + perp_basis_annualized * holding_years
    net = gross - total_fees
    return net / holding_years
