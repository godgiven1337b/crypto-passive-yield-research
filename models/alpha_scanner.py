"""
alpha_scanner.py — поиск аномалий доходности (спрэдов) по DefiLlama Yields API.

Логика: для каждого стейбл-актива строим «базовый уровень» по blue-chip пулам
(TVL > $100M), затем ищем пулы с существенным превышением. Аналогично для LST.
Пороги консервативные: спрэд > 100 б.п. и TVL > $1M.

Запуск: python3 models/alpha_scanner.py
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request

CATEGORIES = {
    "USDC": "usdc", "USDT": "usdt", "USDS": "usds", "USDe": "usde",
    "DAI": "dai", "sUSDe": "susde", "sUSDS": "susds", "stUSDS": "stusds",
}
BLUE_CHIP_PROJECTS = {"aave-v3", "compound-v3", "spark", "sky-lending", "morpho-blue", "kamino-lend", "fluid"}
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "alpha_candidates.json")


def fetch_pools() -> list[dict]:
    url = "https://yields.llama.fi/pools"
    with urllib.request.urlopen(url, timeout=40) as r:
        return json.load(r)["data"]


def main() -> None:
    pools = fetch_pools()
    print(f"Пулов загружено: {len(pools)}")

    # индекс по символу пула
    by_symbol: dict[str, list[dict]] = {}
    for p in pools:
        sym = (p.get("symbol") or "").upper()
        if not sym or len(sym) > 40:
            continue
        by_symbol.setdefault(sym, []).append(p)

    findings: list[dict] = []

    for label, key in [("USDC", "USDC"), ("USDT", "USDT"), ("USDS", "USDS"),
                       ("sUSDS", "SUSDS"), ("stUSDS", "STUSDS"), ("sUSDe", "SUSDE"),
                       ("USDe", "USDE")]:
        candidates = by_symbol.get(label, [])
        # базовый уровень: blue-chip, большой TVL
        base_pool = [
            p for p in candidates
            if p.get("project") in BLUE_CHIP_PROJECTS and (p.get("tvlUsd") or 0) > 50e6
        ]
        if not base_pool:
            continue
        base_apy = sorted(p.get("apy") or 0 for p in base_pool)[len(base_pool)//2]  # медиана
        for p in candidates:
            apy = p.get("apy") or 0
            tvl = p.get("tvlUsd") or 0
            if tvl < 1e6 or apy <= 0:
                continue
            spread = apy - base_apy
            if spread > 1.0:  # >100 б.п.
                findings.append({
                    "asset": label, "pool": p.get("symbol"), "project": p.get("project"),
                    "chain": p.get("chain"), "apy_pct": round(apy, 2),
                    "base_bluechip_pct": round(base_apy, 2),
                    "spread_bp": round(spread * 100),
                    "tvl_usd": round(tvl), "exposure": p.get("exposureToken") or "",
                    "stablecoin_risk": p.get("stablecoinRisk") or "",
                    "predicted": p.get("predicted") is True,
                })

    # LST-спрэды: тот же актив-класс, разные протоколы
    for lst in ["WSTETH", "RETH", "OSETH", "CBETH", "JITOSOL", "MSOL", "JUPSOL", "BNSOL", "WBETH"]:
        cands = [p for p in by_symbol.get(lst, []) if (p.get("tvlUsd") or 0) > 5e6 and p.get("apy")]
        if len(cands) >= 2:
            apys = sorted(c.get("apy") for c in cands)
            med = apys[len(apys) // 2]
            for c in cands:
                if c["apy"] - med > 0.8:
                    findings.append({
                        "asset": lst, "pool": c.get("symbol"), "project": c.get("project"),
                        "chain": c.get("chain"), "apy_pct": round(c["apy"], 2),
                        "base_bluechip_pct": round(med, 2),
                        "spread_bp": round((c["apy"] - med) * 100),
                        "tvl_usd": round(c.get("tvlUsd") or 0), "exposure": "",
                        "stablecoin_risk": "", "predicted": False,
                        "note": "LST spread vs class median",
                    })

    findings.sort(key=lambda f: -f["spread_bp"])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump({"generated": "2026-10-16", "findings": findings}, f, indent=1, ensure_ascii=False)

    print(f"\nНайдено аномалий: {len(findings)}  -> {OUT}\n")
    print(f"{'Актив':<8} {'Проект':<22} {'Цепь':<12} {'APY':>7} {'База':>6} {'Спрэд':>7} {'TVL,$M':>8}")
    for f in findings[:40]:
        print(f"{f['asset']:<8} {f['project']:<22} {f['chain']:<12} {f['apy_pct']:>6.2f}% "
              f"{f['base_bluechip_pct']:>5.2f}% {f['spread_bp']:>6}bp {f['tvl_usd']/1e6:>8.1f}")


if __name__ == "__main__":
    main()
