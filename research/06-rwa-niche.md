# WS-6: RWA (токенизированные гособлигации) и нишевые кредитные протоколы

**Дата исследования:** 15 октября 2026
**Автор:** crypto-research agent
**Статус данных:** все ключевые цифры проверены по живым источникам (FRED, rwa.xyz, DeFiLlama, сайты эмитентов) на 13–15 октября 2026. Оговорки по непроверённым позициям — в разделе «Что не удалось проверить».

---

## 1. Макросреда (критично для RWA yield)

### 1.1 Ставка ФРС

| Параметр | Значение | Дата/источник |
|---|---|---|
| Fed funds target range | **3.75–4.00%** | после заседания FOMC 17 сент 2026 (federalreserve.gov) |
| Fed funds effective (DFF) | **3.88%** | 13 окт 2026, FRED |
| Следующее заседание FOMC | 27–28 окт 2026 | federalreserve.gov |

### 1.2 Кривая доходности US Treasuries (CMT, FRED, 13 окт 2026)

| Tenor | Yield |
|---|---|
| 3M | **4.26%** |
| 6M | **4.34%** |
| 1Y | **4.48%** |
| 2Y | **4.79%** |

Кривая крутая вверх (2Y − 3M ≈ +53 б.п.), и **T-bills торгуются ВЫШЕ effective fed funds** — рынок закладывает дальнейшее ужесточение.

### 1.3 Инфляция

- CPI (SA, FRED): сентябрь 2026 = 336.298 против 324.245 в сентябре 2025 → **YoY ≈ 3.7%**.
- Инфляция выше таргета 2% — согласуется с разворотом ФРС к hikes.

### 1.4 Траектория ставок 2025–2026 (факты FOMC)

| Дата | Решение | Target range |
|---|---|---|
| 18 сен 2025 | cut −25 б.п. | 4.00–4.25% |
| 30 окт 2025 | cut −25 б.п. | 3.75–4.00% |
| 11 дек 2025 | cut −25 б.п. («делённое» решение, сигнал паузы) | 3.50–3.75% |
| янв–июн 2026 | пауза (мартовский dot plot — медиана ещё +1 hike в 2026) | 3.50–3.75% |
| **17 сен 2026** | **hike +25 б.п.** (первое повышение за ~3 года) | **3.75–4.00%** |

**Вывод для RWA-стратегии:** режим сменился с easing на re-tightening. Доходности RWA-продуктов в октябpe 2026 (3.3–3.8%) ещё отражают «дно» траектории (они следуют за ставками с лагом); при продолжении hikes верхняя граница будет подтягиваться к 4.3–4.5%+ в течение 1–2 кварталов (кривая уже там). Tokenized treasuries рынок: **~$15.4B (май 2026)** против <$200M в начале 2024 (Spark research).

---

## 2. Сводная таблица продуктов

| Продукт | Тип | Текущий yield | AUM/TVL | Вход / KYC | Liquidity | Риск-скор (1–10) |
|---|---|---|---|---|---|---|
| USDY (Ondo) | T-bill note | 3.68–3.75% APY | $2.35B | ~$500 primary (KYC, non-US); secondary без KYC | Отличная (13 сетей, DEX/CTLP) | 4 |
| OUSG (Ondo) | T-bill fund (держит BUIDL и др.) | 3.65% | $319M | $100k primary (KYC, accredited) | Средняя (limited secondary) | 3.5 |
| BUIDL (BlackRock/Securitize) | MMF (T-bills/repo) | 3.48–3.82% (div monthly) | $2.16B (~$2.5B май 2026) | $5M, институц. KYC | Хорошая (9 сетей,Securitize secondary) | 2.5 |
| BENJI/FOBXX (Franklin Templeton) | US MMF (’40 Act) | 3.79% eff. 7-day | $680M (+iBENJI $1.71B BVI) | **$20** (Benji app, US, KYC) | Средняя (on-chain transfer permissioned) | 2.5 |
| iBENJI (Franklin, BVI) | Институц. MMF | ~3.7% (как класс) | $1.71B | Институциональный, KYC | Ограниченная | 3 |
| USYC (Circle/Hashnote) | T-bill fund (NAV accretion) | 3.38% | $2.35B ($2.4B rwa.xyz) | $100k, институц. | Хорошая (ETH/BSC) | 3 |
| Invesco USTB (б. Superstate) | Short-dur. Gov fund | 3.57% | $606M ($950M–1B на транзите Q2 2026) | $100k, accredited | Средняя (ETH/SOL/Plume) | 3 |
| OpenEden TBILL | T-bill vault | 3.54% | $295M (rwa.xyz) | Низкий вход, KYC (non-US/аккр.) | Средняя (5+ сетей) | 4 |
| JTRSY (Anemoy/Centrifuge) | T-bill fund | 3.30% | $345M | Институц., KYC | Ограниченная | 4 |
| USAT (Tether America/Anchorage) | Yield-bearing stablecoin (T-bills) | 3.73% | ~$293M | Пока ограничен (институц. каналы) | Средняя (мультисеть, Centrifuge) | 5 |
| USDM (Mountain) | — | **МЁРТВ** | ~$0 (остатки $1.4M) | wind-down закрыт 22 авг 2025 | Нет | 10 |
| syrupUSDC (Maple) | Корп. кредит (secured, overcollateralized) | **5.20% APY** | $2.83B (пул) | Нет KYC для депозитов (ERC-4626) | Отличная (Aave/Morpho/Kamino коллатерал) | 5.5 |
| syrupUSDT (Maple) | То же | **5.54% APY** | $747M | Нет KYC | Отличная | 5.5 |
| syrupUSDG (Maple) | То же (USDG) | 4.91% | $525M | Нет KYC | Хорошая | 5.5 |
| sUSDS (Sky) | Savings rate (RWA-backed) | ~3.6–3.75% | $5.5B sUSDS supply | Нет KYC, любой размер | Отличная (ETH, Robinhood Chain) | 4.5 |
| OpenTrade | T-bill vault (USDC/USDT) | ~5.5% (30D) | $247M | Через партнёров (CEX/fintech), без розничного KYC | Средняя | 4.5 |
| Midas (midas-rwa пулы) | RWA yield пулы | 1.8–10.2% (по пулам) | ~$400M+ (сумма пулов) | Зависит от канала | Средняя | 5 |
| Yearn v3 (USDC vaults) | Агрегатор yield | 3.6–7.0% | $154M (протокол) | Нет KYC | Хорошая | 5.5 |
| Goldfinch | Корп. кредит | — | $1.9M | — | Нет | 9 (мёртв) |
| Clearpool | Uncollateralized lending | ~3.5% (USDX) | ~$11M | — | Нет | 8 (сжался) |
| TrueFi | Uncollateralized lending | — | $22K | — | Нет | 9.5 (мёртв) |
| Level (lvlUSD) | CDP/stable | — | $460K | — | Нет | 8 (заморожен) |
| Idle | Агрегатор | низкий | $623K | Нет KYC | Слабая | 8 (зомби) |
| Tempus | Fixed yield | — | $0 | — | Нет | 10 (мёртв) |
| Sense | Fixed yield | — | $28K | — | Нет | 10 (мёртв) |
| Ethena sUSDe (для сравнения) | Basis/delta-neutral | 4.92% | $1.2B в sUSDe | Нет KYC | Отличная | 6.5 |

---

## 3. Детальные разборы

### 3.1 Ondo Finance — USDY / OUSG / Global Markets

- **USDY** (US Dollar Yield): токенизированная нота под краткие T-bills/repo. **Yield 3.75% APY (daily accrual, на 13 окт 2026 по сайту Ondo; DeFiLlama 3.68%)**. TVL **$2.35B** (rwa.xyz, 15 окт; крупнейшие размещения: Ethereum $1.26B, Stellar $537M, Sei $260M, Solana $180M — всего 13 сетей). Цена токена ~$1.15 — доход «вшит» в стоимость (покупка по $1.15 даёт текущий yield, не 3.75% на номинал). Первичка — от ~$500 (Spark research, июнь 2026), только non-US с KYC; **вторичный рынок (DEX/CEX) — без KYC**, токен freely transferable. Redemption: через Ondo primary (быстро, T+0/T+1) или мгновенная продажа на вторичке.
- **OUSG**: $319M, **3.65%**; держит преимущественно BUIDL + фонды Franklin Templeton / WisdomTree / Fidelity / Wellington. Вход $100k, accredited. Используется как collateral (например, Flux Finance).
- **Ondo Global Markets**: январь 2026 — **200+ токенизированных акций/ETF на Solana**, T+0 сеттлмент; Ondo стал крупнейшим RWA-эмитентом по совокупному охвату. Октябрь 2026: линейка «Ondo Intelligent Portfolios» расширена до 7 (включая fixed yield loans).
- Риски: USDY — необеспеченное обязательство эмитента (Ondo XXVI), без страховки; регуляторный риск для non-US схемы; рыночный (depeg) минимальный.

### 3.2 BlackRock BUIDL (Securitize)

- AUM **$2.16B** (rwa.xyz, 15 окт; ~$2.5B в мае 2026; $1B — март 2025). Мультичейн: Ethereum, Solana, Aptos, Arbitrum, Avalanche, BNB, OP, Polygon и др.
- Yield: **3.48–3.82% APY** (по пулам DeFiLlama на разных сетях), daily accrual, **monthly dividend** эйрдропом через Securitize. Встречающиеся оценки «4.75–5.25%» — устаревшие (уровень ставок 2024–нач.2025).
- Вход: $5M, институциональные квалифицированные инвесторы, KYC через Securitize. Распространяется через интеграторов (Securitize Markets, P2P-обёртки типа sBUIDL/BNBUIDL у партнёров — именно так Sky и DeFi-интеграторы получают доступ).
- Redemption: через Securitize, USDC/USD. Риск-скор минимальный среди RWA (спонсор BlackRock + BNY Mellon кастодиум).

### 3.3 Franklin Templeton Benji (FOBXX / BENJI / iBENJI)

- **FOBXX** (BENJI): первый US-registered токенизированный MMF (’40 Act), ≥99.5% в гособлигациях/репо. **7-day effective yield 3.79%** (3.72% current), расходы 0.20%. Дивиденды ежедневно, минт новых BENJI в кошельки. AUM (on-chain) **$680M** (30D: −11.6% — отток в пользу iBENJI/конкурентов).
- **iBENJI**: Franklin OnChain Institutional Liquidity Fund Ltd (BVI), институциональный офшорный класс, **$1.71B**. Суммарно бренд Benji ≈ **$2.4B** — топ-3 среди tokenized treasuries.
- Вход: **$20** через Benji Investments app (US, полный KYC) — самый низкий в классе; on-chain переводы BENJI — только whitelisted адреса (permissioned secondary). Риски минимальные (regulated fund), ликвидность on-chain ограничена комплаенсом.

### 3.4 Mountain Protocol USDM — МЁРТВ

- Сентябрь 2024: Bermuda Monetary Authority запретила issuance USDM.
- **12 мая 2025: Anchorage Digital приобрёл Mountain Protocol**; USDM отправлен в orderly wind-down. Phase 2 завершена **22 августа 2025** — primary market закрыт, остатки выкуплены. На rwa.xyz в таблице treasuries отсутствует; остаточный TVL ~$1.4M ( remnants в Curve/Aave на L2). Урок: регуляторный риск оффшорных yield-стейблкоинов реализуется быстро; KYC-эмитенты с US-фондами (BENJI/BUIDL) пережили цикл без потерь.

### 3.5 OpenEden / Superstate (USTB, USCC) / Centrifuge

- **OpenEden TBILL**: $294.6M (rwa.xyz; on-chain видимо ~$84M + TBL на XRPL $63M и др.), **3.54%**; запущен новый **USDO** (3.39%) и cUSDO. Сети: Ethereum, Solana, Arbitrum, BNB, XRPL. KYC обязателен (non-US/аккредитованные). Redemption через primary.
- **Superstate USTB → Invesco USTB**: март 2026 — Invesco забрал управление фондом (первый случай «внешнего» менеджера на платформе Superstate); Q2 2026 фонд стал **Invesco USTB** (~$950M–1B на транзите; сейчас **$606M**, 3.57%, accredited, $100k). Сети: Ethereum, Solana, Plume.
- **USCC — поправка**: это НЕ корпоративный кредит, а **Superstate Crypto Carry Fund** (токенизированный cash-and-carry по BTC/ETH + T-bills, июль 2024, qualified purchasers; связан с Bitwise). Корпоративного кредитного фонда у Superstate в 2026 не найдено.
- **Centrifuge**: старые tin pools фактически вытеснены новыми форматами: **JTRSY** (Anemoy Capital SPC, US Treasury Debt) — $345M, 3.30%; **USAT** (Tether America USD, эмитент Anchorage Digital Bank) — ~$293M, 3.73% — знаковый вход Tether в yield-bearing токены; APXUSD и мелкие USDC-пулы на Base/Avalanche/Plume под 3.3–3.7%.

### 3.6 Maple Finance (сироп)

- **syrupUSDC 5.20% / syrupUSDT 5.54% / syrupUSDG 4.91% APY** (DeFiLlama, 15 окт 2026; официальный срез 8 окт: 5.21%/5.46%). Это корпоративное кредитование (private credit), НЕ T-bills.
- Масштаб: пул USDC **$2.83B**, USDT $747M, USDG $525M (≈$4.1B в пулах); loans outstanding **ATH $1.9B в Q2 2026 (+123% YoY)**; заявлено $25B cumulative originated, $4.8B AUM, $100M выплачено lenders. syrup-токены приняты как collateral в Aave v3 (в т.ч. Monad $161M), Kamino, Jupiter Lend, Morpho — лучшая «collateral-liquidity» среди yield-токенов.
- История дефолтов 2022–23: **$36M defaulted, суммарный bad debt $54M, затронуто ~30% активных займов** (The Block/EarnPark). После пивота на overcollateralized/secured lending (2023) новых дефолтов не зафиксировано; APY прошёл цикл 9.1% (окт 2025) → 4.2% (апр 2026) → 5.2% (окт 2026).
- KYC: для депозиторов в syrup-пулы **нет** (permissionless ERC-4626); заёмщики — KYC-институции. Оговорка: институциональные займы идут под 9–14% на 30–180 дней, ретейл-APY ниже за счёт спреда и страховки (pool cover).

### 3.7 Goldfinch / Clearpool / TrueFi — статус

| Протокол | Статус (окт 2026) | Комментарий |
|---|---|---|
| Goldfinch | TVL **$1.9M** — почти мёртв | пик >$100M (2022); убытки по emerging-market кредиту, withdrawals ограничены |
| Clearpool | Пулы lending ~$11M (USDX на Flare 3.5%) | пивот на собственный L2 Ozean; unc3ollateralized lending фактически заморожен |
| TrueFi | TVL **$22K** — мёртв | исторические дефолты ~$90M (uncollateralized book 2022–23, ~половина портфеля в NPL); продукт свернут |

Рынок on-chain private credit в целом: **~$8B активного TVL (середина 2026)** — рост почти целиком за счёт Maple; сектор uncollateralized-ретейл-кредита вымер, институциональный secured — выжил.

---

## 4. Sky / MakerDAO RWA exposure (пересечение с WS-1)

- Sky — **крупнейший DeFi-потребитель tokenized treasuries**: RWA обеспечивают **~40% collateral USDS** и **>60% выручки** (Spark research, 2026). Резервы аллоцируются через Monetalis / BlockTower / напрямую в фонды (включая экосистему BUIDL/Securitize). Исторический пик RWA-взрывов ~$3.3B (конец 2023).
- **sUSDS (Sky Savings Rate): ~3.6% (окт 2026)**; был 3.75% в середине 2026, 4.75% годом ранее — ставка следует за FFR с лагом. sUSDS supply **$5.52B (июль 2026, +149% YoY)**; USDS supply ~$10B. Дополнительно: пулах Spark встречается 4.2% (с бустами), Pendle stUSDS даёт фиксацию.
- Механика: T-bill доходность фонда → SSR (governance parameter) → sUSDS. При hike-цикле SSR будет поднят с лагом (риск недополучения относительно 3M T-bill 4.26%).
- Риски: governance (Sky Atlas), S&P рейтинг **B-** (авг 2025), кастодальный/правовой риск SPV-схем. Для WS-1: sUSDS — главный «без-KYC» бенчмарк RWA-доходности.

---

## 5. CEX Earn (для сравнения)

| Биржа | Продукт | Ставка (окт 2026) | Формат |
|---|---|---|---|
| Binance | Simple Earn USDC | **4.04%** real-time APR | flexible |
| Binance | Simple Earn USDT | точно не верифицировано (обычно ниже USDC, промо выше) | flexible/locked |
| OKX | Savings USDT | **3.5%** est. APR | flexible |
| OKX | Savings USDC | **~5.0% avg** (est. до 9.5% — промо-пики) | flexible |
| Bybit | Flexible USDT | **~3.2–6%** базовая APR (промо-бустеры до 50–777% на ограниченные балансы — маркетинг) | flexible |
| Kraken | USDC rewards | **1.75–2%** стандарт, до **4.0–4.5%** с Kraken+; награды начисляются максимум на 50% стейкаемого баланса | flexible |

Кастодиальный/регуляторный риск:

- **FTX (нояб 2022)**: earn-депозиты — unsecured creditors; clawback-процесс Ch11 растянулся на годы, восстановление частичное. Ключевой прецедент: «flexible earn» юридически = необеспеченный кредит бирже.
- **Bybit hack (21 фев 2025)**: ~**$1.46–1.5B ETH** из cold wallet (Lazarus/TraderTraitor, атрибуция FBI). Выводы приостанавливались лишь на часы; биржа пережила bank-run (мост-кредиты/резервы), но: индийский FIU заблокировал доступ (фев 2025), уход из Франции и др. юрисдикций — пример regulatory freeze поверх технического риска.
- Binance: settlement DoJ $4.3B (2023), выборочный уход из юрисдикций; frozen-кейсы по запросам LE.
- **Вывод CEX vs DeFi**: розничные flexible-ставки CEX (≈3.5–6%) сопоставимы с RWA-продуктами (3.3–5.5%) и ниже Maple. Но CEX даёт: (а) custodial риск потери принципала (FTX/Bybit), (б) регуляторные заморозки, (в) опаковость реального использования средств. DeFi RWA/Yield (USDY secondary, syrupUSDC, sUSDS) даёт ту же или большую доходность при self-custody, с риском смарт-контракта вместо кастодиального. Для суммы > порога комфорта CEX-earn — доминируемая стратегия; locked-продукты CEX дают +1–3% но усиливают freeze-риск.

---

## 6. Нишевые vaults 2025–2026 (статус)

| Протокол | Статус | Ставка/TVL |
|---|---|---|
| **OpenTrade** | Жив, растёт | ~5.5% APY (30D), $247M TVL; T-bill-backed USDC/USDT; интеграции с WOO X, Criptan и др. CEX/fintech |
| **Midas (midas-rwa)** | Жив, расширился | Пулы USDC 1.81–10.21% на Ethereum/Base/Monad/Robinhood Chain/Plasma/Etherlink; ~$400M+ суммарно. **mBASIS в 2026 в топ-пулах не наблюдается** (basis-спред сжался) — фокус смещён на yield-пулы для стейблкоинов/бирж |
| **Level (lvlUSD)** | Заморожен/сжался | TVL $460K (CDP); perps $0.4K — активность минимальна |
| **Idle** | Зомби | $623K TVL |
| **Yearn v3** | Жив | $154M TVL (aggregator + $49M curating); USDC vaults 3.6–7.0% |
| **Tempus** | Мёртв | $0 |
| **Sense** | Мёртв | $28K |
| **Tribe** | Не идентифицирован | значимого живого vault-продукта под этим именем не найдено (tribe.run — нерелевантный SoFi $179K) |
| Ethena sUSDe (вне скоуп, бенчмарк) | Жив | 4.92%, $1.2B в sUSDe |

Заметный новичок 2026: **Liminal (LIMUSD)** — basis-trading vault 8.08% APY, $8.5M (Hyperliquid/Arbitrum) — ниша, Monitoring-only.

---

## 7. Дефолт-история кредитных протоколов (сводка)

| Протокол | Период | Дефолты/потери | Судьба |
|---|---|---|---|
| Maple | 2022–23 | **$36M defaulted / $54M bad debt, ~30% активных займов** (Orthogonal/Auros/mentos) | Пережил: пивот на secured lending, сейчас $4.8B AUM, дефолтов с 2023 нет |
| TrueFi | 2022–23 | **~$90M** NPL (uncollateralized: Celsi, Alameda-adjacent и др.) | Не восстановился, TVL $22K |
| Goldfinch | 2022–24 | Убытки по EM-кредитам (Ftitle, Aladdin и др.), точная сумма раскрыта не полностью | TVL $1.9M — фактически мёртв |
| Clearpool | 2022–24 | Отдельные NPL по uncollateralized полюсам (в т.ч. конфликтные кейсы 2024) | Пивот на Ozean/lending свернут |
|lend | — | — | — |

Паттерн: uncollateralized-кредит умер везде; выжившие модели — overcollateralized (Maple syrup) или фондовые RWA.

---

## 8. Итоговые рекомендации (по доступность/риск)

1. **Лучший доступ/риск для розницы без KYC**: **USDY** (secondary) и **sUSDS** — глубокая ликвидность, 3.6–3.75%, риск смарт-контракта вместо кастодиального.
2. **Лучший компромисс доходность/риск**: **Maple syrupUSDC/USDT** (5.2–5.5%) — при принятии кредитного циклического риска; наблюдать за закредитованностью институциональных заёмщиков при hike-цикле.
3. **Минимальный риск**: BUIDL / BENJI (regulated фонды) — для сумм/статусов, позволяющих вход; для US-розницы BENJI от $20.
4. **Наименьшая эффективность**: CEX flexible earn — та же доходность, худший профиль риска принципала.
5. Мониторинг: при подтверждении hike в окт/дек 2026 FOMC — ожидать подтягивания RWA-ставок к 4.3–4.7% с лагом 1–2 мес.; USAT/USDO/OpenTrade — кандидаты в «fast followers».

---

## 9. Что не удалось проверить / оговорки

- **Binance USDT flexible APR** — точное текущее значение (endpoint закрыт, JS-рендер); USDC 4.04% подтверждён по странице Simple Earn. Locked-ставки всех CEX не снимались.
- **Минимальный вход OpenEden TBILL/USDO** — по каналам различается (до $100 на некоторых сетях против $10k институционально); в таблице указан диапазон.
- **Текущий 30D APY JTRSY/USAT по rwa.xyz** — скрыт за логином; использованы значения DeFiLlama (3.30%/3.73%).
- **Точная структура RWA-портфеля Sky по vault'ам** (BUIDL vs Monetalis vs BlockTower в долларах) — публичной разбивки не найдено; даны оценки ~40% collateral.
- **Тribe** — однозначной идентификации протокола из брифа нет.
- **USDM residual** — точная сумма невостребованных остатков после 22 авг 2025 неизвестна.
- Оценки `hack_probability_annual_pct` — экспертные (субъективные вероятности loss-of-funds событий), не рыночные котировки.

---

## 10. Источники (URL + дата проверки)

| Источник | Дата |
|---|---|
| https://www.federalreserve.gov/monetarypolicy/openmarket.htm — target range 3.75–4.00%, история FOMC | 2026-10-15 |
| https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS3MO,DGS6MO,DGS1,DGS2 — кривая CMT | 2026-10-15 (данные 2026-10-13) |
| https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL,DFF — CPI, DFF | 2026-10-15 (данные 2026-09 / 2026-10-13) |
| https://app.rwa.xyz/ — AUM tokenized treasuries (USDY $2.35B, BUIDL $2.16B, iBENJI $1.71B, BENJI $680M, USYC $2.4B, USTB $606M, OUSG $319M, TBILL $295M) | 2026-10-15 |
| https://app.rwa.xyz/assets/JTRSY — Anemoy, $345M | 2026-10-15 |
| https://app.rwa.xyz/assets/USAT — Tether America USD / Anchorage Digital Bank | 2026-10-15 |
| https://yields.llama.fi/pools + https://api.llama.fi/protocols — APY/TVL (BUIDL, USDY, OUSG, USYC, USTB, TBILL, syrup*, Yearn, Maple TVL, OpenTrade, Midas и др.) | 2026-10-15 |
| https://ondo.finance/usdy — USDY 3.75% APY | 2026-10-13 (по сниппету) |
| https://www.franklintempleton.com/.../FOBXX — 7-day yield 3.79% | 2026-10-15 |
| https://mountainprotocol.com/company — USDM wind-down, Phase 2 до 22 авг 2025 | 2026-10-15 |
| https://www.prnewswire.com/news-releases/invesco-and-superstate-advance-institutional-tokenization-through-ustb-partnership-302722437.html — Invesco/USTB | 2026-03-24 (анонс) |
| https://superstate.com/assets/uscc — USCC = Crypto Carry Fund | 2026-10-15 |
| https://www.spark.money/research/tokenized-treasuries-onchain-yield — рынок $15.4B, минимальные входы, Sky RWA ~40% collateral | 2026-06 (статья) |
| https://maple.finance + https://maple.finance/insights/maple-q2-2026-ecosystem-update — loans $1.9B ATH, AUM $4.8B | 2026-10-15 |
| https://earnpark.com/en/posts/maple-finance-review-2026 — дефолты $36M/$54M | 2026-09-18 (статья) |
| https://x.com/SkyEcosystem + https://earnpark.com/en/posts/susds-review-2026 — SSR 3.60%, sUSDS $5.5B | 2026-10 (публикации) |
| https://www.binance.com/en/earn/simple-earn — USDC 4.04% flexible | 2026-10-15 |
| https://www.okx.com/api/v5/finance/savings/lending-rate-summary — USDT 3.5%, USDC ~5.0% | 2026-10-15 |
| https://coinbureau.com/review/bybit-earn-review — Bybit 3.2–6% | 2026-07-24 (статья) |
| https://support.kraken.com/articles/stablecoin-rewards — Kraken 2–4.5% | 2026-10 (статья) |
| https://www.bybit.com/en/learn/this-week-in-bybit/bybit-security-incident-timeline + https://www.fbi.gov/investigate/cyber/alerts/2025/north-korea-responsible-for-1-5-billion-bybit-hack — hack 21 фев 2025 | 2025 |
| https://eco.com/support/en/articles/15254025-tokenized-private-credit-2026-maple-centrifuge-goldfinch-compared — Goldfinch $1.9M | 2026-09-16 (статья) |
| https://www.opentrade.io/case-studies/woo-x + X @opentrade_io — OpenTrade 5.53% 30D | 2026-10 |
