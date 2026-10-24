#!/usr/bin/env python3
"""WS-28: simultaneous cross-venue snapshots Limitless <-> Polymarket <-> Kalshi (crypto up/down).
Appends snapshot dicts to data/ws28_crossarb.json. Run in background, ~60s cadence.
"""
import json, time, urllib.request, urllib.error, datetime, os, sys

OUT = "/home/coder/projects/strategy/data/ws28_crossarb.json"
LIM = "https://api.limitless.exchange"
GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
KAL = "https://api.elections.kalshi.com/trade-api/v2"
BIN = "https://api.binance.com"

HDRS = {"User-Agent": "Mozilla/5.0 (research)", "Accept": "application/json"}

def get(url, timeout=12):
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

def ts():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

CRYPTO_PREFIX = ("btc-", "eth-", "sol-", "doge-", "bnb-", "xrp-", "what-price-will-bitcoin")

def limitless_leg(t_rec):
    active = get(f"{LIM}/markets/active?limit=25")
    markets = []
    for m in active["data"]:
        if not m["slug"].startswith(CRYPTO_PREFIX):
            continue
        entry = {
            "slug": m["slug"], "externalSlug": (m.get("metadata") or {}).get("externalSlug"),
            "stableSlug": m.get("stableSlug"), "title": m["title"],
            "categories": m.get("categories"), "prices": m.get("prices"),
            "tradePrices": m.get("tradePrices"), "volume": m.get("volume"),
            "volumeFormatted": m.get("volumeFormatted"),
            "startAt": m.get("startAt"), "expirationTimestamp": m.get("expirationTimestamp"),
            "metadata_fee": (m.get("metadata") or {}).get("fee"),
            "liquidityNum": None, "book": None,
        }
        try:
            ob = get(f"{LIM}/markets/{m['slug']}/orderbook")
            entry["book"] = {"bids": ob.get("bids", [])[:4], "asks": ob.get("asks", [])[:4]}
        except Exception as e:
            entry["book_err"] = str(e)[:80]
        markets.append(entry)
    t_rec["limitless_ts"] = ts()
    t_rec["limitless"] = markets
    return markets

def pm_leg(t_rec, ext_slugs):
    out = []
    for s in ext_slugs:
        if not s:
            continue
        try:
            arr = get(f"{GAMMA}/markets?slug={s}")
            if not arr:
                out.append({"slug": s, "found": False}); continue
            g = arr[0]
            tok = json.loads(g.get("clobTokenIds") or "[]")
            entry = {
                "slug": s, "found": True, "question": g.get("question"),
                "outcomePrices": json.loads(g.get("outcomePrices") or "[]"),
                "liquidityNum": g.get("liquidityNum"), "volume": g.get("volume"),
                "endDate": g.get("endDate"), "active": g.get("active"), "closed": g.get("closed"),
                "takerBaseFee": g.get("takerBaseFee"), "makerBaseFee": g.get("makerBaseFee"),
                "books": [],
            }
            for tid in tok[:2]:
                try:
                    b = get(f"{CLOB}/book?token_id={tid}")
                    entry["books"].append({
                        "token": tid[:16] + "...",
                        "bids": b.get("bids", [])[:4],
                        "asks": b.get("asks", [])[:4],
                    })
                except Exception as e:
                    entry["books"].append({"err": str(e)[:80]})
            out.append(entry)
        except Exception as e:
            out.append({"slug": s, "err": str(e)[:80]})
    t_rec["polymarket_ts"] = ts()
    t_rec["polymarket"] = out

def kalshi_leg(t_rec):
    out = {"series": {}, "books": {}}
    for st in ("KXBTC", "KXETH"):
        try:
            d = get(f"{KAL}/markets?series_ticker={st}&status=open&limit=200")
            mkts = []
            for m in d.get("markets", []):
                mkts.append({
                    "ticker": m["ticker"], "title": m.get("title"),
                    "yes_bid": m.get("yes_bid_dollars"), "yes_ask": m.get("yes_ask_dollars"),
                    "vol24": m.get("volume_24h_fp"), "oi": m.get("open_interest_fp"),
                    "close_time": m.get("close_time"),
                })
            out["series"][st] = mkts
        except Exception as e:
            out["series"][st] = {"err": str(e)[:80]}
    # books for current-hour + next-hour + daily nearest strikes
    want = []
    now = datetime.datetime.now(datetime.timezone.utc)
    for st in ("KXBTC", "KXETH"):
        for hh in ((now.hour - 4) % 24, (now.hour - 3) % 24):  # ET hour = UTC-4 (EDT)
            want.append(f"{st}-26OCT24{hh:02d}")
    for st in ("KXBTC", "KXETH"):
        for m in out["series"].get(st, []) if isinstance(out["series"].get(st), list) else []:
            tk = m["ticker"]
            if "26OCT2417" in tk and (m.get("yes_bid") or 0) > 0.02:
                want.append(tk)
    want = list(dict.fromkeys(want))[:12]
    for tk in want:
        try:
            ob = get(f"{KAL}/markets/{tk}/orderbook")
            out["books"][tk] = {"yes": ob.get("yes", [])[:4], "no": ob.get("no", [])[:4]}
        except Exception as e:
            out["books"][tk] = {"err": str(e)[:80]}
    t_rec["kalshi_ts"] = ts()
    t_rec["kalshi"] = out

def binance_leg(t_rec):
    for sym in ("BTCUSDT", "ETHUSDT"):
        try:
            d = get(f"{BIN}/api/v3/ticker/price?symbol={sym}")
            t_rec.setdefault("spot", {})[sym] = {"price": d["price"], "ts": ts()}
        except Exception as e:
            t_rec.setdefault("spot", {})[sym] = {"err": str(e)[:80]}

def cycle():
    rec = {"cycle_start_utc": ts()}
    lim_mkts = limitless_leg(rec)
    ext = [m["externalSlug"] for m in lim_mkts]
    pm_leg(rec, ext)
    kalshi_leg(rec)
    binance_leg(rec)
    rec["cycle_end_utc"] = ts()
    return rec

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    data = {"meta": {
        "created": ts(),
        "description": "WS-28 cross-venue snapshots: Limitless <-> Polymarket (mirrored crypto up/down) <-> Kalshi (KXBTC/KXETH) + Binance spot ref",
        "note": "5-min/15-min/hourly/daily up/down families; books top-4 levels",
    }, "snapshots": []}
    if os.path.exists(OUT):
        try:
            old = json.load(open(OUT))
            if "snapshots" in old:
                data = old
        except Exception:
            pass
    for i in range(n):
        try:
            rec = cycle()
            data["snapshots"].append(rec)
            tmp = OUT + ".tmp"
            json.dump(data, open(tmp, "w"), separators=(",", ":"))
            os.replace(tmp, OUT)
            print(f"[{rec['cycle_start_utc']}] lim={len(rec['limitless'])} pm={len(rec['polymarket'])} kal_books={len(rec['kalshi']['books'])}", flush=True)
        except Exception as e:
            print("cycle ERR:", e, flush=True)
        time.sleep(60)
    print("done", flush=True)

if __name__ == "__main__":
    main()
