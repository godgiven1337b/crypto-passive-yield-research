# Crypto Passive Yield Research — октябрь 2026

Глубокое исследование возможностей пассивного заработка в крипте: каталог протоколов,
количественная оценка рисков и доходностей, синтез стратегий с минимальным риском.

**Дата данных:** 15–16 октября 2026 · **Итоговый отчёт:** [`REPORT.md`](REPORT.md)

## Структура репозитория

```
PLAN.md                    — план исследования (7 воркстримов, гипотезы H1–H5)
REPORT.md                  — ИТОГОВЫЙ ОТЧЁТ: консервативная база (начинать отсюда)
ALPHA.md                   — охота за спрэдами: stUSDS, Solana, carry, reUSD
APY-MAX.md                 — МАКСИМИЗАЦИЯ APY: лупы, наградные стеки, малые протоколы, поинты
OPTIONS.md                 — 📋 СВОДНАЯ ТАБЛИЦА ВСЕХ ВАРИАНТОВ (APY/капитал/риски)
QUANT-EDGES.md             — МИКРОСТРУКТУРА: Pendle mispricing, undersupplied-пулы, фандинг
models/live_monitor.py     — живой монитор дислокаций (фандинг/пеги/vol-TVL/PT)
research/                  — детальные отчёты по воркстримам
  01-stablecoin-lending.md — money markets (Aave, Morpho, Sky, ...)
  02-lsd-restaking.md      — liquid staking / restaking ETH+SOL
  03-delta-neutral.md      — Ethena, funding, cash-and-carry
  04-pendle-fixed-yield.md — фиксированная доходность через PT
  05-dex-lp.md             — LP в AMM: IL/LVR, стейбл-пулы
  06-rwa-niche.md          — токенизированные T-bills, Maple, CEX
  07-market-state-risks.md — снимок рынка, реестр взломов, p_hack
  08-11 (alpha)            — stUSDS, Solana, Pendle high-yield, carry
  12-15 (apy-max)          — программы наград, поинты/аирдропы, малые протоколы, лупинг
  16-19 (quant)            — DEX-микроструктура, Pendle-бэктест, ликвидации, депеги
data/*.json                — машиночитаемые данные (проверены cross-check)
models/                    — количественные модели (Python, numpy)
  yield_math.py            — APR↔APY, комиссии, газ
  il_math.py               — impermanent loss (v2 + concentrated)
  risk_model.py            — E[yield] с вероятностью взлома, VaR/CVaR
  funding_model.py         — дельта-нейтральные стратегии, стресс-тесты
  portfolio.py             — аллокации: risk-budget, fractional Kelly
  strategies.py            — синтез стратегий S1–S4 (генерирует report/)
tests/                     — pytest: 108 тестов (формулы + регрессии)
report/                    — авто-вывод моделей + итоговые артефакты
```

## Быстрый старт

```bash
pip install pytest numpy
python3 -m pytest tests/ -q          # 108 тестов
python3 models/strategies.py         # пересчёт стратегий из data/*.json
python3 models/alpha_scanner.py      # сканер аномалий доходности (DefiLlama)
```

## Ключевые выводы по уровням риска

| Уровень | Документ | Доходность | Суть |
|---|---|---|---|
| Консервативный | REPORT.md | E[APY] ~3.4% | T-bill RWA + blue-chip lending + PT-фикс |
| Альфа-оверлей | ALPHA.md | ~4.3–4.5% | stUSDS + Solana + carry + reUSD |
| Максимум | APY-MAX.md | **9.7% гросс / 8.5% E[APY]** | Лупы на дешёвом долге + наградные стеки + поинты-опционы |
| Квант | QUANT-EDGES.md | **~10–14%** | PT-mispricing (hit 92%), undersupplied LP, фандинг-дислокации |

## Ключевые выводы (TL;DR)

1. **Октябрь 2026 — режим «денежного рынка»**: Fed funds 3.75–4.00% (hike в сент!),
   T-bill 3M 4.1–4.3%. Весь крипто-yield сжался к этой базе: lending 3–6%, RWA 3.4–3.8%,
   blue-chip фикс (Pendle PT) ~5%.
2. **Эра 20%+ «безрисковых» ставок закончилась** (Ethena-цикл 2024). Двузначный yield
   теперь = кредитный риск новичков.
3. Минимальный риск = лестница: T-bill RWA + blue-chip lending + LST + PT-фикс.
   Модельная оценка: ~4–4.5% E[APY] при P(потери >25% капитала) < 0.1%/год.
4. Взломы никуда не делись: Bybit $1.5B (фев 2025), KelpDAO/LayerZero $290M (апр 2026,
   создал $190M bad debt на Aave). Диверсификация обязательна.

## Методология

- Все ставки/TVL проверены минимум по 2 источникам (DefiLlama API + дашборды протоколов)
- Независимый cross-check: `curl api.llama.fi`, FRED CSV (см. отчёт)
- Каждая формула покрыта тестами; риски = вероятность × ущерб (не качественно, а количественно)
- Уровни уверенности помечены: подтверждено / ⚠️ один источник
