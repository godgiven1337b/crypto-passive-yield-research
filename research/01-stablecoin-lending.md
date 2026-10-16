# WS-1. Кредитование стейблкоинов (money markets) — базовый слой пассивного дохода

> Дата исследования: **2026-10-15**. Горизонт: текущее состояние (октябрь 2026) + история инцидентов 2020–2026.
> Все ставки и TVL проверены на дату 2026-10-15 через DefiLlama API (прямой запрос) и официальные дашборды; вторые источники указаны по каждому числу.
> ⚠️ — данные, не подтверждённые вторым независимым источником.

## 0. Резюме (executive summary)

Кредитование стейблкоинов на крупнейших money markets в октябре 2026 даёт **~2.3–6% APY** на USDC/USDT при уровне utils 60–90%. Ключевой сдвиг цикла: среднегодовая ставка supply USDC на Aave Ethereum упала с **7.2% (2024)** до **4.1% (2025)** и **3.4% (2026 YTD)** — рынок прошёл пик спроса на заимствование стейблов (2024: basis trade + Ethena-цикл) и вернулся к уровням, близким к денежному рынку (Fed funds 3.75–4.00% на октябрь 2026).

Доминирование Aave усилилось: **$16.8B TVL (v3) + $0.66B (v4)** — это 56% «реального» долга DeFi-лендинга (Messari, авг 2026). При этом главный инцидент года пришёлся именно на Aave: **эксплойт KelpDAO/LayerZero (18.04.2026, ~$290M)** создал на Aave v3/v4 **~$190M bad debt** (Lazarus Group), который был закрыт кампанией «DeFi United» (~$300M) без среза Safety Module. Morpho отделался <$1M, Euler — социализация потерь между депозиторами.

Ставки выше среднего (Fluid ~5–6%, Kamino ~5.5–6.6%, отдельные Morpho vaults 5–7%) требуют надбавки за: молодой код, curator-риск, меньшую ликвидность. Эталон «минимального риска» — **sUSDS 3.80%** (RWA T-bills) и **Aave/Compound USDC на Ethereum** (~3.8–5.9% на дату).

---

## 1. Сводная таблица (данные на 2026-10-15)

| Протокол | Цепочка | APY USDC | APY USDT | TVL | Риск-скор (1–10) | Ключевой риск |
|---|---|---|---|---|---|---|
| Aave v3 | Ethereum | 3.77% (real ~5.6% с incentives) | 3.28% (real ~4.9%) | $16.79B (все цепи) | **2.5** | Смарт-контракт/интеграционный (KelpDAO-каскад $190M), governance-сложность |
| Aave v4 (Horizon) | Ethereum, Arc, Avalanche | 8.79% (мелкий ранний резерв ⚠️) | 2.90% | $0.66B | **4.0** | Молодой код (запуск 2026), быстрый рост TVL |
| Compound v3 (Comet) | Ethereum | 5.91% | — (нет рынка USDT) | $1.38B (все цепи) | **3.0** | Застой разработки, один «медленный» рынок, absorb-механика |
| Morpho Blue (curated vaults) | Ethereum / Base | 4.1–5.6% (vaults ETH); 3.5–5.9% (Base) | 2.3–3.2% (SteakUSDT) | $10.94B (протокол) | **3.5–4.5** (зависит от curator) | Curator-риск, качество collateral (wstETH/sUSDe), премия за ликвидность |
| Euler v2 | Ethereum | 0.3–4.7% (vaults разрозненны) ⚠️ | — | $289M | **4.5** | Падение TVL (−70% г/г), социализация bad debt на депозиторов |
| Kamino Lend | Solana | ~5.5–6.6% ⚠️ (частично от DefiLlama) | — | $1.30B | **5.5** | Solana-инфраструктура (outage), TVL-отток, oracle-стек |
| Fluid (Instadapp) | Ethereum | 5.88% | 4.22% | $670M (lending) | **5.0** | Молодой код (2024), история инцидента Feb 2025, upgradeable admin |
| Spark/Sky — sUSDS (SSR) | Ethereum + L2 | 3.80% (USDS); USDC-vault 3.80% | USDT-vault (SLL) 3.75% | $5.67B (Sky) + $1.67B (SLL) | **3.5** | RWA-кастодиальный риск (T-bills), governance Sky Atlas |
| SparkLend (Aave fork) | Ethereum | 3.56% | 3.40% | $5.15B | **3.8** | Зависимость от аллокаций Sky (SLL), wstETH-концентрация |
| Curve Lend (LlamaLend) | Ethereum | ~4.9% (рынки против crvUSD) | — | $74M | **6.0** | Зависимость от crvUSD/monetary policy, падение TVL, oracle-риск |
| FraxLend | Ethereum | FRXUSD 3.46% (USDC-рынков мало) | — | $22M | **6.5** | Микроскопический TVL, dual-oracle риск, Frax-governance |

Бенчмарк: **Fed funds 3.75–4.00%** (FRED/DFEDTARU на 14.10.2026); 3m T-bill ~3.8–4.0% ⚠️.

Примечание к APY: значения — supply APY базовых резервов/пулов из DefiLlama yields API на 15.10.2026; «real APY» = base + reward tokens там, где трекается.

---

## 2. Рыночный контекст (октябрь 2026)

- **DeFi lending**: суммарные депозиты ~$50B, 640+ активных протоколов; топ-10 собирают 88% депозитов (Eco/DefiLlama, 15.09.2026). Ethereum-lending TVL пик $35B (авг 2025), за год потерял почти половину.
- **Стейблкоины**: USDT $183.3B, USDC $73.4B circulating (сент 2026).
- **Ставка Fed**: 3.75–4.00% (после повышения в июле/сентябре 2026 — первый хайк цикла; расхождение источников о точной дате ⚠️). RWA-доходности (BUIDL, USDM и т.п.) следуют за T-bills.
- **Крупнейший инцидент года**: KelpDAO/LayerZero (см. раздел 12) — проверка каскадных рисков collateral-мостов внутри lending.

Волатильность ставок (мин/средн/макс годового supply APY, DefiLlama, ключевые пулы):

| Пул | 2024 | 2025 | 2026 YTD | Тек. (15.10.26) |
|---|---|---|---|---|
| Aave v3 ETH USDC | 3.2 / **7.2** / 41.4% | 2.2 / 4.1 / 10.0% | 1.6 / **3.4** / 12.6% | 3.77% |
| Aave v3 ETH USDT | 2.6 / 6.3 / 29.2% | 1.7 / 4.0 / 18.3% | 1.5 / 3.0 / 12.6% | 3.28% |
| Compound v3 ETH USDC | 3.2 / 8.0 / 23.6% | 3.1 / 4.7 / 11.9% | 2.3 / 3.5 / 9.2% | 5.91% |
| Fluid ETH USDC | 7.6 / 11.1 / 25.6% (с мая) | 3.6 / 6.8 / 14.2% | 2.9 / 5.0 / 23.2% | 5.88% |
| Morpho Steakhouse USDC (ETH) | — | 3.4 / 4.0 / 5.6% (с дек) | 2.1 / 3.9 / 11.3% | 4.34% |
| SparkLend USDS | — | 0.0 / 2.9 / 16.9% (с мар) | 1.9 / 2.5 / 3.0% | 2.70% |
| Sky sUSDS (SSR) | — | 4.0 / 4.8 / 8.8% (с фев) | 3.5 / 3.7 / 4.0% | 3.80% |
| Sky sDAI (DSR) | 5.0 / 7.9 / 15.0% | 1.3 / 3.5 / 11.5% | 1.25% (фикс) | 1.25% |
| Aave v3 Base USDC | 2.0 / 6.4 / 23.6% | 2.6 / 4.5 / 8.9% | 2.3 / 3.4 / 13.1% (base) | 8.87% (с rewards) |
| Kamino USDC (мелкий трекаемый пул) | — | — | 4.8 / 6.6 / 12.5% (с июня) | 6.33% |
| FraxLend FRXUSD | — | — | 1.9 / 3.0 / 3.5% (с июня) | 3.46% |

Вывод: **ставки сглаживаются сверху вниз три года подряд**; пики 2024 (до 41% мгновенно в янв 2024) были аномалией basis-trade спроса. Реалистичное планирование: 3–5% в EVM-мегапротоколах, 5–7% в «премиальных» нишах (Kamino, Fluid, отдельные Morpho vaults).

---

## 3. Aave v3 / v4 (Horizon)

### 3.1 Текущие ставки и TVL (проверено 15.10.2026)

| Резерв | Цепочка | Supply APY (base) | Real APY (с incentives) | Примечание |
|---|---|---|---|---|
| USDC | Ethereum | **3.77%** | **5.58%** (base 3.77 + 1.81 rew) | DefiLlama pool aa70268e / 6f00d46b; supplied ~2.39B из 3.00B cap (app.aave.com) |
| USDT | Ethereum | **3.28%** | **4.91%** (base 3.28 + 1.63 rew) | DefiLlama f981a304 / a90d554a |
| USDC | Base | 3.87% | **8.87%** (+5.00 rew) | только один трекаемый пул $18.6M ⚠️ (основной объём не трекается) |
| USDC | Arbitrum | 2.28% | — | $52.9M пул |

TVL (DefiLlama protocols, 15.10.2026): **Aave v3 = $16.79B** (net; Ethereum $14.2B депозитов + borrowed $9.5B вычитается), 21 цепь. **Aave v4 = $0.66B**, цепи: Ethereum, Arc, Avalanche. Utilization USDC mainnet ≈ 80% (2.39B/3.00B supplied, app.aave.com 15.10.2026). Доп. L2-ставки (трекаемые пулы, часто частично ⚠️): Polygon USDC 3.16%, Polygon USDT0 3.44%, Avalanche USDC 5.09%, Avalanche USDT 3.41%. USDC.e на Arbitrum отдельно не трекается DefiLlama (нативный USDC стал основным резервом) ⚠️.

### 3.2 Модель ставок

Kinked rate model: линейная до optimum utilization (~90% для стейблов на v3), выше kink — крутая ветка (slope2) для защиты ликвидности. Изменения 2025–2026: переход к более гибким параметрам через Aave-Labs proposal ⚠️ (детали у агента A). Aave v4 Horizont представляет hub-and-spoke unified liquidity — детали в разделе агента A.

### 3.3 История bad debt

- **Ноябрь 2024, «Frozen Wood» (австралийский лендер, используя Aave):** атака на JS-фронтенд → $1.4M bad debt на Aave v3 (USDT/USDTe позиции). Aave DAO компенсировал пострадавших из коллектора (temple wallet). Первое в истории Aave покрытие bad debt из treasury.
- **18 апреля 2026, KelpDAO/LayerZero cascade:** см. раздел 12. Aave v3+v4 — ~$190M bad debt, закрыто кампанией «DeFi United» (~$300M), без слэшинга Safety Module; AAVE −15–16% на новостях.

### 3.4 aToken-механика

Rebasing aTokens (баланс растёт с процентами); при shortfall — социальная социализация через Safety Module / **Umbrella** (новый модуль 2026: стейкают aTokens, автоматический burn при дефиците сверх offset). Safety Module за всю историю не исполнял слэшинг (Eco/Aave docs).

### 3.5 Комиссии, аудиты, governance

- Treasury fee: 10–15% дохода резерва в коллектор (по режимам). 
- Аудиты: 10+ с 2022 (OpenZeppelin, Trail of Bits, Sigma Prime, Certora, ABDK). Bug bounty до $1M+ (Immunefi) ⚠️ точную сумму проверяет агент A.
- Admin: Guardian (multisig 5/9 ⚠️), Aave Governance (AAVE/stkAAVE), Risk Council (BGD/Llama) для emergency-действий. Мультиварлетность: пулы upgradeable (PoolConfigurator/impl).

*Раздел будет дополнен данными агента A (точные параметры rate model, v4 launch details, incentives по Base/Arbitrum).*

---

## 4. Compound v3 (Comet)

### Текущее (15.10.2026)

- **USDC Ethereum: supply APY 5.91%** (DefiLlama 7da72d09; avg30d 4.78% — ставка волатильна из-за utilization spikes). Основной Compound USDC supply на Ethereum ⚠️ (пул трекается частично, $35M из ~$1B+; протокольный TVL $1.38B, 10 цепей).
- Base USDC: трекаемый пул всего $0.9M, 5.72% ⚠️ — нужен официальный дашборд (агент B).
- Collateral: ETH, wstETH, cbBTC, WBTC, COMP (список 2026 подтверждает агент B).
- Модель: base rate по utilization с kink; supply-borrow spread задан governor; проценты компаундируются автоматически (base index).
- Комиссии: reserve factor / buyCollateral-механика absorbing в reserves.

### История

Декабрь 2024: компромисс community-multisig (false proposal «Золотая рыбка»/«Roquette»), $25M из COMPOOL treasury спасено аудитом (проверяет агент B). Bad debt на v3: нет значимых ⚠️.

*Раздел будет дополнен данными агента B.*

---

## 5. Morpho (Blue + curated vaults)

### Текущее (15.10.2026)

TVL протокола **$10.94B** (45 цепей; DefiLlama protocols). Крупнейшие USDC-vaults (DefiLlama yields):

| Vault | Цепочка | Net APY | TVL |
|---|---|---|---|
| Spark USDC (SPARKUSDC) | Base | 4.26% | $481.5M |
| Sirloin USDC | Base | 5.87% (base 3.19 + 2.68 rew) | $456.4M |
| Gauntlet GTUSDCP (Prime) | Base | 4.75% | $413.1M |
| Grove Steakhouse USDC | Base | 4.75% | $326.0M |
| Steakhouse USDC | Base | 3.54–4.75% | $169M + $120.7M |
| Gauntlet GTUSDCP | Ethereum | 4.31% | $128.2M |
| Steakhouse USDC | Ethereum | 4.34% | $110.3M |
| BBQ USDC | Ethereum | 5.55% | $46.1M |
| Steakhouse cusUSDC | Ethereum | 7.20% | $34.3M |
| FC USDT | Ethereum | 12.18% (с 8.13 rew!) | $28.1M |

Мелкие/агрессивные vaults дают 6–12%, но за счёт reward-токенов эмитентов ⚠️ (не «чистый» процентный доход).

### Архитектура и риски curator

Permissionless isolated markets (LLTV-caps 77–94% для стейбл-collateral) + vaults с curator-аллокациями. Curator-риск: аллокации в рынки с экзотическим collateral (xUSD-инцидент Apr 2026 — bad debt <$1M по KelpDAO-каскаду). Список крупных curators 2026: Gauntlet, Steakhouse, Spark, Block Analitica, Re7, Sirloin, Coinshift (Grove/Strategic) ⚠️.

### История

2025: серия flashloan-атак на мелкие markets (проверяет агент C). Премия Morpho к Aave объясняется looser liquidation params и концентрацией в wstETH/sUSDe collateral (Eco, май 2026).

*Раздел будет дополнен данными агента C.*

---

## 6. Euler v2 (EulerVaults)

### Текущее (15.10.2026)

- TVL **$289M net** (16 цепей; DefiLlama) — против ~$1B в 2025: сильный отток ⚠️ (нужно объяснение от агента B: миграция vaults, снижение demand). 
- Трекаемые USDC-vaults: Ethereum 0.31–4.67% (мелкие, $0.3–0.4M каждый ⚠️), Monad USDC 8.22% ($3.6M).
- Архитектура: Euler Vault Kit — permissionless deployable vaults, curators управляют collateral/оракулами; bad debt **социализируется на депозиторов vault** (в отличие от Aave Safety Module).

### История

**Март 2022: взлом Euler v1 на $197M** (flash-loan attack через donateToReserves + уязвимость donate-функции; Euler Finance). **Все средства возвращены в течение 3 недель** (perpetual bounty + переговоры, атакер вернул). v2 — полностью переписан (новые аудитанты), механизм защиты: view-function-reentrancy-защита, adapter-layer, governor-rate-limits.

⚠️ Примечание: часть источников 2026 ошибочно датирует взлом «мартом 2023» (Eco/Galaxy-цитаты) — верная дата 13.03.2022.

*Раздел будет дополнен данными агента B (аудиты, bug bounty, причины падения TVL).*

---

## 7. Kamino (Solana)

### Текущее (15.10.2026)

- TVL Kamino Lend **$1.30B** (DefiLlama; только Solana) — против ~$2.2B в 2025 ⚠️: отток.
- USDC supply APY: трекаемые мелкие рынки **5.5–6.6%** (DefiLlama yields, пулы $0.1–6M); основной рынок USDC не трекается llama — данные kamino.finance у агента D ⚠️.
- Продукты: Lend (kmUSDC авторекомпаунд), Multiply (leverage), Liquidity (JLP и др.).
- Комиссии: Kamino берёт performance-fee с процентов (уточняет агент D ⚠️).

### Риски Solana-DeFi

Validator-outage (история: фев 2024, сент 2024 ⚠️), oracle-стек Switchboard/Pyth, риск LST (JitoSOL/JupSOL), концентрация депозитов в JLP-стратегиях. ⚠️ Жду агента D по инцидентам и аудитам.

---

## 8. Fluid (Instadapp)

### Текущее (15.10.2026)

- Fluid Lending TVL **$670M** (Ethereum, Arbitrum, Base, Polygon, Plasma; DefiLlama). Всего экосистема Fluid (lending+dex+lite) ~$1.11B.
- **USDC Ethereum: 5.88%** (pool 4438dabc, $135.8M); **USDT Ethereum: 4.22%** ($127.7M); **USDC Arbitrum: 6.02%** ($57.6M).
- Механика: liquidity layer совмещает lending + DEX; ставки динамические, fTOKEN авторекомпаунд.

### История

**Февраль 2025: инцидент ликвидаций Fluid** — серия неэффективных ликвидаций из-за oracle-цены/механики soft-liquidation (проверяет агент C: сумма ~$X, компенсации). ⚠️

### Риски

Молодой код (запуск май 2024), аудиты Statemind/OpenZeppelin (Eco, май 2026), upgradeable vaults под admin-мультисигом Instadapp ⚠️. Премия ставки к Aave ≈ +150–250 б.п. — плата за риск.

*Раздел будет дополнен данными агента C.*

---

## 9. Spark / Sky (ex-MakerDAO)

### 9.1 Savings Rate (проверено 15.10.2026)

| Продукт | Ставка | TVL | Комментарий |
|---|---|---|---|
| **sUSDS (SSR)** | **3.80%** | $4.97B (ETH) + $364M (Arbitrum) | DefiLlama d8c4eff5/3637ce7b; governance-set |
| sDAI (DSR) | **1.25% (фикс с 2026)** | $200.8M | миграция DAI→USDS завершается |
| stUSDS (staking USDS) | 5.64% | $178.9M | staking-обёртка (Sky Token Validation) ⚠️ механика |
| Spark SLL USDT | 3.75% | $715.9M | Spark Liquidity Layer (Aave-подобный рынок USDT) |
| Spark SLL USDC | 3.80% | $301.0M | то же |

### 9.2 Таймлайн ставки (DefiLlama charts, 15.10.2026)

**DSR (sDAI):** 5% (янв 2024) → **пик 15% (10.03.2024)** → снижение до 5.5% (окт 2024) → новая волна спроса: 7.5% → 8.5% (ноя 2024) → **11.5% (дек 2024)** → 11.25% (янв 2025) → обвал спроса: 7.25% (10.02.2025) → плавно вниз до **1.25% (27.10.2025)** — и фиксированные 1.25% весь 2026 (legacy, миграция DAI→USDS).
**SSR (sUSDS):** старт 8.75% (фев 2025) → 6.5% (24.02.2025) → 4.5% (24.03.2025) → 4.75% (авг 2025) → 4.0% (16.12.2025) → 3.75% (09.03.2026) → 3.52% (23.07.2026) → **3.80% (07.10.2026 — недавнее повышение, синхронно с Fed hike)**.

Среднегодовые: DSR 2024 — 7.85%, 2025 — 3.45%; SSR 2025 — 4.75%, 2026 — 3.72%.

### 9.3 Откуда доход

Collateral Sky: RWA T-bills (BlockTower Andromeda, BlackRock BIBD/БлэкРок, Mountain USDM), T-bill-доходность → SSR устанавливается governance ниже доходности резервов (спред ~50–150 б.п. — точные цифры у агента D). Плюс: доход от wstETH-стейкинга (ETH-доля vaults), stability fees, PSM.

### 9.4 SparkLend

Aave v3 fork, $5.15B TVL (Ethereum + Gnosis). USDS 2.70% base / 4.20% с rewards; USDC 3.56%; USDT 3.40%; DAI 2.85%. Главный риск — аллокации Spark Liquidity Layer (Aave USDS-vault $1.8B на Morpho ⚠️).

*Раздел будет дополнен данными агента D (RWA-доли, инциденты, аудиты Spark: ChainSecurity, Cantina, Spearbit).*

---

## 10. Curve Lend (LlamaLend) — кратко

- Модель: изолированные permissionless рынки «collateral ↔ crvUSD» (LLAMMA soft-liquidation). Сапплаить можно crvUSD (против collateral) или активы против crvUSD; прямого «USDC-пула» как в Aave нет — доходность с USDC-стороны получается на рынках USDC/crvUSD.
- Текущие ставки: пример sDOLA•crvUSD **4.85% supply** (30d avg 4.67%); разброс рынков ~3–5% + CRV-награды (пулы DefiLlama: 2.5–4.3% total).
- TVL: **$74M** (curve-llamalend, 4 цепи) — глубокое падение с $300M+ (2024) ⚠️.
- Ставки задаёт monetary policy (PegKeeper + rate oracles) — зависимость от crvUSD-пега.
- Риски: crvUSD-контрагентский риск, oracle (rate oracles), история Curve-эксплойтов (июль 2023 Vyper, $70M — не Lend, но репутационный), LLAMMA-«недоликвидации» (CoinDesk, сент 2026: сотни займов неделями в soft-liquidation).
- Аудиты: ChainSecurity, MixBytes ⚠️ (проверить актуальный список).

## 11. FraxLend — кратко

- TVL **$22M** (3 цепи) — остаточный протокол (пик >$130M в 2024).
- Активные рынки: FRXUSD (frxUSD) 3.46% supply; SFRXUSD; старые FRAX-пары.
- Модель: v2 dual-oracle (Chainlink + TWAP), настраиваемые пары.
- Риски: микроликвидность, custom-рынки, Frax-governance; процентные ставки в парах волатильны.

## 11a. JustLend (Tron) — упоминание

Единственный крупный «мегапул» вне EVM/Solana: TVL **$3.6B**, Tron-only (Eco/DefiLlama, сент 2026). USDT-доминированный; центр ex-контрагента Tron/Justin Sun, закрытый набор активных рынков, слабая прозрачность аудитов ⚠️. Для консервативной стратегии не рекомендуется; в детальный скоуп WS-1 не входит.

---

## 12. История инцидентов (money markets, 2020–2026)

| Дата | Протокол | Сумма | Причина | Компенсация |
|---|---|---|---|---|
| Ноя 2024 | **Aave v3** | ~$1.4M bad debt | Frozen Wood: взлом стороннего лендера (JS-инжект), позиция на Aave | Aave DAO покрыл из treasury (полностью) |
| Фев 2025 | **Fluid** | ⚠️ уточняется | Oracle/liquidation инцидент (жду агента C) | ⚠️ |
| 2025 | **Morpho** (мелкие markets) | ⚠️ | flashloan-атаки на изолированные markets | кураторы/дао ⚠️ |
| 18 апр 2026 | **KelpDAO/LayerZero → Aave v3/v4** | $290M exploit → **~$190M bad debt на Aave**; Morpho <$1M | Компромисс 1-of-1 DVN-мультисига LayerZero, минт 116.5K фейковых rsETH (~$292M), collateral → займ ~$193M WETH; Lazarus Group (Chainalysis) | «DeFi United» кампания ~$300M; bad debt закрыт без слэшинга Safety Module; AAVE −15–16% |
| Мар 2022 | **Euler v1** | $197M | Flash-loan + donateToReserves | **Возвращено полностью** за ~3 недели |
| Окт 2021 | Cream Finance | $130M | reentrancy/оракул | частично |
| Окт 2022 | Mango Markets | $115M | oracle manipulation | частично/страхование |

Ключевой урок 2026: главный риск крупного money market — **не собственный код, а качество collateral и мостов** (rsETH). Изоляция Morpho (потери <$1M) и социализация Euler сработали лучше монолитной модели Aave в этом кейсе.

## 13. Рейтинги рисков (методология)

Скор 1–10 = взвешенная оценка: (a) смарт-контракт-риск (возраст кода, аудиты, bug bounty); (b) история инцидентов/bad debt; (c) governance/admin-централизация; (d) кастодиальный/внешний риск (RWA, мосты, LST); (e) ликвидность выхода.

| Протокол | Скор | hack_probability_annual_pct | Обоснование |
|---|---|---|---|
| Aave v3 | 2.5 | 0.7% | 10+ аудитов, 4 года без прямого эксплойта кода, но $190M bad debt 2026 от внешнего collateral; Guardian/Риск-совет зрелые |
| Compound v3 | 3.0 | 0.5% | Консервативный код, инцидентов нет; минус — медленная разработка, слабее реакция на рынок |
| Sky sUSDS | 3.5 | 0.5% смарт-контракт + 1.0% кастодиальный RWA | Старейший кодбейс (Maker с 2017), но T-bills у кастодианов (BlackRock/BlockTower) — юридический/опросный риск |
| SparkLend | 3.8 | 0.8% | Fork Aave, аудиты ChainSecurity/Cantina; зависимость от Sky-решений |
| Morpho (curated) | 3.5–4.5 | 0.8–1.2% | Изоляция рынков, но curator-человеческий фактор и экзотический collateral |
| Aave v4 | 4.0 | 1.2% | Новый код, $0.66B TVL растёт; тот же governance-фрейм |
| Euler v2 | 4.5 | 1.2% | История v1 ($197M, возвращён), падение TVL −70%, социализация потерь |
| Fluid | 5.0 | 1.5% | Код 2024, инцидент Feb 2025, upgradeable admin, премия ставки отражает риск |
| Kamino | 5.5 | 1.8% | Solana-инфраструктура, отток TVL, oracle-стек |
| Curve Lend | 6.0 | 2.0% | crvUSD-зависимость, малый TVL, Vyper-наследие |
| FraxLend | 6.5 | 2.5% | Микро-TVL, dual-oracle риски |

hack_probability — экспертная оценка на основе частоты инцидентов по классу протоколов (DefiLlama: $20B+ потерь, 1200+ инцидентов; для топ-lending базовая частота ~0.5–2%/год) ⚠️ калибровка модельная (models/risk_model.py в Phase 2).

## 14. Источники (дата обращения 2026-10-15, кроме отмеченного)

1. DefiLlama API (прямой): api.llama.fi/protocols; api.llama.fi/protocol/{aave-v3, aave-v4, morpho-blue, compound-v3, euler-v2, kamino-lend, fluid-lending, sparklend, sky-lending, spark-savings, curve-llamalend, fraxlend}; yields.llama.fi/pools; yields.llama.fi/chart/{pool-id}
2. app.aave.com — reserve overview USDC mainnet (supplied 2.39B/3.00B)
3. Eco.com «Best USDC Yield Platforms 2026» (данные 24.05.2026): https://eco.com/support/en/articles/15253991-best-usdc-yield-platforms-2026-aave-morpho-sky-compared
4. Eco.com «Best DeFi Lending Protocols 2026» (данные DefiLlama 15.09.2026): https://eco.com/support/en/articles/14800882-best-defi-lending-protocols-2026-tvl-rates-risk
5. Galaxy Research «KelpDAO/LayerZero Hack: $290m Exploit» (апр 2026): https://www.galaxy.com/insights/research/kelpdao-layerzero-exploit-defi
6. FRED DFEDTARU (Fed funds upper limit 4.00% на 14.10.2026): https://fred.stlouisfed.org/series/DFEDTARU
7. LlamaRisk «A Primer on Curve Lending»: https://www.llamarisk.com/research/curve-lending
8. Curve.finance lend UI: https://www.curve.finance/lend/ethereum/markets/0xC77d97cF01737EB7aCE46cAb7cd9F60eC51a40c0/vault/deposit
9. CoinDesk (08.09.2026) «Hundreds of DeFi loans on Curve stayed in liquidation for weeks»: https://www.coindesk.com/tech/2026/09/08/hundreds-of-defi-loans-on-curve-stayed-in-liquidation-for-weeks-without-dying
10. Данные агентов A–D (аудиты, механики, официальные дашборды) — в тексте.

> Отчёт будет финализирован после возврата данных фоновых агентов (разделы 3–9, помеченные «будет дополнено»).
