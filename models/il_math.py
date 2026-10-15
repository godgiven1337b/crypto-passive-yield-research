"""
il_math.py — математика impermanent loss (IL) для AMM.

v2 (full-range, 50/50):
  Стоимость LP при движении цены в r раз:   V_lp  = V0 * sqrt(r) * (L фикс.)
  Стоимость HODL (просто держать те же доли): V_h = V0 * (1 + r) / 2
  IL(r) = V_lp / V_h - 1 = 2*sqrt(r)/(1+r) - 1

Concentrated liquidity (Uniswap v3):
  Диапазон [p_lo, p_hi], начальная цена p0 (по умолчанию геом. центр).
  При p < p_lo позиция 100% в токене base; при p > p_hi — 100% в quote;
  внутри — x(p) и y(p) из уравнений ликвидности Uniswap v3.
"""

from __future__ import annotations

import math


def il_v2(price_ratio: float) -> float:
    """Классический IL для full-range 50/50 AMM. Отрицательный = потеря vs HODL.

    il_v2(1.0)=0; il_v2(1.21)≈ -0.0199 (~-2%); il_v2(0.5)≈ -0.0572 (~-5.7%).
    Симметричен: il_v2(r) == il_v2(1/r).
    """
    if price_ratio <= 0:
        raise ValueError("price_ratio must be > 0")
    return 2.0 * math.sqrt(price_ratio) / (1.0 + price_ratio) - 1.0


def il_for_move(pct_move: float) -> float:
    """IL при движении цены на ±pct_move (0.10 = ±10%)."""
    if pct_move < 0:
        raise ValueError("pct_move must be >= 0 (амплитуда)")
    return il_v2(1.0 + pct_move)


def position_value_concentrated(price: float, p_lo: float, p_hi: float,
                                capital: float = 1.0, price0: float | None = None) -> float:
    """Стоимость Uniswap v3 позиции (в токене quote) при цене `price`.

    Начальный капитал `capital` делится 50/50 при цене price0
    (по умолчанию price0 = sqrt(p_lo*p_hi)). Формулы Uniswap v3 whitepaper:
      x = L * (sqrt(p_hi) - sqrt(p)) / (sqrt(p) * sqrt(p_hi))
      y = L * (sqrt(p) - sqrt(p_lo))
    """
    if not (0 < p_lo < p_hi):
        raise ValueError("require 0 < p_lo < p_hi")
    if price <= 0:
        raise ValueError("price must be > 0")
    if price0 is None:
        price0 = math.sqrt(p_lo * p_hi)
    if not (p_lo <= price0 <= p_hi):
        raise ValueError("price0 must be inside range")

    sp0, slo, shi = math.sqrt(price0), math.sqrt(p_lo), math.sqrt(p_hi)

    # На единицу ликвидности L при p0:
    x0_per_L = (shi - sp0) / (sp0 * shi)   # base-токен (ETH)
    y0_per_L = (sp0 - slo)                 # quote-токен (USDC)
    L = capital / (x0_per_L * price0 + y0_per_L)

    p = price
    if p <= p_lo:
        # Позиция полностью в base-токене: L * (shi - slo)... нет:
        # при p<p_lo вся позиция в base: amount = L * (1/sqrt(p_lo) - 1/sqrt(p_hi))
        base_amount = L * (1.0 / slo - 1.0 / shi)
        return base_amount * p
    if p >= p_hi:
        # Полностью в quote: L * (sqrt(p_hi) - sqrt(p_lo))
        return L * (shi - slo)

    sp = math.sqrt(p)
    x = L * (shi - sp) / (sp * shi)
    y = L * (sp - slo)
    return x * p + y


def il_concentrated(price_ratio: float, width: float) -> float:
    """IL концентрированной позиции относительно HODL.

    width — полуширина диапазона от начальной цены (0.10 = диапазон ±10%).
    Начальная цена = 1.0 (центр). HODL-бенчмарк: начальные 50/50.
    """
    if not (0 < width < 1):
        raise ValueError("width in (0,1), e.g. 0.10")
    p_lo, p_hi = 1.0 - width, 1.0 + width
    v_lp = position_value_concentrated(price_ratio, p_lo, p_hi, capital=1.0, price0=1.0)
    v_hodl = 0.5 * price_ratio + 0.5
    return v_lp / v_hodl - 1.0


def fee_apr_needed_to_cover_il(price_ratio: float, holding_years: float = 1.0,
                               concentrated_width: float | None = None) -> float:
    """Минимальный fee APR, при котором LP не хуже HODL при финальном движении r."""
    if holding_years <= 0:
        raise ValueError("holding_years must be > 0")
    if concentrated_width is None:
        loss = abs(il_v2(price_ratio))
    else:
        loss = abs(il_concentrated(price_ratio, concentrated_width))
    return loss / holding_years


def expected_il_from_vol(annual_vol: float, holding_years: float = 1.0,
                         concentrated_width: float | None = None) -> float:
    """Ожидаемый (средний) IL при GBM-цене, как положительная доля.

    Для v2: E[IL] ≈ sigma^2 * t / 8 (классическая аппроксимация).
    Для концентрированной позиции IL усиливается; консервативная эвристика
    усиления ~ 1/sqrt(width), ограничена 8x.
    """
    if annual_vol < 0:
        raise ValueError("vol must be >= 0")
    t = holding_years
    base = (annual_vol ** 2) * t / 8.0
    if concentrated_width is None:
        return base
    boost = min(8.0, 1.0 / math.sqrt(concentrated_width))
    return boost * base
