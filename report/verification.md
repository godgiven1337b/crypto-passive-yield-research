# Независимая верификация REPORT.md

- **Дата проверки:** 16.10.2026
- **Верификатор:** независимый агент (вне команды отчёта)
- **Метод:** прямые API (FRED CSV, CoinGecko, DefiLlama api.llama.fi / yields.llama.fi, ethena.fi), новостной поиск (Reuters, CNBC, The Hacker News, TRM Labs, CoinDesk, Chainalysis, Elliptic), трекеры rwa.xyz / defillama.com/rwa. Ни один источник не из репозитория.
- **Допуск:** APY/цены — суточная волатильность ±5–10 б.п./±1%; TVL — ±3% (суточные колебания).

## Таблица вердиктов

| № | Утверждение (REPORT.md) | Вердикт | Источник(и) | Комментарий |
|---|---|---|---|---|
| 1 | Fed funds target range 3.75–4.00%, hike +25 б.п. 17.09.2026 | **ПОДТВЕРЖДЕНО** | [FRED DFF CSV](https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFF); [FOMC statement 16.09.2026](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm); CNBC | FOMC 15–16.09.2026 объявил +25 б.п. до 3-3/4–4% (первое повышение с 2023, единогласно). DFF: 3.63 (01–16.09) → **3.88 (17.09)**, держится до 14.10. Нюанс: коммюнике датировано **16.09**, 17.09 — дата вступления в силу (шаг DFF); формулировка отчёта корректна |
| 2 | BTC ~$82K, ETH ~$2,470, SOL ~$106 на 15–16.10.2026 | **ПОДТВЕРЖДЕНО** | [CoinGecko API](https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd) | На момент запроса: BTC **$82,307**, ETH **$2,467**, SOL **$106.17**. Против отчёта (82.4K / 2,471 / 106) — расхождение <0.2% |
| 3 | DeFi TVL ~$90B на октябрь 2026 (DefiLlama) | **ПОДТВЕРЖДЕНО** | [api.llama.fi/v2/historicalChainTvl](https://api.llama.fi/v2/historicalChainTvl) | 15.10.2026 = **$89.52B**, 16.10.2026 = **$90.03B** — точное попадание. Сноска: пик окт-2025 по этому же ряду ≈ **$148B**, а не $171B (завышение в §2), но «−40% г/г» верно (148→90) |
| 4 | Взлом Bitget $387.5M, 24–25.09.2026 | **ПОДТВЕРЖДЕНО** | [Reuters, 25.09.2026](https://www.reuters.com/legal/government/crypto-exchange-bitget-pauses-withdrawals-after-350-million-stolen-hack-2026-09-25); The Hacker News, 01.10.2026; CNBC, 02.10.2026 | Первичная оценка ~$350–351.6M, уточнена до **$387.5M** (активы найдены в Zcash/TRON). Причина — zero-day стороннего ПО → подпись поддельных выводов; атрибуция — КНДР/Lazarus; CEO: восстановления не ждут. Крупнейший взлом 2026 — подтверждено |
| 5 | Взлом Liquid Network $319M (4,000 BTC), 06–07.09.2026, white-hats вернули 85% | **ПОДТВЕРЖДЕНО** | [TRM Labs, 08.09.2026](https://www.trmlabs.com/resources/blog/2026s-biggest-hack-to-date-attackers-drained-usd-319-million-in-bitcoin-from-liquid-network-then-returned-85-of-funds); CoinDesk 08.09.2026; Chainalysis 09.09.2026 | ~4,000 из 4,200 BTC федерации ≈ **$319–320M**; вектор — обмен «бездоходных» токенов на BTC (баг BTC-sidechain); возвращено **3,400 BTC ≈ 85%**, невозвращено ~$47M. Всё сходится |
| 6 | Взлом Drift Protocol $285M, 01.04.2026 (Solana perp DEX, admin-ключи) | **ПОДТВЕРЖДЕНО** | [TRM Labs, 02.04.2026](https://www.trmlabs.com/resources/blog/north-korean-hackers-attack-drift-protocol-in-285-million-heist); Elliptic 02.04.2026; Chainalysis 09.04.2026 | **$285M** (Elliptic: $286M+), 01.04.2026, крупнейший perp-DEX Solana, вектор — компрометация **privileged/admin-доступа** (не смарт-контракт), атрибуция КНДР. Деталь «6-месячная инфильтрация» явно источниками не подтверждена (упомянут social engineering), на вердикт не влияет |
| 7 | sUSDe sAPY ~4.87–4.89% на 15–16.10.2026 | **ПОДТВЕРЖДЕНО** | [yields.llama.fi chart (pool ethena-usde)](https://yields.llama.fi/chart/66985a81-9c51-46ca-9977-42b4fe7bc6df) | Временной ряд: 14.10 = **4.888**, 15.10 = **4.91**, 16.10 (текущее) = 4.80. Заявленный диапазон 4.87–4.89 попадает в фактический 4.80–4.91 соседних дней (допуск ±5 б.п.). TVL sUSDe $1.20B — тоже совпадает ($1.199B) |
| 8 | Aave v3 USDC supply APY ~3.77% (Ethereum); TVL Aave ~$16.8–17.2B | **ПОДТВЕРЖДЕНО** | [yields.llama.fi/pools](https://yields.llama.fi/pools); [api.llama.fi/tvl/aave-v3](https://api.llama.fi/tvl/aave-v3) | Base APY **3.756%** (отчёт: 3.77) и с инсентивами **5.57%** (отчёт: ~5.6) — практически точное совпадение. TVL Aave v3 = **$17.18B** — внутри заявленного диапазона. (Вся Aave целиком, вкл. v2/v4: $18.25B — как в §2 отчёта) |
| 9 | Pendle TVL ~$1.10–1.12B; PT-sUSDS ~5.12% до 26.11.2026 | **ПОДТВЕРЖДЕНО** (с оговоркой) | [api.llama.fi/tvl/pendle](https://api.llama.fi/tvl/pendle); yields.llama.fi (pendle-v2 sUSDS); [Pendle app](https://app.pendle.finance/trade/markets/0x9c560ebaf78e596cbcc27411d633a74d628dd7dc/swap) | TVL = **$1.110B** — точное попадание. APY: DefiLlama pendle-v2 sUSDS = **5.10%** (≈5.12); индекс страницы Pendle ~4.97–5.57%. Оговорка: на сайте Pendle рынок зрелости **25.11.2026**, в отчёте 26.11.2026 — расхождение в 1 день (возможно, разные рынки/конвенция) |
| 10 | Tokenized treasuries ~$15B (май 2026); RWA-категория $38.6B (сент 2026, DefiLlama) | **ПОДТВЕРЖДЕНО** (числа), **ОГОВОРКА** (атрибуция) | [Libertum, 03.06.2026](https://www.libertum.io/en/blog/tokenized-treasuries-hit-15-billion-compliance-is-the-real-unlock); NBER w35412 ($2.4B → **$15.6B** к маю 2026); [rwa.xyz](https://app.rwa.xyz/) (16.10: топ-10 казначейств ~$12.7B; Distributed Asset Value **$39.19B**); Yellow.com (сент 2026: $33.5B); [defillama.com/rwa](https://defillama.com/rwa) | «>$15B в мае 2026» подтверждено двумя независимыми источниками. $38.6B согласуется с текущим $39.19B (rwa.xyz) и «>$36B» (Libertum), НО у самой DefiLlama сейчас другие метрики: RWA Active Mcap **$31.77B** / Onchain Mcap **$34.65B** / DeFi Active TVL $4.0B. Цифра верна по сути (общий RWA on-chain ≈$35–39B), «категория DefiLlama» — неточная атрибуция |
| 11 | EigenLayer TVL ~$6.3B (окт 2026), пик $20B | **ПОДТВЕРЖДЕНО** (пик — с оговоркой) | [api.llama.fi/tvl/eigenlayer](https://api.llama.fi/tvl/eigenlayer); [api.llama.fi/protocol/eigenlayer](https://api.llama.fi/protocol/eigenlayer) (история) | Сейчас = **$6.36B** — точное попадание. Истинный пик по DefiLlama: **$22.06B (14.08.2025)**, а не «$20.1B (2024)»; масштаб пика ~$20B+ верен, дата/значение занижены. Год к году: 15.10.2025 $17.33B → 6.36B = **−63%** (в отчёте −67% — близко) |
| 12 | Кривая: 3M T-bill ~4.1–4.26%; 1Y ~4.48% | **ЧАСТИЧНО / РАСХОЖДЕНИЕ** | [FRED DTB3](https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTB3); [FRED DGS1](https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS1); [FRED DGS3](https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS3) | DTB3 (дисконт 3M) = **4.09–4.10%** (13–14.10) ✓; DGS1 (1Y CMT) = **4.48%** (13.10) / 4.53 (14.10) ✓; (бонус: DGS2 4.79–4.82 ✓ = «2Y 4.79»). **Расхождение:** «3M T-bill (CMT) 4.26%» — фактически DGS3 = **4.90–4.92%** на 13–14.10.2026 (разрыв −0.66 п.п.). 4.26 не соответствует ни DTB3 (4.00–4.10 за месяц), ни DGS3 (4.81–5.01) |

## Сводка

| Вердикт | Кол-во | Пункты |
|---|---|---|
| ПОДТВЕРЖДЕНО | **10** | 1, 2, 3, 4, 5, 6, 7, 8, 9*, 11* |
| ПОДТВЕРЖДЕНО с оговоркой (числа верны, атрибуция/деталь неточны) | **1** | 10* |
| РАСХОЖДЕНИЕ (частичное) | **1** | 12 |
| НЕ ПРОВЕРЯЕТСЯ | 0 | — |

\* помеченные пункты подтверждены по существу, но содержат мелкие неточности (см. комментарии).

**Итог: 11 из 12 утверждений подтверждены по существу (10 чистых + 1 с оговоркой атрибуции), 1 частичное расхождение, 0 непроверяемых.**

### Список расхождений и неточностей

1. **П.12, «3M T-bill (CMT) 4.26%»** — единственное содержательное расхождение: FRED DGS3 = 4.90–4.92% (13–14.10.2026), т.е. заявленное значение занижено на ~0.66 п.п. Остальные цифры пункта (DTB3 4.10, 1Y 4.48, 2Y 4.79) подтверждены точно.
2. **П.10, атрибуция:** $38.6B соответствует метрике «RWA on-chain value» (rwa.xyz: сейчас $39.19B), а не «категории DefiLlama» (текущие метрики DefiLlama: $31.8B Active / $34.6B Onchain Mcap). Число правдоподобно для сент-2026, источник указан неточно.
3. **П.11, пик EigenLayer:** фактически $22.06B (14.08.2025) против «$20.1B (2024)»; падение г/г −63% против заявленных −67%.
4. **П.9, дата экспирации:** рынок PT-sUSDS на Pendle зрелости 25.11.2026 (в отчёте 26.11.2026).
5. **П.1, дата hike:** коммюнике FOMC датировано 16.09.2026 (заседание 15–16.09); 17.09 — дата вступления в силу. Существенной ошибки нет.
6. **Вне скоупа 12 пунктов (сноска):** «пик DeFi TVL $171B (окт 2025)» в §2 отчёта не подтверждается — по DefiLlama пик октября 2025 ≈ $148B; при этом «−40% г/г» остаётся верным.

### Источники (полный список)

- FRED CSV: DFF, DFEDTARU/L, DTB3, DGS3, DGS1, DGS2 (fred.stlouisfed.org/graph/fredgraph.csv)
- federalreserve.gov — FOMC statement 16.09.2026 (monetary20260916a)
- CoinGecko API simple/price (16.10.2026)
- api.llama.fi: /v2/historicalChainTvl, /tvl/{aave, aave-v3, pendle, eigenlayer}, /protocol/eigenlayer, /protocols
- yields.llama.fi: /pools, /chart/66985a81-… (sUSDe)
- ethena.fi/api/yields (доп.)
- app.rwa.xyz (16.10.2026), defillama.com/rwa, defillama.com/protocols/rwa
- Reuters 25.09.2026 (Bitget); The Hacker News 01.10.2026; CNBC 02.10.2026; Yahoo Finance 06.10.2026
- TRM Labs 08.09.2026 (Liquid) и 02.04.2026 (Drift); CoinDesk 08.09.2026; Chainalysis 09.09.2026; Elliptic 02.04.2026
- Libertum 03.06.2026; NBER WP w35412; Yellow.com Research 09.2026
