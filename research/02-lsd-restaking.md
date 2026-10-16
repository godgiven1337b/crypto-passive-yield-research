# WS-2. Liquid Staking и Restaking ETH/SOL как источник пассивного дохода
**Дата исследования: 15–16 октября 2026.** Все TVL/APY — DefiLlama (пуллевел, 15.10.2026), если не указано иное. Цены/ставки волатильны — перед аллокацией перепроверять на дашбордах.

---

## 1. Сводная таблица

| Инструмент | База, net APY | Доп. yield | TVL | Риск-скор (1–10) | Ключевой риск |
|---|---|---|---|---|---|
| **Lido wstETH** (ETH) | 2.25% | ~0 (стратегии не в счёт) | $22.9B | **3.0** | Смарт-контракты + DAO-админ; peg-риск при рыночном стрессе |
| Binance wbETH (ETH) | 2.24% | 0 | $8.8B | 4.0 | Custodial-риск Binance (ключи у биржи) |
| ether.fi weETH (ETH, LRT) | 2.28% | ~0.1–0.5% (остаточные награды, сворачиваются) | $4.6B | 5.0 | Сложный стек, рестейкинг-обязательства, переходный период (выход из EigenLayer) |
| Rocket Pool rETH (ETH) | 2.11% | 0 | $1.27B | 4.0 | Контракты + депег-механика rate/ETH, низкий net APY |
| StakeWise osETH (ETH) | 2.28% | 0 | $0.92B | 4.5 | Vault-операторы, средний размер протокола |
| Coinbase cbETH (ETH) | 2.31% | 0 | $0.46B (в DeFi) | 4.0 | Централизация (Coinbase), комиссия ~25% |
| Frax sfrxETH (ETH) | 2.66% | 0 | $0.12B | 5.0 | Малый TVL, admin-ключи Frax, Exodus-власть |
| Kelp rsETH (ETH, LRT) | 2.30% | ~0 | $0.96B | **7.5** | Свежий взлом на $290M (18.04.2026); 15% supply было без обеспечения; мост-стек LayerZero |
| Renzo ezETH (ETH, LRT) | 2.49% | ~0 | $0.11B | 7.0 | История депега −79% (апр 2024), падение TVL в 14 раз, пивот протокола |
| Puffer pufETH (ETH, LRT) | 2.32% | 0.12% | $27M | 6.5 | Малый TVL, история депега −5.5%, вымирание сектора LRT |
| **Jito jitoSOL** (SOL) | 4.57% (стейкинг+MEV) | 0 | $1.08B | **4.0** | MEV-доход сжался (APY ниже исторических 7–9%); контракты |
| Jupiter jupSOL (SOL) | 5.45% | 0 | $0.54B | 4.5 | Стимулируемая ставка (5% fee), возможен спад после бустов; контракты Jupiter |
| Marinade mSOL (SOL) | 4.88% | 0 | $0.78B (протокол) | 4.0 | Потеря доли рынка, но zero-fee модель |
| Binance BNSOL (SOL) | 4.59% | 0 | $1.06B | 5.0 | Custodial-риск Binance |

Лучшие по риск-скорректированной доходности: **wstETH** (ядро), **jitoSOL/jupSOL** (SOL-часть), rETH/osETH как диверсификаторы. Restaking-премия в 2026 практически исчезла — держать LRT ради «доп. дохода» больше не имеет смысла (детали в §3).

---

## 2. Базовый контекст (Ethereum)

- **Consensus staking APR: ETH.STORE = 2.87% годовых** (beaconcha.in, окт 2026) — полная рыночная ставка consensus + execution (fees/MEV). Это исторический минимум: 2023 ~4.5–5%, 2024 ~3.5%, 2025 ~3.0–3.3%, окт 2026 ~2.9%. Причина: застейкано рекордные **~33.3% supply** (ATH, 21Shares, июль 2026; ValidatorQueue даёт до 35.7% / 43.6M ETH — методологии расходятся, эффективный баланс по beaconcha.in ~35.7M ETH), эмиссия обратно пропорциональна стейку.
- **Валидаторы: ~835–885 тыс.** (после EIP-7251 идёт консолидация 32→2048 ETH). Очередь входа/выхода на окт 2026 — спокойная: после рекордного сентябрьского 2025 исхода (до 2.65M ETH / ~4.5% стейка в очереди, 21Shares) очередь рассосалась; чурн-лимит ~10% стейка в месяц.
- **Апгрейды**: Pectra (07.05.2025) активировала **EIP-7002** (выход из стейкинга через execution layer, 0x01-креденшл) и **EIP-7251** (max effective balance 2048 ETH). Последствия для LST: (1) Lido/протоколы получили программный контроль над выводами без зависимости от операторов — slashing/exit-риск снизился; (2) компаундинг без новых депозитов; (3) консолидация уменьшила число валидаторов. **Fusaka (03.12.2025)** — про L2 (PeerDAS, BPO-forks, EIP-7892), к стейкингу почти не относится; EIP-7002/7251 — это Pectra, НЕ Fusaka (частая ошибка). Glamsterdam (ePBS EIP-7732 + BAL EIP-7928) на 15.10.2026 прошёл только Sepolia (06.10.2026), mainnet — конец 2026/2027.
- **Комиссии валидаторов**: solo 32 ETH — полные ~2.9%; LST берут 10–25% от наград (Lido 10%, Binance 10%, Coinbase ~25%, Frax ~10%, ether.fi 10% на стейкинг/20% на рестейкинг-часть); биржи (Kraken и др.) — 15–25%.

## 3. Restaking/LRT: 2024 → 2026 — что произошло (главный вывод исследования)

Сектор **не умер, но деградировал кратно и утратил инвестиционный смысл как класс «пассивного дохода»**:

- **Пик**: EigenLayer ~$20.1B TVL (лето 2024), вся restaking-категория >$25B, LRT раздавали «поинты», суммарный attract ~$30B+ (апр 2024).
- **Первая волна исхода (2024–2025)**: поинты сконвертировались в дешёвые токены (EIGEN, REZ, PUFFER упали на 70–95%), AVS-доходность оказалась символической (десятки–сотни бп, в основном платёжными токенами AVS), депеги ezETH/pufETH подорвали доверие. Renzo: −61% TVL за год к маю 2025.
- **Вторая волна (2025)**: булл-ран осени 2025 вернул EigenLayer к ~$19B (окт 2025, arXiv/DefiLlama), но это был последний пик.
- **Обвал 2026**: EigenLayer/EigenCloud $6.3B на 15.10.2026 (−67% за год, −69% от пика). Триггеры: (а) **взлом KelpDAO/LayerZero на $290M 18.04.2026** (Lazarus; крупнейший DeFi-инцидент 2026) — контагия на весь LRT-класс: Aave заморозил rsETH/wrsETH, спреды расширились, TVL DeFi упал на ~$13B за 48 часов; (б) фактическое исчезновение AVS-премий: реальный restaking-доп. yield к окт 2026 — **0–0.9%** (DefiLlama: wstETH на Symbiotic +0.87% наградами, pufETH +0.12%), при том что LRT несут двойной риск (стейкинг + AVS slashing + мосты); (в) **ether.fi — крупнейший LRT ($4.6B) — объявил о полном выходе из EigenLayer к концу 2026** (Blockhead, 29.09.2026) — прямой сигнал, что экономика рестейкинга не сходится даже для №1 сектора; протокол пивнулся в «нео-банк» (карты, токенизированные акции/металлы, Liquid ETH/USD/BTC, страховка балансов до $500K); (г) EigenLayer ребрендился в **EigenCloud** (окт 2025) и пивотится в «verifiable cloud»/AI — ставка больше не на рестейкинг-доходность.
- **Кто выжил/умер**: EigenCloud $6.1B (94% рынка restaking), Kelp $0.96B (после взлома, с haircut-историей), Symbiotic $0.46B (−63% за год), Renzo $0.11B (умер как LRT, доля ~3%, пивот в white-label vaults/basis trades), **Puffer $27M и Swell $28M — фактически мертвы** (−98% от пиков), **Karak $6.7M — мёртв**. Babylon ($3.3B) — BTC-рестейкинг, отдельная история.
- **Вывод для стратегии**: в окт 2026 рестейкинг НЕ даёт материальной премии к базовому стейкингу (0–0.9% при кратном росте риска, включая свежий $290M-инцидент). Корректная роль LRT-токенов в портфеле — не «доходный актив», а collateral для лупов/стратегий, и то с дисконтом за риск.

## 4. Детальные разборы

### 4.1 Lido (wstETH) — базовый якор
- **TVL $22.9B** (~56% рынка ETH LST, считая wbETH/ether.fi; DefiLlama 15.10.2026). **Net APR 2.25%** (после 10% protocol fee).
- **Механика**: stETH — rebasing (баланс растёт ежедневно), wstETH — non-rebasing wrap (растёт цена wstETH/stETH). Ставка = базовая ~2.5% gross минус 10%.
- **Peg**: рыночная цена stETH/ETH держится ~1.0 в норме. Исторический стресс — июнь 2022 (§5). wstETH/ETH ликвидность глубочайшая (Aave/Spark/Morpho/Compound/FraxLend), дисконт в стрессе минимальный среди LST.
- **Лимиты**: staking защищён rate-limit модулем (динамический дневной потолок ~150k ETH на mint/запросы ставки) + protocol buffer; exit — через withdrawal queue, типично 1–5 дней (после EIP-7002 процесс ускорился и управляется протоколом). В самозахороненных стресс-сценариях — очередь.
- **Ключи/upgrade**: DAO-управление, audits + $.Fatalis формальная верификация, bug bounty крупнейший в секторе; риск — governance/админ, но живёт с дек 2020 без потери средств. Dual Governance внедрена.
- **Slashing**: страховка + неснижаемый буфер; единственный инцидент — Launchnodes, окт 2023 (§5), убытки покрыты страховкой, стейкеры не пострадали.
- **Вердикт**: ядро ETH-аллокации; доход = база сектора.

### 4.2 Binance wbETH — $8.8B, 2.24% net
Комиссия 10%. wbETH — non-rebasing; базовый BETH rebasing. Ключи полностью у Binance (custodial), но в обмен — мгновенная конвертация BETH↔ETH 1:1 на бирже (без очередей валидаторов) и глубочайший CEX-ликвидити. Регуляторный риск (санкционные списки, delist по юрисдикциям). Подходит как «транзитный» LST, не как ядро.

### 4.3 Coinbase cbETH — $0.46B в DeFi, 2.31% net
Комиссия исторически 25% от наград (на 2026 не перепроверено — считается от gross). Coinbase-кастодиальный, публичная компания (отчётность). DeFi-TVL токена упал кратно с пика (~$2B в 2023) — рынок мигрировал к wstETH/weETH; сам стейк Coinbase остаётся крупным, но вне токена. Slashing покрывается Coinbase.

### 4.4 Rocket Pool rETH — $1.27B, 2.11% net
Наиболее децентрализованный из крупных: тысячи независимых minipool-операторов (ETH+RPL-бонд), комиссия протокола 5%, операторам 10–20%. rETH растёт курсом к ETH (non-rebasing). Слабое место — самый низкий net APY топ-5 (2.11%) и механический депег-риск через пул rate/ETH в стрессе (исторически небольшие, до пары %). Инцидентов с потерями нет.

### 4.5 StakeWise osETH — $0.92B, 2.28% net
Модель vaults (стейкинг-пулы сторонних операторов с страховкой от slashing внутри каждого vault), osETH — ERC-4626-подобный LST. Децентрализация операторов средняя; комиссии vault-зависимые (обычно 1–10% оператору). Риск — более сложный стек + выбор конкретного vault.

### 4.6 Frax sfrxETH — $0.12B, 2.66% net
Самый высокий net APY среди ETH LST (низкая комиссия + Frax-оптимизации), но TVL упал с ~$1B (2023) до $122M — протокол перегружен в Fraxtal/L2-экспансию. Admin-ключи/мультисиг Frax — точка доверия; endorsed-операторы закрыты, набор операторов узкий. Спекулятивный выбор.

### 4.7 ether.fi weETH — $4.6B, 2.28% base + ~0.1–0.5% остаточных наград
Крупнейший LRT. Базовый доход = staking (fee 10%) + рестейкинг-премии (fee 20%), но последние схлопнулись; ether.fi **выходит из EigenLayer к концу 2026** и трансформируется в нео-банк (карты с cashback, токенизированные акции/металлы, Liquid ETH/USD/BTC, страховка до $500K). weETH остаётся листингованным коллатералом (Aave v3/v4, Spark, Morpho, Compound, Euler — суммарно >$4B). Плюсы: ликвидность, зрелый стек. Минусы: переходный период, диверсификация бизнеса снижает фокус, ключевая ставка компании теперь не «restaking yield». Взломов/депегов не было (апрельский 2025 «инцидент ether.fi» вебом не подтверждён).

### 4.8 Kelp rsETH — $0.96B, 2.30% base — ВЫСОКИЙ РИСК (свежий взлом)
Жив, но с тяжёлым свежим шрамом: **18.04.2026 — $290M** (§5). Механика: LRT-вектор на EigenLayer + собственные стратегии; now де-факто LST с дырой в 15% обеспечения, закрываемой казной/компенсациями (привлечения Aave DAO-бэкстопа $181M, Umbrella ~$54M, замороженные $71M на Arbitrum). Доходность сейчас чисто стейкинговая. Держать только с дисконтом и осознанием bridge/контрактного риска LayerZero-стека.

### 4.9 Renzo ezETH — $0.11B, 2.49% base
Когда-то №2 LRT ($4B+). Апрель 2024: депег до $688 (−79%) на финале Season-1 аирдропа при отключённых withdrawals → $56M ликвидаций в DeFi. К маю 2025 TVL −61% (пик 1.04M ETH → 387k ETH), к окт 2026 — $110M (−97% от пика), доля рынка ~3%. Протокол пивнулся в white-label vaults/basis-трейды. Жив формально; для пассивного дохода не рекомендуется.

### 4.10 Puffer pufETH — $27M, 2.32% + 0.12%
Пик ~$2B (весна 2025); окт 2026 — $27M (−98.5%). Депег макс −5.46% (05.08.2024, LlamaRisk; часто упоминаемый «сентябрьский инцидент ~$1M» вебом не подтверждён). UniFi AVS не стал источником дохода. Фактически мёртв для новых аллокаций.

### 4.11 EigenLayer / EigenCloud, Symbiotic, Karak
- **EigenCloud (ex-EigenLayer)**: TVL $6.1–6.3B (пик $20.1B июнь 2024; ~$19B окт 2025; −67% за 2026). Slashing-механизм mainnet с 17.04.2025 (ELIP-002; флагманы-интеграторы Infura, LayerZero); широко задокументированных крупных slashing-случаев к окт 2026 нет — AVS-спрос на «безопасность» оказался в основном субсидированным. 200+ AVS live/in development (авг 2026, Datawallet), реально платящих yield — единицы десятков; премии — токенами AVS, Deep liquidity слабая. EIGEN стейкинг даёт single-digit APY токеном с высоким волатильным риском. Ребрендинг (окт 2025) в EigenCloud = признание, что монетизация пойдёт через «verifiable cloud»/AI, а не через рестейкинг-комиссии.
- **Symbiotic**: $456M (−63% за год; пик ~$2B). Модель Mellow-LRT/рестейкинг-вектор; жив, но нишевый.
- **Karak**: $6.7M — по факту мёртв.

### 4.12 Solana LST
Базовая ставка Solana (инфляция ~4.5–5% + fees) даёт gross ~6–7%, net LST ниже из-за комиссий и упавшего MEV: окт 2026 все крупные LST дают **4.5–5.5%** (годом ранее 7–9% — MEV-премия сжалась).
- **jitoSOL** ($1.08B; 4.57%; fee ~4% от общих наград + 0–5% комиссия валидаторов): топ-выбор на Solana, ликвидность глубочайшая, VCR (Validator LST voting) — риск-менеджмент распределённый. Механика: staking + MEV-награды через Jito bundles.
- **jupSOL** ($0.54B; 5.45%; fee 5% от стейкинга, 0.1% вывод): самый высокий APY среди гигантов — частично за счёт агрессивной стратегии/бустов экосистемы Jupiter; быстрорастущий, риск — ставка стимулируемая и может снижаться.
- **mSOL / Marinade** ($0.78B протокол; 4.88%): перешли на zero-fee liquid staking; потеря доли ( когда-то №1 на Solana), но протокол зрелый, mnDE-стейкинг DAO. Инцидентов с потерями нет.
- **BNSOL** ($1.06B; 4.59%): Binance-custodial, аналогично wbETH по рискам; плюс — мгновенная конвертация на CEX.
- Оборонная инфраструктура Sanctum ($1.74B) — маршрутизатор LST, снижает депег-риски малых токенов.
- Slashing на Solana исторически мягкий и редкий; основной риск — смарт-контракты + валидатор-сёт.

---

## 5. История инцидентов (depeg / slashing / взломы)

| Дата | Протокол | Что случилось | Масштаб |
|---|---|---|---|
| Июнь 2022 (8–18.06) | **Lido stETH** | Депег на фоне изъятий Celsius/3ACN: stETH/ETH до ~0.93–0.95, Curve-пул перекошен ~90/10. Неисполнимых обязательств не было — чисто ликвидити-кризис; восстановлен за недели | Дисконт до ~5–7%, объёмы продаж сотни млн $; стейкеры не потеряли principal (в redeem) |
| 15.10.2023 | **Lido (Launchnodes NO)** | 20 валидаторов slashed за double-signing (ошибка оператора) | ~20 ETH (~$35k); покрыто страховкой Lido, стейкеры не пострадали (постмортем blog.lido.fi) |
| Окт 2023 (шире) | Ethereum | Коррелированный slashing ~100 валидаторов разных операторов | ~1 ETH на валидатора |
| **24–25.04.2024** | **Renzo ezETH** | Депег −79% до **$688–700** на DEX в финал Season-1 REZ-аирдропа; withdrawals были отключены → паника + $56M каскадных ликвидаций (Gearbox −55% ezETH-TVl, Morpho 150+ ликвидаций на $25M+) | Крупнейший LRT-депег; прямые потери leveraged-фарморев; восстановлен за сутки |
| 25.04.2024 | Renzo ezETH (второй эпизод) | Продажа после аирдропа — отдельный дисконт (Yahoo) | меньший масштаб |
| 05.08.2024 | **Puffer pufETH** | Максимальный депег −5.46% к ETH (LlamaRisk/onchainattack) | без прямых потерь principal |
| 17.04.2025 | **EigenLayer** | Активация slashing на mainnet (ELIP-002) — механизм; реальных крупных slashing-кейсов далее не зафиксировано | — |
| 10.09.2025 | **SSV (операторы Ankr и миграции)** | 39 валидаторов slashed (double-sign, ошибки ключей операторов) | ~11.7 ETH total; протокол SSV не скомпрометирован |
| **18.04.2026** | **KelpDAO rsETH / LayerZero** | **Взлом на ~$290M**: подделанный LayerZero-пакет (RPC-отравление единственного DVN в 1-of-1 конфигурации OFT-адаптера rsETH) выпустил 116 500 несанкционированных rsETH; атакующий занял ~$236M под залог на Aave/Compound/Euler. Атрибуция — Lazarus Group. 112 204 rsETH (~15% supply) остались без обеспечения; сценарный haircut 15.12% (L2-изоляция — до 73.5%). Контагия: TVL DeFi −$13B за 48 ч, Aave −$8.45B, заморозки rsETH/wrsETH/WETH-маркетов, pausa OFT-мостов у Ethena/Lombard | Крупнейший DeFi-инцидент 2026 и второй после Bybit-2025 ($1.4B); частично перекрыто казной Aave ($181M бэкстоп), Umbrella (~$54M), замороженными $71M на Arbitrum |
| 01.04.2026 | Drift (Solana DEX, контекст) | Взлом $285M (также атрибутируется TraderTraitor/Lazarus) | не LST, но часть той же кампании |
| 2020–2026 | Ethereum consensus | Кумулятивно slashed за всю историю — малые доли % от стейка (сотни ETH + inactivity-утечки); slashing на ETH остаётся редким и в основном «ручным» ошибкам операторов | — |

**Не подтвердилось вебом (помечаю как непроверенное):** «slashing $23M у оператора Ethernal/eStore в мае 2024/2025» — источников не найдено; «эксплойт UniV2-пула pufETH на ~$1M в сентябре 2024» — не найден (документирован только депег −5.46% в августе); «инцидент ether.fi в апреле 2025» — не найден; «Dorfrock» как протокол нативного стейкинга — не существует (вероятно, опечатка, возможно имелся в виду Bedrock или solo-staking через Ramp/движки типа Dvt).

---

## 6. Риски — сводка по классам

1. **Slashing**: ETH — редок, мал, страхуется (Lido/Rocket Pool buffer); EigenLayer slashing с апр 2025 добавляет второй слой (AVS-специфичные правила, пока без крупных кейсов); Solana — мягкий slashing, риск операторских ошибок.
2. **Depeg/liquidity**: все LST/LRT торгуются с плавающим дисконтом; депеги случались на ~−5%…−79% (ezETH) без потери underlying — потери несут leveraged/паникующие. Глубина: wstETH ≫ weETH > rETH/osETH > jitoSOL/jupSOL > малые LRT.
3. **Смарт-контракты/мосты**: свежий пример — rsETH (LayerZero-стек, апр 2026, $290M). LRT несут тройной стек: LST + рестейкинг + мосты (rsETH/EZETH мультичейн).
4. **Операторы/централизация**: Binance/Coinbase — custodial (ключи у биржи); Lido — 30+ NO, лимит доминации; Rocket Pool — самая высокая децентрализация; Frax — узкий набор; Solana — распределённые сеты валидаторов + Sanctum LST-voting.
5. **Управляемость/upgrade**: у всех LST есть админ-уровень (DAO/мультисиг); у Lido — самый отработанный процесс (dual governance); у CEX-LST — регуляторный override.
6. **Доходный риск**: база ETH ~2.9% — исторический минимум (стейк 33% supply); SOL net 4.5–5.5% против 7–9% год назад; restaking-премии ~0.

## 7. Практические выводы (окт 2026)

- **Ядро ETH-доли**: wstETH (ликвидность, стресс-история, низкий риск); диверсификация 20–30% в rETH/osETH для снижения single-protocol риска.
- **SOL-доля**: jitoSOL базово, jupSOL — тилт к доходности (следить за устойчивостью ставки), BNSOL — только под CEX-удобство.
- **LRT (weETH/rsETH/ezETH/pufETH) как класс «пассивного дохода» — НЕ рекомендуется в 2026**: премия 0–0.9% не компенсирует риски (свежий $290M-взлом, эскейп ether.fi из сектора, история депегов). Если LRT нужны как collateral — брать только с дисконтом и позиционировать как трейд, не как стейкинг.
- **Кэш-эквиваленты**: нативный стейкинг (solo 32 ETH, ~2.9% gross) — минимальный контрактный риск, максимальный операционный; биржевой — просто и custodial.

---

## 8. Источники (URL, дата обращения 15–16.10.2026)

- DefiLlama API: protocols/yields/pools/tvl (lido, rocket-pool, binance-staked-eth, ether.fi-stake, coinbase-wrapped-staked-eth, stakewise-v3, frax-ether, kelp, renzo, puffer-stake, symbiotic, karak, eigenlayer/eigencloud, jito-liquid-staking, marinade, jupiter-staked-sol, binance-staked-sol, sanctum) — https://api.llama.fi/ , https://yields.llama.fi/pools — 15.10.2026
- Galaxy Research: KelpDAO/LayerZero exploit — https://www.galaxy.com/insights/research/kelpdao-layerzero-exploit-defi — 16.10.2026
- beaconcha.in ETH.STORE — https://beaconcha.in/ethstore — 15.10.2026
- arXiv:2604.03274v2, Financial Dynamics and Interconnected Risk of Liquid Restaking Tokens — https://arxiv.org/html/2604.03274v2 — 16.10.2026
- Ethereum Blog: Fusaka mainnet announcement — https://blog.ethereum.org/2025/11/06/fusaka-mainnet-announcement ; Glamsterdam testnet — https://blog.ethereum.org/2026/09/17/glamsterdam-testnet-announcement — 16.10.2026
- 21Shares: staking ATH 33.33% и exit-queue risk — https://www.21shares.com/en-eu/insights/ethereum-staking-exit-queue-risk — 16.10.2026
- ValidatorQueue — https://validatorqueue.com — 16.10.2026
- SSV Network: Post-mortem Sept 2025 slashing — https://ssv.network/blog/slashing-post-mortem-september-2025 ; CoinDesk — https://www.coindesk.com/tech/2025/09/10/ethereum-rare-mass-slashing-event-linked-to-operator-issues — 16.10.2026
- Lido: Launchnodes post-mortem — https://blog.lido.fi/post-mortem-launchnodes-slashing-incident/ — 16.10.2026
- The Defiant: LRT slump (Renzo −61%) — https://thedefiant.io/news/defi/ethereum-liquid-restaking-sector-slumps-as-incentives-dry-up ; ezETH depeg — https://thedefiant.io/news/defi/renzo-s-restaked-eth-depegs-to-usd700-as-season-1-of-airdrop-ends ; Bankless — https://www.bankless.com/renzo-madness ; DL News — https://www.dlnews.com/articles/defi/renzos-ezeth-loses-ether-peg-drops-79-in-under-one-hour — 16.10.2026
- LlamaRisk: pufETH depeg −5.46% — https://llamarisk.com/research/collateral-risk-assessment-pufeth ; onchainattack.org — 16.10.2026
- Blockhead: ether.fi выходит из EigenLayer — https://www.blockhead.co/2026/09/29/ether-fi-to-fully-exit-eigenlayer-restaking-as-sector-profits-collapse — 16.10.2026
- Tokenomics.com: EigenLayer TVL early 2026 — https://tokenomics.com/articles/eigenlayer-tokenomics-how-eigen-captures-restaking-revenue ; Upshift — https://www.upshift.finance/blog/what-is-restaking — 16.10.2026
- Ether.fi — https://ether.fi/ — 16.10.2026
- Jito Foundation FAQs — https://www.jito.network/ ; eco.com Marinade vs Jito — https://eco.com/support/en/articles/14801193-marinade-vs-jito-solana-liquid-staking-compared — 16.10.2026
- EigenCloud docs — https://docs.eigencloud.xyz/ — 16.10.2026
- Consensys slashing primer; P2P.org exit-queue playbook — 16.10.2026
