> ## Documentation Index
> Fetch the complete documentation index at: https://docs.limitless.exchange/llms.txt
> Use this file to discover all available pages before exploring further.

# LP Rewards

> Earn rewards for providing liquidity with limit orders

## Overview

The LP Rewards program incentivizes providing liquidity by rewarding well-placed limit orders. These rewards promote tighter spreads, thicker order books, and a healthy marketplace.

The design iterates on an industry-standard approach used by dYdX and Polymarket, with specifically tuned parameters to ensure competitiveness and fairness.

## Methodology

* You earn rewards by placing limit orders **within a specific spread from the market midpoint**\*
* The **closer** an order is to the midpoint and the **more competitive** its size, the higher the reward
* To qualify, orders must meet or exceed the **minimum size threshold** set on a per-market basis
* Limitless calculates rewards **every minute** across all markets and pays them out daily at **22:30 UTC**
* The daily payout pays your **full unpaid balance**. There is no minimum payout amount, and sub-cent balances are included.

> [!NOTE]
>
> \*To maintain a fair market-making experience, only limit orders at or above the minimum shares threshold count toward the midpoint calculation.

## Rewards parameters

Each market has 3 parameters that define how rewards are paid out:

| Parameter | Illustrative example | Description |
| - | - | - |
| **Rewards** | \$10 | Daily USDC rewards available for the market |
| **Spread** | 3c | Maximum distance from midpoint to earn rewards |
| **Min Shares** | 100 | Minimum order size to qualify |

These parameters are set to support positive market activity while accounting for each market's uniqueness.

> [!NOTE]
>
> **All three values are set per market and change over time.** The numbers
> above only illustrate the shape of the parameters, not what any market pays.
> For the live, authoritative values, see the
> [Limitless Rewards page](https://limitless.exchange/rewards) or the market
> itself on the platform.

## Bonus multiplier

Limit orders placed **closer to the midpoint** earn additional rewards through a bonus multiplier. The tighter your spread, the greater your share of rewards.

## One-sided liquidity

To promote tail-end speculation, earning from one-sided liquidity is only allowed while the odds are between **5% and 95%**. This provides LPs (liquidity providers) with greater flexibility in managing their positions while still fostering a robust and efficient market structure. Inside that band a one-sided quote earns a reduced score (its size divided by a per-market factor), so two-sided quoting always earns more.

## Time-based reward schedules

A market's daily rewards budget can scale up or down at specific hours or days of the week. Schedules run in **Eastern Time**, and the active window multiplies the per-minute reward rate (for example, a 2× boost during peak hours or a 0.5× dim overnight).

* By default, no schedule applies and rewards pay at the flat rate 24/7.
* A platform-wide schedule can dim rewards during low-activity windows, and it never increases a market's daily cap.
* Individual markets can override the platform schedule to boost specific windows, up to the platform ceiling of \$5,000 per market per day.
* Category or tag schedules can apply to a family of markets; when several match, the lowest rate wins. A schedule rule may also set a fixed daily amount instead of a multiplier.

Limitless records the applied multiplier per market per minute, so your payouts always reflect the schedule that was active when your orders earned.

## Note on adjustments

These parameters are dynamic and may be adjusted over time to meet the exchange's needs and maintain a thriving marketplace.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.