# WS-8. Альфа-аномалии: stUSDS (Sky) + Aave Base / Aave v4 Horizon

> Дата исследования: **2026-10-16**. Рыночные данные — снапшоты DefiLlama Yields API (16:01 UTC), app.sky.money, Aavescan, Merkl API на эту дату.
> Машинно-читаемый дамп: `data/ws8_alpha_sky.json`.
> Аномалия на входе: stUSDS 5.64% base APY / TVL $178.5M против sUSDS 3.80% / $4.96B (+184 б.п.) при одном эмитенте; sDAI 1.25%.

---

## 1. Executive summary

1. **stUSDS — это НЕ ещё одна обёртка Savings Rate, а «risk capital» токен.** Первый «Expert token» Sky Protocol: депозит USDS идёт в обособленный пул, из которого **исключительно** кредитуются заёмщики, ломящие SKY в Lockstake Engine (LSE). Ставка: `stUSDS Rate = U × (SKY Borrow Rate − 0.10%) + (1−U) × SSR`, таргет утилизации ~90%. Запущен **14–16 октября 2025** (анонсы Sky Ecosystem и Spark), т.е. продукту ровно ~1 год.
2. **+184 б.п. — это не launch-инсентивы и не эмиссии.** DefiLlama: reward-компонента = 0, весь доход — base rate. Премия = реальный платёжный спрос SKY-стейкеров (~6.42% годовых, которые они платят за ликвидность под залоченный SKY стоимостью ~$1.21B при фарм-APR ~6.6%). Даты окончания у премии **нет** — она существует, пока живёт Lockstake-заимствование; с 13 авг 2026 (Stage 2) фарм-награды финансируются выручкой протокола (22.5% revenue → байбеки SKY, 22.5% → USDS Staking Rewards), что делает спрос на заём более устойчивым, но и более медленно растущим.
3. **Премия устойчива, но сжимается:** ~+300 б.п. (июль 2026) → +160–185 б.п. (октябрь). Сжатие — следствие срезания эмиссий SKY (мар-2026: −838M SKY/180д; апр-2026: −50% funding). С октября 2026 темп сжатия стабилизировался (SSR сами подняли 3.52→3.80).
4. **Главные ограничения — не ставка, а выход и «хвост»:** redemption ограничен idle-ликвидностью (~10% TVL при таргетной утилизации 90%; фактическая оценка ~73% → ~$48M); Curve USDS-stUSDS — всего $2.4M; формальной exit queue и lockup **нет**. Держатель stUSDS — это страховой капитал LSE: bad debt заёмщиков и governance-slashing списываются прямо с баланса vault (механизм `cut`).
5. **Ёмкость для нас: $5–20M** без разрушения премии (TVL сам откалибровался в коридор 175–215M; приток депозитов снижает утилизацию → авто-кипер режет ставки). Realized yield ~5.0–5.6% годовых против 3.8% в sUSDS при входе/выходе 1:1 через mint/redeem (только газ).
6. **Вердикт stUSDS: структурная альфа** (платёжный спрос + revenue-backed экономика), а не фарм — но с кредитно-governance хвостом и тонким выходом. Риск-скор 5/10. p(потеря ≥2/3 премии за 6 мес) ≈ 35–45%; p(обнуления премии) ≈ 15%.
7. **Aave v3 Base USDC 8.82%** — фарм: база 3.81–3.9% ($188M резерва, U=89.5%) + Merkl-кампания в **нативном USDC** («Lend USDC on Aave — Jumper bridgers»): бюджет ~$361/день, окно 14–28 окт 2026, ограничение по адресам (нужно bridging через Jumper). Токен не дампится (это USDC), но программа недельно-пульсовая. Без eligibility реальная ставка ~3.8–6.4%.
8. **Aave v4 Horizon USDC 8.79%** — отдельный лицензируемый RWA-инстанс Aave (залог — permissioned токенизированные MMF; permissionless поставка стейблов; заёмщики — институционалы). Трекаемый DefiLlama USDC-пул микроскопический ($0.2–0.5M), APY гуляет 4.6–9.6% из-за недельных Merkl-кампаний (net-lending корзины 500–600% APR на «net»-позициях). TVL всего Horizon ~$390M (сен-2026), цель 2026 — $1B+. Ставка местами структурно выше рынка (институциональный спрос на заём), но ёмкость конкретно USDC-резерва мала.

---

## 2. stUSDS: механика (задача 1)

### 2.1. Кто эмитент и что это

- **Эмитент — Sky Protocol (core), не Spark.** Официальная страница: https://sky.money/stusds («stUSDS: High-Performance Risk Capital — Fuel the SKY Staking Engine»). Spark лишь размещает продукт в своём аппе; в твиттере Spark прямо: «This product is offered by Sky, not Spark» (https://x.com/sparkdotfi/status/1978115508970172826, окт-2025). Техдоки: https://developers.skyeco.com/protocol/tokens/stusds; контракт: https://github.com/sky-ecosystem/stusds.
- **Запуск: середина октября 2025.** Анонсы: Sky Ecosystem (https://x.com/SkyEcosystem/status/1978852084838510990) и Spark (https://x.com/sparkdotfi/status/1978115496575934756), оба ~14–16 окт 2025. Обзор Stablewatch опубликован 14 окт 2025 (https://ghostadmin.stablewatch.io/stusds-sky-protocol-risk-capital-token).
- **Механика:** depositor кладёт USDS → получает stUSDS (ERC-4626 + ERC-20 c Permit, UUPS-прокси ERC-1967/1822, AGPL-3.0). Эти USDS образуют **сегрегированный пул**, из которого могут занимать **только** пользователи, залочившие SKY в Lockstake Engine (urn-хранилища, непередаваемые; внутренний токен LSSKY). Кодовая база — потомок SavingsDai (hexonaut) и Pot (MakerDAO devs), т.е. то же семейство, что sDAI/sUSDS.
- **Бэкинг:** 100% USDS-денежный пул (не RWA напрямую!); экспозиция — на заёмы против SKY-залога. «Maximum borrowable USDS = Total USDS currently held in the stUSDS contract» — занять больше депозитов физически нельзя.

### 2.2. Чем отличается от sUSDS / sDAI

| | sUSDS | stUSDS | sDAI |
|---|---|---|---|
| Ставка | SSR (администрируемая, сейчас 3.80%) | U×(SKY Borrow Rate −0.10%) + (1−U)×SSR (сейчас 5.64%) | DSR (1.25%, удерживается ниже SSR принудительно) |
| Источник дохода | Сеньораж протокола (general) | Платежи LSE-заёмщиков + SSR на idle | Сеньораж (legacy, занижен для миграции DAI→USDS) |
| Риск | Protocol-level Sky | + SKY-цена, bad debt LSE, slashing, liquidity-constrained exit | Protocol-level (legacy) |
| Выход | Мгновенный, без зависимости от утилизации (Eco: «instant withdrawal, no utilization dependency») | Ограничен idle-ликвидностью конвертера | Мгновенный |
| TVL | $4.96B | $178.5M | $200.7M |
| Награды/инсентивы | нет (в Sky core) | нет (0% reward по DefiLlama); SPK-инсентивы Spark — только на периферии (Curve/Morpho) | нет |

DSR/SSR-развязка: исторически DSR держали на ~1 п.п. ниже SSR (пример: SSR 12.5% / DSR 11.5%, дек-2024, https://x.com/SkyEcosystem/status/1865543062857941272); сейчас зазор раздут до ~2.55 п.п. (1.25% vs 3.80%) — политика выдавливания DAI→USDS.

### 2.3. Сеттинг ставок: SPBEAM → stUSDS Keeper

- Ставки (supply rate и SKY Borrow Rate) ставятся через `file()` в StUsdsRateSetter, логика на базе **SPBEAM** (Stability Parameter Bounded External Access Module; https://github.com/sky-ecosystem/sp-beam): границы max/min/step, timelock `tau`, circuit-breaker SPBEAMMom. Максимальная ставка — 50% (модуль Conv).
- Алгоритм целится в **утилизацию ~90%**: ниже таргета — borrow rate снижается (привлечь заёмщиков), выше — растёт (сохранить выходную ликвидность) (Stablewatch; форумное упоминание в RFC SummerFi: «target utilization near 90%»).
- **8 октября 2026 — executive vote «stUSDS Keeper launch»** (https://financial.skyeco.com/governance/spells/2026/...-stusds-keeper-launch.md): авторизован автоматический Keeper (`kiss 0x068F9c8F33E13c18B852877A5D8Ec61504971376` на STUSDS_RATE_SETTER), подключён STUSDS_VALUE_REGISTRY (`0xcDb55A799A9B9eAe22Ed0E13037bb6D2E3f1d080`), шаг изменения ставки урезан `stepStrBps/stepDutyBps 1500 → 500` (макс. ±5% абсолютных за обновление). Atlas-правка от 5 окт 2026 заменила формулы ручного сеттинга автоматикой (голосование прошло 9 окт). Ставка стала ещё «автоматичнее» — governance-риск сеттинга снижен, но и гибкость спекулятивного сеттинга исчезла.

---

## 3. Откуда +184 б.п. (задача 2)

### 3.1. Это НЕ launch-инсентивы

- DefiLlama: stUSDS `apyReward = None` — вся 5.64% это base rate. Никаких токен-наград держателю не платится.
- Премия = арифметика формулы: при SSR 3.80%, borrow rate ~6.42% (app.sky.money/stake, окт-2026) и утилизации U: `rate = U×6.32% + (1−U)×3.80%`. При U=73% → 5.64% (расчётная фактическая утилизация; таргет 90% выше — возможно, снапшоты ставок/SSR разнесены во времени). 0.10% accessibility reward (0.05% интеграторам + 0.05% Star Management) несут **заёмщики**, не поставщики.

### 3.2. Кто и почему платит 6.4%

- Заёмщики — SKY-холдеры, залочившие SKY в LSE (текущий TVL SKY-стейкинга ≈ $1.21B, ~17.37B SKY; фарм-APR ~6.6% по app.sky.money). Их мотив: (а) получить ликвидность, не продавая SKY (SKY в lockup); (б) леверидж-петля «lock SKY → borrow USDS → buy SKY → lock». При фарме 6.6% и заёме 6.42% маржа петли почти нулевая — т.е. сейчас это в основном спрос на ликвидность, а не агрессивный левередж (в 2025-м, при более высоком фарм-APR, петля была жиже и ставка stUSDS выше).
- Эволюция финансирования фарм-наград (ключ к durability):
  - **мар-2026**: governance срезал эмиссии — ~838M SKY на 180 дней (~$114.5M), байбеки усилены; SKY +10% на новости (CoinDesk 05.03.2026).
  - **апр-2026**: нормализация LSSKY→SKY-наград до «Three-Stage Staking Rewards Framework» (50% прежнего funding).
  - **13 авг-2026, Stage 2**: награды переведены на revenue-funding — каждый месячный settlement: 22.5% выручки → байбеки SKY для стейкинг-наград, 22.5% → USDS Staking Rewards, 5% → buy-and-burn SKY, 50% → Surplus Buffer; байбеки до $300k USDS/день.
  - **8 окт-2026**: вестинг LSSKY→SKY обновлён — 99,525,882 SKY на 90 дней; запущен stUSDS Keeper.
- Итог: премия стUSDS = производная от (фарм-APR SKY) × (объём залоченного SKY) × (готовность платить за ликвидность). Фарм-APR теперь привязан к выручке Sky (~$200M/год по DefiLlama protocol page), а не к печатному станку.

### 3.3. История премии (DefiLlama, месячные средние)

| Месяц | stUSDS | sUSDS (SSR) | Премия |
|---|---|---|---|
| июл-2026 | 6.62% | 3.58% | **+304 б.п.** |
| авг-2026 | 5.82% | 3.52% | +230 б.п. |
| сен-2026 | 5.18% | 3.59% | +159 б.п. |
| окт-2026 (16-е) | 5.64% | 3.80% | **+184 б.п.** |

TVL при этом держится 175–215M весь период (пик ~215M в сен, сейчас 178M) — рынок сам откалибровал размер. Даты окончания премии **не существует**; сценарий её смерти — обвал SKY (падение залога и фарма) или governance-отказ от LSE-экономики.

---

## 4. Ограничения и выход (задача 3)

- **Lockup: нет.** Withdraw можно инициировать в любой момент (sky.money/stusds). Формальной очереди (exit queue) тоже нет — но:
- **Liquidity-constrained redemption.** Redeemable ограничен «withdrawable amount» = total value − долг stake engine − USDS в аукционе (README stUSDS). При таргетной утилизации 90% мгновенно доступно ~10% TVL (~$18M; при фактической ~73% — до ~$48M). Во время стартового fill-up фазы выводы были полностью заблокированы (исторический факт из README). В стресс выход = ждать возвратов заёмщиков/новых депозитов или продавать с дисконтом.
- **Кап/лимит депозита:** глобальный supply cap и max debt ceiling есть (ставятся через Rate Setter, governance; см. GitHub). Текущие значения нигде не публикуются; судя по 4-месячному плато TVL 175–215M, каппинг не активен — ограничение действует через ставку (приток → утилизация ↓ → кильватер снижает ставку).
- **Вторичный выход:**
  - Curve USDS-stUSDS: TVL **$2.44M**, APY 4.57% (2.65 base + 1.92 награда **SPK** 0xdC035D45d973E3EC169d2276DDab16f1e407384F — стимулы Spark); +Beefy-обёртка того же пула $2.2M. Глубина ~$1.2M на сторону → для $1M+ выход уже с проскальзыванием.
  - Morpho: stUSDS как залог — «Sky Money USDS Flagship» ($40.1M, 5.09% = 0.73 base + 4.36 SPK) и «Sky Money USDC Risk Capital» ($7.7M, 3.89%); мягкий выход через займ USDS/USDC под stUSDS.
  - Pendle PT-stUSDS рынка **нет** (проверено по yields-базе 16.10.2026) — зафиксировать премию через PT нельзя.

---

## 5. Риски (задача 4)

1. **Смарт-контракт:** код новый, но из зрелого семейства (SavingsDai/Pot). Аудиты: **Trail of Bits — stUSDS, 18.08.2025 и 10.04.2026**; **Cantina — Lockstake, 28.07–08.08.2025**; **ChainSecurity — Lockstake, 26.09.2025**; ранний LSE — Cantina, июнь-2024. Реестр: developers.skyeco.com/security/security-measures/overview. Immunefi bug bounty активен (обновлён 19.09.2026). UUPS-прокси — upgradeable.
2. **Экономический хвост (главный отличитель от sUSDS):** держатель — страховой капитал LSE. Bad debt заёмщиков (SKY-обвал, провалы ликвидаций) списывается с vault через `cut`; governance может слэшить напрямую; README прямо предупреждает о run-risk и depeg-риске для интеграций. Буфер: совокупный LTV сейчас ~11–15% (занято ~$130M против $1.21B SKY-залога) — большой запас до bad debt, но SKY — волатильный актив с историей глубоких просадок.
3. **Governance/административный:** полная доверенность Sky governance (upgrade, `cut`, сеттинг ставок с задержкой GSM). Смягчено: SPBEAM-границы (max 50%), шаг ≤5%, Keeper-автоматика, SPBEAMMom kill-switch.
4. **Exit/ликвидность:** описано в §4. При банковском ране первые ~$18–48M выходят по номиналу, дальше — дисконт/ожидание.
5. **Зависимость от Spark Liquidity Layer: отсутствует.** stUSDS — core-модуль Sky; SLL обслуживает Spark Savings Vaults V2 (схема 90% deployed / 10% idle — похожая, но другая система). Роль Spark ограничена дистрибуцией (апп) и SPK-стимулами на периферии (Curve/Morpho Flagship).
6. **Риск ставки:** премия уже сжалась на ~40% за 3 месяца; SSR-хайки (окт: +28 б.п.) сокращают спред.

### Оценка вероятностей (горизонт 6 мес, до апр-2027)

- p(премия ≥ 150 б.п. на всём горизонте) ≈ 55–65%
- p(премия 50–150 б.п.) ≈ 20–30%
- p(премия < 50 б.п., включая 0) ≈ 15% — сценарий: обвал SKY >50% с каскадом, либо governance-демонтаж Stage-2 экономики
- p(loss of principal > 2% от bad debt/slashing) ≈ 3–5% (с учётом LTV ~11% и Chainlink-подобных предохранителей ликвидаций; хвостовой, не базовый)
- Мат. ожидание среднего APY за 6 мес: **~5.0–5.4%** (vs 3.8–4.0% у sUSDS) при отсутствии инцидентов.

---

## 6. Ёмкость и realized yield (задача 5)

- **Емкость без разрушения премии: $5–20M.** Обоснование: TVL эмпирически равновесен на 175–215M; каждый +$10M депозита при неизменном займе (~$130M) снижает U на ~4–5 п.п. → supply rate −10–15 б.п. немедленно, далее кильватер/спрос решают. Для «не заметить себя» — единицы процентов TVL.
- **Realized yield:** вход USDS→stUSDS mint 1:1 (газ only), выход redeem 1:1 при наличии idle (газ only) либо Curve (slippage при размере >$0.5–1M). Комиссий управления для прямого держателя нет (0.10% accessibility несут заёмщики). Итог: **realized ≈ headline 5.64% минус 0–20 б.п. на вход/выход**; за 6 мес ожидание ~5.0–5.4%. Сравнение: sUSDS 3.80% (выход мгновенный), PT-sUSDS 26ноя2026 5.12% фикс (из WS-4) — stUSDS даёт сопоставимую ставку с плавающим upside и большим хвостом.
- **Размещение:** ядро-спутник. Максимум 5–10% стейбл-букета, с планом выхода: (а) мониторинг утилизации/ставки (sky.money, Dune), (б) стоп-сигналы: SKY −30% за 30 дней, U > 95%, governance-тред о снижении фарм-фunding, TVL-отток > 20% за месяц.

---

## 7. Aave v3 Base USDC и Aave v4 Horizon USDC (задача 6, кратко)

### 7.1. Aave v3 Base USDC — «8.82% total (3.82 base + 5.00 rewards)»

- **Reward-токен — нативный USDC на Base** (0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913, DefiLlama rewardTokens). Дамп-риска токена нет — это сам доллар.
- **Программа — Merkl-кампания** «Lend USDC on Aave (Jumper bridgers)», платит в USDC (Aavescan: aavescan.com/base-v3/usdc). По Merkl API (16.10.2026): бюджет **$361/день**, окно **2026-10-14 → 2026-10-28**, eligible TVL $4.99M, заголовочный APR 263% — артефакт адресного таргетинга (Jumper-мостинг): считающая база мала. Цифра DefiLlama «5.00% на $19.5M» — усреднение по eligible-подмножеству, весь резерв $188.4M.
- **База:** резерв $188.4M, утилизация 89.53%, supply APR 3.81% (30д среднее 3.93%, 6м 3.43%). Депозиты сжались с ~395M (мар-2026) до ~175–190M после апреля — программа-зависимость наглядна.
- **Реально собрать:** без Jumper-eligibility ≈ 3.8–3.9%; с eligibility — кратный буст, но бюджет всей кампании ~$5k на 2 недели (ёмкость смешная для институционального размера). Продление кампаний еженедельное/раунд за раундом, не гарантировано.
- **Вердикт: фарм** (короткая адресная кампания), не альфа. Плюс: вознаграждение в USDC. Риск-скор 2/10 (сам Aave), премия-дюрация < 1 мес.

### 7.2. Aave v4 Horizon USDC — «8.79%»

- **Что это:** Horizon — лицензируемый отдельный инстанс Aave (первоначально форк v3.3, задействован в v4 hub-and-spoke; токены вида aHorRwaUSDC / variableDebtHorRwaUSDC): permissioned поставщики закладывают токенизированные RWA/MMF, permissionless — поставляют USDC/RLUSD/GHO; **занимать могут только** заложившие RWA. Pool: 0xAe05Cd22df81871bc7cC2a04BeCfb516bFe332C8 (Ethereum). Доки: aave.com/docs/aave-v3/horizon; анонс: avara.xyz/blog/horizon.
- **Incentives:** стартовые $500k AAVE (ARFC апр-2025, governance.aave.com/t/arfc-horizon-s-rwa-instance/21898); сейчас — недельные Merkl-кампании (API 16.10.2026): net-lending корзины стейблов 500–600% APR ($5.1k/день на $56M net), aHorRwaRLUSD 500% ($14.5k/день, $162M), заём USDC 25–175% APR. Кампании живут 7 дней и перезапускаются. Proposal v4 RWA-hub на Avalanche — $15M инсентивов (temp check май-2026).
- **TVL:** ~$390M (Sentora, 04.09.2026); стартовый кап $30M заполнился быстро; цель 2026 — $1B+. Но **USDC-резерв именно в Horizon мал**: трекаемый DefiLlama пул aHorRwaUSDC — $0.2–0.5M с APY-разбросом 4.6–9.6% за месяц (пульсы Merkl); 8.79% — срез этого волатильного ряда (16.10: 9.57%).
- **Риски:** NAV-оракулы RWA (issuer-reported), разрешения/комплаенс, аварийный мультисиг может останавливать займы; сами стейбл-поставщики несут обычный Aave-риск + инстанс-риск.
- **Вердикт: структурно интересный рынок (реальный институциональный спрос на заём), но конкретно цифра 8.79% по USDC — артефакт малого пула + недельных кампаний.** Для размера — фарм-режим; ёмкость USDC-резерва < $1M. Риск-скор 4/10.

---

## 8. Сводный вердикт WS-8

| Инструмент | Ставка | Источник премии | Ёмкость | Вердикт |
|---|---|---|---|---|
| **stUSDS (Ethereum)** | 5.64% | Плата LSE-заёмщиков (~6.42%) поверх SSR-флора 3.80%; спрос SKY-стейкинга, с авг-2026 revenue-backed | $5–20M без задавливания премии | **Структурная альфа** с кредитным хвостом; ядро-спутник 5–10% стейбл-букета |
| Aave v3 Base USDC | 8.82% (эфф.) | Merkl-кампания в USDC, адресная (Jumper), бюджет ~$361/день, до 28.10.2026 | $1–5M при eligibility | **Фарм** (короткий) |
| Aave v4 Horizon USDC | 8.79% (волатильно 4.6–9.6%) | Институциональный RWA-заём + недельные Merkl-пульсы | <$1M (USDC-резерв) | **Фарм/артефакт малого пула**; сам Horizon — наблюдать (RLUSD-бaskets $162M) |

**Действие:** перевод части стейбл-аллокации из sUSDS → stUSDS в объёме ≤ $20M с мониторингом (utilization, SKY-цена, governance-треды, Curve-глубина). Aave Base — только при готовности гонять Jumper-мост ради 2-недельного буста в USDC. Horizon — в watchlist.

---

## 9. Источники (с датами обращения 2026-10-16)

- Sky Money, stUSDS product page — https://sky.money/stusds (APY 5.64%, supply 165.39M, mechanics, utilization target 90%)
- Sky Protocol Docs — https://developers.skyeco.com/protocol/tokens/stusds; /protocol/rewards/staking-engine; /security/security-measures/overview (реестр аудитов)
- GitHub, sky-ecosystem/stusds — https://github.com/sky-ecosystem/stusds (ERC-4626/UUPS, withdrawable amount, file()-параметры, cap)
- GitHub, sky-ecosystem/sp-beam — https://github.com/sky-ecosystem/sp-beam (SPBEAM границы)
- GitHub, makerdao/lockstake — https://github.com/makerdao/lockstake
- Stablewatch, «stUSDS: Sky's risk capital token» — https://ghostadmin.stablewatch.io/stusds-sky-protocol-risk-capital-token (14.10.2025: формула ставки, accessibility reward 0.10%, target 90%)
- Sky Ecosystem (X) — https://x.com/SkyEcosystem/status/1978852084838510990 (запуск stUSDS, окт-2025); https://x.com/SkyEcosystem/status/1865543062857941272 (DSR=SSR−1пп, дек-2024)
- Spark (X) — https://x.com/sparkdotfi/status/1978115496575934756 и /1978115508970172826 (анонс stUSDS-весфолда; «offered by Sky, not Spark»)
- Executive Vote Oct 8, 2026 «stUSDS Keeper launch» — https://financial.skyeco.com/governance/spells/2026/executive-vote-2026-10-08-stusds-keeper-launch.md (kiss Keeper 0x068F…, STUSDS_VALUE_REGISTRY, stepStrBps/stepDutyBps 1500→500, LSSKY→SKY vest 99,525,882 SKY/90д)
- Atlas Edit Weekly Cycle, 5 окт 2026 — https://vote.sky.money/polling/QmeTG6L6 (прошло 9 окт 2026: авто-механизмы ставок stUSDS)
- CoinDesk, 05.03.2026 — https://www.coindesk.com/markets/2026/03/05/... (срез эмиссий SKY, байбеки)
- DefiLlama Yields API — https://yields.llama.fi/pools и /chart/{poolId} (снапшоты 16.10.2026: STUSDS 5.64%/$178.45M; SUSDS 3.80%/$4.96B; SDAI 1.25%/$200.7M; Curve USDS-STUSDS 4.57%/$2.44M + SPK; история ставок июл–окт 2026)
- app.sky.money/stake (окт-2026, через поиск: SKY staking ~6.64%, borrow rate ~6.42%, 17.37B SKY / $1.21B)
- Aavescan — https://aavescan.com/base-v3/usdc ($188.4M, U 89.53%, 3.81% + 2.64% Merkl USDC, помесячная история)
- Merkl API — https://api.merkl.xyz/v4/opportunities?name=Aave&chainId=8453 / chainId=1 (16.10.2026: кампании, бюджеты, даты)
- Aave Docs — https://aave.com/docs/aave-v3/horizon (Horizon: лицензируемый инстанс, v3.3 fork, permissioned RWA)
- Avara blog — https://avara.xyz/blog/horizon; ARFC — https://governance.aave.com/t/arfc-horizon-s-rwa-instance/21898 (апр-2025, $500k AAVE); temp check Avalanche v4 — governance.aave.com/t/temp-check-deploy-aave-v4-on-avalanche/24981 (май-2026, $15M)
- Sentora research — https://sentora.com/research/articles/aave-horizon-pushes-deeper-into-institutional-credit (04.09.2026, TVL ~$390M, кап $30M)
- Eco Support — https://eco.com/support/en/articles/14798655 (sUSDS vs stUSDS: instant withdrawal vs utilization); https://eco.com/support/en/articles/15254003 (SSR deep dive, сен-2026: 3.60%)
