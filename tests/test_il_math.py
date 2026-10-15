"""Тесты математики impermanent loss (models/il_math.py)."""
import math

import pytest

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.il_math import (
    il_v2, il_for_move, position_value_concentrated, il_concentrated,
    fee_apr_needed_to_cover_il, expected_il_from_vol,
)


class TestILv2:
    def test_no_move_no_loss(self):
        assert il_v2(1.0) == pytest.approx(0.0)

    def test_known_values(self):
        # Классические точки (Uniswap docs): x1.1 -> ~0.11%, x1.25 -> ~0.62%,
        # x2 -> ~5.72%, x4 -> ~20%
        assert abs(il_for_move(0.10)) == pytest.approx(0.0011344, abs=2e-4)
        assert il_v2(1.25) == pytest.approx(-0.0062, abs=2e-4)
        assert il_v2(2.0) == pytest.approx(2 * math.sqrt(2) / 3 - 1)
        assert il_v2(2.0) == pytest.approx(-0.0572, abs=1e-4)
        assert il_v2(4.0) == pytest.approx(-0.2000, abs=1e-4)

    def test_symmetry(self):
        # il_v2(r) == il_v2(1/r)
        for r in [0.25, 0.5, 0.8, 1.2, 2.0, 4.0]:
            assert il_v2(r) == pytest.approx(il_v2(1.0 / r), abs=1e-12)

    def test_always_le_zero(self):
        for r in [0.05, 0.3, 0.7, 1.5, 3.0, 20.0]:
            assert il_v2(r) <= 0.0

    def test_extreme(self):
        # цена к нулю: LP -> 0 vs HODL -> 0.5 -> IL -> -100%
        assert il_v2(1e-6) > -1.0
        assert il_v2(1e-12) == pytest.approx(-1.0, abs=1e-5)

    def test_invalid(self):
        with pytest.raises(ValueError):
            il_v2(0.0)
        with pytest.raises(ValueError):
            il_v2(-1.0)


class TestConcentrated:
    def test_at_center_no_move(self):
        # цена не изменилась -> стоимость неизменна, IL=0
        assert il_concentrated(1.0, 0.10) == pytest.approx(0.0, abs=1e-12)

    def test_concentrated_worse_than_v2(self):
        # При том же движении узкий диапазон теряет больше
        r = 1.05
        assert il_concentrated(r, 0.05) < il_v2(r) < 0
        assert il_concentrated(r, 0.10) < il_v2(r) < 0

    def test_narrower_worse(self):
        assert il_concentrated(1.05, 0.03) < il_concentrated(1.05, 0.10) < 0

    def test_out_of_range_total_conversion(self):
        # цена вышла за диапазон: позиция вся в одном активе
        v = position_value_concentrated(1.5, 0.9, 1.1, capital=1.0, price0=1.0)
        assert v > 0
        # IL при выходе за диапазон хуже, чем внутри
        assert il_concentrated(1.25, 0.10) < il_concentrated(1.15, 0.10)

    def test_value_bounds(self):
        # Внутри диапазона стоимость всегда положительна и растёт с ценой
        prev = 0.0
        for p in [0.95, 0.98, 1.0, 1.02, 1.05]:
            v = position_value_concentrated(p, 0.9, 1.1, capital=1.0, price0=1.0)
            assert v > 0
            assert v > prev
            prev = v

    def test_invalid(self):
        with pytest.raises(ValueError):
            il_concentrated(1.0, 0.0)
        with pytest.raises(ValueError):
            il_concentrated(1.0, 1.5)


class TestFeesBreakeven:
    def test_fee_needed_for_v2_double(self):
        # При удвоении цены нужен fee APR >= 5.72%
        need = fee_apr_needed_to_cover_il(2.0, 1.0)
        assert need == pytest.approx(0.0572, abs=1e-4)

    def test_half_year_scales(self):
        assert fee_apr_needed_to_cover_il(2.0, 0.5) == pytest.approx(0.1144, abs=1e-4)

    def test_no_move_no_fees_needed(self):
        assert fee_apr_needed_to_cover_il(1.0, 1.0) == pytest.approx(0.0)


class TestExpectedIL:
    def test_zero_vol_zero_il(self):
        assert expected_il_from_vol(0.0) == pytest.approx(0.0)

    def test_grows_with_vol_squared(self):
        # удвоение волатильности учетверяет ожидаемый IL
        low = expected_il_from_vol(0.30)
        high = expected_il_from_vol(0.60)
        assert high == pytest.approx(4 * low, abs=1e-12)

    def test_realistic_magnitude(self):
        # ETH 60% годовой вол: E[IL] ≈ 0.36/8 = 4.5% в год
        assert expected_il_from_vol(0.60) == pytest.approx(0.045)

    def test_concentrated_amplified(self):
        assert expected_il_from_vol(0.60, 1.0, 0.05) > expected_il_from_vol(0.60)
