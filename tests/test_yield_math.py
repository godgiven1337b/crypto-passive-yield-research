"""Тесты базовой математики доходности (models/yield_math.py)."""
import math

import pytest

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.yield_math import (
    apr_to_apy, apr_to_apy_continuous, apy_to_apr, net_rate,
    gas_drag, auto_compound_gain, YieldStream, blended_rate,
)


class TestAprApy:
    def test_zero(self):
        assert apr_to_apy(0.0) == 0.0

    def test_simple_compounding(self):
        # 7% APR при ежедневном компаундинге -> ~7.25% APY
        assert apr_to_apy(0.07, 365) == pytest.approx(0.0725, abs=1e-4)

    def test_annual_compound_equals_apr(self):
        assert apr_to_apy(0.10, 1) == pytest.approx(0.10)

    def test_continuous_is_upper_bound(self):
        # непрерывный компаундинг максимален
        assert apr_to_apy_continuous(0.10) > apr_to_apy(0.10, 365)
        assert apr_to_apy_continuous(0.10) == pytest.approx(0.10517, abs=1e-5)

    def test_roundtrip(self):
        apy = apr_to_apy(0.08, 52)
        assert apy_to_apr(apy, 52) == pytest.approx(0.08, abs=1e-9)

    def test_high_rates(self):
        # 100% APR: (1+1/365)^365 - 1 ≈ 171%
        assert apr_to_apy(1.0, 365) == pytest.approx(1.7145, abs=1e-3)

    def test_negative_apr(self):
        # допустимо (отрицательный funding) —loses money
        assert apr_to_apy(-0.05, 365) == pytest.approx(-0.0488, abs=1e-3)

    def test_invalid(self):
        with pytest.raises(ValueError):
            apr_to_apy(-1.5)
        with pytest.raises(ValueError):
            apr_to_apy(0.1, 0)


class TestFeesAndGas:
    def test_net_rate_single_fee(self):
        # 10% от процентов протоколу: 8% * 0.9 = 7.2%
        assert net_rate(0.08, [0.10]) == pytest.approx(0.072)

    def test_net_rate_stacked(self):
        # две комиссии 10% и 5%: 0.08 * 0.9 * 0.95
        assert net_rate(0.08, [0.10, 0.05]) == pytest.approx(0.08 * 0.9 * 0.95)

    def test_net_rate_zero_fee(self):
        assert net_rate(0.08, []) == pytest.approx(0.08)

    def test_net_rate_invalid(self):
        with pytest.raises(ValueError):
            net_rate(0.08, [1.5])

    def test_gas_drag(self):
        # $100 газа на $10,000 за год = 1%
        assert gas_drag(100, 10_000, 1.0) == pytest.approx(0.01)

    def test_gas_drag_small_capital_matters(self):
        # $50 газа на $500 -> 10% годовых drag: мелкий капитал в Ethereum невыгоден
        assert gas_drag(50, 500, 1.0) == pytest.approx(0.10)

    def test_gas_drag_invalid(self):
        with pytest.raises(ValueError):
            gas_drag(10, 0, 1.0)


class TestCompoundingGain:
    def test_auto_compound_positive(self):
        gain = auto_compound_gain(0.10, 12)
        assert gain > 0
        # при 10% APR выигрыш ~0.05-0.06 п.п.
        assert gain < 0.006

    def test_zero_rate_no_gain(self):
        assert auto_compound_gain(0.0) == pytest.approx(0.0)


class TestYieldStream:
    def test_conservative_apr(self):
        ys = YieldStream("test", base_apr=0.10, incentive_apr=0.05,
                         reward_token_volatility=0.5, protocol_fee=0.1,
                         gas_cost_usd=0, capital_usd=1)
        # base net = 0.09; incentives haircut 50% -> 0.025; итого 0.115
        assert ys.conservative_apr() == pytest.approx(0.115)

    def test_gas_reduces(self):
        ys = YieldStream("t", base_apr=0.10, gas_cost_usd=100, capital_usd=10_000)
        assert ys.conservative_apr() == pytest.approx(0.09)

    def test_apy_compounds(self):
        ys = YieldStream("t", base_apr=0.10, incentive_apr=0, protocol_fee=0, gas_cost_usd=0)
        assert ys.apy() == pytest.approx(apr_to_apy(0.10), abs=1e-9)


class TestBlended:
    def test_blended(self):
        assert blended_rate([(0.5, 0.05), (0.5, 0.07)]) == pytest.approx(0.06)

    def test_blended_normalizes(self):
        assert blended_rate([(2, 0.05), (2, 0.07)]) == pytest.approx(0.06)

    def test_blended_invalid(self):
        with pytest.raises(ValueError):
            blended_rate([(0, 0.05)])
