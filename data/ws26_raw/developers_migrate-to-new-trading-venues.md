> ## Documentation Index
> Fetch the complete documentation index at: https://docs.limitless.exchange/llms.txt
> Use this file to discover all available pages before exploring further.

# Migrate to the new trading venues

> What changes for API traders and integrators when markets launch on the new trading venues

New markets on Limitless launch on new trading venues. On these venues the trading fee is paid in USDC from your wallet, instead of being part of the signed order. Markets created before the switch stay on their original venue and work exactly as before.

## Who needs to do what

| You trade through | What to do |
| - | - |
| The Limitless web or mobile app | Nothing. The app handles it. |
| An official SDK | Upgrade to a version listed under [SDK versions](#sdk-versions). |
| Your own code that signs orders | Follow the [checklist](#checklist) below. |
| A server wallet (created and managed by Limitless) | Nothing. Its approvals are set up for you. |

## Checklist

**1. Detect the venue**

`GET /markets/{slug}` returns a `venue` object. A market is on a new venue when `venue.feeModuleType` is `"COLLATERAL"`; the venue then also has a `feeModule` address. Legacy venues don't have either field.

```json theme={null}
{
  "venue": {
    "exchange": "0x05c748E2f4DcDe0ec9Fa8DDc40DE6b867f923fa5",
    "adapter": null,
    "feeModule": "0x7B6ffe5bA8B5ec7afB0AaBaE629D12dA5bC62565",
    "feeModuleType": "COLLATERAL"
  }
}
```

**2. Approve USDC to the fee module**

From the wallet that signs your orders, approve USDC to `venue.feeModule`. A max approval is easiest, and you need it only once per fee module. Every order except `postOnly` needs it, both BUY and SELL.

Simple and NegRisk (grouped) markets use different fee modules, so read the address from the market rather than hardcoding it. See [addresses](#addresses).

**3. Sign feeRateBps as 0**

On new-venue markets, sign every order with `feeRateBps` set to `0`, whatever the market's `metadata.fee` flag or your profile's rate. Orders on legacy venues keep the [existing fee rate rules](https://docs.limitless.exchange/developers/eip712-signing.md#field-reference).

**4. Keep a little extra USDC**

On new venues a buy needs the order amount plus a fee reserve of 5% of it at the standard rate, whatever the limit price. The fee actually charged is lower; see [how the fee is calculated](#how-the-fee-is-calculated). A sell needs no USDC.

**Nothing else changes.** The exchange and adapter contracts are the same, your existing USDC and Conditional Token approvals stay valid, and the [EIP-712 domain](https://docs.limitless.exchange/developers/eip712-signing.md#eip-712-domain) is unchanged.

```typescript theme={null}
import { erc20Abi, maxUint256 } from 'viem';

const API_URL = 'https://api.limitless.exchange';
const USDC = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'; // USDC on Base

const { venue } = await (await fetch(`${API_URL}/markets/${slug}`)).json();
const isNewVenue = venue?.feeModuleType === 'COLLATERAL';

if (isNewVenue) {
  // Once per fee module, from the wallet that signs orders
  await walletClient.writeContract({
    address: USDC,
    abi: erc20Abi,
    functionName: 'approve',
    args: [venue.feeModule, maxUint256],
  });
}

// legacyFeeRateBps follows the legacy rules: your effectiveFeeRateBps
// on fee-enabled markets, 0 on fee-disabled markets.
const feeRateBps = isNewVenue ? 0 : legacyFeeRateBps;
```

## How the fee is calculated

On new venues only the taker pays a fee, always in USDC, and only on fee-enabled markets (`metadata.fee: true`). The standard rate is 5% (500 bps); a lower rate applies only where Limitless has set a per-profile fee cap. The rate is fixed when the order is accepted.

The fee is the rate × (1 − price) of the trade's USDC value, with the same formula for buys and sells. At the standard rate:

| Price | Fee (% of USDC value) |
| - | - |
| \$0.01 | 4.95% |
| \$0.10 | 4.50% |
| \$0.25 | 3.75% |
| \$0.50 | 2.50% |
| \$0.75 | 1.25% |
| \$0.90 | 0.50% |
| \$0.99 | 0.05% |

* **Buy:** the fee is paid on top of the order cost. Buying 100 shares at \$0.40 costs \$40.00 plus a \$1.20 fee.
* **Sell:** the fee comes out of the proceeds. Selling 100 shares at \$0.40 pays \$40.00 minus a \$1.20 fee, so you receive \$38.80. The fee module collects it after the proceeds arrive, in the same transaction, so a sell doesn't need a USDC balance.

The exact amount is computed once per match, from that match's raw totals (6 decimals) summed across every maker order it fills:

```text theme={null}
fee = rate_bps * N * (S - N) / (10000 * S)
```

`N` is the USDC the taker pays (buy) or receives (sell) before the fee, and `S` is the shares traded, so `N / S` is the taker's average price for the match. The result is rounded half-up to the nearest 10 raw units (0.00001 USDC). There is no minimum fee.

## Balance and approval checks

When you place an order on a new venue, the API checks:

* **Buy:** your available USDC covers the order amount plus a fee reserve of your rate × the order amount (5% at the standard rate). The reserve is the most the fee can reach, because a buy can fill at better prices than its limit. The fee charged is the amount above.
* **Sell:** no USDC balance is needed.
* **Both:** your USDC approval to `venue.feeModule` covers the fee. A max approval is easiest.

## Fees in order results

On new venues, the `execution` object in the [Create Order](https://docs.limitless.exchange/api-reference/trading/create-order.md#execution-response) and order status responses reports the taker's fee as follows:

| Field | Value on new venues |
| - | - |
| `feeRateBps` | `0`, the signed rate |
| `effectiveFeeBps` | The rate actually charged, in whole basis points of `usdGross`: `floor(usdFee * 10000 / usdGross)` |
| `totalsRaw.usdGross` | USDC paid (buy) or received (sell) before the fee |
| `totalsRaw.usdFee` | USDC fee charged |
| `totalsRaw.usdNet` | Sell: `usdGross - usdFee`. Buy: equal to `usdGross`. The fee is only in `usdFee`, so a buy's total cost is `usdGross + usdFee`. |
| `totalsRaw.contractsGross`, `totalsRaw.contractsNet` | Shares traded. They are equal, because no fee is taken in shares. |
| `totalsRaw.contractsFee` | `0` |

Makers pay no fee, so a maker's fill reports a fee of `0`.

Elsewhere:

* `GET /portfolio/positions`: `cost` includes the fee. A buy adds it to the cost basis and a sell subtracts it from the proceeds, so PnL is net of fees.
* `GET /portfolio/history`: a trade's `collateralAmount` is its USDC value before the fee. Read the fee from the order's execution.
* On-chain, every match emits `TakerOrderMatched` from the fee module, with `taker`, `notional`, `shares` and `takerFeeAmount`.

## Addresses

On Base. Always prefer the address returned in `venue.feeModule`.

| Contract | Address |
| - | - |
| Fee module, simple markets | `0x7B6ffe5bA8B5ec7afB0AaBaE629D12dA5bC62565` |
| Fee module, NegRisk markets | `0x01b7dF643247B377D5c39FcC40b9c28B4A827524` |
| USDC | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |

The exchange and adapter addresses are unchanged. See [Smart Contracts](https://docs.limitless.exchange/user-guide/smart-contracts.md) for the full list.

## SDK versions

Version 1.2.0 of every official SDK detects the venue and signs `feeRateBps` as `0` on new-venue markets, including cancel-replace and delegated orders.

| SDK | Minimum version |
| - | - |
| [TypeScript](https://docs.limitless.exchange/developers/sdk/typescript/getting-started.md) (`@limitless-exchange/sdk`) | 1.2.0 |
| [Python](https://docs.limitless.exchange/developers/sdk/python/getting-started.md) (`limitless-sdk`) | 1.2.0 |
| [Go](https://docs.limitless.exchange/developers/sdk/go/getting-started.md) (`limitless-exchange-go-sdk`) | v1.2.0 |
| [Rust](https://docs.limitless.exchange/developers/sdk/rust/getting-started.md) (`limitless-exchange-rust-sdk`) | 1.2.0 |

```bash theme={null}
npm install @limitless-exchange/sdk@^1.2.0
pip install -U "limitless-sdk>=1.2.0"
go get github.com/limitless-labs-group/limitless-exchange-go-sdk@v1.2.0
cargo add limitless-exchange-rust-sdk@1.2.0
```

The SDKs don't send the fee module approval for you. Approve it once per signing wallet, as in the [checklist](#checklist).

If you build orders with a low-level builder, such as `OrderBuilder`, instead of the order client, set `feeRateBps` to `0` yourself on new venues. Builders don't look up the market's venue.

## Errors

| Error | Cause | Fix |
| - | - | - |
| `Insufficient collateral allowance for the order fee.` | The signing wallet hasn't approved USDC to `venue.feeModule`. | Approve USDC to the fee module, then resubmit. |
| `FEE_RATE_MISMATCH` | The order was signed with a non-zero `feeRateBps` on a new venue. | Sign a new order with `feeRateBps` set to `0`. |

For how venues work in general, see [Venue system](https://docs.limitless.exchange/developers/venue-system.md#new-trading-venues).


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.