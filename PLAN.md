# План глубокого исследования: пассивный заработок в крипте

> **Статус: ВЫПОЛНЕН 2026-10-16.** Все 7 воркстримов завершены, 75 тестов зелёные, итог в [REPORT.md](REPORT.md).

> Дата старта: 2026-10-15. Горизонт анализа: текущее состояние рынка (октябрь 2026), история инцидентов 2020–2026.
> Цель: каталог всех реалистичных вариантов пассивного дохода, количественная оценка рисков и доходностей, синтез стратегий с минимальным риском.

---

## Phase 0 — Инфраструктура

| # | Задача | Статус |
|---|--------|--------|
| 0.1 | Создать локальный git-репозиторий | ✅ |
| 0.2 | Создать GitHub-репозиторий `crypto-passive-yield-research` | ✅ |
| 0.3 | Пригласить коллаборатора `@boggda` | ✅ |
| 0.4 | Структура каталогов: `research/`, `models/`, `tests/`, `data/`, `report/` | ✅ |

## Phase 1 — Исследовательские воркстримы (параллельные подагенты)

### WS-1. Кредитование стейблкоинов (базовый слой наименьшего риска)
- Aave v3/v4 (и Horizon), Compound v3, Morpho (v1 + Blue), Euler v2, Kamino (Solana), Fluid (Instadapp), Spark/Sky (sUSDS Savings Rate), Curve Lend, FraxLend, Fluid,colo: JustLend (Tron)
- По каждому: текущий APY supply (нативный token vs USDC vs USDT), TVL, размер доступной ликвидности, история изменений ставок (волатильность APY), collateral quality, параметры risk premium
- История инцидентов: Bad DebtDAI 2023 (Morpho market), Curve oracle bug 2025 и т.п.
- Риски: смарт-контракт, оракул, governance, bad debt, изменение rate model, концентрация заёмщиков

### WS-2. Liquid Staking & Restaking
- LST ETH: Lido (wstETH), Rocket Pool (rETH), Coinbase (cbETH), Binance (wbETH), StakeWise, Frax (frxETH)
- LRT/restaking: EtherFi (weETH), Renzo (ezETH), Kelp (rsETH), Puffer (pufETH), EigenLayer (EIGEN стейкинг), Symbiotic, Karak — состояние на окт. 2026 (многие LRT деградировали после 2025 — проверить что живо)
- Solana: Jito (jitoSOL), Marinade (mSOL), Jupiter (jupSOL)
- Доходность базового стейкинга ETH (~3%?) + бонусы AVS/airdrops; комиссии протоколов
- Риски: slashing, depeg LST/LRT (кейсы ezETH Jul-2024, pufETH...), операционный риск валидаторов, liquidity discount при выходе

### WS-3. Дельта-нейтральные и синтетические доллары
- Ethena (sUSDe/sUSDS): механика (шорт перпы + лонг базового collateral), история funding rate по годам/кварталам, текущий sAPY, история "Exodus risk", инцидент 2025 (оступ BTC collateral / Bybit hack contagion), insurance fund
- Usual (USD0/USD0++), Reservoir (RUSD), уровень доходности и бэкинга
- Анализ: зависимость доходности от состояния рынка, сценарии отрицательного funding, haircut риск при redemption
- Самостоятельная дельта-нейтральная стратегия: cash-and-carry (спот + шорт перп) — спреды по биржам, требуемый капитал, ставки

### WS-4. Pendle и фиксированная доходность
- Механика PT/YT, current PT yields: PT-sUSDe, PT-USDe, PT-sUSDS, PT-wstETH, PT-eETH по ключевым датам экспирации (окт 2026 – июль 2027)
-PENDLE LP (зарплата в PENDLE incentives), а также Boros money-market
- Сравнение fixed yield vs плавающей ставки; implicit APY подразумеваемый рынком
- Риски: смарт-контракт (3 взлома Pendle-подобных кейсов 2024 — стандарт ERC-5095 exit liquidity), ликвидность выхода до экспирации, discount при досрочной продаже

### WS-5. LP в DEX / AMM
- Curve (stableswap) + Convex: CRV/CVX incentives vs pool APR, текущая доходность stables pools (tricrypto, usdt/usdc/dai)
- Uniswap v3/v4 позиционируемый LP + менеджеры (Gamma, Arrakis, Ichi)
- Aerodrome/Velodrome (Solidly-модель на Base/Optimism) — AERO emissions, real yield
- Подсчёт impermanent loss для разных диапазонов; fee APR vs IL; сравнение LP vs hold
- Метапулы, Concentrated liquidity. Beefy/Yearn autocompounders — их комиссии
- Риски: IL при волатильности, LVR (loss-vs-rebalancing), смарт-контракт, rug incentives

### WS-6. RWA / токенизированные облигации и нишевые протоколы
- Ondo (USDY), BlackRock BUIDL, Benji (BUIDL-подобный Franklin), Mountain (USDM), OpenEden (TBILL), Superstate, Centrifuge, Maple (syrupUSDC/syrupUSDT)
- Доходность привязана к ставке FED — текущая FED funds rate окт. 2026, кривая доходности
- Лимиты KYC/аккредитации, secondary liquidity, redemption gate
- Ниша: Goldfinch, Clearpool, TrueFi (кредитование реального бизнеса) — статус дефолтов
- Кратко: CEX earn (Binance/Bybit/Kraken simple earn) — rates, custodial risk, historical freezes

### WS-7. Состояние рынка и реестр рисков (октябрь 2026)
- Снимок: общий DeFi TVL, TVL по цепочкам (Ethereum/Solana/Base/Arbitrum), топ-10 протоколов
- Ключевые взломы/инциденты 2025–2026 с суммами и причинами (кривая Bybit → CEX, протокольные взломы)
- Регуляторика: MiCA (стейблкоины/EUR), SEC/CFTC stance на стейкинг/lending, налоговые аспекты (общее)
- Ставка FED, инфляция — влияние на RWA/stable yields
- Исторические yearly returns по классам: stETH, sUSDe, Aave USDC, Curve 3pool — за 2023/2024/2025 (фактические)

## Phase 2 — Количественные модели (python + pytest)

| Модель | Файл | Проверяется тестами |
|--------|------|---------------------|
| Компаундинг APR→APY, нетто после комиссий/газa | `models/yield_math.py` | `tests/test_yield_math.py` |
| Impermanent loss (v2-стиль и concentrated) | `models/il_math.py` | `tests/test_il_math.py` |
| Annualization funding rate, expected yield Ethena | `models/funding_model.py` | `tests/test_funding_model.py` |
| Risk-adjusted scoring: expected value с вероятностью взлома, drawdown | `models/risk_model.py` | `tests/test_risk_model.py` |
| Аллокация портфеля: risk-budgeting, max-diversification | `models/portfolio.py` | `tests/test_portfolio.py` |

Гипотезы для проверки тестами:
- H1: APY stablecoin lending на Aave в среднем > RWA yield на ~1-2% при большем хвостовом риске
- H2: IL концентрированной LP в ±10% диапазоне превышает fee income при 30-d волатильности >60% (годовых)
- H3: Pendle PT фиксирует доходность выше медианной плавающей на >100 б.п. на горизонте 6 мес
- H4: ожидаемая (вероятностно-взвешенная) доходность Ethena ниже её номинального sAPY из-за хвостового риска
- H5: диверсификация по 5+ протоколам снижает вероятность потери >50% капитала до <1% (при p_hack≈0.5-2%/год на протокол)

## Phase 3 — Синтез стратегий (минимальный риск, пассив)

- S1 «Ультраконсервативный»: только T-bills RWA + Aave USDC/USDT + sUSDS — целевая доходность, риск-бюджет
- S2 «Консервативный+»: S1 + wstETH + Pendle PT (фикс)
- S3 «Умеренный»: + sUSDe (доля ограничена), + Curve LP
- По каждой: веса, ожидаемая APY, VaR/CVaR (модель), сценарии stress (depeg -10%, взлом протокола -100% доли), ребалансировка, gas-издержки
- Сравнение с бенчмарком: US T-bill + 0%, и просто hold ETH/BTC

## Phase 4 — Верификация и отчёт

- Кросс-проверка всех ключевых чисел вторым независимым подагентом (источники: DefiLlama, официальные дашборды протоколов, CoinGecko)
- Прогон всех pytest-тестов, фикс результатов
- Итоговый отчёт `REPORT.md` (полный, на русском) + executive summary
- README, коммит, пуш, проверка что @boggda приглашён

---

## Критерии качества
1. Каждое число в отчёте имеет источник и дату.
2. Каждая стратегия имеет количественные риски (вероятность × ущерб), а не слова.
3. Все формулы покрыты тестами; тесты зелёные.
4. Отдельно помечены данные, которые не удалось проверить (уровень уверенности).
