"""Тесты модели рисков (models/risk_model.py)."""
import pytest

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.risk_model import (
    ProtocolRisk, expected_yield, risk_penalty, risk_adjusted_score,
    PortfolioPosition, portfolio_expected_yield, portfolio_loss_probability,
    var_cvar, breakeven_risk_tolerance,
)


def make(**kw):
    d = dict(name="test", apy=0.05, p_hack=0.005, lgd_hack=0.9,
             p_depeg=0.002, lgd_depeg=0.1, rate_volatility=0.02,
             recovery_rate_hack=0.3)
    d.update(kw)
    return ProtocolRisk(**d)


class TestExpectedYield:
    def test_no_risk_equals_apy(self):
        pr = make(p_hack=0, p_depeg=0)
        assert expected_yield(pr) == pytest.approx(0.05)

    def test_hack_reduces(self):
        pr = make(p_hack=0.01)
        # penalty = 0.01*0.9*0.7 (hack) + 0.002*0.1 (depeg) = 0.0065
        assert expected_yield(pr) == pytest.approx(0.05 - 0.0065)

    def test_depeg_reduces(self):
        pr = make(p_depeg=0.01, lgd_depeg=0.2)
        assert expected_yield(pr) == pytest.approx(0.05 - 0.002 - 0.005 * 0.9 * 0.7)

    def test_full_recovery_like_euler(self):
        # Euler 2022 вернул всё: recovery=1 -> взлом не снижает E[yield]
        pr = make(p_hack=0.02, recovery_rate_hack=1.0)
        assert expected_yield(pr) == pytest.approx(0.05 - 0.002 * 0.1, abs=1e-9)

    def test_risk_penalty_positive(self):
        assert risk_penalty(make()) > 0

    def test_score_prefers_safe(self):
        safe = make(name="safe", p_hack=0.0005)
        risky = make(name="risky", p_hack=0.03)
        assert risk_adjusted_score(safe) > risk_adjusted_score(risky)


class TestPortfolio:
    def test_weights_validation(self):
        pos = [PortfolioPosition(make(), 0.6), PortfolioPosition(make(), 0.6)]
        with pytest.raises(ValueError):
            portfolio_expected_yield(pos)

    def test_portfolio_yield(self):
        a = PortfolioPosition(make(apy=0.05), 0.5)
        b = PortfolioPosition(make(apy=0.07), 0.5)
        # каждый несёт пенальти: hack 0.005*0.9*0.7=0.00315 + depeg 0.0002
        assert portfolio_expected_yield([a, b]) == pytest.approx(0.06 - 0.00335)

    def test_diversification_reduces_catastrophe_prob(self):
        """H5: диверсификация по 5+ протоколам снижает P(потеря >50%) до <1%."""
        one = [PortfolioPosition(make(p_hack=0.01, lgd_hack=0.95, recovery_rate_hack=0.0), 1.0)]
        many = [PortfolioPosition(make(p_hack=0.01, lgd_hack=0.95, recovery_rate_hack=0.0), 0.2)
                for _ in range(5)]
        p_one = portfolio_loss_probability(one, threshold=0.5)
        p_many = portfolio_loss_probability(many, threshold=0.5)
        assert p_many < p_one
        # один инструмент: потеря >50% капитала = вероятность взлома
        assert p_one == pytest.approx(0.01, abs=0.005)
        # пять инструментов по 20%: потеря >50% требует 3+ одновременных взломов
        assert p_many < 0.0001

    def test_var_cvar_ordering(self):
        pos = [PortfolioPosition(make(p_hack=0.02), 1.0)]
        var95, cvar95 = var_cvar(pos, alpha=0.95, n_sims=50_000)
        assert cvar95 >= var95 >= 0

    def test_var_increases_with_risk(self):
        safe = [PortfolioPosition(make(p_hack=0.001), 1.0)]
        risky = [PortfolioPosition(make(p_hack=0.05), 1.0)]
        assert var_cvar(risky, n_sims=50_000)[0] >= var_cvar(safe, n_sims=50_000)[0]

    def test_var_nonzero_when_catastrophe_likely(self):
        """Регрессия: p_hack=50% -> VaR95 должен быть ~0.59 (loss 0.63 - yield).

        Ловит баг, когда потери не накапливались в losses и VaR всегда был 0.
        """
        pr = make(p_hack=0.5, apy=0.04, rate_volatility=0.0, p_depeg=0.0,
                  recovery_rate_hack=0.3)
        pos = [PortfolioPosition(pr, 1.0)]
        var95, cvar95 = var_cvar(pos, alpha=0.95, n_sims=50_000)
        assert var95 == pytest.approx(0.59, abs=0.01)
        assert cvar95 == pytest.approx(0.59, abs=0.01)

    def test_var99_captures_tail(self):
        """При совокупной p_hack ~3% хвост должен попадать в VaR99."""
        pos = [PortfolioPosition(make(p_hack=0.008, apy=0.04, p_depeg=0.0), 0.25)
               for _ in range(4)]
        var99, cvar99 = var_cvar(pos, alpha=0.99, n_sims=200_000)
        # один взлом: 0.25*0.9*0.7 = 15.75% потерь минус ~4% дохода
        assert 0.05 < var99 < 0.20
        assert cvar99 >= var99

    def test_diversified_lower_var(self):
        """Диверсификация снижает МАСШТАБ хвостовой потери.

        Сравниваем на alpha=0.99: у одиночной позиции взлом (p=2%) попадает
        в 1%-хвост с потерей ~57%; у разбитой на 4 части 1%-хвост — потеря
        одного сегмента ~9%. На alpha=0.95 сравнение некорректно: у одиночной
        позиции 2% < 5% и VaR95=0 (хвост не пересекает порог).
        """
        single = [PortfolioPosition(make(p_hack=0.02, apy=0.06), 1.0)]
        spread = [PortfolioPosition(make(p_hack=0.02, apy=0.06), 0.25) for _ in range(4)]
        var_single = var_cvar(single, alpha=0.99, n_sims=60_000)[0]
        var_spread = var_cvar(spread, alpha=0.99, n_sims=60_000)[0]
        assert var_single == pytest.approx(0.57, abs=0.05)
        assert var_spread == pytest.approx(0.095, abs=0.05)


class TestBreakeven:
    def test_better_than_riskfree(self):
        # APY 6% vs RF 4%: edge = 0.02 - 0.0002 (depeg) = 0.0198; tolerance = 0.0198/(0.9*0.7)
        pr = make(apy=0.06)
        assert breakeven_risk_tolerance(pr, risk_free=0.04) == pytest.approx(0.0198 / 0.63)

    def test_worse_than_riskfree(self):
        pr = make(apy=0.03)
        assert breakeven_risk_tolerance(pr, risk_free=0.04) == 0.0
