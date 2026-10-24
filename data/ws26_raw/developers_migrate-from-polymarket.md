> ## Documentation Index
> Fetch the complete documentation index at: https://docs.limitless.exchange/llms.txt
> Use this file to discover all available pages before exploring further.

# Migrate from Polymarket

> Map Polymarket concepts, endpoints, and agent code to the Limitless API

If you've built bots or agents on Polymarket, this guide maps every concept, endpoint, and code pattern to the Limitless equivalents so you can port your code in minutes.

> [!NOTE]
>
> This guide reflects Polymarket's **CLOB V2**. The V1 clients (`py-clob-client`, `@polymarket/clob-client`, the Rust `rs-clob-client`, and the `Polymarket/agents` framework) were archived in May 2026 and no longer work against production. If you're still on V1 code you have to move to V2 regardless, so the mappings below target V2.

## What changed

| | Polymarket (CLOB V2) | Limitless |
| - | - | - |
| **Chain** | Polygon (137) | Base (8453) |
| **Collateral** | pUSD (6 decimals, wraps USDC.e) | USDC (6 decimals) |
| **REST hosts** | `gamma-api.polymarket.com` (markets, search) + `clob.polymarket.com` (orderbook, pricing, trading) + `data-api.polymarket.com` (positions, trades, activity) | `api.limitless.exchange` (unified) |
| **WebSocket** | `wss://ws-subscriptions-clob.polymarket.com` | `wss://ws.limitless.exchange` |
| **Auth model** | L1/L2 — derive API creds with EIP-712, sign every request with HMAC across 5 `POLY_*` headers | HMAC-signed scoped API tokens (`lmts-api-key`/`lmts-timestamp`/`lmts-signature`) for all integrations; granular scopes for [partner integrations](https://docs.limitless.exchange/developers/programmatic-api.md) |
| **SDKs** | V2 CLOB clients `@polymarket/clob-client-v2`, `py_clob_client_v2` (V1 clients archived) | [Python SDK](https://docs.limitless.exchange/developers/sdk/python/getting-started.md), [TypeScript SDK](https://docs.limitless.exchange/developers/sdk/typescript/getting-started.md), [Go SDK](https://docs.limitless.exchange/developers/sdk/go/getting-started.md), [Rust SDK](https://docs.limitless.exchange/developers/sdk/rust/getting-started.md), or direct REST |
| **Wallet types** | EOA, Proxy, Gnosis Safe, 1271 (`signatureType` 0-3) | EOA (`signatureType` 0) for self-signed API orders, or server-managed wallets via [delegated signing](https://docs.limitless.exchange/developers/programmatic-api.md#delegated-order-types). Other signature types exist for the web app's smart wallets and are verified on-chain, but they are not a Polymarket-style proxy/Gnosis mapping; use 0. Self-signing also requires the profile to be in EOA trading mode; see [Trading wallet mode](https://docs.limitless.exchange/developers/eip712-signing.md#trading-wallet-mode-whose-address-signs) |
| **Market lookup** | `conditionId` or `clobTokenIds` | `slug` or address |
| **Token IDs** | `clobTokenIds` paired with `outcomes` by index | `tokens.yes` = Yes, `tokens.no` = No |
| **Order signing** | EIP-712 `verifyingContract` = CTF Exchange V2, domain version `"2"` | EIP-712 `verifyingContract` = `venue.exchange`, domain version `"1"` |
| **Order struct** | V2 dropped `taker`, `nonce`, `feeRateBps`, `expiration` from the signed order and added `timestamp`, `metadata`, `builder` | Classic CTF fields: `taker`, `expiration`, `nonce`, `feeRateBps` (no `timestamp`/`metadata`/`builder`) |
| **Order freshness** | V2 order carries a mandatory creation `timestamp` (ms); GTD orders have a \~1 minute expiration threshold | Optional `timestamp` + `recvWindow` on `POST /orders`; stale orders rejected with HTTP `425`. See [Receive Window](https://docs.limitless.exchange/api-reference/trading/create-order.md#receive-window). |
| **NegRisk** | Separate Neg Risk CTF Exchange V2 contract | Handled via [venue system](https://docs.limitless.exchange/developers/venue-system.md) — extra approval to `venue.adapter` for SELL |

## Authentication

Polymarket requires deriving API credentials (apiKey, secret, passphrase) through an L1 EIP-712 handshake, then signing every request with HMAC-SHA256 across 5 `POLY_*` headers.

Limitless uses a scoped API token (a token ID + secret) generated in the UI. You sign each request with HMAC-SHA256 and send three headers: `lmts-api-key`, `lmts-timestamp`, and `lmts-signature`.

**Polymarket (V2)**

```python theme={null}
from py_clob_client_v2 import ClobClient

client = ClobClient(host="https://clob.polymarket.com", chain_id=137, key=private_key)
creds = client.create_or_derive_api_key()

client = ClobClient(
    host="https://clob.polymarket.com",
    chain_id=137,
    key=private_key,
    creds=creds,
)
```

**Limitless**

```python theme={null}
import hmac, hashlib, base64, requests
from datetime import datetime, timezone

API_BASE = "https://api.limitless.exchange"
TOKEN_ID = "your_token_id_here"
SECRET = "your_token_secret_here"  # base64-encoded secret

def sign_request(token_id: str, secret: str, method: str, path: str, body: str = "") -> dict:
    timestamp = datetime.now(timezone.utc).isoformat()
    message = f"{timestamp}\n{method}\n{path}\n{body}"
    signature = base64.b64encode(
        hmac.new(base64.b64decode(secret), message.encode("utf-8"), hashlib.sha256).digest()
    ).decode("utf-8")
    return {"lmts-api-key": token_id, "lmts-timestamp": timestamp, "lmts-signature": signature}

# Sign per request. The message is: {ISO timestamp}\n{METHOD}\n{path+query}\n{body}
# (GET body is ""). Add Content-Type for requests with a JSON body.
```

Generate your token at [limitless.exchange](https://limitless.exchange) → profile → **Api keys**.

No `POLY_*` headers, but you do sign each request: derive the three `lmts-*` headers with `sign_request(TOKEN_ID, SECRET, method, path, body)` for every authenticated call. The timestamp must be within 30 seconds of server time. See the full [Authentication guide](https://docs.limitless.exchange/developers/authentication.md) for details, and the [Programmatic API guide](https://docs.limitless.exchange/developers/programmatic-api.md) for partner scopes (sub-account management and delegated order signing).

## Endpoint mapping

### Market data

| Action | Polymarket (CLOB V2) | Limitless |
| - | - | - |
| List active markets | `GET gamma-api.polymarket.com/markets?closed=false` | `GET /markets/active` |
| Get market by slug | `GET gamma-api.polymarket.com/markets/slug/:slug` | `GET /markets/:slug` |
| Search markets | `GET gamma-api.polymarket.com/public-search?q=...` | `GET /markets/search?query=...` |
| Orderbook | `GET clob.polymarket.com/book?token_id=...` | `GET /markets/:slug/orderbook` |
| Price history | `GET clob.polymarket.com/prices-history?market=...` | `GET /markets/:slug/historical-price` |
| Midpoint price | `GET clob.polymarket.com/midpoint?token_id=...` | Compute from orderbook response |

### Trading

| Action | Polymarket (CLOB V2) | Limitless |
| - | - | - |
| Place order | `POST clob.polymarket.com/order` | `POST /orders` |
| Cancel order | `DELETE clob.polymarket.com/order` (`orderID` in body) | `DELETE /orders/:orderId` |
| Cancel multiple | `DELETE clob.polymarket.com/orders` (array of ids in body) | `POST /orders/batch-cancel` (`orderIds` or `clientOrderIds`; all in one market). `POST /orders/cancel-batch` is the older `orderIds`-only form and still works. |
| Cancel all | `DELETE clob.polymarket.com/cancel-all` | `DELETE /orders/all/:slug` |
| Get open orders | `GET clob.polymarket.com/data/orders` | `GET /markets/:slug/user-orders` |
| Get order by ID | `GET clob.polymarket.com/data/order/:id` | `POST /orders/status/batch` |

### Portfolio

| Action | Polymarket (CLOB V2) | Limitless |
| - | - | - |
| Get positions | `GET data-api.polymarket.com/positions?user=0x...` | `GET /portfolio/positions` |
| Get trades | `GET clob.polymarket.com/data/trades?maker_address=0x...` | `GET /portfolio/trades` |
| PnL chart | N/A | `GET /portfolio/pnl-chart` |
| Trade history | `GET data-api.polymarket.com/activity?user=0x...` | `GET /portfolio/history` |

## Fetch a market

**Polymarket (V2)**

```python theme={null}
# Gamma for metadata, CLOB for trading, data-api for positions/activity
market = requests.get(
    "https://gamma-api.polymarket.com/markets/slug/will-trump-win"
).json()

# clobTokenIds and outcomes are parallel arrays — pair by index, don't assume [0] = Yes
token_ids = market["clobTokenIds"]
outcomes = market["outcomes"]
yes_idx = outcomes.index("Yes")
token_id = token_ids[yes_idx]

condition_id = market["conditionId"]
neg_risk = market["negRisk"]
tick_size = market["orderPriceMinTickSize"]
```

**Limitless**

```python theme={null}
# Market reads are public, but signing also works on any endpoint.
path = "/markets/will-trump-win"
market = requests.get(
    f"{API_BASE}{path}",
    headers=sign_request(TOKEN_ID, SECRET, "GET", path),
).json()

token_id = market["tokens"]["yes"]   # Yes token
venue = market["venue"]               # exchange + adapter addresses
```

No `conditionId`, `negRisk`, or `tickSize` needed in the order payload. The [venue system](https://docs.limitless.exchange/developers/venue-system.md) handles contract routing.

## Build and sign an order

Both sides use EIP-712 typed data, but the order field sets diverge in V2. Polymarket V2 dropped `taker`, `nonce`, `feeRateBps`, and `expiration` from the signed struct and added `timestamp`, `metadata`, and `builder`. Limitless keeps the classic CTF-style fields (`taker`, `expiration`, `nonce`, `feeRateBps`) and has no `timestamp`/`metadata`/`builder`. Key differences:

| Field | Polymarket (CLOB V2) | Limitless |
| - | - | - |
| `chainId` | `137` (Polygon) | `8453` (Base) |
| `verifyingContract` | CTF Exchange V2 `0xE111180000d2663C0091e4f400237545B87B996B` (Neg Risk: `0xe2222d279d744050d28e00520010520000310F59`) | `venue.exchange` from market data |
| `name` (EIP-712 domain) | `"Polymarket CTF Exchange"` (same for Neg Risk) | `"Limitless CTF Exchange"` |
| `version` (EIP-712 domain) | `"2"` | `"1"` |
| `tokenId` source | `clobTokenIds[i]` paired with `outcomes[i]` | `tokens.yes` / `tokens.no` |
| Fields dropped vs your V1 code | `taker`, `nonce`, `feeRateBps`, `expiration` | n/a |
| Fields added | `timestamp` (ms), `metadata`, `builder` | n/a |
| `feeRateBps` | Not in the signed order (removed in V2) | Must equal your `effectiveFeeRateBps` on fee-enabled markets; `0` on fee-disabled markets and on [new trading venues](https://docs.limitless.exchange/developers/venue-system.md#new-trading-venues) |

> [!WARNING]
>
> On fee-enabled markets (`metadata.fee: true`), sign with your profile's `effectiveFeeRateBps` from [`GET /profiles/me`](https://docs.limitless.exchange/api-reference/portfolio/get-current-profile). On fee-disabled markets, sign `0`. On [new trading venues](https://docs.limitless.exchange/developers/venue-system.md#new-trading-venues) (`venue.feeModuleType: "COLLATERAL"`), always sign `0`. If the API returns `FEE_RATE_MISMATCH`, build and sign a new order with `expectedFeeRateBps`. Polymarket V2 has no `feeRateBps` field.

**Polymarket (V2)**

```python theme={null}
from py_clob_client_v2 import OrderArgs, OrderType, PartialCreateOrderOptions, Side

resp = client.create_and_post_order(
    order_args=OrderArgs(token_id=token_id, price=0.50, size=10, side=Side.BUY),
    options=PartialCreateOrderOptions(tick_size="0.01"),
    order_type=OrderType.GTC,
)
```

**Limitless**

```python theme={null}
import json, time
import requests
from eth_account import Account
from eth_account.messages import encode_typed_data
from web3 import Web3

account = Account.from_key(private_key)
price, shares = 0.50, 10
maker_amount = int(price * shares * 1e6)
taker_amount = int(shares * 1e6)
fee_rate_bps = 0  # always 0 on new trading venues (feeModuleType "COLLATERAL")
if market["venue"].get("feeModuleType") != "COLLATERAL" and (market.get("metadata") or {}).get("fee"):
    path = "/profiles/me"
    profile_resp = requests.get(
        f"{API}{path}",
        headers=sign_request("GET", path),
    )
    profile_resp.raise_for_status()
    fee_rate_bps = profile_resp.json()["effectiveFeeRateBps"]

order_data = {
    "salt": int(time.time() * 1000),
    "maker": Web3.to_checksum_address(account.address),
    "signer": Web3.to_checksum_address(account.address),
    "taker": "0x0000000000000000000000000000000000000000",
    "tokenId": token_id,
    "makerAmount": maker_amount,
    "takerAmount": taker_amount,
    "expiration": 0,
    "nonce": 0,
    "feeRateBps": fee_rate_bps,
    "side": 0,          # 0=BUY, 1=SELL
    "signatureType": 0,  # EOA
}

domain = {
    "name": "Limitless CTF Exchange",
    "version": "1",
    "chainId": 8453,
    "verifyingContract": Web3.to_checksum_address(venue["exchange"]),
}
types = {
    "EIP712Domain": [
        {"name": "name", "type": "string"},
        {"name": "version", "type": "string"},
        {"name": "chainId", "type": "uint256"},
        {"name": "verifyingContract", "type": "address"},
    ],
    "Order": [
        {"name": "salt", "type": "uint256"},
        {"name": "maker", "type": "address"},
        {"name": "signer", "type": "address"},
        {"name": "taker", "type": "address"},
        {"name": "tokenId", "type": "uint256"},
        {"name": "makerAmount", "type": "uint256"},
        {"name": "takerAmount", "type": "uint256"},
        {"name": "expiration", "type": "uint256"},
        {"name": "nonce", "type": "uint256"},
        {"name": "feeRateBps", "type": "uint256"},
        {"name": "side", "type": "uint8"},
        {"name": "signatureType", "type": "uint8"},
    ],
}
encoded = encode_typed_data({
    "types": types,
    "primaryType": "Order",
    "domain": domain,
    "message": order_data,
})
signed = Account.sign_message(encoded, private_key=private_key)
signature = signed.signature.hex()

path = "/orders"
body = json.dumps({
    # expiration is signed as uint256 0 but sent as the string "0"; price is wire-only and required for GTC
    "order": {**order_data, "expiration": "0", "price": price, "signature": signature},
    "ownerId": owner_id,
    "orderType": "GTC",
    "marketSlug": "will-trump-win",
})
auth_headers = sign_request(TOKEN_ID, SECRET, "POST", path, body)
auth_headers["Content-Type"] = "application/json"
resp = requests.post(f"{API_BASE}{path}", headers=auth_headers, data=body)
```

> [!NOTE]
>
> `ownerId` is your Limitless profile ID — a required field on every `POST /orders` request. Fetch it once from [`GET /profiles/me`](https://docs.limitless.exchange/api-reference/portfolio/get-current-profile) (the `id` field) and cache it. Polymarket's SDK handles this internally; on Limitless you pass it explicitly.

> [!TIP]
>
> If you use the [Python SDK](https://docs.limitless.exchange/developers/sdk/python/getting-started.md), [TypeScript SDK](https://docs.limitless.exchange/developers/sdk/typescript/getting-started.md), [Go SDK](https://docs.limitless.exchange/developers/sdk/go/getting-started.md), or [Rust SDK](https://docs.limitless.exchange/developers/sdk/rust/getting-started.md), order building and signing are handled for you — similar to how Polymarket's V2 CLOB clients (`@polymarket/clob-client-v2`, `py_clob_client_v2`) work.

## Porting a Polymarket agent

If you're adapting a Polymarket trading bot (a V2 CLOB client integration, or a port of the now-archived `Polymarket/agents` framework), here's a checklist:

**1. Swap credentials**

Replace `POLYGON_WALLET_PRIVATE_KEY` with your existing private key on Base. Add your scoped API token (`TOKEN_ID` + `SECRET`) and sign each request with HMAC (`lmts-api-key`/`lmts-timestamp`/`lmts-signature`) instead of Polymarket's `POLY_*` headers. You still drop Polymarket's L1/L2 credential derivation — Limitless tokens are issued in the UI.

**2. Collapse the three hosts into one**

Replace `gamma-api.polymarket.com`, `clob.polymarket.com`, and `data-api.polymarket.com` all with `api.limitless.exchange`. Positions and history that you read from `data-api` move to `/portfolio/*`.

**3. Change chain ID**

Update `chainId` from `137` to `8453` in all EIP-712 domain definitions.

**4. Update EIP-712 domain**

Change the domain `name` from `"Polymarket CTF Exchange"` to `"Limitless CTF Exchange"`, and the `version` from `"2"` to `"1"`.

**5. Swap token ID fields**

Replace `clobTokenIds` lookups with the market's `tokens` object. On Limitless the convention is fixed: `tokens.yes` = Yes, `tokens.no` = No (unlike Polymarket, where you pair `clobTokenIds` against `outcomes`).

**6. Use venue addresses**

Fetch `venue.exchange` from `GET /markets/:slug` and use it as `verifyingContract`. On Polymarket V2 you targeted the fixed CTF Exchange V2 contract — on Limitless each market can have its own venue.

**7. Rework the order fields**

Remove the V2 fields `timestamp`, `metadata`, and `builder` — Limitless doesn't use them. Add back the classic CTF fields Limitless requires: `taker`, `expiration`, `nonce`, and `feeRateBps`. Also drop SDK-side params like `tick_size` and `signature_type` from your order construction.

**8. Add ownerId to order submissions**

`POST /orders` requires an `ownerId` field (your Limitless profile ID, from [`GET /profiles/me`](https://docs.limitless.exchange/api-reference/portfolio/get-current-profile)). Polymarket's SDK handles this internally; on Limitless you pass it explicitly in every order payload alongside `order`, `orderType`, and `marketSlug`.

**9. Update approvals**

Approve USDC on Base (not pUSD on Polygon) to `venue.exchange`. For NegRisk SELL orders, also approve Conditional Tokens to `venue.adapter`. On [new trading venues](https://docs.limitless.exchange/developers/venue-system.md#new-trading-venues), also approve USDC to `venue.feeModule`. See [venue system](https://docs.limitless.exchange/developers/venue-system.md).

## WebSocket

| | Polymarket (CLOB V2) | Limitless |
| - | - | - |
| **URL** | `wss://ws-subscriptions-clob.polymarket.com/ws/market` and `/ws/user` | `wss://ws.limitless.exchange` |
| **Namespace** | Channel-based (`market`, `user`) | Socket.IO namespace `/markets` |
| **Auth** | `auth` object (`apiKey`, `secret`, `passphrase`) in the user-channel subscribe message | HMAC auth headers (`lmts-api-key`/`lmts-timestamp`/`lmts-signature`) during handshake |

See [WebSocket events](https://docs.limitless.exchange/developers/websocket/overview.md) for the full event reference.

## Quick reference for agents

If you're building an LLM-powered agent or bot, here's the minimal flow:

```python theme={null}
import os, json, time, hmac, hashlib, base64, requests
from datetime import datetime, timezone
from eth_account import Account
from eth_account.messages import encode_typed_data
from web3 import Web3

API = "https://api.limitless.exchange"
TOKEN_ID = os.environ["LMTS_TOKEN_ID"]      # scoped API token id
SECRET   = os.environ["LMTS_TOKEN_SECRET"]  # base64-encoded secret
PK  = os.environ["PRIVATE_KEY"]      # 0x...
OWNER_ID = int(os.environ["OWNER_ID"])  # Profile ID from GET /profiles/me

def sign_request(method: str, path: str, body: str = "") -> dict:
    timestamp = datetime.now(timezone.utc).isoformat()
    message = f"{timestamp}\n{method}\n{path}\n{body}"
    signature = base64.b64encode(
        hmac.new(base64.b64decode(SECRET), message.encode("utf-8"), hashlib.sha256).digest()
    ).decode("utf-8")
    return {"lmts-api-key": TOKEN_ID, "lmts-timestamp": timestamp, "lmts-signature": signature}

CHAIN_ID = 8453
ZERO_ADDR = "0x0000000000000000000000000000000000000000"
ORDER_TYPES = {
    "EIP712Domain": [
        {"name": "name", "type": "string"},
        {"name": "version", "type": "string"},
        {"name": "chainId", "type": "uint256"},
        {"name": "verifyingContract", "type": "address"},
    ],
    "Order": [
        {"name": "salt", "type": "uint256"},
        {"name": "maker", "type": "address"},
        {"name": "signer", "type": "address"},
        {"name": "taker", "type": "address"},
        {"name": "tokenId", "type": "uint256"},
        {"name": "makerAmount", "type": "uint256"},
        {"name": "takerAmount", "type": "uint256"},
        {"name": "expiration", "type": "uint256"},
        {"name": "nonce", "type": "uint256"},
        {"name": "feeRateBps", "type": "uint256"},
        {"name": "side", "type": "uint8"},
        {"name": "signatureType", "type": "uint8"},
    ],
}

# 1. Find a market
markets = requests.get(
    f"{API}/markets/active",
    headers=sign_request("GET", "/markets/active"),
).json()
slug = markets["data"][0]["slug"]  # rows with a nested "markets" list are groups; pick a child slug for trading

# 2. Get venue + token IDs (cache per market — these are static)
market_path = f"/markets/{slug}"
market = requests.get(
    f"{API}{market_path}",
    headers=sign_request("GET", market_path),
).json()
venue_exchange = market["venue"]["exchange"]
yes_token = market["tokens"]["yes"]
fee_rate_bps = 0  # always 0 on new trading venues (feeModuleType "COLLATERAL")
if market["venue"].get("feeModuleType") != "COLLATERAL" and (market.get("metadata") or {}).get("fee"):
    profile = requests.get(
        f"{API}/profiles/me",
        headers=sign_request("GET", "/profiles/me"),
    )
    profile.raise_for_status()
    fee_rate_bps = profile.json()["effectiveFeeRateBps"]

# 3. Build order (BUY 10 YES shares at $0.50)
acct = Account.from_key(PK)
order = {
    "salt": int(time.time() * 1000),
    "maker": Web3.to_checksum_address(acct.address),
    "signer": Web3.to_checksum_address(acct.address),
    "taker": ZERO_ADDR,
    "tokenId": yes_token,
    "makerAmount": 5_000_000,   # 0.50 * 10 * 1e6
    "takerAmount": 10_000_000,  # 10 * 1e6
    "expiration": 0,
    "nonce": 0,
    "feeRateBps": fee_rate_bps,
    "side": 0,
    "signatureType": 0,
}

# 4. Sign (EIP-712) — same encode_typed_data mechanism as Polymarket, different fields
encoded = encode_typed_data({
    "types": ORDER_TYPES,
    "primaryType": "Order",
    "domain": {
        "name": "Limitless CTF Exchange",
        "version": "1",
        "chainId": CHAIN_ID,
        "verifyingContract": Web3.to_checksum_address(venue_exchange),
    },
    "message": order,
})
sig = Account.sign_message(encoded, private_key=PK).signature.hex()

# 5. Submit (HMAC-sign the request over method + path + body)
order_body = json.dumps({
    # expiration is signed as uint256 0 but sent as the string "0"; price is wire-only and required for GTC
    "order": {**order, "expiration": "0", "price": 0.50, "signature": sig},
    "ownerId": OWNER_ID,
    "orderType": "GTC",
    "marketSlug": slug,
})
order_headers = sign_request("POST", "/orders", order_body)
order_headers["Content-Type"] = "application/json"
resp = requests.post(f"{API}/orders", headers=order_headers, data=order_body)
print(resp.json())
```

## Partner and platform migrations

If you're migrating a platform that manages multiple user accounts on Polymarket (e.g., a trading desk, social trading app, or embedded prediction market), the Limitless [Programmatic API](https://docs.limitless.exchange/developers/programmatic-api.md) provides a first-class partner flow:

| Polymarket pattern | Limitless equivalent |
| - | - |
| Manage many wallets and private keys | Create sub-accounts with server-managed wallets — no private key management |
| Sign orders per-user with their keys | [Delegated signing](https://docs.limitless.exchange/developers/programmatic-api.md#delegated-order-types) — server signs via Privy, submit unsigned orders |
| Derive HMAC creds per integration | Derive [scoped API tokens](https://docs.limitless.exchange/developers/authentication.md#scoped-api-tokens-hmac) with granular permissions |

> [!NOTE]
>
> **Recommended setup for partners:**
>
> * Store HMAC credentials on your backend — never expose them to frontends
> * Use the SDK server-side to sign partner-authenticated requests
> * Expose only your own app-specific endpoints to the frontend
> * Keep public market reads (orderbooks, prices) directly in the browser

GTC (limit), FAK (fill-and-kill) and FOK (fill-or-kill) order types are supported for delegated orders. See the [Delegated Orders](https://docs.limitless.exchange/developers/sdk/typescript/delegated-orders.md) SDK pages for full examples.

## Next steps

> **[Python quick start](https://docs.limitless.exchange/developers/quickstart/python.md)**
>
> Full end-to-end walkthrough with error handling.

> **[Venue system](https://docs.limitless.exchange/developers/venue-system.md)**
>
> How venue contracts and token approvals work.

> **[Programmatic API](https://docs.limitless.exchange/developers/programmatic-api.md)**
>
> Partner integrations, sub-accounts, and delegated signing.

> **[API reference](https://docs.limitless.exchange/api-reference/introduction.md)**
>
> Complete endpoint documentation.

> **[EIP-712 signing](https://docs.limitless.exchange/developers/eip712-signing.md)**
>
> Full order type definition and field reference.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.