> ## Documentation Index
> Fetch the complete documentation index at: https://docs.limitless.exchange/llms.txt
> Use this file to discover all available pages before exploring further.

# WebSocket Overview

> Connection details, handshake authentication, and the event reference for the Limitless WebSocket API

This page covers how to connect to the Limitless WebSocket API, how to sign the handshake for authenticated channels, and the full list of client and server events. Each subscription has its own page pairing the subscribe call with the payloads it delivers.

## Connection

**URL:** `wss://ws.limitless.exchange`
**Namespace:** `/markets`
**Transport:** WebSocket only (no polling fallback)

> [!NOTE]
>
> **No client PING required.** The server runs the Socket.IO heartbeat (server-initiated `ping` / client `pong`) automatically. Every official Socket.IO client (JavaScript, Python `python-socketio`, Go, Rust) responds to it out of the box. Do not send your own PING frames. Keep the connection open and rely on the built-in heartbeat and the auto-reconnect flow in [WebSocket quick start](https://docs.limitless.exchange/developers/quickstart/websocket.md#auto-reconnection).

> [!WARNING]
>
> **Connections close after 24 hours.** Our load balancer closes every WebSocket connection 24 hours after it opens, whether or not it is active. The close arrives without a close frame, so your client sees code `1006`. Reconnect with freshly signed HMAC headers (the original handshake timestamp is past the 30-second window) and re-emit your subscriptions, since the server does not keep them across connections. The example below and the [quick start client](https://docs.limitless.exchange/developers/quickstart/websocket.md#auto-reconnection) both re-sign on reconnect. To avoid a gap, open a second connection shortly before the 24-hour mark and switch over.

Authenticated channels (positions, order events) require an HMAC-signed handshake. Sign a fixed canonical message — `{ISO-8601 timestamp}\nGET\n/socket.io/?EIO=4&transport=websocket\n` — with the base64-decoded `secret` and pass three headers as `extraHeaders`:

```typescript theme={null}
import { createHmac } from 'crypto';
import { io } from 'socket.io-client';

function wsAuthHeaders(tokenId: string, secret: string) {
  const timestamp = new Date().toISOString();
  const message = `${timestamp}\nGET\n/socket.io/?EIO=4&transport=websocket\n`;
  const signature = createHmac('sha256', Buffer.from(secret, 'base64'))
    .update(message)
    .digest('base64');
  return { 'lmts-api-key': tokenId, 'lmts-timestamp': timestamp, 'lmts-signature': signature };
}

const socket = io('wss://ws.limitless.exchange/markets', {
  transports: ['websocket'],
  extraHeaders: wsAuthHeaders(TOKEN_ID, SECRET),
});

// Socket.IO replays the original headers on reconnect, and their timestamp is
// stale by then. Re-sign before every attempt.
socket.io.on('reconnect_attempt', () => {
  socket.io.opts.extraHeaders = wsAuthHeaders(TOKEN_ID, SECRET);
});
```

See [Authentication](https://docs.limitless.exchange/developers/authentication.md) for how to generate `TOKEN_ID` and `SECRET`. If you use an official SDK, prefer its WebSocket client, which signs the handshake automatically from `hmacCredentials` (TypeScript) / `hmac_credentials` (Python) / `WithHMACCredentials` (Go).

> [!WARNING]
>
> **Authenticated subscribes must be sent within 30 seconds of the handshake timestamp.** The server re-validates the handshake HMAC headers on every `subscribe_positions`, `subscribe_order_events`, and `subscribe_transactions` message and rejects any whose `lmts-timestamp` is more than 30 seconds from the server clock with an `exception` carrying `Invalid HMAC authentication`. Emit these subscriptions immediately after `connect`. To change an authenticated subscription later (for example to narrow `subscribe_positions`), open a new connection with freshly signed headers; a re-emit on a connection older than 30 seconds is rejected. Public channels are not affected.

## Event reference

| Event | Direction | Auth required | Description |
| - | - | - | - |
| `connect` | Server → Client | No | Connection established |
| `disconnect` | Server → Client | No | Connection lost |
| `subscribe_market_prices` | Client → Server | No | Subscribe to price/orderbook updates |
| `subscribe_positions` | Client → Server | Yes | Subscribe to position updates |
| `subscribe_order_events` | Client → Server | Yes | Subscribe to OME and settlement events for your CLOB orders |
| `subscribe_transactions` | Client → Server | Yes | Subscribe to settlement results for your own transactions (`tx`) |
| `subscribe_market_lifecycle` | Client → Server | No | Subscribe to market creation, schedule, and resolution events, optionally filtered by `categoryIds` |
| `unsubscribe_market_lifecycle` | Client → Server | No | Unsubscribe from market lifecycle events |
| `subscribe_oracle_price_data` | Client → Server | No | Subscribe to oracle price feeds for the given markets (same `marketAddresses` / `marketSlugs` payload; legacy alias `subscribe_chainlink_oracle_data`) |
| `unsubscribe_oracle_price_data` | Client → Server | No | Unsubscribe from oracle price feeds (legacy alias `unsubscribe_chainlink_oracle_data`) |
| `subscribe_unrealized_pnl` | Client → Server | No | Subscribe to Unrealized PnL leaderboard invalidation hints |
| `unsubscribe_unrealized_pnl` | Client → Server | No | Unsubscribe from Unrealized PnL invalidation hints |
| `unrealizedPnlProjectionChanged` | Server → Client | No | Hint that a subscribed Unrealized PnL leaderboard changed; refetch the REST route |
| `newPriceData` | Server → Client | No | AMM market price update |
| `orderbookUpdate` | Server → Client | No | CLOB orderbook update |
| `oraclePriceData` | Server → Client | No | Oracle price update for a subscribed market |
| `marketCreated` | Server → Client | No | New market created and visible |
| `marketUpdated` | Server → Client | No | A sports or esports match's start time, deadline, or match status changed |
| `marketResolved` | Server → Client | No | Market resolved with a single winning outcome (not sent for split resolutions) |
| `positions` | Server → Client | Yes | Position balance update |
| `orderEvent` | Server → Client | Yes | OME lifecycle, FAK/FOK execution, and settlement updates for your CLOB orders |
| `tx` | Server → Client | Yes | Settlement result for one of your transactions (`status` is `CONFIRMED` or `FAILED`) |
| `system` | Server → Client | No | System notifications |
| `exception` | Server → Client | No | Error notifications |
| `error` | Server → Client | No | Error frame: `{ message }` or `{ code, message }` |

There is no authentication confirmation event. A successful authenticated subscribe is acknowledged only by that channel's `system` message; a failed one surfaces on `exception`.

The server also handles `subscribe_live_sports`, `subscribe_live_esports`, `subscribe_ugm_live_offers` and `unsubscribe_ugm_live_offers`. These channels are not documented and are subject to change.

## Unsubscribing

There is no generic `unsubscribe` event. Only two channels have an explicit unsubscribe: `unsubscribe_market_lifecycle` and `unsubscribe_unrealized_pnl`.

`subscribe_market_prices`, `subscribe_positions`, and `subscribe_order_events` have none. Each of those **replaces** its previous subscription on the same connection when you emit it again, so to drop a market you re-emit the subscribe with the smaller set (for the authenticated channels, only within 30 seconds of the handshake; otherwise reconnect). To stop everything, disconnect. An unsubscribe event name that the server does not register never gets an acknowledgement, so a client waiting on one times out.

## Related

Each subscription has its own page pairing the subscribe call with the payloads it delivers:

* [Market data](https://docs.limitless.exchange/developers/websocket/market-data.md): `subscribe_market_prices`, `newPriceData`, `orderbookUpdate`
* [Positions](https://docs.limitless.exchange/developers/websocket/positions.md): `subscribe_positions`, `positions`
* [Order events](https://docs.limitless.exchange/developers/websocket/order-events.md): `subscribe_order_events`, `orderEvent`
* [Market lifecycle](https://docs.limitless.exchange/developers/websocket/market-lifecycle.md): `subscribe_market_lifecycle`, `unsubscribe_market_lifecycle`, `marketCreated`, `marketUpdated`, `marketResolved`
* [Unrealized PnL](https://docs.limitless.exchange/developers/websocket/unrealized-pnl.md): `subscribe_unrealized_pnl`, `unsubscribe_unrealized_pnl`, `unrealizedPnlProjectionChanged`


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.