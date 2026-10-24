> ## Documentation Index
> Fetch the complete documentation index at: https://docs.limitless.exchange/llms.txt
> Use this file to discover all available pages before exploring further.

# For Developers

> REST and WebSocket APIs for programmatic trading on Limitless

Build on Limitless with **REST** and **WebSocket** APIs for programmatic trading, market data, and portfolio management.

**Base URL:** `https://api.limitless.exchange`

**API Reference:** [docs.limitless.exchange/api-reference](https://docs.limitless.exchange/api-reference/introduction.md)

**WebSocket URL:** `wss://ws.limitless.exchange`

**Regions:** Both URLs are single global endpoints. There are no regional base URLs, mirrors, or region selection. All clients connect to the same endpoints regardless of location.

**Network:** Base mainnet (chain ID `8453`). There is no sandbox, testnet, mock mode, or Base Sepolia deployment — all integrations run against production with real USDC. To rehearse a flow without significant capital, place small live orders (e.g. the minimum order size for a CLOB market) on a low-volume market.

> **[Join the Limitless Builders Chat](https://t.me/LimitlessBuildersChat)**
>
> Building on the API or SDKs? The Builders Chat on Telegram is the place for API/SDK updates, help, and to connect with other builders.

## Choose your path

> **[Individual trader or bot](#trading-for-yourself)**
>
> You want to trade on Limitless programmatically — placing orders with your own wallet via a bot, script, or agent. **You do not need to apply for anything.** Get a scoped API token from the UI and start trading.

> **[Platform or partner](#building-a-platform)**
>
> You are building a product where **other users** trade through your platform. You need sub-accounts, delegated signing, or managed wallets. **Requires a partner application.**

***

## Trading for yourself

If you are an individual trader, bot operator, or agent builder, this is your path. You trade with your own wallet and sign your own orders.

### How it works

**1. Get a scoped API token**

Generate a scoped API token (a token ID + secret) from the [Limitless Exchange UI](https://limitless.exchange) → profile menu → Api keys. Sign every request with HMAC-SHA256 and send the `lmts-api-key`, `lmts-timestamp`, and `lmts-signature` headers. See [Authentication](https://docs.limitless.exchange/developers/authentication.md) for the signing protocol.

If your account has ever enabled 1-click (smart wallet) trading in the app, switch the profile to EOA trading mode before placing API orders — see [Trading wallet mode](https://docs.limitless.exchange/developers/eip712-signing.md#trading-wallet-mode-whose-address-signs).

**2. Fetch market data**

`GET /markets/:slug` returns market info including **venue contract addresses** (fetch once per market and cache).

**3. Build and sign orders**

Construct order payloads and sign with **EIP-712** using the venue's exchange address as `verifyingContract`.

**4. Submit orders**

`POST /orders` with your signed order, `ownerId` (your profile ID from `GET /profiles/{address}`), `orderType`, and `marketSlug`.

### Get started

> **[Authentication](https://docs.limitless.exchange/developers/authentication.md)**
>
> API keys, scoped tokens, and how auth works.

> **[Python quick start](https://docs.limitless.exchange/developers/quickstart/python.md)**
>
> End-to-end trading in Python.

> **[Node.js quick start](https://docs.limitless.exchange/developers/quickstart/nodejs.md)**
>
> TypeScript/Node.js integration with viem.

> **[EIP-712 signing](https://docs.limitless.exchange/developers/eip712-signing.md)**
>
> How to sign orders for the CLOB.

***

## Building a platform

If you are a partner building a product where other users trade through your platform, this is your path. You manage sub-accounts on behalf of your users and optionally use delegated signing so your users never need to manage private keys.

> [!NOTE]
>
> **You must apply for Programmatic API access** before you can create sub-accounts or use delegated signing. Individual trading with your own wallet does not require an application.

### What you get

| Capability | Description |
| - | - |
| **Scoped API tokens** | HMAC-SHA256 authenticated tokens with granular scopes (`trading`, `account_creation`, `delegated_signing`) |
| **Partner sub-accounts** | Create and manage user profiles linked to your partner account |
| **Delegated signing** | Submit orders without end users managing private keys — the server signs via a managed wallet |

### Get started

> **[Programmatic API](https://docs.limitless.exchange/developers/programmatic-api.md)**
>
> Full guide: partner lifecycle, sub-accounts, delegated signing, and order types.

> **[Authentication (HMAC)](https://docs.limitless.exchange/developers/authentication.md#hmac-request-signing)**
>
> HMAC signing protocol for partner API tokens.

> **[Migrate from Polymarket](https://docs.limitless.exchange/developers/migrate-from-polymarket.md)**
>
> Map Polymarket concepts to Limitless equivalents.

> **[API reference](https://docs.limitless.exchange/api-reference/introduction.md)**
>
> Full endpoint documentation.

***

## Official SDKs

All SDKs support both individual trading and partner integrations.

> **[TypeScript SDK](https://docs.limitless.exchange/developers/sdk/typescript/getting-started.md)**
>
> Type-safe client with signing and real-time streaming.

> **[Python SDK](https://docs.limitless.exchange/developers/sdk/python/getting-started.md)**
>
> Async client for markets, orders, and partner features.

> **[Go SDK](https://docs.limitless.exchange/developers/sdk/go/getting-started.md)**
>
> Typed Go client for CLOB and NegRisk markets.

> **[Rust SDK](https://docs.limitless.exchange/developers/sdk/rust/getting-started.md)**
>
> Async Rust client for trading, partner flows, and WebSockets.

## Additional resources

> **[Venue system](https://docs.limitless.exchange/developers/venue-system.md)**
>
> Contract addresses and token approvals.

> **[WebSocket API](https://docs.limitless.exchange/developers/quickstart/websocket.md)**
>
> Real-time market and orderbook streaming.

## Docs MCP for coding agents

Point your coding agent or docs assistant at the live Model Context Protocol server to give it up-to-date access to this documentation:

```
https://docs.limitless.exchange/mcp
```

Useful for agent frameworks and IDE tooling that support MCP — the server exposes the full docs (endpoints, SDK references, guides) as searchable context. See [Build a Trading Agent](https://docs.limitless.exchange/developers/build-a-trading-agent.md) for an end-to-end agent example.

To let an assistant trade, use the [Limitless trading MCP](https://docs.limitless.exchange/developers/mcp-server.md) at `https://api.limitless.exchange/mcp`.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.