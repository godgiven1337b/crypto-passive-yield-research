"""Тесты математики лупинга (models/loop_math.py)."""
import pytest

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.loop_math import (
    loop_apy, max_leverage, carry_breakeven_leverage,
    liquidation_move_same_asset, effective_hack_risk, loop_stack_ev, optimal_leverage,
    same_pool_spread,
)


class TestLoopApy:
    def test_no_leverage_equals_supply(self):
        assert loop_apy(0.05, 0.04, 1.0) == pytest.approx(0.05)

    def test_classic_positive_carry(self):
        # s=5%, b=4%, L=3: 3*5% - 2*4% = 7%
        assert loop_apy(0.05, 0.04, 3.0) == pytest.approx(0.07)

    def test_negative_carry_kills(self):
        # s=4%, b=5%, L=3: 12% - 10% = 2%? нет: 3*4-2*5 = 2% ... подожди
        # 3*0.04 - 2*0.05 = 0.12 - 0.10 = 0.02 > 0!
        # Отрицательный carry s<b даёт d(APY)/dL = s-b < 0, но при L=3 всё ещё +
        # из-за константы b: carry(L) = L(s-b)+b
        assert loop_apy(0.04, 0.05, 3.0) == pytest.approx(0.02)
        # а вот выше безлупового уровня:
        assert loop_apy(0.04, 0.05, 3.0) < 0.04

    def test_spread_amplification(self):
        # каждый +1 к L добавляет (s-b): 5%-4.5% = 0.5% на единицу плеча
        l2 = loop_apy(0.05, 0.045, 2.0)
        l3 = loop_apy(0.05, 0.045, 3.0)
        assert l3 - l2 == pytest.approx(0.005)

    def test_reward_boosts_supply_leg(self):
        base = loop_apy(0.05, 0.04, 3.0)
        boosted = loop_apy(0.05, 0.04, 3.0, reward_apy_on_supply=0.01)
        assert boosted - base == pytest.approx(0.03)  # 1% на supply-часть * L=3

    def test_invalid_leverage(self):
        with pytest.raises(ValueError):
            loop_apy(0.05, 0.04, 0.5)

    def test_jupiter_spike_scenario(self):
        """Луп на пике всплеска ставки (Jupiter 8.98% supply, borrow ~9.5%): ловушка.

        Если borrow растёт вместе со supply (kink утилизации), carry может быть
        отрицательным даже при высокой supply-ставке.
        """
        # при kink borrow rate кратко был 15.3%
        assert loop_apy(0.0898, 0.153, 2.0) < loop_apy(0.0898, 0.08, 2.0)


class TestMaxLeverage:
    def test_aave_usdc_ltv(self):
        # LTV 0.81, буфер 0.65 -> L = 1/(1-0.5265) = 2.112
        assert max_leverage(0.81, 0.65) == pytest.approx(2.112, abs=0.001)

    def test_higher_ltv_more_leverage(self):
        assert max_leverage(0.9) > max_leverage(0.7)

    def test_full_ltv_rejected(self):
        # ltv=1.0 некорректен (проверка входа) — луп с полным LTV = гарантированная ликвидация
        with pytest.raises(ValueError):
            max_leverage(1.0, 1.0)

    def test_invalid(self):
        with pytest.raises(ValueError):
            max_leverage(0.0)
        with pytest.raises(ValueError):
            max_leverage(0.8, 0.0)


class TestLiquidation:
    def test_same_asset_needs_huge_depeg(self):
        # L=2, liquidation LTV 0.85: LTV0 = 0.5; нужен depeg коллатераля к долгу
        move = liquidation_move_same_asset(2.0, 0.85)
        assert move == pytest.approx(1 - 0.5 / 0.85)  # ~41% depeg

    def test_higher_leverage_closer_liquidation(self):
        m2 = liquidation_move_same_asset(2.0, 0.85)
        m3 = liquidation_move_same_asset(3.0, 0.85)
        assert m3 < m2  # при L=3 (LTV0=0.667) нужен меньший depeg

    def test_already_liquidatable(self):
        assert liquidation_move_same_asset(2.0, 0.4, start_ltv=0.5) == 0.0


class TestSamePoolSpread:
    def test_negative_at_any_utilization(self):
        for u in (0.1, 0.5, 0.8, 0.99):
            s, spread = same_pool_spread(0.09, u, 0.10)
            assert spread < 0  # луп внутри одного пула всегда убыточен

    def test_high_utilization_minimizes_loss(self):
        _, spread_low = same_pool_spread(0.09, 0.3, 0.10)
        _, spread_high = same_pool_spread(0.09, 0.99, 0.10)
        assert spread_high > spread_low  # ближе к нулю, но не положителен
        assert spread_high == pytest.approx(-0.09 * (1 - 0.99 * 0.9))

    def test_zero_reserve_factor_still_negative(self):
        _, spread = same_pool_spread(0.09, 0.9, 0.0)
        assert spread == pytest.approx(-0.009)  # даже RF=0: s−b = −b(1−u) < 0


class TestStackRisk:
    def test_layers_compound(self):
        p1 = effective_hack_risk([1], 0.008)
        p3 = effective_hack_risk([1, 2, 3], 0.008)
        assert p3 > p1
        assert p1 == pytest.approx(0.008)
        assert p3 == pytest.approx(1 - 0.992 ** 3)

    def test_ev_below_gross(self):
        r = loop_stack_ev(0.05, 0.04, 3.0, protocol_layers=2)
        assert r["ev_apy"] < r["gross_apy"]
        assert r["gross_apy"] == pytest.approx(0.07)

    def test_optimal_leverage_monotone_when_carry_positive(self):
        res = optimal_leverage(0.05, 0.04, 0.81)
        apys = [r["gross_apy"] for r in res["results"]]
        assert all(a < b for a, b in zip(apys, apys[1:]))  # APY растёт с плечом
        # но depeg-до-ликвидации падает
        moves = [r["depeg_move_to_liquidation_pct"] for r in res["results"]]
        assert all(a > b for a, b in zip(moves, moves[1:]))

    def test_no_carry_no_loop(self):
        assert carry_breakeven_leverage(0.04, 0.05) is None
        assert carry_breakeven_leverage(0.05, 0.04) == float("inf")
