> ## Documentation Index
> Fetch the complete documentation index at: https://docs.limitless.exchange/llms.txt
> Use this file to discover all available pages before exploring further.

# Market Resolution

> How markets are resolved on Limitless Exchange

## Overview

Every market on Limitless has a defined resolution condition and deadline. When the deadline passes, the market is resolved based on objective data from the designated oracle source.

## Resolution process

**1. Market deadline passes**

Each market has a specific deadline (e.g., "Feb 16, 17:00 UTC"). Limitless accepts no new trades after this time.

**2. Oracle reports the outcome**

The designated oracle source provides the verified result. **Pyth Network** now resolves the majority of markets automatically.

**3. Team reviews (if needed)**

For manually resolved markets (admin-created event markets with no data feed), the Limitless team reviews the outcome against the resolution criteria defined on the market page. Resolution typically occurs within **24–72 hours** of the market deadline, depending on event complexity and data availability.

**4. Winning shares pay out**

Winning shares ("Yes" or "No" depending on outcome) are redeemable for \$1.00 each after the payout has been settled on-chain. Losing shares become worthless. If the market resolves [50-50](#50-50-resolution), every share is redeemable for \$0.50 instead.

## Claiming vs. selling before resolution

Redeeming winning shares after a market resolves is **not the same** as selling them on the order book before resolution:

| Action | When | Payout | Fees |
| - | - | - | - |
| **Claim / redeem** | After the market resolves and the on-chain payout is posted | Exactly \$1.00 USDC per winning share (\$0.50 per share on a 50-50 resolution) | No trading fee on the redemption itself |
| **Sell on the order book** | Anytime before resolution (or before you claim) | Current market price (less than \$1.00) | Taker fee applies if the order matches immediately (see [Fees](https://docs.limitless.exchange/user-guide/fees.md)) |

> [!NOTE]
>
> If you sold or accepted "claim now" liquidity on the order book before resolution, the USDC you received is the market price minus the taker sell fee. That amount is not the \$1.00 redemption value. The sell fee on CLOB markets is dynamic and peaks at **1.50%** near \$0.50. See the [sell fee curve](https://docs.limitless.exchange/user-guide/fees.md#sell-fee-curve) for the full table. Maker (resting limit) sells are fee-free.

## Oracle sources

> [!NOTE]
>
> Market resolution and on-chain redemption readiness are related but not identical. A market can appear resolved in the API before the underlying payout is fully settled on-chain. Direct redemption attempts may need to wait until the payout data has been posted.

> [!NOTE]
>
> The exact method of market resolution is normally determined on the market page. Always check the resolution source and criteria on the specific market before trading.

**Pyth Network** now resolves the majority of markets. Other markets may use manual resolution by the Limitless team.

| Oracle | Used for | Resolution time |
| - | - | - |
| **Pyth Network** | Majority of markets — crypto prices, stock prices, and other data feeds | Automatic at deadline |
| **Chainlink TWAP** | Short-cadence crypto up/down markets (5-minute and 15-minute) | Automatic at deadline |
| **Sports data providers** | Football, tennis and cricket (API-Sports) and esports (PandaScore) markets | Automatic; checked every 5 minutes (esports props every 15 minutes, esports match groups hourly) once the match reaches full time |
| **External venue parity** | Markets mirrored from another venue | Automatic, within minutes of the source venue settling |
| **Creator (user-generated custom markets)** | [Custom markets](https://docs.limitless.exchange/user-guide/custom-markets.md) created by users | The creator's wallet reports the outcome, at any time; Limitless syncs it every 15 minutes |
| **Manual** | Admin-created event markets with no data feed (politics and other custom events) | Typically 24–72 hours after deadline |

For Pyth-resolved markets, both the captured baseline price (`metadata.openPrice`) and the strike price quoted in the auto-generated market description use the full precision of the underlying Pyth feed. That is typically 8 decimal places for crypto feeds. Chainlink-resolved markets use the 18-decimal padded value matching the on-chain feed.

### Chainlink TWAP resolution

Short-cadence crypto up/down markets are moving to **time-weighted average price (TWAP)** resolution. Instead of comparing two instantaneous prices, both sides of the comparison come from the same Chainlink TWAP stream: an average over a fixed window. The market's description names the exact feed and window length.

* The **Price to Beat** is the TWAP captured at the market's open time.
* At the deadline, the closing TWAP is read from the same stream. The market resolves **Up** when the closing value is greater than or equal to the Price to Beat, and **Down** otherwise.
* Because the value is an average over the window rather than a single tick, a momentary price spike at the boundary does not decide the market on its own.
* The report at the exact resolution time is used first. If it is unavailable, the first Chainlink observation within the market's stated tolerance window is used. If no report exists in that window, the market is not resolved automatically and is handled per its description.

Each TWAP market's description states the exact feed, window, tolerance, and Price to Beat — always the authoritative source for that market's rule.

## Resolution for different market types

### Standard (CLOB) markets

Binary Yes/No markets normally resolve with one winning outcome and one losing outcome. When explicitly permitted by the market's resolution criteria, they may instead resolve [50-50](#50-50-resolution).

### NegRisk (category) markets

Only one outcome in the group can win. All other outcomes resolve to "No". See [NegRisk markets](https://docs.limitless.exchange/user-guide/negrisk-overview.md) for details.

## Market-specific resolution rules

The mechanics above describe how a Yes/No outcome pays out once chosen. The resolution criteria on each market page decide **which** outcome wins. Those criteria can cover event-specific edge cases — for example, a tied match, a cancelled game, or a "None of the above / Other" clause on a bracket-style market.

> [!NOTE]
>
> Always read the market page before you trade. It defines exactly which real-world results resolve **Yes**, which resolve **No**, and how ties, cancellations, or unlisted outcomes are handled. Unless the market's criteria specify a 50-50 resolution or another applicable outcome, failure to meet the stated criteria for **Yes** results in the market resolving **No**. This includes cases where the market page lists a fallback such as "Other" or "None of the above".

## 50-50 resolution

Some markets may resolve 50-50 when the market's resolution criteria do not allow either outcome to be selected as the sole winner. A 50-50 resolution is only available for CLOB, AMM, and Ladder markets. A Ladder consists of multiple CLOB markets grouped under a shared title.

The circumstances that trigger a 50-50 resolution are defined in the resolution criteria on each market page. Always check the specific market's rules before trading.

When a market resolves 50-50, every share pays out \$0.50 USDC, regardless of which outcome it represents.

For example, if a trader holds:

* 100 shares of Yes
* 50 shares of No

the total payout is:

(100 × \$0.50) + (50 × \$0.50) = \$75.00 USDC

> [!NOTE]
>
> A 50-50 resolution is not a refund. The payout is based on the number of shares held at resolution, not the amount originally paid for those shares.

### Tennis match markets

Tennis match markets (Player A vs Player B) resolve based on the official outcome of the match. The scenarios below describe how each situation is handled. The market page states the exact rules and deadline for each match.

| Scenario | Resolution |
| - | - |
| **Walkover**: a player withdraws before the match begins and the opponent advances automatically | 50-50 |
| **Retirement, default, or disqualification**: the match begins but is not completed, and one player advances | The player who advances |
| **Cancelled match**: the match is called off before it begins and neither player withdraws | 50-50 |
| **Tie** | 50-50 |
| **Delayed or postponed match**, played by the deadline on the market page | The winner of the match |
| **Delayed or postponed match**, no winner by the deadline on the market page | 50-50 |

**Walkover.** Player A withdraws before the match starts and Player B advances automatically. The match was never played, so the market resolves 50-50.

**Retirement, default, or disqualification.** Player A and Player B begin their match and play one set. Player B retires during the match, so Player A advances and the market resolves to Player A.

**Cancelled match.** Player A and Player B are scheduled to play, but the match is called off before it begins and neither player withdraws. The market resolves 50-50. This differs from a walkover: in a walkover a player withdraws and the other advances, whereas in a cancellation the match itself is called off.

**Delayed or postponed match.** The market page sets a deadline for a winner to be determined, currently 23:59 UTC on the 14th day after the scheduled start. If the match between Player A and Player B is postponed and played before that deadline, the market stays open and resolves to whichever player wins. If no winner has been determined by the deadline, the market resolves 50-50.

> [!NOTE]
>
> Tennis total sets and total games markets follow different rules. If the match is not completed, they resolve to any outcome already guaranteed by the play so far, and 50-50 otherwise. Check the market page for the exact criteria.

If the published criteria are ambiguous or you cannot apply them to the real-world result, Limitless treats the market as misresolved and refunds users per the [Refund Policy](https://docs.limitless.exchange/user-guide/refund-policy.md). You get back the bet amount, not the \$1.00 payout.

## Disputes and misresolutions

If a market is misresolved, Limitless refunds the bet amount. See the [Refund Policy](https://docs.limitless.exchange/user-guide/refund-policy.md) for details.

If you believe a market was resolved incorrectly, contact the team through the **support channel** on [limitless.exchange](https://limitless.exchange) (footer), via email at [help@limitless.network](mailto:help@limitless.network), or on [Discord](https://discord.com/invite/yb4SscD8RZ).


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.