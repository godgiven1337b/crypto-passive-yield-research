> ## Documentation Index
> Fetch the complete documentation index at: https://docs.limitless.exchange/llms.txt
> Use this file to discover all available pages before exploring further.

# Fees

> How trading fees work on Limitless Exchange

## Overview

Fees on Limitless adapt to the **market price**: the fee model is designed to reward early conviction and discourage manipulation. The base taker rate is the same for every account; a lower rate applies only where Limitless has set a per-profile fee cap.

## Fee structure by market type

### AMM markets

A flat **0.40%** fee applies to all trades. No curves, no complexity. Certain promotional or specific markets may have a reduced or zero fee.

[Custom markets](https://docs.limitless.exchange/user-guide/custom-markets.md) written by users run on their own liquidity pool with the pool fee set at creation, currently **2%** per trade. That fee goes to the market creator as the pool's only liquidity provider, not to Limitless.

### Order book (CLOB) markets

Fees are dynamic and adjust based on the current market price:

| Side | Fee range | Paid in |
| - | - | - |
| **Buy** | 0.40% – 3.00% | Outcome tokens (contracts) |
| **Sell** | 0.42% – 1.50% | Collateral (USDC) |

> [!NOTE]
>
> These rates, and the curves below, apply to markets on legacy venues. New markets launch on new trading venues, where the fee is paid in USDC on both buys and sells. See [Fees on new trading venues](#fees-on-new-trading-venues).

## Makers vs takers

> [!WARNING]
>
> **Fees only apply to takers** — orders that instantly settle against the order book.

| Order type | Fees? | Details |
| - | - | - |
| **Limit orders (makers)** | No fees | Even though you sign a transaction with fee terms, you pay nothing if your order is placed in the book |
| **Market orders (takers)** | Fees apply | Only orders that match immediately are charged |

If you provide liquidity to the book, you can trade **completely fee-free**.

## The fee curve

The fee curve adjusts dynamically based on where the market price is when you trade.

### Buy fee curve

Buy fees start at 3.00% for low-probability markets and decrease as probability increases:

| Price | Buy fee |
| - | - |
| \$0.01 – \$0.50 | 3.00% |
| \$0.55 | 2.52% |
| \$0.60 | 2.13% |
| \$0.65 | 1.80% |
| \$0.70 | 1.51% |
| \$0.75 | 1.26% |
| \$0.80 | 1.05% |
| \$0.85 | 0.85% |
| \$0.90 | 0.68% |
| \$0.95 | 0.53% |
| \$0.99 | 0.42% |
| \$0.999 | 0.40% |

### Sell fee curve

Sell fees peak at the midpoint (\$0.50) and decrease toward the extremes:

| Price | Sell fee |
| - | - |
| \$0.01 | 0.45% |
| \$0.05 | 0.60% |
| \$0.10 | 0.78% |
| \$0.20 | 1.11% |
| \$0.30 | 1.32% |
| \$0.40 | 1.44% |
| \$0.50 | **1.50%** (peak) |
| \$0.60 | 1.44% |
| \$0.70 | 1.32% |
| \$0.80 | 1.11% |
| \$0.90 | 0.78% |
| \$0.95 | 0.60% |
| \$0.99 | 0.45% |
| \$0.999 | 0.42% |

> [!NOTE]
>
> By discouraging exits at the midpoint, the fee curve protects market integrity when uncertainty is highest.

### Reading the exact fee programmatically

The curve is not published as a closed-form formula, and the tables above list representative prices rather than every point. You do not need either: every order execution reports the fee that was actually applied.

* `effectiveFeeBps` — the rate applied to that execution
* `usdFee` and `contractsFee` — the amount charged, in the asset you received
* `feeRateBps` — the fee rate your profile is charged on that market (`0` on fee-free markets); the signed order must carry the same value or it is rejected with `FEE_RATE_MISMATCH`

See [Create Order](https://docs.limitless.exchange/api-reference/trading/create-order.md) for where these appear in the response. On new trading venues these fields work differently; see [fees in order results](https://docs.limitless.exchange/developers/migrate-to-new-trading-venues.md#fees-in-order-results).

## Example: how fees play out

Imagine you're buying **YES** shares in a market where the current probability is **40%** (\$0.40):

**1. You buy early at 40%**

Your buy fee = **3.00%**. You pay the full fee, but you're getting in early with better payout odds.

**2. Market moves to 70%**

If you sell when the market hits 70%, you pay a **1.32% sell fee** because you're away from the 50/50 uncertainty zone.

**3. Someone else buys at 70%**

They pay a **1.51% buy fee** — lower than yours, but they get worse odds since the price is already high.

It's all about conviction. Act early and stay smart. The fee curve gives you the edge.

## Fees on new trading venues

New markets launch on [new trading venues](https://docs.limitless.exchange/developers/venue-system.md#new-trading-venues). On these markets the taker fee is paid in USDC on both buys and sells. At the standard rate it is 5% × (1 − price) of the trade's USDC value, the same for buys and sells. Makers still pay nothing.

| Price | Fee (% of USDC value) |
| - | - |
| \$0.01 | 4.95% |
| \$0.10 | 4.50% |
| \$0.25 | 3.75% |
| \$0.50 | 2.50% |
| \$0.75 | 1.25% |
| \$0.90 | 0.50% |
| \$0.99 | 0.05% |

* **Buying** 100 shares at \$0.40 costs \$40.00 plus a \$1.20 fee.
* **Selling** 100 shares at \$0.40 pays \$40.00 minus a \$1.20 fee, so you receive \$38.80.

A lower rate applies only where Limitless has set a per-profile fee cap. Markets created before the switch keep the legacy fees above. API integrators can find the exact calculation in [Migrate to the new trading venues](https://docs.limitless.exchange/developers/migrate-to-new-trading-venues.md#how-the-fee-is-calculated).

## Why this fee model works

The fee structure is inspired by proven models (including Polymarket and Kalshi) and is designed to:

* **Reward early traders** for taking risk
* **Discourage flip-flopping** and short-term manipulation
* **Incentivize long-term** loyal participation
* **Keep markets fair**, liquid, and meaningful


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.