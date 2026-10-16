# Лупинг и рычаг для максимизации APY (WS-15) — октябрь 2026

Дата проверки: **16.10.2026** (on-chain срезы 18:00–18:30 UTC; DefiLlama/протокольные API — на ту же дату; все ставки плавающие, кроме отмеченного).
Контекст рынка: ETH ≈ $2 414–2 429, gas Ethereum **0.11–0.12 gwei** (исторический минимум — издержки входа в луп практически обнулены). Бенчмарки пассивного доллара: sUSDe стейкинг 4.75–4.87%, sUSDS 3.80%, Aave v3 USDC supply 3.75–3.77%.

Входные аномалии (наши данные окт-2026): Jupiter Lend USDC 8.98% (всплеск за 9 дней, было 4.21% 07.10), Kamino USDC 7–8%, Fluid «borrow GHO-USDC 1.6%», «8% RWA-велт» Pareto FalconX.

**Ключевые выводы (кратко):**

1. **Математика безжалостна: положительный спрэд s−b внутри одного пула невозможен** (s = u·b·(1−RF) < b всегда). Все живые лупы — кросс-активные или кросс-рыночные: доходный актив в залог (syrupUSDC, sUSDe, wstETH, RWA-транши) против дешёвого долга (USDC на Maple-рынке Kamino 3.56%, PYUSD 4.2–4.7%, WETH 1.96%). «Луп на всплеске ставки» (Jupiter 8.98%) — ловушка: всплеск создан спросом на займ, т.е. твоей же borrow-ногой (внутри Jupiter borrow ≈ 9–10% > supply).
2. **Классика 2024–2025 местами мертва**: стейбл-луп на Aave v3 отрицателен (USDC 3.75 supply / 4.47 borrow), Ethena-петля sUSDe→USDe на Aave инвертирована (4.80 против borrow USDe 6.61–6.84%, с апреля-2026 спайки до 17.35%), «levered vaults» Gauntlet на Morpho в старом виде не существуют — направление ушло в RWA.
3. **Живые положительные петли окт-2026**: Kamino syrupUSDC/USDC(Maple) ≈ 13.8% при 5.3x; RWA-петли (3F wFalconX 11–17% при 3–6.5x; ONyc/USDC ≈ 26% при 2.2x; PRIME/PYUSD ≈ 19% при 5x); Morpho sUSDe/PYUSD ≈ 7.7% при 5.9x (+ TESS-обёртка на IPOR 9.3–9.9% net, депозиты закрыты); классика wstETH/ETH ≈ 3.6% при 5x (переживает всё, но и даёт мало); IPOR stETH-loop 5.7/5.2% net при 9.7x.
4. **Главный риск — не ликвидация, а спрэд**: у лупа с плечом L чистая ставка падает на (L−1) п.п. на каждый +1 п.п. borrow. Морфо-петля 5.9x умирает при +0.6 п.п. (запас спрэда всего 0.60 п.п.), wstETH 5x — при +0.32 п.п. Устойчивы только петли с запасом спрэда ≥1.5 п.п. на дешёвом долге (Maple-рынок, Figure-рынок, FalconX).
5. **«Fluid GHO 1.6%» — не ставка, а Merkl-награда** поверх gross borrow 5.66% (T4 smart-debt велт с LP-коллатералем). Структурного дешёвого GHO-funding на Fluid нет. Аналогично «8% RWA-велт» FalconX жив не как один vault, а как стек Pareto→(Gauntlet|3F)→Morpho с плечом 2.3–6.5x.
6. **stUSDS (Sky) на Solana делистнут** с Jupiter Lend и Kamino (в доках/Jupiter Market и скане 50 рынков Kamino от 16.10.2026 отсутствует) — премисса WS-9/WS-10 про «луп на stUSDS» устарела; нишу yield-доллара на Solana заняли syrupUSDC/sUSDai/reUSD/ONyc/PRIME.

---

## 1. Математика лупинга (реализовано в models/loop_math.py, тесты 108 passed)

### 1.1. Базовая формула

Капитал C, плечо L (total supply = L·C, долг = (L−1)·C), supply APY s, borrow APY b:

```
net = L·s − (L−1)·b = s + (L−1)·(s−b)          # loop_apy()
d(net)/dL = s − b                                # каждая единица плеча добавляет спрэд
Δnet = −(L−1)·Δb                                 # чувствительность к ставке долга
```

Положительный carry ⇔ **s > b** (плюс издержки). Если s ≤ b — любое плечо только ухудшает (база b остаётся, `carry_breakeven_leverage` возвращает None).

**Таблица: net APY (%) при базе s=5% и спрэде d = s−b:**

| L \ d | +0.5 п.п. | +1 п.п. | +2 п.п. | +3 п.п. |
|---|---|---|---|---|
| 1x | 5.00 | 5.00 | 5.00 | 5.00 |
| 2x | 5.50 | 6.00 | 7.00 | 8.00 |
| 3x | 6.00 | 7.00 | 9.00 | 11.00 |
| 5x | 7.00 | 9.00 | 13.00 | 17.00 |
| 10x | 9.50 | 14.00 | 23.00 | 32.00 |

**Чувствительность (главная таблица риска):** +1 п.п. к borrow-ставке отнимает (L−1) п.п. net: L=3 → −2 п.п., L=5 → −4 п.п., L=10 → −9 п.п. Высокое плечо на тонком спрэде = ставка на неизменность ставок.

### 1.2. Закон одного пула: почему луп «внутри» невозможен

В любом money market supply-ставка резерва — это доля borrow-ставки:

```
s = u · b · (1 − RF)        # u — утилизация, RF — reserve factor
s − b = −b · (1 − u·(1−RF)) < 0   при любых u<1, RF≥0   # same_pool_spread()
```

Пример: u=90%, RF=10% → s = 0.81·b. Луп «supply USDC → borrow USDC» того же пула теряет ~19% borrow-ставки на каждом обороте. Следствия:
- **положительный спрэд бывает только между разными резервами/активами** (sUSDe vs USDe/PYUSD; syrupUSDC vs USDC другого рынка; wstETH vs WETH) или за счёт внешнего yield (стейкинг, RWA-доход, LP-комиссии);
- всплеск supply-ставки (Jupiter 8.98%) — зеркало всплеска borrow (≈9–10%): «залупить всплеск» = платить его же своей долговой ногой;
- кросс-рыночный луп = арбитраж утилизаций между рынками (USDC Kamino main 9.07% borrow против USDC Maple-рынка 3.56% — вот где carry).

### 1.3. Максимальное плечо и ликвидационная дистанция

```
L_max = 1/(1−LTV); практическое L = 1/(1−k·LTV), k≈0.6–0.7    # max_leverage()
Ликвидация: LTV_тек = (L−1)/L · (P_долг/P_коллатерал) ≥ LT
Допустимое относительное падение коллатераля: x = 1 − (L−1)/(L·LT)   # liquidation_move_same_asset()
```

| L | LT=76% | LT=86% | LT=91.5% | LT=95% |
|---|---|---|---|---|
| 2x | 34.2% | 41.9% | 45.4% | 47.1% |
| 3x | 12.3% | 22.5% | 27.1% | 29.5% |
| 5x | −5.3% (невозможно) | 7.0% | 12.6% | 15.3% |
| 10x | — | — | 1.6% | 4.8% |

Для same-asset пар (sUSDe/PYUSD, syrupUSDC/USDC, wFalconX/USDC) «падение коллатераля» = **депег/NAV-просадка** доходного актива к доллару; для LST (wstETH/ETH) — депег к ETH (исторически ≤1%, кроме стресс-эпизодов ~0.5–1%).

### 1.4. Компаундинг и издержки

- Луп **самокомпаундится** (ставки начисляются поблочно на растущие балансы): net APR 8% → APY 8.33%, 12% → 12.75%.
- **Gas (16.10.2026, base 0.11 gwei, ETH $2 414):** итерация supply+borrow+swap+supply на Ethereum ~0.8–1.1M gas ≈ **$0.5–1.5**; выход на 5x (4–5 итераций) ≈ $5–15; при спайке 2 gwei ×5. Ручной луп на $50k: разово 0.01–0.03% капитала, ежемесячный ребаланс ≈ 0.05–0.15%/год. На $500k — <0.01%/год. **Газ перестал быть фильтром размера; фильтр — комиссии агрегаторов** (DeFi Saver 0.01% стейблы / 0.10% correlated + 0.05% за авто-триггер; Furucombo закрыт в 2026).
- Solana: Jupiter Multiply/Strategies — **0 протокольной комиссии, flashloan бесплатный**, ~0.02 SOL создание позиции; Kamino flashloan **0.001%** за транзакцию, ликвидационный penalty Multiply **~0.1%** (снижен на 90% с сент-2025).
- Break-even времени: издержки 0.3% капитала при прибавке +2 п.п. → окупаемость 1.8 мес.

### 1.5. Стек-риск

Каждый протокол в цепочке — независимый смарт-контрактный риск (`effective_hack_risk`, p_hack≈0.8%/слой/год): 2 слоя → 1.6%, 4 слоя → 3.2%/год. При LGD 80% хвост-издержка 4-слойного лупа ≈ 2.5 п.п. EV-ставки. Кросс-чейн стеки (RWA-транш + обёртка + Morpho + оракул NAV) — до 5–6 слоёв.

---

## 2. Живые луп-структуры на октябрь 2026

### Сводная таблица (все цифры — 16.10.2026; расчёт net по формуле п.1.1 на заявленных ставках)

| # | Структура (где) | Плечо | Спрэд s−b | **Net APY на капитал** | Ликв. дистанция | Стек | Вердикт |
|---|---|---|---|---|---|---|---|
| 1 | **Kamino syrupUSDC / USDC-Maple** (Solana) | 5.26x (факт. средн.) | **+1.94 п.п.** (5.5 vs 3.56) | **≈13.8%** | NAV-депег syrupUSDC ~14% (LT~94%, расч.) | Kamino+Maple CCIP | **ТОП: толстый спрэд, дешёвый долг** |
| 2 | **3F wFalconX 3–5x** (Ethereum, RWA Pareto/FalconX) | 3–5x (тиры до 6.5x) | +1.77 п.п. (7.90 vs 6.13) | **11.0–14.2%** (6.5x → 16.7%) | NAV −12.6% при 5x (LLTV 91.5) | Pareto+IdleCDO+3F+Morpho+RedStone (5+) | **ТОП: USD-депег-буфер большой, но месячная ликвидность** |
| 3 | **Morpho sUSDe / PYUSD LLTV 91.5%** (Ethereum; TESS-обёртка на IPOR) | 5.9x (макс 11.8x) | **+0.60 п.п.** (4.80 vs 4.20) | **7.7%** (TESS net 9.3–9.9%, депозиты закрыты) | депег sUSDe/PYUSD 9.2% | Morpho+(Ethena)+(IPOR/TESS) | ТОП по простоте, **хрупкий спрэд** (умирает при +0.6 п.п.) |
| 4 | Kamino ONyc / USDC-OnRe (Solana, RWA) | 2.2x | +8.3 п.п. (16 vs 7.74) | ≈26% (база 16% из доков, live не публикуется) | NAV-депег ~30–40% (LT не вериф.) | Kamino+OnRe+Chainlink NAV | Макс. APY; риск = кредит RWA + ставка-оценка |
| 5 | Kamino PRIME / PYUSD-Figure (Solana, HELOC RWA) | 5x | +2.76 п.п. (8 vs 5.24) | ≈19% | NAV-депег ~9% (LT~88%) | Kamino+Figure+Chainlink | Высокий APY, кредитный риск Figure |
| 6 | Kamino USDe / PYUSD-Ethena (Solana) | 9.32x (факт.) | est +0.8–1.3 п.п. (yield USDe не публикуется) | est 12–15% | депег USDe ~6% при 9.3x | Kamino+Ethena+Paxos | Высокое плечо = хрупкость; оценка, не факт |
| 7 | Jupiter Strategies USDe/PYUSD Sentora (Solana, с 30.09.2026) | до 16.3x (94/95) | пример доков: +0.5 п.п. → 13.5% при 16x | est 10–13.5% (live не публикуется) | депег USDe ~1.2% при 16x | Fluid Layer+Jupiter+Ethena/Paxos | Пиковое плечо, микроскопический буфер |
| 8 | Kamino jupSOL/SOL (Solana LST) | 7.5x (eMode 87%) | +0.39 п.п. (5.39 vs 5.00) | 7.9% | ценовой НЕТ (SOL-номин., stake-rate oracle) | Kamino+Jupiter staking | Чистый rate-spread; инверсия ставки = минус |
| 9 | IPOR Fusion stETH Looping (Spark+Morpho+Aave) | 9.7x | ≈+0.33 п.п. эфф. | **5.7% gross / 5.2% net (реал. 30d)** | депег wstETH ~4–8% при 9.7x (LT не вериф.) | IPOR+Spark+Morpho+Aave+Lido (5) | Реализованный, но тонкий |
| 10 | Aave v3 wstETH/ETH eMode 93/95 (классика) | 5x (макс 14.3x) | +0.32 п.п. (2.28 vs 1.96) | 3.6% (10x → 5.2%) | депег wstETH −15.8% (5x) | Aave+Lido | Жив, но carry почти нулевой |
| 11 | Aave v3 стейбл-луп USDC/USDT | до 4x (75/78) | **−0.4…−1.2 п.п.** | отрицательный | — | Aave | **Мёртв** |
| 12 | Aave v3 Ethena sUSDe→USDe | до ~5.5x (eMode 90/92) | **−1.81 п.п.** (4.80 vs 6.61) | отрицательный (2x → 3.0% < 4.8% базы) | — | Aave+Ethena | **Мёртв** (перегрет с апр-2026; спайк borrow 17.35%) |
| 13 | IPOR AavEthena Loop Mainnet (TAU) | 9.5x | отриц. (46% залога в нестейканом USDe!) | **−10.2%** (держится наградами ~23% APR) | borrow/collateral 89.4% — HF≈1.0 | IPOR+Aave+Ethena | **Анти-пример**: не заходить |
| 14 | Gauntlet gpAAFalconX (Ethereum, Morpho-рынок AA_FalconX 77%) | 2.27x (рынок) | +2.23 п.п. (7.4 net CV vs 5.17) | ≈10.2% (расч.; APY vault не раскрыт) | NAV −27% (LLTV 77) | Pareto+Gauntlet+Morpho (4) | Институциональный, min $50k, accredited |
| 15 | Fluid GHO T4 «borrow 1.56%» (Ethereum) | — | Merkl-награда поверх gross 5.66% | LP-структура, не классический луп | penalty 2%, CF 92/LT 94 (sUSDe/GHO) | Fluid+Merkl+LP | Субсидия, не ставка; min borrow ~$11.5k |
| 16 | Kamino JLP/USDC | 2.2x | **−0.45 п.п.** (8.62 vs 9.07) | 8.1% < базы 8.62% | −17% JLP | Kamino+JLP | При текущих ставках мёртв (только с наградами) |
| 17 | Jupiter Offerbook fixed-rate loops (Solana, новый) | по офферу | фикс. ставка 1–30 дн. | «до 18.7%» (доки; 25% interest upfront) | ценовых ликвидаций нет, риск maturity | Offerbook escrow | Фиксирует спрэд, но депозит = collateral при дефолте контрагента |

Ставки-первоисточники: Kamino API (срез 18:00 UTC): USDC main borrow 9.07 / supply 7.28; SOL borrow 5.00; USDC-Maple borrow **3.56**; PYUSD-Figure borrow 5.24; PYUSD-Ethena borrow 4.70; OnRe USDC borrow 7.48–8.00. Aave v3 on-chain (блок 26206858): USDC 3.75/4.47, USDT 3.29/4.19, WETH 1.33/**1.96**, USDe 0.25/**6.61**, sUSDe 0/0 (доход в rate токена 4.8%), wstETH supply ~0 + Lido стейкинг 2.23. Morpho GraphQL: PYUSD/sUSDe LLTV 91.5%, supply 3.77/borrow 4.20, $109.5M/$98.5M, util 89.9%. DefiLlama: Jupiter USDC 7.94% (UI-мгновенное 8.98%), USDS 5.87%; sUSDe 4.8.

### 2.1. Solana: Jupiter Lend Multiply/Strategies (искомое «JLM»)

Продукта «JLM» нет — официальные названия **Multiply** (произвольное плечо на любом vault, слайдер 1.1x…max), **Strategies** (one-click лупы на max-leverage по pegged-парам: JupSOL/SOL, INF/SOL, syrupUSDC/USDC, LBTC/cbBTC, USDe Loop) и **Smart Vaults** (v2, авг-2026: collateral/debt = LP Jupiter AMM, +Trading APR к lending-yield). Формула APY в интерфейсе — ровно наша: `APY = SupplyAPY×Lev − BorrowAPY×(Lev−1)`.

- Механика: **одна атомарная транзакция** (flash-borrow → swap через агрегатор Jupiter → deposit → borrow → repay), 0 протокольных комиссий, flashloan бесплатный, ~0.02 SOL на позицию.
- Ликвидации: tick-based **частичные** (тики через 0.15% D/C-ratio, штраф только с ликвидируемой части, penalty ~1%: JUICED 1%, Sentora 1%), Liquidation Max Limit — полная продажа в ноль. Pegged-пары оракулятся по redemption/exchange-rate — **рыночный депег не ликвидирует**, только падение redemption-ставки (slashing/дефолт эмитента).
- Рынки: Jupiter Market (куратор Fluid); Bitwise×Ethena Market (USDe/USDG, LTV 94/LT 95, **max 16.3x** — сворачивается); **Sentora Market USDe/PYUSD (94/95, живёт с 30.09.2026)**. Пример из доков: 16x при supply 6/borrow 5.5 → 13.5%.
- Ловушка плеча 16x: D/C = 93.9% при LT 95% → буфер **~1.1 п.п.** Депег/расхождение ставок на 1% — и позиция в зоне ликвидации (частичные тики сглаживают, но при гэпе NAV — пролетает).
- **stUSDS на Jupiter Lend отсутствует** (и в Earn, и в collateral; в сент-2025 был флагманским). USDS supply 5.87% (16.10; 15.10 было 3.52% — тоже скачет). Borrow-ставки Jupiter не публикуются в API; оценка по supply≈0.9·b·u при u~90–95%: **borrow USDC ≈ 9–10%** → луп внутри Jupiter USDC = отрицательный (закон п.1.2).
- **Offerbook** (новое, окт-2026): P2P **фиксированные** ставки 1–30 дней под любой collateral, **без ценовых ликвидаций** (риск = maturity: не вернул в срок — теряешь депозит). Позволяет зафиксировать спрэд лупа; цена — 25% оценённых процентов upfront с заёмщика + 10% с кредитора.

### 2.2. Solana: Kamino Multiply

Один атомарный луп через flashloan (**0.001%**), депозитных/выводных комиссий нет (старая инфа про 0.25% устарела). Ликвидационный penalty **~0.1%**; close factor 10–20% долга за транзакцию; **auto-deleveraging** (72-часовой margin call без штрафа, затем эскалация) — ни разу не активировался. История: 06–07.04.2025 — $16M seized, 0 bad debt; **05–06.02.2026 (SOL −18%) — $19.4M, 0 bad debt; ноль ценовых ликвидаций LST-Multiply за всю историю** (JLP-Multiply ликвидировался в оба краха — он не SOL-номинирован).

Живые петли (api.kamino.finance, 16.10.2026 18:00 UTC; deposit$/avg leverage/позиции):

| Петля | Депозит | Плечо | Ставки (s / b) | Net (расч.) |
|---|---|---|---|---|
| ONyc/стейблы (OnRe Market) | **$91.8M** (+$25.5M) | 2.20–2.24x | 16% (доки) / 7.48–8.00 | **≈26%** |
| PRIME/PYUSD+USDC+CASH (Figure) | ~$74M | 4.9–5.5x | 8% (доки) / 5.24 | **≈19%** |
| syrupUSDC/стейблы (Maple) | **$40.2M** | 5.26x | ~5.5 / **3.56** | **≈13.8%** |
| JLP/USDC (JLP Market) | $23.3M | 2.19x | 8.62 / 9.07 (main) | отрицательный спрэд, только с наградами |
| USDe/PYUSD (Ethena Market) | $15.8M | **9.32x** | est 5–6 / 4.70 | est 12–15% |
| vSOL/SOL, JupSOL/SOL, bonkSOL/SOL | $5.9–14.8M | 4.2–5.4x | 5.39 (jupSOL) / 5.00 | 7.9% (jupSOL) |
| JitoSOL/SOL (Jito, rate-cap) | $3.9M | 6.16x | 4.71 / 4.60 | 5.3% |
| sUSDai/USDC, reUSD/USDG+USDC | $1.3–3.5M | 4.0–4.25x | — / 6.13–7.31 | согласуется с WS-10 (reUSD) |

eMode-плечи: Standard 75% LTV (~4x); SOL/BTC ~87% (~7.5x); Jito 90% (10x); стейбл/RWA-петли до 8.3–10x; JLP/USDC 67% LTV (~3.2x). Протокольный спред (доля от процентов): SOL 11%, USDC 15–20%.

Ключевая механика выживания LST-петель: **обе ноги номинированы в SOL** (коллатерал jupSOL, долг SOL), оракул — stake rate, ценового риска нет вообще; риск только инверсия «стейкинг-ставка − borrow SOL». У стейбл/RWA-петель (ONyc, PRIME, syrupUSDC) — NAV-риск базового кредита + спайк borrow.

### 2.3. Aave v3/v4: стейблы мертвы, классика жива еле-еле

- **Aave v4 живёт с 30.03.2026** (Hub&Spoke: Liquidity Hub + споки; Target-HF-ликвидации, User Risk Premium; сети: ETH→Avax→Arc→Base 07.10.2026 с Equities Hub). Но **v3 — основной рынок**: TVL v3 $16.98B против v4 $653M (16.10.2026); миграции нет, лупить пока надо на v3.
- **Стейбл-луп на v3 Ethereum невозможен по ставкам**: все пары дают −0.4…−1.2 п.п. (USDC 3.75/4.47; USDT 3.29/4.19; DAI borrow 4.96 при LTV 0). Generic stablecoin eMode **не существует** (скан всех категорий on-chain: только «sUSDe Stablecoins» 90/92, «USDe Stablecoin» 90/93, ETH-correlated 93/95, PT/EURC/LINK/XAUt) — стейбл-стейбл плечо идёт по base 75/78. Спрэд «sUSDS 3.8 vs USDC» ≈ 0 — тоже нет.
- **wstETH/ETH (eMode 93/95, bonus 101%)**: стейкинг Lido 2.23% + supply ~0 vs WETH borrow **1.96%** → L=3x: 2.9%, L=5x: 3.6%, L=10x: 5.2%. Ликвидационная дистанция 15.8% (5x) / 5.3% (10x) депега wstETH/ETH (исторический де-пег ≤1%). weETH-вариант сопоставим (weETH supply 0 / WETH borrow 1.96 + стейкинг ether.fi ~2.5–3%). **Максимальная живучесть, минимальный carry** — разумно только как «парковка с бустом», не как доходная стратегия.
- Новое: Merkl-кампания «Borrow wstETH with tETH on Aave» 0.5% (16.10.2026) — LST↔LST-петля с почти нулевым borrow; механика/эмитент tETH глубоко не проверялись (флаг для WS-16).
- Автоматизация: DeFi Saver (v3, 6 сетей; v4 не поддерживает) — fee 0.01%/0.10%/0.25% по типу пары + 0.05% за авто-срабатывание; Furucombo закрыт. При gas 0.11 gwei ручной луп дешевле агрегатора.

### 2.4. Ethena-луп: где он жив и где умер

- **Aave v3 (классика sUSDe→borrow USDe): инвертирован.** sUSDe yield 4.80 против borrow USDe **6.61%** (on-chain блок 26206858; IPOR-API в тот же день 6.84%, весь октябрь «прибитые» 6.83–6.84 — утилизация pinned у kink). История с марта-2026: 2.4% → спайк **17.35%** (апр–май) → 2.7–3.2% → 6.16% (сен) → 6.8% (окт). CryptoSlate (11.09.2026): «rising Aave borrow rates threaten to flip Ethena's USDe yield loops into negative carry» — уже перевернули. Спрэд −1.81 п.п. за оборот → оптимальное плечо = 1x.
- **Morpho: живой рынок PYUSD/sUSDe (LLTV 91.5%)**: borrow PYUSD 4.20 против sUSDe 4.80 → **+0.60 п.п.**, $109.5M/$98.5M, утилизация 89.9%. L=5.9x (HF 1.1) → net ≈ 7.7%, ликвидация при относительном депеге sUSDe/PYUSD **9.2%**. Рынок USDe-loan против sUSDe фактически пуст. Мелкие рынки: USDtb borrow 6.92%, DAI 9–9.5% (крошечные) — отрицательные.
- **Обёртки на IPOR Fusion**: TESS sUSDe PYUSD Loop — TVL $1.36M, **net 9.3–9.9%** (30d 9.0%), плечо 7.6x, депозиты закрыты; TESS USDe sUSDe Loop (Aave, borrow USDT 4.27) — $858K, net 8.9%, депозиты закрыты. Т.е. живые Ethena-петли выжили, **заменив долг USDe на дешёвый USDT/PYUSD**.
- **Aave v4 «Ethena Ecosystem» спок (Plus Hub) + промо Ethena «Liquid Leverage»** (награды USDe с сент-2026): депозит 50% sUSDe + 50% USDe, заявлено «~12% APY» — промо-ставка, кампании кончаются (аналитика предупреждает о пост-промо обвале); чистых live-цифр нет.
- **Solana**: Kamino Ethena Market USDe/PYUSD (borrow 4.70) 9.32x — est 12–15%; Jupiter Sentona USDe/PYUSD 16.3x — est 10–13.5% (живые цифры не публикуются).
- Риски петли: funding-волатильность sUSDe (диапазон 2024–2026 ~0–30%), оракул exchange-rate, депег USDe (прецедент апр-2025), концентрация sUSDe-залога на Aave (гайвенс-дискуссия).

### 2.5. Morpho + Gauntlet/Pareto/3F: levered = RWA

Скан всего списка vault'ов Morpho (топ-1000 V1 + 500 V2): **ни одного vault с «lever/levered/loop» в имени, кроме RWA-сегмента**. «Levered USDe/USDC, sUSDe/USDC, wstETH/ETH vault'ов Gauntlet» не существует.

- **Pareto × FalconX Credit Vault** (март-2025): USDC → займы институналам через desk FalconX (overcollateralized, SPV OspreyX, first-loss FalconX, M11 curator, Sygnum lender of record с мая-2026). Доходность **8.25% gross 30d (июнь-2026)** − 10% perf fee ≈ **7.4% net**; TVL пик $144M (23.06.2026); **месячные циклы** ликвидности; NAV месячный.
- **Gauntlet «gpAAFalconX»** (авг-2025): AA-транш CV как коллатераль на Morpho (рынок AA_FalconX/USDC, **LLTV 77%**): сейчас $12.53M коллатерала / $7.00M долга под **5.17%** → LTV 55.9% ≈ 2.27x. Расчётный net ≈ 10.2%; APY vault не раскрывается (JS-страница), min **$50k, accredited, через команду**. Целевое плечо ~3.45x (правдоподобно: запас до LLTV ~7.8% NAV).
- **3F (grunt)** — основной «levered vault» экосистемы: обёртки wFalconX (LLTV 91.5% рынок $29.3M collateral / $23.3M borrow под 6.13%, кредиторы Smokehouse/Clearstar 5.51%). Тиры 3x–6.5x, **safe LTV 87.5%**, target 67.3–84.9%. Итог: **3x ≈ 11.0%, 5x ≈ 14.2%, 6.5x ≈ 16.7%** (с учётом 0.15%/год на весь коллатерал; сайт заявляет max 19.46% при более дешёвом borrow 5.8%). Ликвидационная дистанция (падение NAV wFalconX до LLTV 91.5%): 3x −27%, 5x −12.6%, 6.5x −7.5%; **до ретаргета 87.5% — 6.5x всего −3%**. Вход/выход через intent + bridge loan (Symbiotic), месячная ликвидность наследует FalconX-циклы, KYC/KYB-обёртки. Риски: **месячный NAV прыгает дискретно** (может пролететь все буферы разом), кредитный риск FalconX/заёмщиков, зависимость от USDC-ликвидности Morpho-рынка.
- Рядом: 3F wUSCC (Bitwise, 17x, 5.72% → 13.8%), wJAAA (10x, 3.03%); Gauntlet Levered RWA на sACRED (Apollo/Securitize, Polygon+Drift) — числа не раскрыты, $50k+ accredited. Steakhouse/0xphenom levered-велтов нет (участвуют кредиторской стороной: Smokehouse USDC 5.87% gross в wFalconX/AA-рынки).

### 2.6. IPOR Fusion: инфраструктура чужих петель

Протокол вырос в **$83.8M TVL, 545 волтов, 13 сетей** (16.10.2026); «стратегии IPOR» уступили кураторам (Atomist — риски, Alpha — исполнение; TESS, TAU, Clearstar, Reservoir).

- **AavEthena Loop Mainnet (наследник оригинала, куратор TAU): анти-пример.** TVL $141K (пик $2.93M апр-2026), **momentum APY −10.2%**, 30d −13.6%; конструкция деградировала: 46% залога лежит в нестейканом USDe (0.25%) при плече 9.5x и borrow USDT 4.27%; выживает только на **~23% APR наград** (DefiLlama показывает пул как +23% — только rewards, вводит в заблуждение). Реализованный share-price 30d ≈ +3.1% годовых net. Borrow/collateral 89.4% — HF ≈ 1.0–1.05. Отрицательный momentum каждый месяц с марта-2026.
- **stETH Looping (IPOR DAO): $4.87M, 9.7x через Spark** (supply wstETH $45.2M / borrow WETH $40.6M) + Morpho + Aave — **5.7% gross / 5.2% net, 30d реал 5.4%**. Самый крупный «честный» луп Fusion.
- **Optimizer (USDC Lending)**: не петля — аллокатор по ставкам; в октябре реально мигрировал Aave→Morpho→Euler (ушёл из Aave при 3.82%). 4.4% gross / **2.4% net** (fee drag 1.5 п.п. — самый высокий), TVL $260K.
- **yoUSD Loooper (Clearstar, Base)**: yoUSD = Yield Optimizer USD (YO Protocol, yo.xyz; НЕ Yuncan/Yard); сейчас **делевериджирована** (borrow 0 — спрэд отрицателен: yoUSD-доходность < USDC borrow 7.72%), 4.5% gross / 3.5% net.
- Комиссии: performance fee ~10% (HWM), mgmt ~0.2%/год, on/offboarding contribution ~0.1% (per-vault); фактический gross→net drag 0.5–1.5 п.п. Вывод: scheduled withdrawal (не мгновенный) + redemption delay до 7 дней (immutable). Risk recipient как механизм не существует — потери несут депозиторы ( Covered Vaults с OpenCover/Nexus — только для отдельных волтов с 18.06.2026).

### 2.7. Fluid: развенчание «GHO 1.6%»

- **Gross borrow GHO на Fluid = 5.66% для всех GHO-велтов** (ETH/GHO, wstETH/GHO, sUSDe/GHO и др.; API 16.10.2026). Заявленные в Merkl «1.56%» — это **reward APR в GHO** за borrow из T4 smart-debt велта «GHO-sUSDe/GHO-USDC» (коллатерал = LP GHO/sUSDe, долг = GHO+USDC, 70 позиций, кампания до 06.12.2026). Родственные кампании: borrow GHO-USDC T4 1.74%, lend 1.57%, supply fGHO 1.67%. **Дешёвого структурного GHO-funding на Fluid нет** (нет и burn/mint-фасилитатора): вся «дешевизна» = Merkl-субсидии + swap-fee доход LP.
- Экономика: fGHO supply 3.77% base + 1.67% Merkl = 5.43% ($24.1M). Гипотетический арбитраж «borrow Aave GHO ~4.5% (не подтверждено on-chain) → supply fGHO 5.43%» = +0.9 п.п. **без плеча** и с GHO-шортом; не подтверждён, не торгуй без верификации.
- Классического T1-велта «USDC-коллатерал → GHO-долг» на Fluid нет. Живые пары: sUSDe/GHO (CF 92/LT 94/penalty 2%), reUSD/GHO (+0.85% Merkl → net ~4.81% borrow). **Минимальный заим ~$11.5–12k** — экономический минимум позиции $15–20k.
- Интересное для луперов на Fluid: **wstETH/ETH borrow 2.39%** (penalty 0.1%, CF 93–95/LT 95–97) — луп уступает Aave (2.39 > 1.96); **weETH/wstETH borrow 0.13%** — LST↔LRT-петля с почти нулевым долгом (механику не проверяли глубоко); USDC borrow 7.33% — дорого. fUSDC 5.43% — лучший стейбл-supply из крупных.

---

## 3. Стресс-сценарии

### 3.1. Спрэд → 0 / инверсия (кейс: Jupiter 8.98% → 4.21% за 9 дней)

Всплеск Jupiter USDC (4.21% 07.10 → 8.98% 16.10) создан borrow-спросом при оттоке ликвидности (TVL $538M фев → $475M). Кто «залупил» на пике:
- внутри Jupiter: borrow ≈ 9–10% > supply 8.98% → **минус с первого дня** (закон п.1.2);
- кросс-рыночно (занять дешевле где-то, ссудить в Jupiter): при нормализации 8.98→4.21 за неделю (факт) доходность упала в 2.1 раза; если borrow-нога не упала синхронно (Maple/Fluid USDC 5.4–5.6% на Solana-мостах не гасятся мгновенно), спрэд инвертируется на дни;
- чувствительность: луп L=3, построенный при спрэде +1 п.п., даёт 5+2=7%; спрэд → 0 → 5% (= базе, т.е. плечо бесплатно несёт риск); спрэд → −0.5 → 4% < базы. **Луп на пике плавающей ставки — всегда опцион шорта этой ставки, проданный бесплатно.**
- фиксация: Jupiter Offerbook (1–30 дн. фикс) решает проблему ставки, добавляя контрагентский maturity-риск.

### 3.2. Каскад ликвидаций (тип окт-2025 / фев-2026)

Прецеденты в данных: **05–06.02.2026, SOL −18%: Kamino $19.4M seized, 0 bad debt, LST-петли не ликвидированы ни одной** (SOL-номинация + stake-rate oracle); JLP-петли ликвидировались (долларовый долг против волатильного JLP). Апр-2025 (тарифный шок): USDe депег до ~$0.95–0.97 — стейбл-петли 5–9x с дистанцией 6–9% депега прошли в ~2 п.п. от ликвидации; спайк Aave USDe borrow до 17.35% (апр-май 2026) убил carry мгновенно.
Каналы поражения лупа в каскаде: (1) депег доходного актика (NAV/USDe/syrupUSDC) — у петель 9x+ буфер 1–6% = ликвидация; (2) спайк borrow-ставок при массовой размотке (все петли — вынужденные заёмщики-продавцы одновременно); (3) gas/конгестия: 0.11 gwei сегодня, в каскаде окт-2025 — сотни gwei: ручная размотка дорожает на 2 порядка, авто-защита (DeFi Saver) требует работающего mempool; (4) месячная ликвидность RWA (3F/FalconX) — выйти в каскаде нельзя в принципе, NAV переоценится после; (5) каскадные ликвидации TESSELL-типа на частичных тиках Jupiter сглаживают, но гэп NAV пролетает тики разом.

### 3.3. Hike ФРС (и почему cut опаснее)

Hike: базы вверх симметрично — sUSDe растёт (funding ≈ SOFR+бasis), стейбл-supply растёт, спрэды в п.п. примерно сохраняются; главный канал ущерба — **волатильность ставок**: плавающий borrow у kink реагирует мгновенно (прецедент: Aave USDe 2.4→17.35% за два месяца при утилизационном спросе), а (L−1)-множитель превращает +1 п.п. в −4…−9 п.п. net (таблица ниже). Новые ingress-капиталы сжимают спрэды.

**Численно (+Δ к borrow-ставке):**

| Петля | base net | +1 п.п. | +2 п.п. | Запас спрэда до паритета с 1x |
|---|---|---|---|---|
| syrupUSDC/Maple 5.26x | 13.8% | 9.5% | 5.2% | **1.94 п.п.** (b: 3.56→5.50) |
| 3F wFalconX 5x | 14.2% | 10.2% | 6.2% | **1.77 п.п.** (b: 6.13→7.90) |
| Morpho sUSDe/PYUSD 5.9x | 7.7% | 2.8% | **−2.1%** | **0.60 п.п.** (b: 4.20→4.80) |
| Aave wstETH/ETH 5x | 3.6% | **−0.4%** | −4.4% | 0.32 п.п. (b: 1.96→2.28) |

Cut (более актуальный режим 2026): все базы вниз, но спрэды в п.п. сжимаются медленней абсолютных ставок → headline-APY падает быстрее базы; у RWA-петель (FalconX 8.25%, PRIME 8%) ставка фиксирована контрактом — спрэд даже расширяется. Инверсия стейкинг-ставки (LST) при cut: jupSOL 5.39 vs borrow SOL 5.00 — запас 0.39 п.п. исчезает за один пересмотр.

---

## 4. Вердикт

**Устойчивый положительный carry + адекватный буфер (рейтинг):**

1. **Kamino syrupUSDC / USDC-Maple @5.3x ≈ 13.8%** — лучший профиль: спрэд +1.94 п.п. на дешёвом долге (3.56% — субсидированный Maple-рынок), pegged-оракул, penalty 0.1%, TVL $40M, история Kamino без bad debt. Ломается при: USDC-Maple borrow > 5.5% (инсентивы Maple кончились/перелив ликвидности), кредитный эписод Maple/syrup, инверсия за ночь (утилизационный спайк). Размер: $50k–2M (комфортно <5% TVL петли).
2. **3F wFalconX 3–5x ≈ 11–14% (6.5x = 16.7%)** — самый большой ликвидационный буфер среди доходных петель (−12.6% NAV при 5x; у 3x −27%), доллар-к-доллару (нет крипто-цены), спрэд +1.77 п.п. Оговорки: **месячная ликвидность и месячный NAV** (кредитный эписод FalconX маркируется разом), KYC-обёртки, 5-слойный стек. Ломается при: NAV-просадка > 12.6% (5x) / > 7.5% (6.5x), Morpho USDC borrow > 7.9%. Размер: $25k–500k (exposure $29M, pro-rata вывод).
3. **Morpho sUSDe/PYUSD @5.9x ≈ 7.7%** (TESS-обёртка 9.3–9.9% net — депозиты закрыты, ждать капа) — самая чистая формула, но запас спрэда **0.60 п.п.**: одна переоценка borrow — и carry = базе. Утилизация рынка 89.9% — добавление позиций само поднимает ставку. Ломается при: b≥4.80%, депег sUSDe > 9.2%, срез Ethena-наград. Размер: $100k–5M (рынок $110M).

**Специальные упоминания:** ONyc/OnRe ≈ 26% @2.2x — максимум APY, но base-yield не публикуется live (16% из доков) и это частный кредит: только с самостоятельной оценкой OnRe. PRIME/PYUSD ≈ 19% @5x — доходный, но буфер NAV всего ~9%. Aave v4 Ethena-промо ~12% — кампания, брать только с планом выхода. wstETH/ETH 3.6% — не доходная стратегия, а «парковка с бустом» (зато переживает всё, кроме borrow > 2.3%). Jupiter/Sentona 16x — не рекомендуется: буфер 1.1 п.п.

**Мёртвые (не заходить):** стейбл-луп Aave v3 (отрицательный carry), Ethena sUSDe→USDe на Aave (−1.81 п.п., перегрет с апр-2026), IPOR AavEthena TAU (−10% momentum, HF≈1), JLP-петля при текущих ставках, «Fluid GHO 1.6%» как ставка (Merkl-субсидия на LP).

**Размерная граница осмысленности:** gas больше не фильтр (0.11 gwei: $5–15 вход на любом размере; Solana — центы). Реальные фильтры: (а) доля в петле < 5–10% TVL (иначе сам двигаешь утилизацию против себя — у Morpho-рынка 89.9% это уже проблема); (б) капы/закрытые депозиты (TESS закрыт, Gauntlet $50k accredited, IPOR caps); (iii) Merkl-награды размываются pro-rata — считать по базе; (г) RWA-циклы месячные — размер, который можешь заморозить на квартал. Минимум осмысленности: Solana $10–20k, Ethereum-ручной $50k, RWA-обёртки $25–50k.

---

## 5. Источники (все проверены 16.10.2026, если не указано иное)

**On-chain / live API (16.10.2026, 18:00–18:30 UTC):**
- Aave v3 Pool 0x87870Bca…fA4E2: getReserveData/getEModeCategoryData, блок 26206858 (кросс-чек с DefiLlama: совпадение supply-ставок до 0.01 п.п.)
- api.kamino.finance: /v2/kamino-market, /kamino-market/{pk}/reserves/metrics, /kamino-market/{pk}/leverage/metrics (ставки, плечи, позиции петель)
- api.morpho.org/graphql: рынки и vault'ы (PYUSD/sUSDe LLTV 91.5%; скан levered-велтов)
- api.fluid.instadapp.io/v2/1/vaults (borrow-ставки GHO/USDC/ETH/wstETH, параметры ликвидации)
- api.merkl.xyz/v4/opportunities (Fluid GHO T4 1.56% reward; borrow wstETH/tETH 0.5%)
- api.ipor.io/v2/fusion/vaults, /fusion/vaults, /v2/fusion/vault-history/*, /dapp/plasma-vaults-list (TVL/APY/плечи волтов, блок 26206750)
- eth_gasPrice (publicnode): 0.112 gwei; coins.llama.fi: ETH $2 414
- yields.llama.fi/pools + /chart/*: Jupiter Lend USDC 7.94% (история с 27.02.2026), USDS 5.87%, sUSDe 4.8, lido stETH 2.23, fUSDC 5.43, TVL aave-v3/v4

**Документация:**
- docs.jup.ag: earn/lend/{multiply,strategies,markets,supported-assets,liquidation-mechanism,faq}, offerbook/* (16.10.2026)
- kamino.com/docs: products/multiply/{how-it-works,strategies,risks}, borrow/{fees,liquidations}, risk/safeguards/auto-deleverage (16.10.2026)
- docs.3f.xyz: protocol/deployments/wfalconx (тиры, LLTV 91.5, оракул RedStone), fees; app.3f.xyz (exposure $39.7M, APY)
- docs.ipor.io: fusion user-guide (fees, withdrawing/deposit caps), security-and-audits (Protofire 2024-09, BlocSec 2025-02)
- docs.fluid.instadapp.io; aave.com/docs (v4 changelog: mainnet 30.03.2026, Base 07.10.2026)
- help.defisaver.com: fees, supported-chains (16.10.2026)

**Пресса/анонсы (дата):** gauntlet.xyz/resources/falconx-levered-rwa-strategy-with-pareto (18.08.2025); falconx.io/newsroom credit-vault (24.06.2026, 8.25% 30D, $144M); X @paretocredit (14.01.2026, $55M+); aave.com/blog/aave-v4-live-ethereum (30.03.2026); X @ethena + cryptotimes.io (07.09.2026, USDe-награды в Aave v4); cryptoslate.com «Rising Aave borrow rates threaten to flip Ethena's USDe yield loops into negative carry» (11.09.2026); coindesk.com Jupiter Lend v2 (10.08.2026); prnewswire Jupiter Lend beta (29.08.2025); rwa.xyz Pareto TVL.

**Честные пробелы:** borrow-ставки Jupiter Lend (нет публичного API; оценка 9–10% по supply≈0.9·b·u); live-ставки Sentona/Bitwise-рынков Jupiter; APY/плечо gpAAFalconX и sACRED (JS/закрытый API); base-yield ONyc и USDe-компонента Kamino Ethena Market; Aave GHO borrow live; LT Spark для stETH-loop IPOR; судьба делистинга stUSDS (rate-limited); «JLM» и «Daesoo» как названия не существуют.
