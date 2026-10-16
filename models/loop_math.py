"""
loop_math.py — математика лупинга (supply → borrow → supply) для максимизации APY.

С капиталом C: supply = L·C, borrow = (L−1)·C.
  APY_на_капитал = L·s − (L−1)·b, где s = supply APY, b = borrow APY.
Положительный carry: s > b. Прибыль от плеча: d(APY)/dL = s − b.

Максимальное плечо из LTV: L_max = 1/(1−LTV)  (LTV кредитной пары).
Практическое плечо: L = 1/(1−k·LTV), k ≈ 0.6–0.7 — буфер до ликвидации.

Ликвидация: для same-asset пулов (sUSDe/USDe) ценового риска нет; для LST (wstETH/ETH)
дистанция ликвидации зависит от движения цены и плеча.

Также: учёт смарт-контрактного стека (каждый слой протокола умножает p_hack) и
стакинг наград (reward APY на supply-часть).
"""

from __future__ import annotations

import math


def loop_apy(supply_apy: float, borrow_apy: float, leverage: float,
             reward_apy_on_supply: float = 0.0) -> float:
    """APY на капитал при лупе. Все ставки — доли (0.05 = 5%).

    leverage = 1.0 — без плеча; 3.0 — депозит 3x капитала.
    """
    if leverage < 1.0:
        raise ValueError("leverage must be >= 1")
    total_supply_rate = supply_apy + reward_apy_on_supply
    return leverage * total_supply_rate - (leverage - 1.0) * borrow_apy


def max_leverage(ltv: float, buffer_fraction: float = 0.65) -> float:
    """Практическое плечо при данном LTV и буфере.

    ltv=0.81 (Aave USDC), buffer 0.65 -> L = 1/(1-0.5265) ≈ 2.11x
    """
    if not (0 < ltv < 1):
        raise ValueError("ltv in (0,1)")
    if not (0 < buffer_fraction <= 1):
        raise ValueError("buffer_fraction in (0,1]")
    return 1.0 / (1.0 - buffer_fraction * ltv)


def carry_breakeven_leverage(supply_apy: float, borrow_apy: float) -> float | None:
    """При каком плече carry = 0. Возвращает None, если s <= b (луп всегда убыточен).

    carry(L) = L·s − (L−1)·b = L·(s−b) + b. При s > b растёт с L без ограничений
    (кроме ликвидации); при s <= b — луп не имеет смысла.
    """
    if supply_apy <= borrow_apy:
        return None
    return math.inf


def liquidation_move_same_asset(leverage: float, liquidation_ltv: float,
                                start_ltv: float | None = None) -> float:
    """Насколько должен 'подорожать долг против коллатераля' для ликвидации (same-asset почти не бывает).

    Для LST: ликвидация при LTV_текущем > liquidation_ltv.
    Текущий LTV при плече L и начальном LTV0 = (L−1)/L (полностью заёмщик-безопасная точка):
      LTV(p) = LTV0 · (debt/collateral growth).
    Для same-asset стейблов возвращает требуемое расхождение цен (практически depeg).
    """
    ltv0 = start_ltv if start_ltv is not None else (leverage - 1.0) / leverage
    if ltv0 >= liquidation_ltv:
        return 0.0  # уже в зоне ликвидации
    # цена коллатераля должна упасть так, чтобы LTV0/price_drop > liquidation_ltv
    price_drop = 1.0 - ltv0 / liquidation_ltv
    return price_drop  # доля падения collateral к долгу


def effective_hack_risk(layers: list[float], per_layer_p_hack: float = 0.008) -> float:
    """Совокупный риск стека протоколов: каждый слой независим.

    layers — количество протоколов в цепочке (например Aave+Flashloan+Wrapper=3).
    Возвращает годовую вероятность инцидента.
    """
    if len(layers) == 0 and isinstance(layers, list):
        return 0.0
    n = len(layers) if isinstance(layers, list) else int(layers)
    return 1.0 - (1.0 - per_layer_p_hack) ** n


def loop_stack_ev(supply_apy: float, borrow_apy: float, leverage: float,
                  protocol_layers: int = 2, p_hack_per_layer: float = 0.008,
                  lgd: float = 0.8, reward_apy_on_supply: float = 0.0) -> dict:
    """EV лупа: APY минус хвост-риск стека протоколов."""
    apy = loop_apy(supply_apy, borrow_apy, leverage, reward_apy_on_supply)
    n_layers = protocol_layers + 1  # +1 за сам факт лупа (доп. код интеграции)
    p = effective_hack_risk(list(range(n_layers)), p_hack_per_layer)
    ev = apy - p * lgd
    return {
        "gross_apy": apy,
        "stack_hack_p_annual": p,
        "ev_apy": ev,
        "reward_share_of_apy": reward_apy_on_supply * leverage / apy if apy > 0 else 0.0,
    }


def optimal_leverage(supply_apy: float, borrow_apy: float, ltv: float,
                     buffer_fraction: float = 0.65,
                     tail_per_layer: float = 0.008, lgd: float = 0.8) -> dict:
    """Перебор плеча: EV = loop APY − tail. Показывает, растёт ли EV с плечом.

    Хвост растёт с числом слоёв слабо (p^n), поэтому при s > b EV почти всегда растёт
    с L — ограничитель не EV, а ликвидационный риск и ёмкость.
    """
    results = []
    for k in [0.5, 0.6, 0.65, 0.7, 0.75, 0.8]:
        L = max_leverage(ltv, k)
        r = loop_stack_ev(supply_apy, borrow_apy, L, protocol_layers=1,
                          p_hack_per_layer=tail_per_layer, lgd=lgd)
        liq_move = liquidation_move_same_asset(L, ltv * 1.05)  # liquidation threshold чуть выше LTV
        results.append({"buffer_k": k, "leverage": round(L, 2),
                        "gross_apy": round(r["gross_apy"], 4),
                        "ev_apy": round(r["ev_apy"], 4),
                        "depeg_move_to_liquidation_pct": round(liq_move * 100, 1)})
    return {"results": results,
            "carry_per_leverage_unit": supply_apy - borrow_apy}
