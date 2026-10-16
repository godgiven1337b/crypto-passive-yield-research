# WS14 — Малые/непопулярные протоколы: фарм-возможности vs ловушки

**Дата:** 2026-10-16
**Автор:** дефи-аналитик (WS14)
**Данные:** DefiLlama API (protocols, yields pools, charts — срез 16.10.2026), Hyperliquid API, CoinGecko, RPC Monad/Ethereum, Blockscout, DexScreener; доки/блоги протоколов, пресса (Blockworks, The Block, CoinDesk, Reuters, rekt.news). Кросс-ссылки: [ALPHA.md](../ALPHA.md), WS-9 (Solana carry), WS-13 (поинты/аирдропы).

---

## 1. Резюме (TL;DR)

Сканер дал 14 кандидатов. После проверки источника дохода, команды, аудитов и TVL-динамики:

- **1 кандидат класса (a)** «реальный доход + фарм»: **Accountable** — проценты платят именованные институциональные заёмщики (Valos, K3→Galaxy, Hyperithm), плюс живые ACC-поинты (TGE нет). Но first-loss не задокументирован → входить ограниченно.
- **5 кандидатов класса (b)** «реальные деньги, новый код — малый размер»: **Ensuro** (19.3%, страховые премии, лицензия BMA), **Veranta** (20%, реальные перп-комиссии, циклично), **Ember** (10%, кредитные буки, команда Bluefin), **Harvest→40 Acres** (27%, фандинг-бэзис — режимный всплеск), **Rhea** (12-13%, органический спрос на плечо NEAR).
- **1 кандидат класса (c)** «субсидии/эмиссии умрут»: **ZEROBASE** (7% реального бэзиса на Binance + 2% эмиссиями ZBT −93% от TGE; кастодиальный риск).
- **7 отсеяно как красный флаг (d) или шум**: **Agua** (ставка задаётся админом, `adminWithdraw` на любой адрес), **Bitway** (фиксированные 8% из непрозрачных CEX, TVL −53% за 3 недели), **Vectis** (анонимы, 0 аудитов, потери в хаке Drift), **GrowiHF** (0 аудитов, выводы заблокированы), **Morini Morpho [UNVERIFIED]** ($347K, Турция в кризисе), **Nawa/ZIGChain** (родственный кредит внутри закрывающейся экосистемы), **SharpByte** (deprecated-волт, артефакт сканера).

Общая картина: у малых протоколов «двузначные APY на стейблы» почти всегда раскладываются на (а) кредитную премию с непрозрачным first-loss, (б) торговые/страховые денежные потоки с хвостовым риском, (в) умирающие эмиссии после TGE. Готовой «высокодоходной стейбл-программы без риска» в списке нет. Лучший скорректированный спред к бенчмарку (Aave ETH USDC 3.75%, Pareto/Midas 7.4-8.1%) дают Accountable и Ensuro.

---

## 2. Сводная таблица вердиктов

APY/TVL — срез DefiLlama 16.10.2026. Классы: **(a)** реальный доход + фарм → взять; **(b)** реальные деньги, новый код → малый размер; **(c)** эмиссии/субсидии умрут → фарм только при ликвидном токене; **(d)** красный флаг → не входить. «Размер» — максимум на позицию при нашем книжном масштабе.

| # | Протокол (цепь) | APY / TVL | Источник дохода | Токен/поинты | Аудиты | TVL-тренд | Класс | Вердикт | Размер |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Accountable** (Monad) | 9.8% / $75M | Проценты заёмщиков (кредитные волты, DVN-верификация) | ACC Points, TGE нет; WMON ~0.3% | Cyfrin, Quantstamp, ABA; Cyba 03.2025: 1C+4H | $0.13M→$75M за 9 мес | **(a)** | Взять ограниченно: реальный кредитный доход + поинты; first-loss не раскрыт | $250–750K |
| 2 | Accountable (Ethereum) | 10.4–21.7% / $1–12M | Тот же + волт Morini BMMF (FX-арбитраж) | В пуле 21.7% — 11.3% платится PIKU (ликвидность $968!) | те же | Стабильно | (b) | Реальная часть — 10.4–15.6% базы; PIKU-награду считать нулём | $150–400K |
| 3 | **Ensuro** (Ethereum) | 19.3% / $1.3M | Страховые премии параметрики (Otonomi, Koala, IBISA) | Нет токена | Quantstamp 2022 (V2), SlowMist 2021; **V3 без публичного аудита** | $0.4M→$2.3M за год | **(b)** | Реальный некоррелированный доход; катастрофический хвост; кэп = ~10% пула | $50–150K |
| 4 | **Veranta** (Base, экс-Avantis) | 20.0% / $9.7M | 70% торговых комиссий перпов (LP-волт) | AVNT (TGE 09.2025, −95.6%); XP закрыты | Zellic, Zokyo, Sherlock (v1/v1.5); v2 отчёты не опубликованы | −90% от ATH $119M | **(b)** | Реальные комиссии, но циклично (01.09 было 2.9%); объёмы держатся промо | $100–250K |
| 5 | **Ember** (Sui/ETH) | 9–13% / $8.5–18M | Кредитные буки (Y10K, Hilbert) + RWA-фонды (Bitwise, R25, Tulipa) | Нет | OtterSec 10.2025 + 2 без имени | $126M→$104M (сдувание Pharos) | **(b)** | Доход реальный, но «ровно 10%» — таргет-ставка менеджера (сглаживание) | $200–500K |
| 6 | **Harvest → 40 Acres** (Base) | 27.2% / $1.8M | Фандинг перпов (дельта-нейтральный бэзис, Hyperliquid) | FARM (старый) | Harvest: PeckShield/Haechi/CertiK/Halborn 2025; 40 Acres: 2 аудита | Пул растёт с июня | **(b)**, эпизод | Режимный всплеск (база пула была 4–8%); предиктор Llama: Down 95% | $100–200K, эпизодически |
| 7 | **Rhea Lend** (NEAR, экс-Burrow) | 12.1–13.4% / $1.7M | Проценты заёмщиков (спрос на плечо в ралли NEAR) | RHEA (TGE 07.2025, −62%) | BlockSec ×2 (2022); **взлом 16.04.2026 −$18.4M** в послеаудитном коде | $97M→$197M за месяц (NEAR ×3) | (b) | Реальные ставки с NEAR-бетой; хак-история; = 96% DeFi всей цепи | $100–200K |
| 8 | **ZEROBASE** (7 сетей) | 8.8–9% / $7–17M | ~7% бэзис-трейд на Binance (zk-верификация) + 2% эмиссии ZBT | ZBT (−93% от TGE) | PeckShield + Salus (родственная!) | $543M→$61M (−89%) | **(c)** | Реальных ~7% при кастодиальном риске Binance; «двойка» истекает (кампания 60д с 14.08) | $0–100K |
| 9 | **Agua** (ETH/Monad) | 10.0% / $20.6M | **Ставка задаётся админом** (`setRate`); фактически DeFi-кэрри (Aave/Morpho/Euler/IPOR) | Нет | 1 непрозрачный скан («SSC») | Рост $5.5M→$20.6M | **(d)** | Custodial-риск: `adminWithdraw` на любой адрес, exit-fee до 100%, команда скрыта | 0 |
| 10 | **Bitway Earn** (BSC) | 8% / $22.7M | «Институциональные стратегии на CEX» — фиксированный промисс, неверифицируем | BTW (ATH 14.10.2026!) | BlockSec, Salus (контракты, не стратегия) | **−53% за 3 недели** | **(d)** | Паттерн наёмного капитала: USD1-пул слит целиком на фоне пампа токена | 0 |
| 11 | **Vectis** (ETH/Solana) | 13.7% / $1.8M | Funding/basis-арбитраж (Binance/HL/OKX >90%) | Нет | **0 аудитов** | $21M→$5.1M | **(d)** | Анонимная команда + прямые потери в хаке Drift ($286M) + цепочка кастодиев | 0 |
| 12 | **GrowiHF** (Hyperliquid) | ~10–33% / $13.7M | Квант mean-reversion PnL (APY скачет 0→120%→5%) | Нет | **0 аудитов** (при заявлении «audited») | Стабильно $13.7M | **(d)** | Подтверждено: аудитов нет; сейчас `allowDeposits=false`, `maxWithdrawable=0` | 0 |
| 13 | **Morini** [UNVERIFIED] (Morpho) | 7.4% / $0.35M | Лендинг против «emerging-market collateral»; машина — арбитраж USD/TRY, Borsa Istanbul | Нет | — (не листингован Morpho) | Стабильно крошечный | **(d)** | Турция в фондовом кризисе ($18.3B ликвидаций 09–10.2026); волт нелистингован | 0 |
| 14 | **Nawa** (ZIGChain) | 9.3% / $3.5M | Private credit / trade finance, курируется связанным ZIG Markets | NAWA (TGE нет) | Halborn/Oak по прессе; ссылка на отчёт 404 | Плоско | **(d)** | Родственный доход внутри экосистемы (Zignaly закрывает платформу); Nawa = 88% TVL цепи | 0 |
| 15 | SharpByte (Monad) | 0.7% «High Yield» | — | — | 0 | Волт deprecated | шум | Мёртвый волт (реальный нет-APY ~6.5%), исключить из сканера | 0 |

Бенчмарки на 16.10.2026 (DefiLlama): Aave USDC Ethereum 3.75%, Maple 5.23%, Fluid 5.43%, **Pareto Credit 8.06%, Midas 7.43%** (институциональный кредит), Base: Midas 6.2%.Monad: Aave USDC 5.6% (4.12+1.5 WMON), Morpho 6.3–8.1%, Euler 8.2%. Sui: Navi 5.7%, Current 6.9%. NEAR: только Rhea.

---

## 3. Детальные разборы (топ-5)

### 3.1. Accountable — кредитные волты с DVN-верификацией (класс a, лимитировано)

**Что это.** Uncollateralized Lending / YieldApp поверх Data Verification Network (DVN): пул депозитов → кредитные волты заёмщикам, данные заёмщика (позиции/дебиторка) публикуются криптографически и верифицируются сетью. Листинг DefiLlama 04.12.2025. Задеплоено в кредиты **$330M** (Monad $283M, Ethereum $21M, Arbitrum $12M), «идл» всего $2.3M — **утилизация ~99%**, всё работает.

**Кто заёмщики (главный вопрос задачи):**
- **Valos** (Хельсинки) — институциональный приватный кредит 50+ займами **tier-1 крипто-маркетмейкерам**, волт $100M/$200M cap, net 7–8%, расчёты в AUSD (Agora: резервы UST+repo, VanEck управляет, State Street кастодия, Grant Thornton аудитор). Это пул AUSD $100.5M @ 6.55%.
- **K3 Capital → Galaxy** — кредитная линия $30M (план $100M) под **7.5%** в AUSD на Monad (27.07.2026).
- **Hyperithm** (восточноазиатский трейдинг-деск) — дельта-нейтральный волт, вырос $0→$65M; шеры aHYPER используются как коллатерал во 2-м рынке Morpho Monad. Профиль и размеры совпадают с «нашим» пулом USDC $75M @ 9.5% (официального подтверждения нет).
- **Morini Capital / Piku** — BMMF (дельта-нейтральный FX-арбитраж USD/TRY), запущен 04.06.2026 через инфраструктуру Accountable = пул «21.7%» на Ethereum.
- Пермиссионлесс USDC-волт Monad — «working capital команды под дебиторку», имя заёмщика не раскрыто.

**Ставки/дефолты.** Дефолтов публично не зафиксировано (DefiLlama hacks пусто), но это отсутствие информации, а не подтверждение. **First-loss публично не задокументирован**: в docs прямо — «no platform-provided deposit insurance or loss-protection mechanism», дефолт волта «can result in partial or total loss».

**Команда/бэкинг.** CEO Wojtek Pawlowski (ex-Maven 11 / M11 Credit), основана 02.2024, BVI. Seed $2.3M (12.2024): Zee Prime, MitonC, Maven 11. **$7.5M (10.2025): Pantera Capital** + OKX Ventures, Auros, kpk, Onigiri. TrueFi DAO публиковал меморандум (11.2025).

**Аудиты.** Заявлены 6 (Cyfrin, Quantstamp, ABA); в docs — Credit Vaults v1 + re-audit Cyfrin, NAV vault. Отдельный аудит **Cyba (ABA/Silverologist) 03.2025: 1 Critical + 4 High + 3 Medium** — «resolved or acknowledged».

**Поинты/токен.** Токена нет; **ACC Points** живы с 12.2025 (начисляются от USD-стоимости депозитов, конвертация «будет объявлена») + множители NFT/тестнета. Награды в пулах: Monad — **WMON** ~0.1–0.5% (Monad Momentum, MON $0.0225, ликвиден), Ethereum-пул 21.7% — **PIKU** 11.3% (цена $0.010, ликвидность $968, объём $12/сутки — считать нулём).

**Экономика ставки.** Monad USDC 9.5% базы = кредитная премия +3–8 п.п. к обеспеченным рынкам Monad (Aave 4.1% базы) при Aave-базе Ethereum 3.75% и Pareto/Midas 7.4–8.1%. Это цена беззалогового кредита — доход реальный, риск кредитный. APY-тренд пула: 17.9% (июль) → 9.8% сейчас — reward-часть умерла, база стабильна.

**Вердикт: (a) — взять ограниченно.** Лучший кандидат списка: именованные институциональные заёмщики, верификация, Pantera, поинты. Ограничители: непрозрачный first-loss, 99% утилизация (депозиты работают без буфера), молодой протокол. Входить в Monad USDC (9.5%) и/или ETH-пулы с базой 10.4–15.6% (12.12% пул — стабильный фикс с 08.2026); пул Morini/PIKU не брать вовсе или считать PIKU нулём. **$250–750K**, kill-switch: первый дефолт любого волта, заморозка выводов, обвал WMON-наград ниже 0.2% не критичен.

### 3.2. Ensuro — параметрическое перестрахование (класс b)

**Что это.** Децентрализованный капитал для страхового риска: eTokens (Junior под партнёра / Senior диверсифицированный), премии делятся на pure premium + cost of capital для LP. **Лицензия Bermuda Monetary Authority** (digital asset + general reinsurance), V3 на Ethereum с 03–04.2026 (миграция с Polygon). Основатели — аргентинцы Марко Мирабелла (CEO) и Гильермо Нарваха (Circle Impact founder series, 2024).

**Источник дохода — премии, не субсидии.** Рископриносители: **Otonomi** (задержки грузов, $11.5M ёмкости), Koala (travel), IBISA+One Acre Fund (урожай, Кения), Rentennials (прокат LatAm), Avata, «Spot» (под него Junior 34%). Senior пул исторически **25.2% годовых за 2024–25 (Sharpe 2.13)** по докам. Свободный капитал кладётся в Aave/Morpho. TVL $0.39M→$2.28M за год, утилизация ~90%.

**Риски.** (1) **Нет публичного аудита V3/Ethereum** — Quantstamp 2022 и SlowMist 2021 покрывали V2/Polygon; (2) катастрофический хвост параметрики: серия событий ест Junior и может дотронуться Senior (за это и платят 19%); (3) APY уже сползает (30d 21.5%→19.3%, предиктор Down 82%); (4) партнёры маленькие и малопрозрачные; (5) ёмкость: пул $1.3M — нашим входом двигаем рынок, кэп ~10–15% пула.

**Вердикт: (b).** Реальный, декоррелированный от DeFi доход — редкий зверь в списке; но V3-аудит гэп + катастрофический хвост. **$50–150K максимум**, только Senior. Фактически это венчурный карман типа reUSD (WS-10), только микро-размером.

### 3.3. Veranta (экс-Avantis) — перп-декс с RWA-пивотом (класс b)

**Что это.** Perpetuals-биржа на Base (листинг DefiLlama 02.2024), ребрендинг Avantis→**Veranta** 14.09.2026, пивот на перпы к RWA (акции, FX, металлы, индексы, 100+ рынков). Фандинг $12M: seed $4M Pantera (09.2023, с Founders Fund, Galaxy, Base Ecosystem Fund), Series A $8M co-лид Founders Fund+Pantera (06.2025).

**Источник 20%.** Пул = avUSDC LP-vault (ERC-4626): волт — контрагент всех сделок, проф-маркетмейкеры держат его дельта-нейтрально; LP получают **70% opening/closing/win-fee + 100% margin-fee**, 30% идёт на buyback&burn AVNT. Эмиссий в пул нет (apyReward=0), XP-программа закрыта 28.02.2026. Экономика сходится: объёмы $13.7B/30d, fees $585K/30d (трейлинг-год $13.3M) на TVL волта $9.7M ≈ двузначный APY. Рост синхронен бета-промо (zero-fee RWA): 2.9% (01.09) → 21% (17.09) → 20% сейчас.

**Риски.** (1) Доходность = функция объёмов; при окончании промо возвращается к 3–10% (так было весь 2025); (2) хвост LP: выплаты трейдерам сверх буфера бьют по телу волта; (3) AVNT −95.6% от ATH ($2.64→$0.116), FDV $117M; (4) **аудиты v2 (Guardian/Sherlock/Zellic) «будут опубликованы» — их всё ещё нет**; (5) TVL −90% от ATH $119M (ноябрь 2025): история доходности была подкарплена XP-инсентивами (в 2024 APY доходил до 157%).

**Вердикт: (b).** Честные комиссионные, но режимные. Входить с ожиданием нормализации к 8–12%; **$100–250K**; kill-switch: 30d объёмы ×0.5, публикация v2-аудитов с критами.

### 3.4. Ember — маркетплейс кредитных буков от команды Bluefin (класс b)

**Что это.** «Onchain Capital Markets»: инфраструктура запуска чужих продуктов + собственные агрегационные волты. Запущен 09.2025 **командой Bluewater (строители перп-декса Bluefin)** — подтверждено Sui Network, CryptoRank, миграцией легаси-волтов Bluefin и зеркалом GitHub org fireflyprotocol. До «пивота в капитал-маркетс» был yield-агрегатором на Sui (NAVI/Suilend/Cetus). Лондон, ~7 сотрудников, со-фаундер Ibra Barbery; публичных раундов нет.

**Куда идёт доход.** Сторонние Vault Managers: **Y10K Capital USD** (ETH, $18M @ 9%) — кредитная бука; **Hilbert hLEND** — сверхобеспеченный кредит (+200 б.п. маркетинговый буст 3 мес, до $15M — Ember добавил $1M своих); **Bitwise Premium+** ($14.9M @ 5.6%); **R25 Treasury** (Sui, 8% + 4% в SUI); Tulipa ($1.6M @ 12.9%); Zodiac Treasury Plus (Monad, 12.6%). «Ember Earn» 10.03% — **таргет-ставка менеджера, ровная по построению** (сглаживание), не мгновенный ончейн-захват.

**Аудиты/токен.** OtterSec (10.2025) + отчёт 12.2025 (аудитор не назван) + отчёт 10.2026 (Atomic Liquidity Vault, аудитор не извлекается). Токена и поинтов нет.

**TVL.** $126M (22.07) → $103.6M: сдувание Pharos-кампании ($61.8M→$14.7M, включая −$16M за последние 2 дня) и разовый вывод $21.8M на Ethereum в июне; Sui/Base растут.

**Вердикт: (b).** Реальные кредитные/RWA-потоки с платформенным риском концентрации на одной команде и молодых эмитентах (Y10K, Enigma, Tulipa). Предпочесть пулы с идентифицируемым эмитентом (Bitwise — ок 5.6%, Y10K 9% — если принять кредитный риск Buchner-буквы). **$200–500K** суммарно.

### 3.5. Harvest Finance → 40 Acres: 27% как режимный всплеск фандинга (класс b, эпизод)

**Что это.** Пул 27.17% на Base — не лендинг и не эмиссии: vault Harvest, размещающий USDC в **40 Acres** (40acres.finance, TVL $49.6M) — дельта-нейтральный basis-трейдинг (шорт-перпы, площадка Hyperliquid), доход = фандинг. Harvest — старый агрегатор (аудиты PeckShield/Haechi/CertiK 2020, Halborn 01.2025 по Base-контрактам; инцидент 26.10.2020 $24M — 6 лет назад; timelock вывода 12ч).

**Стабильность.** Нет: 2025 — 10–16%, декабрь–май — 4–8%, подъём с июня (23.5% 12.06), пик 32.9% (07.10), сейчас 27.2%. apyPct30D = −103% (месяц назад ~55%), предиктор Llama **Down с вероятностью 95% (conf 3)**. Это тот же профиль, что керри-всплеск Jupiter (WS-9): реальный поток, но недельно-месячный режим.

**Риски.** Отрицательный фандинг (стратегия теряет), контракты 40 Acres, площадочный риск Hyperliquid, композитность. Соседние USDC-волты Harvest на Base дают 7–10% — ориентир «нормы».

**Вердикт: (b)-эпизод.** Взять маленько на пик фандинга с планом выхода при нормализации (<12%) — $100–200K, горизонт недели, не «парковка».

---

## 4. Красные флаги (не входить)

### 4.1. Agua — «административные 10%» и полный custodial-контроль
Ставка 10.001% не сломана ни разу с 13.08.2026, потому что это **не рыночный поток**: единая переменная `cumulativeRateFactor`, админ вызывает `setRate(uint256)`; «Yield is not distributed as new token mints» (docs.tropicalwater.xyz). Реальный носитель — аллокации в Aave/Morpho/Euler/IPOR + «leveraged looping, basis, carry» — при базовых ставках 4–8% чистая десятка правдоподобна только с левереджем. Управление: ADMIN_ROLE = MPC 3/5, **`adminWithdraw(ASSET, balanceOf(vault), anyAddress)`** — в доках: «Users of this vault unconditionally trust the ADMIN_ROLE key holder». `earlyRedemptionFee` 5% → до **100%**. Юрлицо Tropical Water Management Corp. (оболочка на аппе Reservoir/Fortunafi-контур), ответственность по Terms **US$100**, команда не раскрыта, шеры не дают прав на активы. Аудит — один 10MB-скан без текстового слоя («SSC»). Monad-волт запущен 14.10.2026, Curvance уже оборачивает aguaUSDCgc ($9.1M, APY 0). **Класс (d): не входить** — это «trusted yield» в самой буквальной форме при ненужном нам риске ключа.

### 4.2. Bitway Earn — фиксированный промисс при исходе капитала
8% «flat» (30d mean ровно 8.0 — ставка административная) из «институциональных стратегий на CEX» под «институциональной кастодией»; никакой верификации трейдов (в отличие от ZEROBASE). Экс-Side Protocol (L1-пивот), раунды ~$5.4M (TRON DAO Ventures, HTX Ventures), FDV токена BTW $18–27B (~5000x к привлечённому), токен на ATH **ровно 14.10.2026**, при этом TVL **−53% за 3 недели**: USD1-пул слит целиком ($10.5M→$0.02M), U −63%, USDT −23%. Классический паттерн наёмного капитала, ушедшего после промо. Аудиты BlockSec/Salus — контракты, не стратегия. **(d)**.

### 4.3. Vectis Finance — анонимы + 0 аудитов + уже сгорели в Drift
Дельта-нейтральный funding/basis-арбитраж, >90% капитала на Binance/Hyperliquid/OKX (Ceffu/Cobo), ETH-волт — на инфраструктуре Accountable (VaaS). Команда анонимна, аудитов 0 (на сайте — слова «audited» без аудитора). TVL $21.2M→$5.1M: главная причина — **хак Drift 01.04.2026 ($286M, DPRK)**: у Vectis есть официальный портал «Drift Recovery Token Claim» и пометка «UltraX Arbitrage — Affected» — прямые потери LP. Новый ETH-пул (с 08–09.10.2026) — рестарт после инцидента. 13.7% не покрывают хвост безымянной команды. **(d)**.

### 4.4. GrowiHF — подтверждение прежнего диагноза
Аудитов **по-прежнему 0** (DefiLlama; на growi.fi «audited» без отчёта). Hyperliquid API (16.10): APR 30d 32.98%, лидер-фонд 5%, НО **allowDeposits=false и maxWithdrawable=0** — мгновенный вывод закрыт. Серии дневного APY 0→50–120→5% — это PnL mean-reversion, «29%» — сглаживание. Контекст: 85% H-vault'ов Hyperliquid убыточны (по их же Medium), кейс HLP0 ($29M юзер-фондов уведено в другие цепи). **(d): не добавлять**, следить за разблокировкой выводов.

### 4.5. Morini [UNVERIFIED] на Morpho — Турция в разгар кризиса
Morini Capital — эмерджент-маркет менеджер: арбитраж USD/TRY между Binance TR/OKX TR и фиат-рельсами, керри TRY, бэзис Borsa Istanbul. Morpho-волт «USDC Emerging Yield» (V2.0, 0x58E0...14d6): net 7.43%, **TVL $346.7K**, не листингован Morpho (потому UNVERIFIED), fee 10% performance. Старшие продукты: FXArbUSDTRY ~24.8% ожид. (через Accountable — пул «21.7%» с PIKU-наградой), StockMarketTRBasis Senior на Royco 25.4% ($802K). Красный флаг контекста: **Турция с 09.2026 в фондовом кризисе** — регулятор ликвидирует 131 инвестфонд на ~$18.3B после понци-схем (Reuters 02.10.2026). Доходность реальна ровно до контрагентского сбоя турецких бирж/банков. Мелкий размер + нелистингованность = **(d)** для книжки; любопытный нишевый сторителлинг, не позиция.

### 4.6. Nawa / ZIGChain — родственный кредит в закрывающейся экосистеме
ZIGChain = Cosmos SDK L1 c EVM от Zignaly ($100M ecosystem fund с DWF Labs, 04.2024; mainnet beta 06.2025). «Настоящего» DeFi TVL ~$4.3M, Nawa — $3.5M (88%). Nawa — шариат-волты (сертификат Amanie Advisors, 04.2025), доход из private credit / trade finance, **курируется ZIG Markets — структурно связанной стороной** (BD/risk-ветка Zignaly). Независимой верификации денежного потока нет; ссылка на аудит с DefiLlama отдаёт 404; Zignaly в 2026 объявил о закрытии трейдинг-платформы и пивоте в «ZIG Finance». 9.3% не компенсируют связанность + цепочечный риск. **(d)**.

### 4.7. SharpByte — артефакт сканера
Волт «USDC High Yield» на Monad помечен Morpho как **DEPRECATED**, реальный нет-APY ~6.5% ($506K). 0.7% в сканере — артефакт расчёта по share price мёртвого волта. Ethereum-волт SharpByte — $0 TVL, deposits disabled. Исключить из скоринга как шум.

---

## 5. Экосистемы

### 5.1. Monad (TVL DeFi ~$1.0B / $1.9B c займами, стейблы $684M)
- **Monad Momentum** (Foundation): матчинг инцентивов команд до 1:1 в MON — источник WMON-наград в Aave/Morpho/Curvance/Accountable. Монета MON $0.0225 (−54% от ATH 26.11.2025), в обращении 11.8B из 100.7B (12%) — **фарм-ценность инцентивов низкая и тает**; пост-TGE поинтовой программы фонда нет.
- **Кто платит за USDC** (16.10.2026): Aave v3 USDC **5.6%** (4.12 база + 1.5 WMON, $17.2M; отдельный SYRUPUSDC-пул $157M даёт 1.1% — не путать); Morpho 6.3–8.1% (+0.7–1.4 WMON); Euler v2 8.2%; **Curvance 6.1–7.3%** (4.3–7.3 базы + 1.35–1.8 наград; Bytes-поинты продолжаются, токена нет); Agua 10% (см. красный флаг); Accountable 9.5–12%.
- **Curvance**: жив ($101.6M TVL на Monad, общие liquid incentives >$750K за первый месяц, эпохи 2 недели), но по USDC даёт обычные 6–9%; интересен скорее через Bytes-поинты (кросс-ссылка WS-13), через оборачивание Agua (AGUAUSDCGC $9.1M — APY сейчас 0) заходить не стоит по 4.1.
- **AUSD (Agora)** — крупнейший стейбл Monad (~$100M+): резервы UST+overnight repo, VanEck/State Street/Grant Thornton, предварительное одобрение OCC. Крупнейшие AUSD-пулы — волты Accountable (Valos $100.5M @ 6.55%, K3→Galaxy $30.8M @ 6.74%).
- Kinetiq — НЕ Monad (это Hyperliquid LST, kHYPE $850M); «Meteor» ушёл туда же. Не искать на Monad программы Kinetiq.

### 5.2. ZIGChain
Cosmos SDK L1 от Zignaly, газ ZIG ($0.054, FDV $105M). Весь «DeFi» — LST Valdora ($78M) + $4.3M протоколов; Nawa — 88% последнего. Причина «9.3% за USDC» — бутстрап экосистемы: доход заявлен как реальный (private credit/trade finance), но курируется связанным ZIG Markets внутри закрытого контура, а Zignaly сворачивает основную платформу. Ставка не переносится на другой размер: при $10M+ депозитов этот рынок не расширяется. Смотреть, не входить.

### 5.3. NEAR (Rhea)
Rhea Lend (Burrow+Ref слияние 02.2025, TGE RHEA 07.2025, $0.075, −62% от ATH) — **96% всего DeFi TVL NEAR** ($196.5M supply + LST rNEAR + DEX). Взлёт TVL за месяц — переоценка NEAR (×3 с августа до $5.01 на AI-нарративе + NEAR Intents-инсентивы + сокращение эмиссии), а не приток долларов. Ставки USDC/USDT 12–13.4% — органический спрос на плечо в ралли; reward-APY = 0. Хак 16.04.2026 (−$18.4M, фейковые NEP-141 через баг валидации в margin V2, **вышедшей после обоих аудитов BlockSec**; частично компенсировано). Это ставка на продолжение NEAR-ралли: при развороте ставки и TVL сожмутся синхронно. Малый размер или мимо.

### 5.4. Sui (Ember)
База Ember — команда Bluefin/Bluewater; Sui-ветка стабильна $29–34M. Бенчмарки USDC на Sui: Navi 5.7%, Current 6.9% — пулы Ember 10–12% это премия за кредитную книгу/RWA менеджера, а не субсидия SUI (SUI платится только в одном пуле R25). Часть легаси-волтов Bluefin мигрировала в Ember — институциональная преемственность есть, токена/поинтов нет.

---

## 6. Поинты/аирдроп-потенциал (пересечение с WS-13)

| Протокол | Поинты | Токен | Статус | Оценка аирдроп-потенциала |
|---|---|---|---|---|
| **Accountable** | **ACC Points** (с 12.2025, множители NFT 1.2–1.4x) | нет | Конвертация не объявлена | **Высокий**: Pantera-бэкинг, $330M выдано, поинты = «future reward allocation» |
| **Curvance** (Monad-контекст) | Bytes | CDT нет TGE | Эпохи продолжаются | Средний: TVL $100M+, но по USDC ставки обычные |
| Ember | нет | нет | — | Низкий (команда уже пережила TGE Bluefin) |
| Nawa | нет | NAWA, TGE нет | — | Низкий (закрытый контур ZIG) |
| Ensuro / Agua / Vectis / Morini / SharpByte | нет | нет | — | Нет фарма-ценности |

Итого из 15 позиций **неназванный токен с внятной гипотезой аирдропа — у 2 (Accountable, Curvance)**; у остальных либо токен уже есть (Veranta/AVNT, Rhea/RHEA, ZEROBASE/ZBT, Bitway/BTW, Harvest/FARM), либо поинтов нет вовсе.

---

## 7. Методология и что проверено

- Доходность: разбивка apyBase/apyReward по каждому пулу + 7/30/90d статистика (mean/min/max) из yields.llama.fi chart; reward-токены идентифицированы адресно (RPC eth_call symbol → WMON; PIKU через Blockscout; ликвидность через DexScreener).
- TVL-динамика: protocol-level история (365/180/90/30 дней) + pool-level; для Accountable сверена методология tvl/borrowed ($330M deployed, утилизация 99%).
- «Плоские» ставки (Agua 10.001%, Bitway 8.0, ZEROBASE 9.0) трактованы как административные — подтверждено доками (Agua `setRate`) и историей (нулевая дисперсия).
- Качественные факты (команды, раунды, аудиты, инциденты) — только с первоисточников, приведённых ниже; конфликт «сайт заявляет 6 аудитов» vs «DefiLlama 2» отражён как есть.
- Данные DefiLlama raises API недоступны (платный тариф) — фандинг из прессы.

## 8. Источники (ключевые, с датами)

- DefiLlama API: protocol/yields/chart эндпоинты, срез 16.10.2026; pools (accountable, ember-protocol, veranta, ensuro, vectis-finance, rhea-lend, agua, zerobase-cedefi, nawa-protocol, bitway-earn, harvest-finance, growihf, royco-v2, morpho-blue, curvance, aave-v3).
- Accountable: Blockworks 29.10.2025 (раунд Pantera $7.5M); The Defiant 29.10.2025; docs.accountable.capital (acc-points, multipliers, audits, «no insurance»); valos.io 17.02.2026 + monad.xyz/blog 07.05.2026 (волт Valos $100M); GlobeNewswire 27.07.2026 (K3→Galaxy $30M @ 7.5%); accountabledata.substack.com 30.03.2026 (Hyperithm $65M); Cyba Blockchain Security, отчёт 25.04.2025 (1C+4H); piku.co 04.06.2026 (Morini vault suite); RPC Monad (символ WMON), Blockscout (PIKU), DexScreener (PIKU: liq $968; WMON: liq $1.2M).
- Monad: monad.xyz/blog (Monad Momentum 18.09.2025; Aave live 02.07.2026; ecosystem highlights 01.10.2026; Early Investor Liquidity Program 17.08.2026); Curvance X 25.11.2025 + docs.curvance.com; CoinGecko MON 16.10.2026.
- Ember: defillama.com/protocol/ember-protocol (листинг 17.09.2025); x.com/SuiNetwork 09.2025 («Ember vaults with Bluewater»); learn.bluefin.io (миграция легаси-волтов); github.com/fireflyprotocol; ember.so/earn/pALPHA; finance.yahoo.com 15.09.2026 (Hilbert×Ember, +200 bps); caplight.com (Лондон, 2025); github.com/ember-protocol/Ember-Vaults/audits (OtterSec 10.2025).
- Agua: docs.tropicalwater.xyz (Terms v1.0 11.06.2026; /architecture/yield-mechanics; /architecture/admin-operations; /architecture/security-and-trust-model; audits); app.reservoir.xyz.
- Veranta: veranta.xyz/blog 14.09.2026 (ребрендинг); techcrunch.com 26.09.2023 (seed $4M Pantera); theblock.co 03.06.2025 (Series A $8M Founders Fund+Pantera); docs.veranta.xyz (avUSDC LP-vault, XP ended 28.02.2026, AVNT token, audits); CoinGecko AVNT 16.10.2026; DefiLlama volumes/fees 16.10.2026.
- Ensuro: docs.ensuro.co (pools overview, «25.2% annualized 2024–25»); circle.com/blog 26.08.2024 (фаундеры); otonomi.medium.com ($11.5M capacity); DefiLlama hallmark «Ensuro V3 Launch» 18.03.2026; аудиты Quantstamp 09.11.2022 / SlowMist 29.09.2021.
- Vectis: docs.vectis.finance; chainalysis.com 09.04.2026 + elliptic.co 02.04.2026 (хак Drift $286M); vectis.finance/recovery-token.
- Rhea: near.org/blog (RHEA TGE 07.2025); guide.rhea.finance (white paper); rekt.news/rhea-finance-rekt (−$18.4M, 16.04.2026); github.com/NeardeFi/burrowland (BlockSec ×2); CoinGecko RHEA; fool.com 12.10.2026 (NEAR +16% за уик-энд).
- ZEROBASE: CoinGecko ZBT (TGE 17.10.2025, ATH $1.025, сейчас $0.072); binance.com 23.09.2025 (pre-TGE event) + Binance Booster S2; bitget.com/academy (механика ZBT/CEFFU); peckshield + salusec GitHub (аудиты); hindenrank.com 15.02.2026 (Grade C 44/100); CMC 14.08.2026 (zkStaking кампания 60д).
- Bitway: docs.bitway.com (how-does-it-work, points); DefiLlama adapter (CORE_ALPHA/ABSOLUTE_RETURN побуквенно); Gate 14.07.2026; анлок 02.11.2026 (101.6M BTW).
- Harvest/40 Acres: DefiLlama poolMeta «40 Acres»; 40acres.finance; docs.harvest.finance/other/security/audites.md (Halborn 01.2025); usd.net (gross 32.93/net 23.94, C58); предиктор Llama (Down 95%, conf 3).
- GrowiHF: Hyperliquid API 16.10.2026 (APR 30d 32.98%, allowDeposits=false, maxWithdrawable=0); growi.fi; thedefiant.io 07.08.2025 (кейс HLP0); DefiLlama (audits: 0).
- Morini: app.morpho.org (vault 0x58E0...14d6, UNVERIFIED, net 7.43%, $346.7K); morini.capital; rwa.xyz; piku.co 04.06.2026; royco (TR Basis Senior 25.4%); turkishminute.com 18.09.2026 + reuters.com 02.10.2026 (ликвидация фондов $18.3B).
- ZIGChain/Nawa: coindesk.com 17.04.2024 ($100M fund, DWF Labs); chainwire 29.04.2025 (Amanie Shariah); thearmchairtrader.com 25.11.2025; iq.wiki; zignaly.com («Nine Years of Building…» — закрытие платформы); DefiLlama nawa (ссылка на аудит 404).
- SharpByte: app.morpho.org (vault 0xf57E...542D, DEPRECATED); defillama.com/protocol/sharpbyte.

**Не проверяемо/не найдено** (честные пробелы): заёмщик пула $75M USDC (вероятно Hyperithm — не подтверждено); first-loss у волтов Valos/K3; конвертация ACC-поинтов; аудитор отчётов Ember 12.2025 и 10.2026; юрисдикция Bitway; итог меморандума TrueFi по Accountable.
