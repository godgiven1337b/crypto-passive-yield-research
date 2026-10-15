"""Тесты аллокации портфеля (models/portfolio.py) и funding-модели (funding_model.py)."""
import pytest

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.risk_model import ProtocolRisk, PortfolioPosition, expected_yield
from models.portfolio import (
    equal_weight, risk_budget_weights, yield_tilted_weights, kelly_allocation, summarize,
)
from models.funding_model import (
    annualize_funding, funding_to_apy, DeltaNeutralPosition, cash_and_carry,
)


def make(name, **kw):
    d = dict(name=name, apy=0.05, p_hack=0.005, lgd_hack=0.9,
             p_depeg=0.002, lgd_depeg=0.1, rate_volatility=0.02,
             recovery_rate_hack=0.3)
    d.update(kw)
    return ProtocolRisk(**d)


class TestAllocations:
    def test_equal_weight(self):
        pos = equal_weight([make("a"), make("b"), make("c")])
        assert sum(p.weight for p in pos) == pytest.approx(1.0)
        assert all(p.weight == pytest.approx(1 / 3) for p in pos)

    def test_risk_budget_favors_safe(self):
        risky = make("risky", apy=0.12, p_hack=0.04)
        safe = make("safe", apy=0.04, p_hack=0.0005)
        pos = risk_budget_weights([risky, safe])
        w = {p.risk.name: p.weight for p in pos}
        assert w["safe"] > w["risky"]
        assert sum(w.values()) == pytest.approx(1.0)

    def test_yield_tilted_positive_edge(self):
        rf = 0.04
        hi = make("hi", apy=0.12, p_hack=0.01)
        lo = make("lo", apy=0.045, p_hack=0.001)
        pos = yield_tilted_weights([hi, lo], risk_free=rf)
        assert sum(p.weight for p in pos) == pytest.approx(1.0, abs=1e-6)
        w = {p.risk.name: p.weight for p in pos}
        # инструмент с большим edge/risk наливается до max_weight
        assert w["hi"] >= 0.40 - 1e-9
        assert w["lo"] >= 0.40 - 1e-9
        # остаток уходит в cash
        assert w.get("cash@4.0%", 0) == pytest.approx(0.20, abs=1e-9)

    def test_yield_tilted_respects_max_weight(self):
        risks = [make(f"p{i}", apy=0.10 + i * 0.01, p_hack=0.01) for i in range(4)]
        pos = yield_tilted_weights(risks, max_weight=0.30)
        assert all(p.weight <= 0.30 + 1e-9 for p in pos)

    def test_kelly_no_overbet(self):
        risks = [make("a", apy=0.15, p_hack=0.01), make("b", apy=0.06, p_hack=0.002)]
        pos = kelly_allocation(risks)
        assert sum(p.weight for p in pos) == pytest.approx(1.0, abs=1e-6)
        # рисковые позиции не превышают 40%; остаток — cash-позиция (без риска)
        risky = [p for p in pos if not p.risk.name.startswith("cash")]
        assert all(p.weight <= 0.40 + 1e-9 for p in risky)
        cash = sum(p.weight for p in pos if p.risk.name.startswith("cash"))
        assert cash >= 0

    def test_kelly_zero_edge_goes_safe(self):
        risks = [make("neg", apy=0.01), make("safe", apy=0.05, p_hack=0.0005)]
        pos = kelly_allocation(risks, risk_free=0.04)
        w = {p.risk.name: p.weight for p in pos}
        assert w["safe"] > w.get("neg", 0.0)

    def test_summarize(self):
        pos = equal_weight([make("a"), make("b")])
        s = summarize(pos)
        assert s["n_positions"] == 2
        assert s["hhi_concentration"] == pytest.approx(0.5)
        assert s["max_weight"] == pytest.approx(0.5)


class TestFunding:
    def test_annualize(self):
        # 0.01% за 8ч * 1095 = 10.95% годовых
        assert annualize_funding(0.0001) == pytest.approx(0.1095)

    def test_funding_to_apy_constant(self):
        # постоянный funding 0.01%/8ч с fee 20% -> net 0.008%/8ч
        series = [0.0001] * 30
        apy = funding_to_apy(series, protocol_fee=0.20)
        expected = (1 + 0.00008) ** 1095 - 1
        assert apy == pytest.approx(expected, rel=1e-9)

    def test_funding_to_apy_empty(self):
        with pytest.raises(ValueError):
            funding_to_apy([])

    def test_expected_yield_positive_typical(self):
        pos = DeltaNeutralPosition("sUSDe-like", funding_annual_mean=0.08,
                                   funding_annual_vol=0.06)
        ey = pos.expected_yield()
        assert ey > 0
        assert ey < 0.08 * 0.8  # меньше нетто-funding из-за хвостов

    def test_stress_negative_funding(self):
        pos = DeltaNeutralPosition("x", funding_annual_mean=0.08, funding_annual_vol=0.06)
        stressed = pos.stress_scenario(months_negative=3, annual_negative_rate=-0.10)
        normal = pos.expected_yield()
        assert stressed < 0.08 * 0.8
        assert stressed > -0.05  # даже стресс не катастрофичен

    def test_simulation_reasonable(self):
        pos = DeltaNeutralPosition("x", funding_annual_mean=0.10, funding_annual_vol=0.08)
        res = pos.simulate_year(n_sims=20_000)
        assert res["p5"] < res["p50"] < res["p95"]
        assert 0.0 < res["prob_negative"] < 0.3

    def test_cash_and_carry(self):
        # funding 8%, basis 1%, fees 0.2% -> ~8.8%
        assert cash_and_carry(100_000, 0.01, 0.001, 0.001, 0.08) == pytest.approx(0.088)


class TestHypotheses:
    """Проверка гипотез из PLAN.md (границы уточняются данными из research/)."""

    def test_h2_il_exceeds_fees_when_volatile(self):
        """H2: IL концентрированной LP ±10% при воле 60%+ превышает типовой fee APR (~5-15%)."""
        from models.il_math import expected_il_from_vol
        eil = expected_il_from_vol(0.60, 1.0, 0.10)
        # при ширине ±10% ожидаемый IL > 10%, что выше реалистичного stable/volatile fee APR
        assert eil > 0.10

    def test_h4_tail_risk_reduces_ethena(self):
        """H4: E[yield] sUSDe < номинального sAPY из-за хвостов."""
        pos = DeltaNeutralPosition("sUSDe", funding_annual_mean=0.09, funding_annual_vol=0.07)
        nominal = 0.09 * (1 - 0.20)
        assert pos.expected_yield() < nominal

    def test_h5_diversification(self):
        """H5: 5+ инструментов -> P(потерь >50%) < 1% при p_hack 0.5-2%."""
        from models.risk_model import portfolio_loss_probability
        for p in (0.005, 0.01, 0.02):
            many = [PortfolioPosition(
                ProtocolRisk(name=f"p{i}", apy=0.06, p_hack=p, lgd_hack=0.9,
                             p_depeg=0.002, lgd_depeg=0.1, rate_volatility=0.02,
                             recovery_rate_hack=0.2), 1 / 6) for i in range(6)]
            assert portfolio_loss_probability(many, threshold=0.5) < 0.01
