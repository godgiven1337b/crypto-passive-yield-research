# WS-12. Карта программ наград DeFi: Merkl, IPOR Fusion, нативные и цепочечные инсентивы

Дата: 2026-10-16. Автор сессии: дефи-аналитик ( Claude Code).
Контекст: предыдущие WS-8..WS-11 показали, что Merkl — «тонкий слой» 0.3–2 п.п. поверх базовой ставки. Задача WS-12 — полная карта надёжных программ наград и поиск мест, где 2–3 программы стекаются на одном капитале.

Главные данные — собственный срез API Merkl на 2026-10-16 (897 LIVE-возможностей, суммарно **$678 742/день**, ~$20.4M/мес) + DeFiLlama yields + докам протоколов.

---

## 1. Merkl (merkl.xyz) — главный рынок наград

### 1.1 Как это работает (по docs.merkl.xyz, проверено 2026-10-16)

- **Кто платит**: создатели кампаний — протоколы, эмитенты стейблов, цепочки. Бюджет вносится **ончейн в контракт DistributionCreator** заранее (либо через token wrapper с кастодией). Merkl не платит из своих — он инфраструктура. Это ключевой факт для надёжности: деньги уже в контракте до старта кампании.
- **Как считается**: off-chain движок Merkl пересчитывает награды **каждые ~2 часа** на кампанию. Учёт time-weighted («area under the curve»), без снапшотов — не надо держать позицию в конкретный момент. Если ончейн-состояние расходится с расчётом >1%, движок читает позиции всех пользователей ончейн.
- **Дерево**: каждые ~8 ч (4–12 ч) публикуется один merkle root на цепочку в контракт Distributor.
- **Dispute period**: 1–2 часа после каждого апдейта любой может оспорить root (невалидный диспут сжигает залог). Merkl держит независимых dispute-ботов.
- **Claim**: в той же цепочке, где заработаны награды; **одной транзакцией** забираются все кампании цепочки. Прорядок: proof'ы живут в среднем ~4 часа (root обновился — tx падёт, надо перегенерить). Есть **autoclaim** (Merkl сам пушит в кошелёк; работает не во всех сетях/протоколах), **operator mode** (клейм за вас другим адресом — важно для мультисигов), **claim recipient** и **callback-клейм** (автодепозит/автосвоп наград — этим пользуются волты IPOR Fusion и агрегаторы).
- **Админ**: контракты под 4/6 мультисигом.

### 1.2 Реальный опыт claim (оценка)

- Скорость: награды начисляются каждые ~2 ч, климить можно практически сразу после публикации root (~8 ч цикл). Для фармера это «почти стриминг».
- Газ: одна транзакция на все кампании цепочки; на L2/Base доли цента. Проблемы только на Ethereum mainnet при мелких суммах (claim от ~$50+ имеет смысл).
- Риск не получить: (а) задержки движка — лечится catch-up ретроактивно; (б) кампания закончилась — всё начисленное остаётся климабельным бессрочно; (в) централизованный оракул — теоретический риск ошибки/злоупотребления, страховка — dispute-период и ончейн-бюджет; (г) точки/поинты в наградах (Orbital Points и т.п.) имеют номинальную «цену» — фильтровать. Практический вывод: **для кампаний с ликвидным токеном награды Merkl надёжен**, за 2+ года работы массовых невыплат не зафиксировано.

### 1.3 Структура бюджета Merkl (срез 2026-10-16)

По цепочкам ($/день):

| Цепочка | $/день | Кол-во opp |
|---|---|---|
| Ethereum | 242 401 | 217 |
| Base | 136 928 | 146 |
| Robinhood Chain | 92 453 | 50 |
| Plasma | 80 563 | 8 |
| Monad | 69 911 | 156 |
| Stellar | 13 775 | 9 |
| Mantle / World / Arbitrum / Tempo / Arc / Katana / HyperEVM | 9.4k / 6k / 5.9k / 3.6k / 3.1k / 2.5k / 2.1k | … |

Кто чем платит (по классам, на примере Morpho — 166 кампаний, $347k/день = 51% всего Merkl):
- **Ликвидные стейблы** — крупнейший класс: USDe (Ethena, ~$104k/день только на Morpho-кампаниях), PYUSD (PayPal, $47.8k/д), USDC ($47.7k/д), steakUSDG ($40.5k/д), RLUSD (Ripple, $34.5k/д), GHO (Aave DAO).
- **Нативные токены**: WMON (~$40k/д на Monad), MORPHO ($12.7k/д), ARB ($4.2k/д) — ликвидны, но волатильны.
- **Поинты**: Orbital Points, Curvance Bytes, kHYPE-поинты — номинальная цена, спекулятивны.

### 1.4 Топ-10 LIVE-кампаний по dailyRewards (2026-10-16, ANY актив)

| # | Кампания | Цепочка | Протокол | $/день | APR | TVL | Токен награды | Конец кампании |
|---|---|---|---|---|---|---|---|---|
| 1 | Lend USDe on Aave (looping required) | Plasma | Aave | **69 711** | 4.5% | $605M | aPlaUSDe (USDe) | 2026-10-23, еженедельно |
| 2 | Deposit USDe as collateral USDe/USDC 91.5% | Base | Morpho | **50 447** | 4.75% | $388M | USDe | 2026-10-23 |
| 3 | Deposit USDe as collateral USDe/USDG 91.5% | Robinhood Chain | Morpho | **45 686** | 4.75% | $351M | USDe | 2026-10-23 |
| 4 | Supply Steakhouse USDG V2 (Robinhood only) | Robinhood Chain | Morpho | **40 490** | 2.92% | $506M | steakUSDG | **2027-07-01** |
| 5 | Supply Sentora RLUSD Main V2 | Ethereum | Morpho | **34 480** | 2.78% | $453M | RLUSD | 2026-10-22 |
| 6 | Supply Steakhouse High Yield USDC V2 | Base | Morpho | **32 899** | 2.66% | $463M | USDC+MORPHO | **2026-11-12** |
| 7 | Supply Paypal USD Main V2 | Ethereum | Morpho | **31 661** | 2.93% | $395M | PYUSD | 2026-10-22 |
| 8 | Lend USDe on Aave (looping) | Ethereum | Aave | **30 290** | 4.8% | $246M | aEthUSDe | 2026-10-23 |
| 9 | Supply USDC on USDe/USDC 91.5% | Base | Morpho | **21 047** | 2.0% | $384M | USDC | 2026-11-12 |
| 10 | Lend USD1 on Dolomite | Ethereum | Dolomite | 18 697 | 5.1% | $134M | WLFI | — |

Дальше: Aave Monad USDe $17.2k/д, Aave Horizon RLUSD $14.5k/д, Flowdesk Confidential USDT $8.1k/д (8.9% APR), Upshift Stellar USDC $8.8k/д (8%).

**Вывод по Merkl**: это не «тонкий слой» вообще — это рынок, где **эмитенты стейблов покупают депозитный спрос** (Ethena, PayPal, Ripple, Sky, Worldcoin…). Топ-10 кампаний = $370k/день (55% рынка), все платят ликвидными стейблами. Слой наград 1.9–5 п.п. поверх базы — там, где база сама 3–5%, суммарно выходит 6–8% на blue-chip стейблах с минимальным риском. Кампании Ethena/Aave продлеваются еженедельно (стабильно с 2024), issuer-кампании Morpho — тоже еженедельно/помесячно.

---

## 2. IPOR Fusion (ipor.io) — агрегатор лупнутых стратегий

### 2.1 Механика (по docs.ipor.io, проверено 2026-10-16)

- ERC-4626 волты; стратегией управляет сторонний куратор — **Atomist**; стратегии модульные (**Fuses** — интеграции Aave V3, Morpho, Euler V2, Compound V3, Gearbox, Fluid, Uniswap V3, **Merkl** и др.).
- **Автоматизация**: авто-ребалансировка, автоматический риск-менеджмент (при стрессе волт сам выводит ликвидность из DeFi), Guardian-роли (security-фирмы могут поставить волт на паузу), изоляция рисков между волтами (no socialized losses).
- **RewardsManager**: волт сам климит награды (включая Merkl — есть специальный fuse) и вестит их — стек «стратегия + Merkl» работает из коробки.
- **Комиссии**: management 0.2–0.3%/год (на AUM) + automation 0.2%/год + performance **2%** с прибыли (типовой сетап; жёсткие капы протокола — 5% mgmt / 50% perf). Performance fee =买back&burn IPOR + доля куратору.

### 2.2 Текущие APY (DeFiLlama, 2026-10-16)

| Волт | Цепочка | TVL | APY сейчас | 30-д средн |
|---|---|---|---|---|
| Fusion ETH (крупнейший) | Ethereum | $14.65M | 6.26% | 5.98% |
| USDC (лучшая ставка на стейблах) | Ethereum | $0.80M | 13.06% | 12.35% |
| Base USDC Optimizer | Base | $1.07M | 6.31% | 6.34% |
| Base USDC (крупный) | Base | $2.92M | 4.75% | 4.59% |
| RUSD | Ethereum | $0.62M | 7.61% | 4.44% |

Всего Fusion ~$55M TVL — карлик против Morpho ($15B+).

### 2.3 Экономика лупов и что случилось в 2026

Флагманские **AavEthena Loop** (supply USDe/sUSDe на Aave → borrow USDe → луп) работали в 2024–2025. К сентябрю 2026 Aave поднял ставки (proposal +13…+89 bps): **заём USDe 6.0–6.4% против доходности sUSDe ~5.0%** — луп ушёл в negative carry; AavEthena Loop Mainnet слил >95% TVL (осталось ~$95k, помечен «likely abandoned»), Plasma-версия «phased out». Раскрутка ~$7B USDe-лупов на Aave в 2026 (Bitquery) закончилась стагнацией. Сами sUSDe/sUSDS: 4.80%/3.80%.

### 2.4 Вердикт по IPOR Fusion

- Плюсы: one-click, изолированный риск, автоклейм Merkl, прозрачные performance reports.
- Минусы: на стейблах 4.5–6.3% — **не бьёт ручной стек** (см. раздел 5); 2% performance fee + 0.4–0.5% фикс съедают апсайд; зависимость от качества Atomist; риск рецепта автоматизации (guardian-пауза замораживает депозиты и вывод).
- Роль в карте: **не источник альфы, а удобная обёртка**. Для стейблов рационально только если не хочется manually климить Merkl и ребалансить.

---

## 3. Нативные incentive-программы протоколов

| Программа | Кто платит / чем | Слой APY (2026-10-16) | Надёжность | Ёмкость |
|---|---|---|---|---|
| **Morpho rewarded vaults** (через Merkl) | эмитенты стейблов (Ethena, PayPal, Ripple, Sky/Steakhouse) платят **стейблами**; MORPHO-токен $12.7k/д | 1.9–4.9 п.п. | **высокая** (бюджет ончейн, еженедельные продления) | сотни $M на волт; $347k/день всего |
| **Aave Merit** | Aave DAO: stkAAVE+GHO, исторически ~$5M/квартал, эпохи ~2 недели | 0.5–2 п.п. оппортунистически | средняя: **на 2026-10-16 активной эпохи на Merkl не видно** (0 LIVE merit-кампаний); sGHO/stkGHO участвуют (ARFC 2026-02). Считать бонусом, не базой | весь Aave ($17B) |
| **Aave v3 сторонние кампании** (через Merkl) | спонсоры (Ethena на USDe-нетто, WMON на Monad, aBascbETH и др.) | 1.5–5 п.п. (Base WETH +5%, ETH RLUSD +3.3%, Monad +1.5–2.5) | средняя-высокая | большие |
| **Kamino сезоны + $CASH** | KMNO (сезоны ~квартальные; S4 vesting до 2026-05, S5 с 2025-11) + **$CASH initiative $540k/мес** | 2.4–5.4 п.п. (USDC 8.6% c 5.4 rewards, PYUSD 6.39% c 2.38, USDG 7.61% c 2.5) | средняя-высокая | $1.83B Kamino Lend |
| **Jupiter Lend** | сейчас **без наград** — чистая база | USDC 7.94% (спайк 8.98% из WS-9 остыл) | — | $1.33B |
| **Fluid** | GHO (Aave DAO) на ETH/Plasma; USDC на Base (Jumper) | 1.7–3.2 п.п. reward-слой | средняя: бюджеты малы ($4k/д на Merkl) | $1B |

Ключевой сдрыв: **награды Morpho — это на самом деле бюджеты эмитентов стейблов**, раздаваемые через Merkl. Жидким (USDC/стейблы) платят: Ethena, PayPal, Ripple, Sky/Steakhouse, Worldcoin (WLD), partially Gauntlet (USDG); своим токеном: MORPHO, ARB (Arbitrum DAO через Gauntlet-волты), KMNO, AERO (через Arc-кампании платят USDC), WMON.

---

## 4. Программы цепочек

| Цепочка | Что происходит (2026-10-16) | Платит чем / сколько / кому / как долго |
|---|---|---|
| **Monad** | Самая активная «новая» цепочка в Merkl: **156 кампаний, $69 911/день**. По протоколам: Aave $41k, Euler $8.5k, Morpho $7k, Curvance $5.9k, Accountable $2.2k, neverland $0.7k | **WMON** в основном (ликвидный нативный токен); Curvance платит cWMON + поинты «Bytes»; Ethena доплачивает USDe за луп на Aave. Curvance: >$750k ликвидных инсентивов в первый месяц (анонс). Pendle-Monad: 470k MON за 2 недели YT-холдерам (июль 2026). Монотематика:Monad скупает TVL нативным токеном — классический пост-mainnet сезон, идущий уже несколько месяцев |
| **Plasma** | 8 кампаний, $80 563/день, из них $69.7k — кампания #1 всего Merkl (USDe-луп на Aave) | aPlaUSDe (=USDe) за USDe-луп, еженедельно; GHO от Aave DAO/Fluid до 2026-11-05. Аирдроп XPL был в 2025; сейчас — кэшевые кампании |
| **Base** | 146 кампаний, $136 928/день; 79% — Morpho-волты (Ethena USDe-луп $50.4k + Steakhouse USDC $32.9k) | USDC/USDe/MORPHO. «Base camps» как программы нет — Base не эмитирует токен, инсентивы приходят от протоколов и эмитентов стейблов. Aerodrome-кампании на Merkl: LP токенизированных акций Coinbase платят **USDC** 25.8% APR (Revert-вельт, $2.5M TVL, до 2026-10-22) |
| **Arbitrum** | 19 кампаний, всего **$5 885/день** | STIP/LTIPP давно завершены. Остатки: Gauntlet USDG Premium Morpho-волт $3.6k/д в **ARB** (до 10-20), GMX USDG vault $1.5k/д в USDG. Вывод: цепочка для наград мертва |
| **Hyperliquid HyperEVM** | 6 кампаний, $2 102/день (ProjectX kHYPE $1.6k, HyperSwap xSWAP) | Экономика фарма — поинты и мультипликаторы эко-протоколов (HypurrFi, Kinetiq, HyperLend, Felix); **Season 2 HYPE не подтверждена** (документация Hyperliquid не показывает фазы после Nov-2024, eco.com 2026-10-06); ~33% supply HYPE зарезервировано под community rewards. Строго спекулятивно |
| **ZIGChain** | **Программа закрыта**: ZIG Rewards Program завершилась 2026-05-03 (docs.zigchain.com) | Остался $100M ecosystem fund — но для билдеров, не для фарма. Вычёркиваем |
| **Stellar** | 9 кампаний, $13 775/день | **Upshift платит USDC**: sentUSDC 8% APR ($8.8k/д, до 10-22), earnUSDC 6.2% ($4.3k/д, до 11-18). Templar — borrow-награды. Ниша с ликвидной выплатой |
| **Arc** | 14 кампаний, $3 084/день | **Aero LP платит USDC**: cirBTC-USDC 38.6% APR, WETH-USDC 33.7% (до 10-22, $2.5M TVL — ёмкость мала). Плюс Morpho платит MORPHO за borrow USDC |
| **Tempo / Katana / Mantle / World / Avalanche / Pharos** | 3.6k / 2.5k / 9.4k / 6.0k / 2.0k / 1.4k $/д | Tempo — pathUSD/OUSD hold-награды 3.3–3.6%; Mantle — Aave USDT0; World — WLD; второстепенные |

---

## 5. СБОРКА: стеки 2–3 программ на одном капитале

Принцип: один капитал = базовая ставка венья + кампания Merkl (+ нативный слой протокола/цепочки). Все цифры — нетто-APY на 2026-10-16.

### Стек 1. «Issuer-якорь»: Morpho Sentora RLUSD (Ethereum) — ЛУЧШИЙ риск-скоррекнутый
- Компоненты: base волта 4.30% + **Merkl RLUSD 2.75%** (платит Ripple-кампания $34.5k/д).
- **Итого ~7.05% на RLUSD**, выплата в RLUSD (ликвидно, Dust=0).
- Ёмкость: TVL $457M, спокойный вход/выход. Куратор Sentora.
- Надёжность: **высокая** — бюджет ончейн, еженедельные продления с 2025. Риски: depeg RLUSD (малый), конец кампании (следить за продлением), смарт-риск Morpho-волта.
- Аналоги той же конструкции: Paypal PYUSD Main 5.28% (2.31+2.97), Sentora PRIME (PYUSD) 5.70% (3.74+1.96), Flowdesk Confidential USDT 8.89% (base 3.3 + 8.9 rewards = ~12% но меньше ёмкость/кампания до 11-08).

### Стек 2. «Двойной сироп» Steakhouse High Yield USDC / SIRLOINUSDC (Base)
- Компоненты: base 3.15% + **Merkl 2.66% (64% USDC + 36% MORPHO)**.
- **Итого ~5.81% на USDC**, кампания до **2026-11-12**, $32.9k/д.
- Надёжность: **высокая** (Sky + Steakhouse; волт $463M — консенсусный институциональный вень). Морфо-токен сразу продавать.
- Тот же капитал на Robinhood Chain: Steakhouse USDG 2.92% наград + база (кампания до **июля 2027** — самая длинная), но только для юзеров Robinhood.

### Стек 3. «Ethena-машина»: USDe-луп (Plasma Aave или Base Morpho) — максимальная выплата $/день
- Plasma Aave: supply USDe + borrow USDe + loop. Награда **4.46–4.75% APR на нетто-позицию USDe** (distributionType AAVE_NET_APR, платят USDe-обёрткой), $69.7k/день только на Plasma (плюс $30k/д на Ethereum, $17k/д на Monad). База USDe-саппли ~0.3%, borrow USDe субсидирован — нетто-экономика сходится на награде. Газ на Plasma ~0.
- Base Morpho USDe/USDC 91.5%: **две камеры одновременно**: 4.75% на USDe-коллатерал (Ethena, $50.4k/д) + 2.0% на USDC supply-сторону ($21k/д, до 11-12) — полный луп (депозит USDe → borrow USDC → swap → redeposit) стекает обе + базовые ставки. Оценка нетто: **~6.5–7% на капитал при 2–3x плече** (зависит от borrow USDC ~4.5%).
- Надёжность: средняя-высокая (Ethena платит еженедельно >2 лет, но контракты 7-дневные — проверять продление). Риски: rate-риск (повтор сценария сентября-2026: рост ставки USDe-borrow убивает луп), ликвидация в Morpho-варианте (91.5% LTV!), смарт-риск моста/цепочки (Plasma).

### Стек 4. «Monad-мультистек»: Aave USDC + WMON (+ Curvance-слой)
- Ядро: Aave Monad USDC = base 4.12% + **Merkl WMON 1.5%** = 5.61% ($8.6k/д).
- На части капитала: **Curvance** wsrUSD/USDC market +1.8% cWMON ($1.6k/д) + поинты Bytes; Accountable, Euler-волты — ещё WMON-кампании ($8.5k/д). Итого по цепочке реально собрать **~5.6–6.5% + экспозиция на MON**.
- Надёжность: средняя — выплаты волатильным WMON, инфраструктура моложе, 7-дневные контракты. Это стэк для тех, кто хочет long MON: награда в MON = сатовое накопление с апсайдом.

### Стек 5. «Solana-сезон»: Kamino USDG/PYUSD + $CASH
- Kamino USDG: base 5.11% + rewards 2.50% = **7.61%**; PYUSD: 4.02%+2.38% = 6.39%; топ-USDC-пулы до 8.6% (из них 5.4 — rewards).
- Слои: база + $CASH initiative ($540k/мес) + сезонные KMNO. Альтернатива без наград: Jupiter Lend USDC **7.94% чистой базой** (лучший «наградо-независимый» флор на стейблах вообще).
- Надёжность: средняя-высокая; сезонная структура — брать фикс текущего сезона. Ёмкость: $1.8B+$1.3B.

### Пассивная обёртка: IPOR Fusion Base USDC Optimizer 6.31% (внутри — стратегии + автоклейм Merkl). Уступает стекам 1–3, но нулевой операционный труд.

---

## 6. Риски (сводно)

1. **Сроки кампаний**: большинство топ-контрактов 7-дневные с автопродлением решением спонсора. Прецедент сентября-2026 (Aave × USDe-лупы) показывает, как быстро экономика ломается rate-ходом. Правило: считать нетто с текущей базы, мониторить продление еженедельно.
2. **Волатильность токена награды**: WMON/MORPHO/ARB/KMNO — хеджировать продажей сразу после claim (claim→callback→своп прямо в Merkl).
3. **Depeg стейбла выплаты/актива**: RLUSD/PYUSD/USDG/USDe — все «новое поколение»; размер позиции в одном эмитенте ограничивать.
4. **Смарт-риск**: каждый стек добавляет венья (Morpho-волт + куратор + Merkl-контракты; лупы — плюс liquidation-логика; Monad/Plasma — плюс молодые цепочки).
5. **Механика Merkl**: proof живёт ~4 ч (перегенерация перед климом); dispute-период — защита, но оракул централизован; поинты-кампании фильтровать (Orbital Points и т.п. — номинальная цена).
6. **IPOR Fusion**: guardian-пауза замораживает депозит/вывод; performance fee 2% + 0.4-0.5% фикс; abandoned-волты (AavEthena) — проверять TVL-тренд перед входом.
7. **Гео/доступ**: часть Robinhood Chain кампаний «Robinhood Users Only».

---

## 7. Источники и даты

- Merkl API v4 `api.merkl.xyz/v4/opportunities` — собственный срез 897 LIVE-кампаний, 2026-10-16 (полные данные: `data/ws12_rewards.json`).
- Merkl docs: [Technical Overview](https://docs.merkl.xyz/merkl-mechanisms/technical-overview), [Earning/Claim](https://docs.merkl.xyz/earn-with-merkl/earning-with-merkl) — механика, dispute 1–2 ч, root ~8 ч, autoclaim, proofs ~4 ч (проверено 2026-10-16).
- IPOR: [docs.ipor.io](https://docs.ipor.io) (llms-full.txt: Atomists, Fuses, Guardian, капы комиссий 5%/50%, Merkl fuse, RewardsManager), DeFiLlama `fusion-by-ipor` пулы (2026-10-16), Reserve RFC May-2025 (0.3+0.2+2%), CryptoSlate/CryptoTicker Sep-2026 (USDe borrow 6.0–6.4% vs sUSDe 5.0%), tradingstrategy.ai (AavEthena Loop Mainnet ~$95k TVL, Aug-2026).
- Aave Merit: [aave.com/docs incentives](https://aave.com/docs/aave-v3/concepts/incentives), ARFC 16646, ARFC sGHO 24346 (Mar-2026), Oak Research Mar-2025, AInvest Apr-2025 ($6M Anti-GHO); отсутствие LIVE-эпох — срез Merkl API 2026-10-16.
- Kamino: kamino.com/season4 (vesting 2026-05-12), gov.kamino.finance Season 5 (2025-11-07), $CASH initiative; DeFiLlama kamino-lend/jupiter-lend (2026-10-16).
- Monad/Curvance: Curvance X (>$750k месяц-1), Pendle-Monad 470k MON (CoinMarketCal/TradingView Jul-2026); разбор кампаний — Merkl API.
- Hyperliquid: eco.com «HYPE Genesis Facts and Season 2 Status» (2026-10-06) — Season 2 не подтверждена; Monolith VC (~33% supply под rewards).
- ZIGChain: docs.zigchain.com — Claim Rewards (программа закрыта 2026-05-03).
- DeFiLlama yields API: morpho-blue, aave-v3, fluid-lending, ethena, kamino-lend, jupiter-lend — 2026-10-16.
