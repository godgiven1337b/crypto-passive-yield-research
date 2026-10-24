> ## Documentation Index
> Fetch the complete documentation index at: https://docs.limitless.exchange/llms.txt
> Use this file to discover all available pages before exploring further.

# WebSocket Integration

> Real-time market data and position updates using Python WebSocket client

## Overview

The Limitless WebSocket API provides real-time market prices, orderbook updates, and position notifications. This guide covers connecting with Python using `python-socketio` with asyncio.

## Prerequisites

**1. Install dependencies**

Install the required packages:

```bash theme={null}
pip install "python-socketio[asyncio]" eth-account==0.10.0 requests
```

> [!TIP]
>
> Use a virtual environment to isolate dependencies. Run `python -m venv venv` then `source venv/bin/activate` (Unix) or `venv\Scripts\activate` (Windows) before installing.

## Authentication modes

**Public (no auth)**

Connect without authentication to receive **public market data** only:

* `newPriceData` (AMM market prices)
* `orderbookUpdate` (CLOB orderbook)
* `system` (system notifications)

No API key required. Use this for read-only market monitoring.

**Authenticated (HMAC)**

Sign the connection handshake with your scoped API token for **authenticated features**:

* All public events
* `positions` (position balance updates)

Required for `subscribe_positions`. Pass three HMAC headers (`lmts-api-key`, `lmts-timestamp`, `lmts-signature`) during the handshake — see [Authentication](https://docs.limitless.exchange/developers/authentication.md). Generate a scoped API token at [limitless.exchange](https://limitless.exchange) → profile → Api keys.

> [!WARNING]
>
> **Never** commit your API token ID or secret to version control or expose them in client-side code. Use environment variables (e.g. `LMTS_TOKEN_ID` / `LMTS_TOKEN_SECRET`) and load them at runtime.

> [!NOTE]
>
> Cookie-based session authentication is **deprecated**. Authenticate the handshake with HMAC-signed headers (`lmts-api-key`, `lmts-timestamp`, `lmts-signature`) — see [Authentication](https://docs.limitless.exchange/developers/authentication.md).

## Connection details

| Setting | Value |
| - | - |
| **URL** | `wss://ws.limitless.exchange` |
| **Namespace** | `/markets` |
| **Transport** | WebSocket only (no polling) |

Authenticated connections sign the Socket.IO handshake with HMAC. The signed canonical message uses a fixed path and empty body, and the HMAC key is the base64-decoded `secret`:

```python ws_auth.py theme={null}
import base64
import hashlib
import hmac
from datetime import datetime, timezone


def ws_auth_headers(token_id: str, secret: str) -> dict:
    timestamp = datetime.now(timezone.utc).isoformat()
    message = f"{timestamp}\nGET\n/socket.io/?EIO=4&transport=websocket\n"
    signature = base64.b64encode(
        hmac.new(
            base64.b64decode(secret), message.encode("utf-8"), hashlib.sha256
        ).digest()
    ).decode("utf-8")
    return {
        "lmts-api-key": token_id,
        "lmts-timestamp": timestamp,
        "lmts-signature": signature,
    }
```

See [Authentication](https://docs.limitless.exchange/developers/authentication.md) for how to generate the token ID and secret.

```python Public (no auth) theme={null}
import asyncio
import os
import socketio

sio = socketio.AsyncClient(logger=os.environ.get("DEBUG") == "1")

@sio.event(namespace="/markets")
async def connect():
    print("Connected to /markets")

async def main():
    await sio.connect(
        "wss://ws.limitless.exchange",
        transports=["websocket"],
        namespaces=["/markets"],
    )
    await sio.wait()

asyncio.run(main())
```

```python Authenticated (HMAC) theme={null}
import asyncio
import os
import socketio

from ws_auth import ws_auth_headers

token_id = os.environ.get("LMTS_TOKEN_ID")
secret = os.environ.get("LMTS_TOKEN_SECRET")
if not token_id or not secret:
    raise ValueError("LMTS_TOKEN_ID and LMTS_TOKEN_SECRET environment variables required")

sio = socketio.AsyncClient(logger=os.environ.get("DEBUG") == "1")

@sio.event(namespace="/markets")
async def connect():
    print("Connected to /markets")

async def main():
    await sio.connect(
        "wss://ws.limitless.exchange",
        transports=["websocket"],
        namespaces=["/markets"],
        # A function, not a dict, so every reconnect is signed with a fresh timestamp
        headers=lambda: ws_auth_headers(token_id, secret),
    )
    await sio.wait()

asyncio.run(main())
```

## Subscribing to market prices

Emit `subscribe_market_prices` with market identifiers. Subscriptions **replace** previous ones, so include all markets you want in a single call.

```python AMM markets (contract addresses) theme={null}
# Market addresses are Ethereum contract addresses in hex format
await sio.emit(
    "subscribe_market_prices",
    {"marketAddresses": ["0x1234567890abcdef1234567890abcdef12345678"]},
    namespace="/markets",
)
```

```python CLOB markets (slugs) theme={null}
# Use human-readable slugs for CLOB orderbook markets
await sio.emit(
    "subscribe_market_prices",
    {"marketSlugs": ["btc-100k-weekly", "eth-daily"]},
    namespace="/markets",
)
```

```python Both AMM and CLOB theme={null}
# Include both to avoid overwriting subscriptions
await sio.emit(
    "subscribe_market_prices",
    {
        "marketAddresses": ["0x1234567890abcdef1234567890abcdef12345678"],
        "marketSlugs": ["btc-100k-weekly"],
    },
    namespace="/markets",
)
```

> [!WARNING]
>
> Subscriptions **replace** previous ones. If you want both AMM prices and CLOB orderbook, send both `marketAddresses` and `marketSlugs` together in a single `subscribe_market_prices` call.

> [!NOTE]
>
> The server answers every `subscribe_market_prices` call, first or repeat, with one `orderbookUpdate` per CLOB slug carrying the full current book, including books with empty `bids` and `asks`. You do not need a REST call to seed local state. See [Initial snapshot](https://docs.limitless.exchange/developers/websocket/market-data.md#initial-snapshot).

## Subscribing to positions

Position updates require authentication. Emit `subscribe_positions` after connecting. Pass the markets you want position updates for (`marketSlugs` and/or `marketAddresses`); an empty payload is ignored server-side.

```python theme={null}
# Requires HMAC auth headers during the handshake (see ws_auth_headers above)
await sio.emit("subscribe_positions", {"marketSlugs": ["your-market-slug"]}, namespace="/markets")
```

## Handling events

Register handlers for each event type. All handlers use `namespace="/markets"`.

| Event | Auth required | Description |
| - | - | - |
| `newPriceData` | No | AMM market price update |
| `orderbookUpdate` | No | CLOB orderbook update |
| `positions` | Yes | Position balance update |
| `system` | No | System notifications |
| `exception` | No | Unhandled gateway exception, e.g. unauthorized `subscribe_positions`: `{ "status": "error", "message": "..." }` |
| `error` | No | Subscription rejected: `{ "message": "..." }` (missing marketSlugs/marketAddresses, all requested markets resolved, subscribe failure) |

### Event payloads

**`newPriceData`** — AMM market price update. Live updates carry `updatedPrices` as an array and no top-level `marketAddress`:

```json theme={null}
{
  "updatedPrices": [
    { "marketAddress": "0x1234...", "marketId": 123, "yesPrice": 0.65, "noPrice": 0.35 }
  ],
  "blockNumber": 12345678,
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

The initial snapshot sent after subscribing carries a top-level `marketAddress` and an `updatedPrices` object:

```json theme={null}
{
  "marketAddress": "0x1234...",
  "updatedPrices": {
    "collateralDecimals": 6,
    "marketAddress": "0x1234...",
    "marketId": 123,
    "yesPrice": 0.65,
    "noPrice": 0.35
  },
  "blockNumber": 0,
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

**`positions`** — Position balance update (auth required):

```json theme={null}
{
  "account": "0xabcd...",
  "marketAddress": "0x1234...",
  "positions": [
    { "tokenId": "123456", "balance": "1000000", "outcomeIndex": 0 }
  ],
  "type": "AMM"
}
```

**`system`** — System notification:

```json theme={null}
{
  "message": "Notification text",
  "markets": ["0x1234..."]
}
```

## Complete async Python client

```python limitless_ws_client.py theme={null}
import asyncio
import base64
import hashlib
import hmac
import logging
import os
from datetime import datetime, timezone
from typing import Optional

import socketio

logging.basicConfig(
    level=logging.DEBUG if os.environ.get("DEBUG") == "1" else logging.INFO
)
logger = logging.getLogger(__name__)

WS_URL = "wss://ws.limitless.exchange"
NAMESPACE = "/markets"


def ws_auth_headers(token_id: str, secret: str) -> dict:
    timestamp = datetime.now(timezone.utc).isoformat()
    message = f"{timestamp}\nGET\n/socket.io/?EIO=4&transport=websocket\n"
    signature = base64.b64encode(
        hmac.new(
            base64.b64decode(secret), message.encode("utf-8"), hashlib.sha256
        ).digest()
    ).decode("utf-8")
    return {
        "lmts-api-key": token_id,
        "lmts-timestamp": timestamp,
        "lmts-signature": signature,
    }


class LimitlessWebSocketClient:
    def __init__(
        self,
        token_id: Optional[str] = None,
        secret: Optional[str] = None,
    ):
        self.token_id = token_id or os.environ.get("LMTS_TOKEN_ID")
        self.secret = secret or os.environ.get("LMTS_TOKEN_SECRET")
        self.sio = socketio.AsyncClient(
            reconnection=True,
            reconnection_attempts=0,
            logger=os.environ.get("DEBUG") == "1",
        )
        self._market_addresses: list[str] = []
        self._market_slugs: list[str] = []
        self._subscribe_positions = False
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        @self.sio.event(namespace=NAMESPACE)
        async def connect():
            logger.info("Connected to %s", NAMESPACE)
            await self._resubscribe()

        @self.sio.event(namespace=NAMESPACE)
        async def disconnect():
            logger.info("Disconnected from %s", NAMESPACE)

        @self.sio.event(namespace=NAMESPACE)
        async def newPriceData(data: dict):
            logger.info("Price update: %s", data)

        @self.sio.event(namespace=NAMESPACE)
        async def orderbookUpdate(data: dict):
            logger.info("Orderbook update: %s", data)

        @self.sio.event(namespace=NAMESPACE)
        async def positions(data: dict):
            logger.info("Positions: %s", data)

        @self.sio.event(namespace=NAMESPACE)
        async def system(data: dict):
            logger.info("System: %s", data)

        @self.sio.event(namespace=NAMESPACE)
        async def exception(data: dict):
            logger.error("Exception: %s", data)

        @self.sio.event(namespace=NAMESPACE)
        async def error(data: dict):
            logger.error("Subscription rejected: %s", data)

    async def _resubscribe(self) -> None:
        if self._market_addresses or self._market_slugs:
            payload = {}
            if self._market_addresses:
                payload["marketAddresses"] = self._market_addresses
            if self._market_slugs:
                payload["marketSlugs"] = self._market_slugs
            await self.sio.emit(
                "subscribe_market_prices",
                payload,
                namespace=NAMESPACE,
            )
        if self._subscribe_positions:
            await self.sio.emit(
                "subscribe_positions",
                {"marketSlugs": self._market_slugs, "marketAddresses": self._market_addresses},
                namespace=NAMESPACE,
            )

    async def subscribe_market_prices(
        self,
        market_addresses: Optional[list[str]] = None,
        market_slugs: Optional[list[str]] = None,
    ) -> None:
        self._market_addresses = market_addresses or []
        self._market_slugs = market_slugs or []
        await self._resubscribe()

    async def subscribe_positions(self) -> None:
        if not self.token_id or not self.secret:
            raise ValueError("API token required for position subscription")
        self._subscribe_positions = True
        await self._resubscribe()

    async def connect(self) -> None:
        kwargs = {
            "transports": ["websocket"],
            "namespaces": [NAMESPACE],
        }
        if self.token_id and self.secret:
            # A function, not a dict, so every reconnect is signed with a fresh timestamp
            kwargs["headers"] = lambda: ws_auth_headers(self.token_id, self.secret)

        await self.sio.connect(WS_URL, **kwargs)

    async def disconnect(self) -> None:
        await self.sio.disconnect()

    async def run(self) -> None:
        await self.connect()
        await self.sio.wait()
```

## Usage examples

```python Public market data only theme={null}
import asyncio
from limitless_ws_client import LimitlessWebSocketClient

async def main():
    client = LimitlessWebSocketClient()
    await client.connect()

    await client.subscribe_market_prices(
        market_addresses=["0x1234567890abcdef1234567890abcdef12345678"],
        market_slugs=["btc-100k-weekly"],
    )

    await client.sio.wait()

asyncio.run(main())
```

```python Authenticated with positions theme={null}
import asyncio
import os
from limitless_ws_client import LimitlessWebSocketClient

async def main():
    token_id = os.environ["LMTS_TOKEN_ID"]
    secret = os.environ["LMTS_TOKEN_SECRET"]
    client = LimitlessWebSocketClient(token_id=token_id, secret=secret)
    await client.connect()

    await client.subscribe_market_prices(
        market_slugs=["btc-100k-weekly"],
    )
    await client.subscribe_positions()

    await client.sio.wait()

asyncio.run(main())
```

## Environment variables

| Variable | Description |
| - | - |
| `LMTS_TOKEN_ID` | Scoped API token ID for authenticated features (positions). Omit for public-only. |
| `LMTS_TOKEN_SECRET` | Token secret used to sign the HMAC handshake. Omit for public-only. |
| `DEBUG` | Set to `1` to enable verbose Socket.IO logging. |

## Auto-reconnection

The client uses `reconnection=True` by default. On reconnect, call `_resubscribe()` in the `connect` handler to restore market and position subscriptions, since the server does not persist them across disconnects.

Authenticated connections pass `headers` as a function. python-socketio calls it before every connection attempt, so each reconnect carries a new timestamp and signature. A plain dict is sent again unchanged on reconnect. The socket still connects, but the server checks the handshake headers on every `subscribe_positions` and `subscribe_order_events`, and a timestamp outside the 30-second window fails that check with `Invalid HMAC authentication`, so the re-subscription is rejected.

Our load balancer closes every connection after 24 hours (see [WebSocket overview](https://docs.limitless.exchange/developers/websocket/overview.md#connection)), so a long-running client always goes through this reconnect path at least once a day.

> [!WARNING]
>
> Store your API token ID and secret securely. Rotate the token if you suspect it has been exposed. Do not log or print the secret.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.