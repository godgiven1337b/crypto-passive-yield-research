"""
alpha_eval.py — количественная оценка "альфа-кандидатов".

Альфа = превышение над базовой ставкой (baseline). Реальная ценность определяется:
  1. Спрэдом (spread_bp)
  2. Живучестью премии (durability_months) — премии умирают: инсентивы кончаются,
     арбитраж выравнивает ставки, программы сворачиваются
  3. Издержками входа/выхода (вход = gas + slippage + время; выход = то же)
  4. Хвостовым риском площадки (p_hack выше у новых протоколов!)
  5. Ёмкостью (capacity) — на большой капитал спрэд сдвигается

EV_за_горизонт = Σ по месяцам: spread(t) − baseline_tail_penalty, где spread(t)
затухает по кривой выживания (hazard rate премии).

Упрощённо (месячная решётка):
  excess(t) = spread_annual/12 * survival(t)
  survival(t) = (1-h)^t  (h = месячный hazard премии)
  EV = Σ_{t=1..T} excess(t) − costs_in_out − p_hack_annual*T/12 * LGD
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AlphaCandidate:
    name: str
    spread_bp: float            # годовой спрэд над baseline, б.п. (184 = 1.84%)
    baseline_apy: float         # базовая ставка альтернативы (доля, 0.038)
    durability_months: float    # ожидаемая живучесть премии (медианный сценарий)
    hazard_monthly: float       # вероятность смерти премии за месяц (0.15 = 15%)
    p_hack_annual: float        # вероятность взлома/инцидента площадки за год
    lgd_hack: float             # потеря при инциденте
    costs_in_out: float         # издержки входа+выхода (доля капитала)
    horizon_months: float = 12
    tail_reload_bonus: float = 0.0  # если премия умерла — капитал возвращается в baseline

    def survival(self, t: int) -> float:
        """Вероятность, что премия ещё жива в месяце t (счёт с 1)."""
        return (1.0 - self.hazard_monthly) ** t

    def expected_excess_apy(self) -> float:
        """Ожидаемый годовой спрэд с учётом затухания (в долях)."""
        spread = self.spread_bp / 10_000.0
        months = int(min(self.horizon_months, 12))
        if months == 0:
            return 0.0
        total = sum(self.survival(t) for t in range(1, months + 1))
        return spread * total / 12.0

    def expected_value(self) -> dict:
        """Полный EV стратегии за горизонт (доля капитала, свёрстанная к годовой)."""
        months = int(self.horizon_months)
        spread = self.spread_bp / 10_000.0
        # помесячный профиль: пока премия жива — spread, умерла — 0 (капитал в baseline)
        excess_sum = sum(spread / 12.0 * self.survival(t) for t in range(1, months + 1))
        baseline_sum = self.baseline_apy * months / 12.0
        hack_penalty = self.p_hack_annual * (months / 12.0) * self.lgd_hack
        costs = self.costs_in_out
        ev_alpha = excess_sum - costs - hack_penalty
        ev_total = ev_alpha + baseline_sum
        return {
            "ev_excess_annualized": ev_alpha * 12.0 / months,
            "ev_total_annualized": ev_total * 12.0 / months,
            "premium_expected_months": sum(self.survival(t) for t in range(1, months + 1)),
            "hack_penalty_annualized": hack_penalty * 12.0 / months,
            "costs_drag": costs * 12.0 / months,
        }

    def verdict(self) -> str:
        ev = self.expected_value()["ev_excess_annualized"]
        if ev > 0.03:
            return "СИЛЬНАЯ АЛЬФА (>300 б.п. ожидаемого спрэда)"
        if ev > 0.01:
            return "УМЕРЕННАЯ АЛЬФА (100-300 б.п.)"
        if ev > 0.002:
            return "СЛАБАЯ (<100 б.п., не стоит операции)"
        return "НЕТ АЛЬФИ (издержки/риски съедают спрэд)"


def compare(candidates: list[AlphaCandidate]) -> list[dict]:
    rows = []
    for c in candidates:
        ev = c.expected_value()
        rows.append({
            "name": c.name, "spread_bp": c.spread_bp,
            "ev_excess_bp": round(ev["ev_excess_annualized"] * 10_000),
            "ev_total_pct": round(ev["ev_total_annualized"] * 100, 2),
            "premium_months": round(ev["premium_expected_months"], 1),
            "verdict": c.verdict(),
        })
    rows.sort(key=lambda r: -r["ev_excess_bp"])
    return rows
