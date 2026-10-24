> ## Documentation Index
> Fetch the complete documentation index at: https://docs.limitless.exchange/llms.txt
> Use this file to discover all available pages before exploring further.

# API Reference

> Complete REST API documentation for Limitless Exchange

## Base URL

```
https://api.limitless.exchange
```

The raw OpenAPI document is served at [https://api.limitless.exchange/api-json](https://api.limitless.exchange/api-json); this site is the interactive reference.

This is a single global endpoint. There are no regional base URLs or region selection. All clients use the same base URL regardless of location.

> [!NOTE]
>
> Building on the API? Join the [Limitless Builders Chat](https://t.me/LimitlessBuildersChat) on Telegram for API/SDK updates, help, and to connect with other builders.

## Authentication

Most endpoints require authentication via **scoped API tokens** with HMAC-SHA256 request signing:

| Method | Headers | Use case |
| - | - | - |
| **Scoped API Token (HMAC)** | `lmts-api-key`, `lmts-timestamp`, `lmts-signature` | All integrations — traders, bots, partners, delegated signing |

> [!NOTE]
>
> Public endpoints like market browsing and orderbook data do **not** require authentication. All authenticated requests use [scoped API tokens with HMAC signing](https://docs.limitless.exchange/developers/authentication.md) (legacy static API-key headers are deprecated and no longer issued).

See the [Authentication guide](https://docs.limitless.exchange/developers/authentication.md) for HMAC signing details, or the [Programmatic API guide](https://docs.limitless.exchange/developers/programmatic-api.md) for the full partner integration workflow.

## Endpoint groups

> **[Authentication](https://docs.limitless.exchange/api-reference/api-tokens/derive-token.md)**
>
> Derive and manage scoped API tokens for authentication.

> **[API Tokens](https://docs.limitless.exchange/api-reference/api-tokens/derive-token.md)**
>
> Scoped API token management for partner integrations — derive, list, and revoke HMAC-authenticated tokens.

> **[Markets](https://docs.limitless.exchange/api-reference/markets/browse-active.md)**
>
> Browse active markets, search, get details and feed events.

> **[Trading](https://docs.limitless.exchange/api-reference/trading/create-order.md)**
>
> Create and cancel orders, batch order status, orderbook, historical prices, and user orders.

> **[System](https://docs.limitless.exchange/api-reference/system/maintenance-status.md)**
>
> Check public maintenance status and temporary trading restrictions.

> **[Partner Accounts](https://docs.limitless.exchange/api-reference/partner-accounts/create-partner-account.md)**
>
> Create and manage sub-accounts for partner integrations.

> **[Portfolio](https://docs.limitless.exchange/api-reference/portfolio/positions.md)**
>
> Positions, trades, PnL chart, history, points, and allowance.

> **[Public Portfolio](https://docs.limitless.exchange/api-reference/public-portfolio/positions.md)**
>
> Public user positions, traded volume, and PnL data.

## Key concepts

| Concept | Description |
| - | - |
| **Venue system** | Each CLOB market has a venue with `exchange` and `adapter` addresses. Fetch via `GET /markets/:slug`. See [Venue System](https://docs.limitless.exchange/developers/venue-system.md). |
| **EIP-712 signing** | Orders are signed using the venue's `exchange` address as `verifyingContract`. See [EIP-712 Signing](https://docs.limitless.exchange/developers/eip712-signing.md). |
| **Order types** | **GTC** (Good-til-cancelled) rests on the orderbook. **FOK** (Fill-or-kill) fills in full immediately or is killed. **FAK** (Fill-and-kill) fills what it can immediately and kills the remainder. |
| **Token IDs** | Each market returns YES and NO token IDs in `tokens` (`tokens.yes` / `tokens.no`). Use these as `tokenId` in orders. |
| **USDC decimals** | USDC on Base has 6 decimals. Amounts are scaled by 1e6. |
| **Receive window** | Optional `timestamp` + `recvWindow` on `POST /orders` reject stale signed orders with HTTP `425`. Opt-in (default disabled). See [Receive Window](https://docs.limitless.exchange/api-reference/trading/create-order.md#receive-window). |
| **Maintenance mode** | Trading can be temporarily restricted during maintenance. Check [`GET /maintenance/status`](https://docs.limitless.exchange/api-reference/system/maintenance-status) and handle `425` responses with a trading-mode `code` from trading endpoints. |

## WebSocket API

For real-time orderbook and position updates, see the [WebSocket Events](https://docs.limitless.exchange/developers/websocket/overview.md) reference.

**URL:** `wss://ws.limitless.exchange` | **Namespace:** `/markets`

## Rate limits

The API enforces rate limits. When you exceed a limit, requests return HTTP `429 Too Many Requests`. Handle `429` responses with:

* **Respect `Retry-After`** — when present on a `429` response, wait for that many seconds before retrying.
* **Exponential backoff** — if no `Retry-After` header is returned, back off starting at 1 second and double on each retry.
* **Throttle at the source** — for high-frequency workloads (e.g. market making), queue outgoing orders instead of firing them concurrently. The TypeScript SDK ships an [`OrderQueue`](https://docs.limitless.exchange/developers/sdk/typescript/error-handling#rate-limiting-with-orderqueue); Python, Go, and Rust SDKs expose configurable retry-on-429 helpers in their error-handling guides.
* **Never retry `400` or `401`** — those indicate a bad request or invalid credentials and will not succeed on retry.

Partner allowance endpoints return a `retryAfterSeconds` field on `429` — see [Retry Partner Account Allowances](https://docs.limitless.exchange/api-reference/partner-accounts/retry-allowances.md).

For higher published limits or a dedicated quota, contact [help@limitless.network](mailto:help@limitless.network).


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.