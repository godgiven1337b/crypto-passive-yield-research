"""Тесты модели оценки альфа-кандидатов (models/alpha_eval.py)."""
import pytest

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.alpha_eval import AlphaCandidate, compare


def mk(**kw):
    d = dict(name="t", spread_bp=184, baseline_apy=0.038, durability_months=6,
             hazard_monthly=0.10, p_hack_annual=0.01, lgd_hack=0.9,
             costs_in_out=0.002, horizon_months=12)
    d.update(kw)
    return AlphaCandidate(**d)


class TestSurvival:
    def test_certain_premium(self):
        c = mk(hazard_monthly=0.0)
        assert c.survival(6) == pytest.approx(1.0)

    def test_decay(self):
        c = mk(hazard_monthly=0.5)
        assert c.survival(1) == pytest.approx(0.5)
        assert c.survival(2) == pytest.approx(0.25)
        # монотонно убывает
        s = [c.survival(t) for t in range(1, 13)]
        assert all(a >= b for a, b in zip(s, s[1:]))


class TestEV:
    def test_no_costs_no_risk_full_premium(self):
        """Идеальный случай: спрэд живёт весь год без рисков -> EV = spread."""
        c = mk(hazard_monthly=0.0, p_hack_annual=0.0, costs_in_out=0.0)
        ev = c.expected_value()
        assert ev["ev_excess_annualized"] == pytest.approx(0.0184)  # 184 б.п.

    def test_costs_reduce(self):
        base = mk(hazard_monthly=0.0, p_hack_annual=0.0)
        costly = mk(hazard_monthly=0.0, p_hack_annual=0.0, costs_in_out=0.01)
        assert costly.expected_value()["ev_excess_annualized"] < \
               base.expected_value()["ev_excess_annualized"]

    def test_hack_penalty_reduces(self):
        safe = mk(p_hack_annual=0.0)
        risky = mk(p_hack_annual=0.10)
        assert risky.expected_value()["ev_excess_annualized"] < \
               safe.expected_value()["ev_excess_annualized"]
        # 10% хак * LGD 0.9 * год = 0.09 штраф
        diff = (safe.expected_value()["ev_excess_annualized"] -
                risky.expected_value()["ev_excess_annualized"])
        assert diff == pytest.approx(0.09, abs=0.005)

    def test_high_hazard_kills_premium(self):
        """Премия с 50%/мес hazard живёт в среднем ~1 месяц."""
        c = mk(hazard_monthly=0.5)
        assert c.expected_value()["premium_expected_months"] == pytest.approx(
            sum(0.5 ** t for t in range(1, 13)), abs=1e-9)
        # EV much lower than full spread
        assert c.expected_value()["ev_excess_annualized"] < 0.0184 / 3

    def test_high_spread_new_protocol_trap(self):
        """Классическая ловушка: 800 б.п. на новом протоколе с p_hack 8%."""
        trap = mk(name="trap", spread_bp=800, p_hack_annual=0.08, hazard_monthly=0.25)
        solid = mk(name="solid", spread_bp=150, p_hack_annual=0.005, hazard_monthly=0.05)
        rows = compare([trap, solid])
        by = {r["name"]: r for r in rows}
        # качественный спрэд бьёт жирный рискованный
        assert by["solid"]["ev_excess_bp"] > by["trap"]["ev_excess_bp"]

    def test_verdict_thresholds(self):
        strong = mk(spread_bp=600, hazard_monthly=0.02, p_hack_annual=0.002,
                    costs_in_out=0.001)
        assert "СИЛЬНАЯ" in strong.verdict()
        dead = mk(spread_bp=50, hazard_monthly=0.5, p_hack_annual=0.05,
                  costs_in_out=0.01)
        assert dead.verdict() in ("НЕТ АЛЬФИ", "СЛАБАЯ (<100 б.п., не стоит операции)")

    def test_total_includes_baseline(self):
        c = mk(hazard_monthly=0.0, p_hack_annual=0.0, costs_in_out=0.0)
        ev = c.expected_value()
        assert ev["ev_total_annualized"] == pytest.approx(0.038 + 0.0184)

    def test_compare_sorts(self):
        rows = compare([mk(name="a", spread_bp=100), mk(name="b", spread_bp=300)])
        assert rows[0]["name"] == "b"
