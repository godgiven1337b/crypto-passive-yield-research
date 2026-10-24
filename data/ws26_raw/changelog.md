> ## Documentation Index
> Fetch the complete documentation index at: https://docs.limitless.exchange/llms.txt
> Use this file to discover all available pages before exploring further.

# Changelog

> Notable changes to the Limitless Exchange platform, API, and SDKs

Welcome to the Limitless Changelog. Here you'll find important changes to the Limitless Exchange platform including API updates, SDK releases, and new features.

## Oct 19, 2026

### Partners can buy and claim curated packs

Partners can now buy curated packs for their managed server-wallet sub-accounts and claim the winnings, through new `/parlay/partner` routes.

* `POST /parlay/partner/quote` prices a catalogue pack for a stake. `POST /parlay/partner/buy` buys it for the sub-account in `onBehalfOf`, with `minPayoutAmount`, a `deadline` at most 480 seconds out, and an `idempotencyKey`. Replay the identical request to recover a lost response.
* `GET /parlay/partner/positions` and `GET /parlay/partner/positions/{id}` read the sub-account's pack positions with the `x-on-behalf-of` header. `POST /parlay/partner/positions/{id}/claim` claims a winning position; repeat it until it returns `CLAIMED`.
* Requires HMAC with the `trading` and `delegated_signing` scopes. All pack routes share a limit of 10 requests per 10 seconds per partner.
* Buys draw on the `parlay-treasury-vault` USDC allowance. Wallets created before this release may need an allowance retry first; a buy that needs it returns `409 PACK_ALLOWANCE_REQUIRED`.
* Amounts are integer micro-USDC strings. Custom packs and partner revenue share are not included.
* All four SDKs support partner packs from 1.3.0.

**Documentation:** [Partner Curated Packs](https://docs.limitless.exchange/developers/partner-packs.md)

## Oct 14, 2026

### Stock dailies in packs

Stock Up or Down Daily markets can now be pack legs, alongside the crypto dailies added on Oct 13.

* `GET /parlay/markets` lists them with `kind: "price"`, for example SPY, AAPL, NVDA, MSFT, GOOGL, META, PLTR, and HOOD. The available set can change from day to day.
* Like a crypto daily, a stock leg stops being buyable 60 minutes before it closes. Read `tradeCutoffAt` rather than computing the cutoff yourself.
* A custom pack can mix up to four crypto legs and two stock legs, one market per asset.

**Documentation:** [Packs](https://docs.limitless.exchange/user-guide/packs.md)

### New markets launch on new trading venues

New markets now launch on new trading venues. On these venues the trading fee is paid in USDC from your wallet instead of being part of the signed order. Markets created before the switch stay on their original venue and work exactly as before.

* A market is on a new venue when `venue.feeModuleType` is `"COLLATERAL"` on `GET /markets/{slug}`. The venue then also has a `feeModule` address.
* From the wallet that signs your orders, approve USDC to `venue.feeModule`, once per fee module. Every order except `postOnly` needs it. Without it, orders are rejected with `Insufficient collateral allowance for the order fee.`
* Sign `feeRateBps` as `0` on new-venue orders. Any other value returns `FEE_RATE_MISMATCH`. Legacy venues keep the existing fee rate rules.
* The exchange and adapter contracts, your existing approvals and the EIP-712 domain are unchanged. Server wallets are approved for you.
* All four SDKs support the new venues from 1.2.0: `@limitless-exchange/sdk` on npm, `limitless-sdk` on PyPI, the Go SDK at `v1.2.0` and the `limitless-exchange-rust-sdk` crate. They sign the fee rate for you; the fee module approval is still yours to send.

**Documentation:** [Migrate to the new trading venues](https://docs.limitless.exchange/developers/migrate-to-new-trading-venues.md) | [Venue system](https://docs.limitless.exchange/developers/venue-system.md#new-trading-venues) | [Smart Contracts](https://docs.limitless.exchange/user-guide/smart-contracts.md)

### Lifecycle events by category, and match schedule updates

The market lifecycle stream can now be filtered by category and reports match schedule changes.

* `subscribe_market_lifecycle` accepts an optional `{ categoryIds: number[] }`, up to 32 IDs. You receive an event when any of them appears in the event's `categoryIds`. Omitting the filter still subscribes to everything, and subscribing again replaces the previous filter.
* New `marketUpdated` event on the same stream. A sports or esports match emits it when its start time, deadline, or match status changes, with `startMatchTimestampInUTC`, `deadline`, `matchStatus`, and `categoryIds`. A market group sends one frame for the whole group.
* `marketResolved` is unchanged and only covers single-winner resolutions. Detect split resolutions, such as 50-50, over REST.

**Documentation:** [Market lifecycle](https://docs.limitless.exchange/developers/websocket/market-lifecycle.md)

## Oct 13, 2026

### Crypto dailies in packs

BTC, ETH, Solana, and XRP Up or Down Daily markets can now be pack legs alongside sports markets.

* `GET /parlay/markets` lists them with `kind: "price"`; sports entries carry `kind: "sport"`. Route on `kind` before drawing a card: a price entry is `isMatch: true` with `outcomeLabels: ["Up", "Down"]`, a `null` `leagueName`, and no kickoff.
* `tradeCutoffAt` is when a leg stops being buyable in packs; it is buyable while the current time is before it. A daily leg stops 60 minutes before it closes. Read the field rather than computing the cutoff yourself.
* `closesAt` is a price leg's close time, for display. It is `null` on sport legs.
* Pack legs from `GET /parlay/packs` carry `kind` and `tradeCutoffAt` as well. Additive fields only.

**Documentation:** [Packs](https://docs.limitless.exchange/user-guide/packs.md)

## Oct 5, 2026

### Positions report when they were opened

`GET /portfolio/positions` and the public `GET /portfolio/{account}/positions` include `openedAt`, an ISO timestamp for when each holding was opened.

* It appears per outcome at `clob[].positions.yes` / `.no` and `group[].markets[].positions.yes` / `.no`, and on each `amm[]` entry.
* `null` means the open time is unknown or the position is no longer held.
* AMM WebSocket position updates carry it as well. CLOB WebSocket items do not, so read it over REST for CLOB positions.
* Additive only. Balances, cost basis, average fill price, and PnL are unchanged.

**Documentation:** [Positions](https://docs.limitless.exchange/api-reference/portfolio/positions.md)

### Filter pack positions to the ones still held

`GET /parlay/{account}/positions` and the authenticated `GET /parlay/positions` accept `open=true`, which returns only the packs a user still holds: `ACTIVE`, or `WON` and not yet claimed.

* Without `open`, both endpoints behave exactly as before.
* `open` cannot be combined with `status`; that returns `400`, as does a non-boolean value such as `open=yes`.

**Documentation:** [Pack positions](https://docs.limitless.exchange/api-reference/public-portfolio/pack-positions.md)

## Oct 2, 2026

### Orderbook sizes are raw 6-decimal units

This is a documentation correction. API behavior has not changed. Several pages described orderbook level sizes as shares. They have always been raw 6-decimal units.

* `bids[].size` and `asks[].size` are raw 6-decimal units (1 share = 1,000,000) on `GET /markets/{slug}/orderbook`, on the initial `orderbookUpdate` after `subscribe_market_prices`, and on every later `orderbookUpdate`. Divide by `1e6` for shares. `price` is not scaled.
* `minSize` uses the same units. REST returns `minSize` and `maxSpread` as decimal strings; WebSocket frames can send them as JSON numbers.
* The Python markets example now reads `OrderBook` fields as attributes. Dictionary-style access raised `TypeError`.
* The order-events and create-order pages now state that a released taker-delay order follows the same rule as any other order: what matches on arrival is one trade, with one `MATCHED` and one terminal frame, even on a partial fill across several makers.

**Documentation:** [Get Orderbook](https://docs.limitless.exchange/api-reference/trading/orderbook.md) | [Market data](https://docs.limitless.exchange/developers/websocket/market-data.md) | [Order events](https://docs.limitless.exchange/developers/websocket/order-events.md)

## Sep 30, 2026

### Trading feed entries show when a position was opened

`GET /feed/trading` entries carry three new fields.

* `openedAt` on `SOLD` and `RESOLVED` entries: when the position being closed was first opened.
* `profile.discordConnected`, a boolean, alongside the existing `xHandle`.
* `parlay.sourcePackId` on pack entries: the catalog pack a purchase came from, kept even if that pack was later removed. It is `null` for a custom pack.
* Additive fields only. No action required.

**Documentation:** [Trading feed](https://docs.limitless.exchange/api-reference/feed/trading-feed.md)

## Sep 25, 2026

### Market maker heartbeat

`POST /heartbeats` arms a profile-wide cancellation deadline, so a market maker that disconnects or wedges does not leave quotes resting on the book.

* Send `cancelAt` as a Unix timestamp in milliseconds, at least five seconds after server time. Each request replaces the previous deadline. An empty body `{}` disarms it.
* One deadline per profile, covering every market that profile trades. There is no per-market state and no heartbeat id.
* When the deadline passes, the orders you had resting at that moment are cancelled. Orders placed after it are not covered, which is why you should stop placing orders as soon as a renewal fails and resume only after one succeeds.
* API tokens need the `trading` scope; without it the call returns `403`.
* Once the deadline passes and cancellation starts, renewing or disarming returns `409`. Cancellation cannot be called off.

**Documentation:** [Market Maker Heartbeat](https://docs.limitless.exchange/api-reference/trading/heartbeats.md)

### Terminal order events are emitted again

Terminal `OME` `EXECUTION` frames for immediate-or-cancel orders stopped reaching `subscribe_order_events` on Aug 27 and are flowing again as of Sep 25. If you added polling to cover their absence, the frames are reliable again.

* A FAK always terminates and now emits its terminal frame, including a zero-fill FAK, which emits `status: "KILLED"` and no settlement frames. A FOK emits one only when it filled.
* Terminal frames are shaped differently from lifecycle frames: `eventId` is the string `terminal:<orderId>`, the frame carries a `status` label, and `price` and `remainingSize` are strings, with `remainingSize` in raw 6-decimal units.
* `POST /orders/status/batch` reports the same zero-fill FAK as `settlementStatus: "UNMATCHED"`. REST and the stream use different vocabulary for one outcome.
* Frames are delivered only to the order owner.

**Documentation:** [Order events](https://docs.limitless.exchange/developers/websocket/order-events.md)

## Sep 23, 2026

### Sign orders with your effective fee rate

On fee-enabled markets the signed `feeRateBps` must now equal the order owner's current effective fee rate. A profile-specific cap can make that lower than the rank rate, so signing with `rank.feeRateBps` alone is no longer safe.

* Read `effectiveFeeRateBps` from your own private profile (`GET /profiles/{account}`, authenticated) and sign with it. On fee-disabled markets sign with `0`.
* A stale or incorrect rate is rejected with `400` and `{ "code": "FEE_RATE_MISMATCH", "expectedFeeRateBps": <number> }`. Build a new order with that rate, sign it again, and resubmit.
* `feeRateBps` is part of the EIP-712 payload. Editing the submitted JSON without re-signing does not work.
* Partner credentials cannot read a sub-account's private profile, so for a signed sub-account order take the rate from the mismatch response. Unsigned delegated orders are signed server side with the correct rate.
* An `effectiveFeeRateBps` of `null` means the profile has no rank and cannot supply a fee rate for a fee-enabled order.

## Sep 21, 2026

### NFL games in packs

NFL moneyline games can now be legs in a pack, alongside football, tennis, cricket, and esports.

* `GET /parlay/markets` lists eligible NFL games. Each carries `leagueName: "NFL"`, team names in `outcomeLabels`, and team logos in `outcomeImageUrls`.
* NFL games carry an `nfl-league` property, the same way other sports carry their league property.
* `GET /markets/{slug}/packs` now resolves a standalone match slug, so an NFL, tennis, or cricket match page returns the packs holding a leg on that market instead of an empty list.
* Response shapes are unchanged. No action required.

**Documentation:** [Packs](https://docs.limitless.exchange/user-guide/packs.md)

## Sep 19, 2026

### Book price on pack legs

Pack and quote responses now expose each leg's order-book price alongside the price the leg is charged.

* `POST /parlay/quote`: every entry in `legs[]` carries `bookPrice` (number, 0-1), always present, the chosen side's price on the market's order book. `price` still reports what the leg is charged.
* `GET /parlay/packs`, `GET /parlay/packs/search`, and `GET /parlay/packs/{id}`: every entry in `legs[]` carries `bookPrice` too. It is `null` when no live or cached pricing source is available, for example on ineligible listings or settled markets.
* Additive response fields only. Pricing, payouts, `livePrice`, and `priceSnapshot` are unchanged. No action required.

**Documentation:** [Search packs](https://docs.limitless.exchange/api-reference/packs/search-packs.md)

## Sep 18, 2026

### Clearer failures when cancelling a delayed order

A cancellation that arrives while a taker-delayed order is already being released now says so explicitly, instead of failing without a usable reason.

* `POST /orders/cancel` returns `409 Conflict` with `reason: "ORDER_RELEASE_IN_PROGRESS"` and `retryable: true` when the release is already under way. Retry the cancel.
* Batch and client-order-id cancellations carry the same `reason` field: `ORDER_NOT_FOUND`, `ORDER_RELEASE_IN_PROGRESS`, or `UNKNOWN_ERROR`, with `retryable` set where it applies.
* Cancellation itself is never subject to the taker delay.
* FAK and FOK orders can only be cancelled while they wait out a taker delay. On markets without one they complete immediately and cannot be cancelled.

**Documentation:** [Cancel order](https://docs.limitless.exchange/api-reference/trading/cancel.md)

## Sep 17, 2026

### Python SDK 1.1.1 recovers subscriptions after a reconnect

`limitless-sdk` 1.1.1 on PyPI fixes the WebSocket client's reconnect path. Upgrade if you hold long-running connections: `pip install -U limitless-sdk`.

* After an automatic reconnect, the client now re-sends every active subscription itself. 1.1.0 did not restore subscriptions on its own.
* Every connection attempt, including automatic reconnects, is signed with a fresh HMAC timestamp. 1.1.0 re-sent the original handshake headers, so authenticated subscriptions such as `subscribe_positions` and `subscribe_order_events` failed with `Invalid HMAC authentication` once the 30-second window had passed.
* WebSocket connections are closed after 24 hours, so every long-running client goes through this path at least once a day.

**Documentation:** [Python SDK WebSocket](https://docs.limitless.exchange/developers/sdk/python/websocket.md) | [Connection limits](https://docs.limitless.exchange/developers/websocket/overview.md#connection)

## Sep 11, 2026

### Username search matches anywhere in a name

`GET /profiles/search` now finds usernames that contain your query, not only ones that start with it. Searching `are` returns `WhyAreYouGay` alongside names beginning with "are".

* Exact and prefix matches still rank first; mid-string matches fill the page when those come up short.
* Mid-string matching applies to queries with at least three consecutive letters or digits.
* No parameter or response changes. No action required.

### `include` now works on the stable-slug market endpoint

`GET /markets/stable/{slug}` accepts the same `include` query parameter as `GET /markets/{addressOrSlug}`, so a stable slug returns the same envelope as an instance slug.

* Pass `include=timelinePreview,nextMarket` to get the timeline preview and successor-round data on a stable slug.
* Without `include`, the response is the bare market DTO exactly as before.
* No action required for callers that do not send `include`.

**Documentation:** [Get market by stable slug](https://docs.limitless.exchange/api-reference/markets/resolve-stable-slug.md)

### Lifetime realized PnL on public profiles

`GET /portfolio/{account}/realized-pnl` accepts `timeframe=all`, returning a wallet's full realized-PnL history instead of only the last day, week, or month.

* `all` joins the existing `1d`, `1w`, and `1m` values; the default is unchanged.
* The response shape is the same as the other timeframes.
* No action required.

**Documentation:** [Realized PnL (Public)](https://docs.limitless.exchange/api-reference/public-portfolio/realized-pnl.md)

### Bug fix: top holders missing on funded custom markets

Top-holder reads could return `404` for funded user-generated custom markets after a split or merge, even though the market was live and had holders.

* Affected custom markets now return their holder list as expected.
* Ordinary hidden markets are still excluded from holder reads, as before.
* Display only; positions, funds, and settlement were never affected. No action required.

## Sep 7, 2026

### Points no longer accrue on user-generated markets

Trading on user-generated markets (the ones with a Community badge) is now excluded from the points program.

* Trade, realized PnL, and hold-to-resolution rewards skip user-generated markets.
* Volume on user-generated markets no longer counts toward daily-activity thresholds.
* All other markets are unaffected. No action required.

**Documentation:** [User-generated markets](https://docs.limitless.exchange/user-guide/user-generated-markets.md)

### Bug fix: pack picker listed outcomes packs cannot accept

The pack-eligible markets list could include outcomes priced outside the range pack creation accepts, so a pick made from the list was rejected when quoted or bought.

* `GET /parlay/markets` now hides markets whose current price falls outside the leg price range that `POST /parlay/create` enforces (10 to 90 cents by default).
* A grouped event is hidden entirely while any of its outcomes is out of range.
* No funds were affected. No action required.

**Documentation:** [Packs](https://docs.limitless.exchange/user-guide/packs.md)

## Sep 4, 2026

### Apply your X handle and picture to your profile

After connecting an X account, you can now copy its handle and profile picture onto your Limitless profile in one call.

* `POST /profiles/x/connection/social-data` (authenticated) takes `{ "username": true, "avatar": true }`, each field optional, and returns `usernameApplied`, `avatarApplied`, and `usernameSkippedReason`.
* If the handle is already taken as a Limitless username, only the username is skipped (`usernameSkippedReason: "taken"`). The picture still applies.
* Disconnecting X reverts your username to a generated one when it still matches the X handle. The profile picture stays and can be changed in profile settings like any other picture.

### AMM markets can be bookmarked

Market bookmarks now cover standalone AMM markets in addition to orderbook markets and groups.

* `PUT /market-bookmarks/amm/{targetId}` saves an AMM market; `amm` joins `clob`, `negrisk`, and `ladder` as accepted kinds.
* Bookmark lists hydrate AMM market data the same way as other kinds. No action required.

### Resolution time on trading feed entries

Market subjects on `GET /feed/trading` now report when the market resolved.

* `subject.resolvedAt` holds the best available resolution time and is `null` until the market resolves.
* Group subjects carry the field as `null`. Additive change, no action required.

**Documentation:** [Trading feed](https://docs.limitless.exchange/api-reference/feed/trading-feed.md)

### Bug fix: cricket over and ball counters disappearing at zero

Live cricket data dropped over and ball counters when their value was zero, so the counters vanished during the first over of an innings and right after an over ended.

* `currentOver` and `ballInOver` on live cricket entries now keep zero values. `currentOver` counts completed overs (0 during the first over), and `ballInOver` counts legal balls bowled in the over in progress (0 right after an over ends).
* Display only; scores and market resolution were unaffected. No action required.

## Sep 3, 2026

### Pack vig raised to 10 percent

Pack pricing now applies a 10 percent vig, up from 4 percent. Displayed multipliers stay net of vig, so the same legs quote a lower multiplier than before.

* `POST /parlay/quote` responses report `vigPercent` as `0.1`; the displayed `multiplier` is `rawMultiplier` with the vig taken out.
* The net multiplier ceiling is now 20x. The pre-vig cap moved to about 22.2x so the 20x net ceiling holds.
* Stake limits are unchanged. Packs already bought keep the vig they were sold at, along with their locked-in multiplier and payout.

**Documentation:** [Packs](https://docs.limitless.exchange/user-guide/packs.md)

### Market bookmarks

Save markets to a personal bookmark list and optionally share it from your profile.

* `PUT /market-bookmarks/{targetKind}/{targetId}` (authenticated) saves a market or group; kinds are `clob`, `negrisk`, and `ladder`. A profile holds up to 100 bookmarks; adding beyond that returns `409`.
* `GET /market-bookmarks/me` returns your bookmarks with hydrated market data and an `availability` of `active`, `resolved`, or `unavailable`. A bookmark on a recurring market resolves to the series' current market.
* `DELETE /market-bookmarks/{bookmarkId}` removes one bookmark; `DELETE /market-bookmarks` clears the list.
* Bookmarks are private by default. `PATCH /market-bookmarks/visibility` with `{ "isPublic": true }` opts in, after which `GET /market-bookmarks/public/{account}` serves the list without authentication; while private, that endpoint returns `404`.

### Live cricket scores

Live score data now covers cricket matches alongside football and tennis.

* `GET /sports/live` and the `live_sports_update` WebSocket event include cricket entries, discriminated by `sportType: "cricket"`.
* Each entry carries per-side `runs`, `wickets`, and a per-over run breakdown (`overRuns`), plus match `status` and `isFinished`.
* `battingTeam`, `currentOver`, and `ballInOver` are optional fields and can be absent when the data source does not report them.
* Additive change. No action required.

### Market lifecycle and prices on trading feed entries

Feed cards from `GET /feed/trading` now carry the subject market's lifecycle and current prices, and no longer carry a per-trader live position block.

* Market subjects gain `createdAt`, `startAt`, `deadline`, `prices` (`[yes, no]` as fractions of 1), `payoutNumerators`, and `winningOutcomeIndex`.
* `prices` holds a resolved market's final resolution or the latest stored midpoint for an open orderbook market, and is `null` whenever no reliable price exists.
* Group subjects carry the new keys as `null`; a card for a group entry uses its child market's own data.
* Feed entries no longer include the `positionNow` block. Value an entry's contracts with the subject's `prices` instead.

**Documentation:** [Trading feed](https://docs.limitless.exchange/api-reference/feed/trading-feed.md)

## Sep 2, 2026

### Trading activity feed

`GET /feed/trading` returns a feed of trading activity across the platform from the last 24 hours.

* `audience` selects `all` (the default), `featured`, or `following`. The following feed requires authentication and covers the profiles you follow.
* Entry types are `BOUGHT`, `SOLD`, `RESOLVED`, `PARLAY_PLACED`, and `PARLAY_RESOLVED`, covering orderbook and AMM trades, settled positions, and pack buys and settlements.
* Each entry carries the trader's public profile, the market or group it concerns, and the trader's live position state when one is open and a valuation is available.
* Pages hold up to 30 entries (`limit`, default 30) with an opaque `cursor` for continuation.
* The `all` and `featured` audiences are CDN-cached for up to 60 seconds, so public entries can trail the newest trades slightly.

**Documentation:** [Trading feed](https://docs.limitless.exchange/api-reference/feed/trading-feed.md)

### Display details on trading feed entries

Entries on `GET /feed/trading` carry everything a card needs to render without extra lookups.

* `profile.xHandle` holds the trader's connected X handle, or `null` when no X account is connected.
* `subject.imageUrl` holds the market or group artwork.
* Pack entries carry an `entry.parlay` block: the source pack name plus per-leg team crests, named outcome labels, league, teams, live score, and kickoff time.
* Additive fields. No action required.

### Cricket match-winner markets

Cricket joins the sports lineup with match-winner markets, starting with the Caribbean Premier League.

* Each match is a standalone binary market with the two teams as its named outcomes.
* Markets resolve to the officially declared winner. A tie decided by an on-field tiebreak such as a Super Over resolves to that winner; a tie with no tiebreak, or a permanently cancelled or abandoned match, resolves 50-50.
* Postponed or rescheduled matches stay open until the listed fixture completes.
* Cricket markets carry a `sport-type` property of `cricket` and a `cricket-league` property for filtering.

### Automatic resolution for markets mirroring external venues

Markets that replicate a listing on another prediction venue now resolve automatically once that venue settles the outcome.

* Resolution can land before the market's own deadline once the source venue settles.
* Only clear-cut outcomes resolve automatically. Split or ambiguous venue results are never auto-resolved.
* Sports and price-automated markets are unaffected and keep their existing resolution paths.
* No action required. Positions redeem as usual once the market resolves.

### Higher Gold and Diamond referral tier thresholds

The top two referral tiers now require more of your own trading volume.

* Gold now requires $3,000,000 of your own CLOB trading volume, up from $1,000,000. Diamond now requires $20,000,000, up from $10,000,000.
* Existing tier floors assigned by Limitless still apply as a minimum.

**Documentation:** [Referral program](https://docs.limitless.exchange/user-guide/referral-program.md)

### MCP server: price history tool and market volume

The MCP server at `https://api.limitless.exchange/mcp` gains a price history tool and now reports trading volume on market reads.

* New `get_market_price_history` tool returns newest-first historical YES midpoint observations for one exact market slug. Interval presets are `5m`, `1h`, `6h`, `1d` (default), `1w`, `1m`, and `all`; longer lookbacks automatically use coarser buckets. For a grouped market, pass a child market slug.
* Returned prices are midpoint observations, not executable prices. Use `get_orderbook` for current liquidity.
* `search_markets`, `list_markets`, `get_market`, and `get_market_group` child entries now include a `volume` object: the raw integer value, a `formatted` amount, the token `decimals`, and explicit `unit` (`contracts`) and `scope` (`cumulative`) fields.
* Additive changes. The new tool follows the same authenticated-connection requirement as every other tool.

**Documentation:** [MCP Server](https://docs.limitless.exchange/developers/mcp-server.md)

## Sep 1, 2026

### Username on referral leaderboard and referral list entries

Entries on `GET /referral/usdc/leaderboard` (including the pinned `me` block), `GET /referral/usdc/leaderboard/friends`, and `GET /referral/usdc/referrals` now include `username: string | null` alongside `displayName`.

* For most accounts `displayName` holds a wallet address. Prefer `username` when labeling users and fall back to `displayName` when `username` is `null`.
* Additive field. `displayName` is unchanged, so existing consumers keep working.

**Documentation:** [Referral leaderboard](https://docs.limitless.exchange/api-reference/referral/leaderboard.md), [My referrals](https://docs.limitless.exchange/api-reference/referral/my-referrals.md)

### Generated usernames for new profiles

New profiles now receive a readable generated username at signup instead of a `null` username.

* The generated name is a random Adjective+Adjective+Noun combination, for example `SwiftQuickHorse`. Limitless checks that the name is free before assigning it.
* Users can still set their own username. Create and update requests cap usernames at 44 characters; existing usernames longer than that remain valid.
* Expect `username` to be populated for newly created profiles. Profiles created before this change may still have `null` until Limitless backfills them.

## Aug 31, 2026

### Usernames on leaderboard, referral, and live-offer payloads

Payloads that previously carried only `displayName` (often a wallet address) now also include the user's `username`, so clients can show readable names.

* Points and volume leaderboard entries on `GET /leaderboard/:type` gain `username`.
* Referral payloads gain `username` per entry: `GET /referral/usdc/referrals`, `GET /referral/usdc/leaderboard`, and `GET /referral/usdc/leaderboard/friends`.
* Live-offer WebSocket frames gain `username` on the `creator` object. It is nullable for frames built before the profile carried a username.
* `displayName` is unchanged everywhere. Additive fields, no action required.

**Documentation:** [My Referrals](https://docs.limitless.exchange/api-reference/referral/my-referrals.md) | [Referral Leaderboard](https://docs.limitless.exchange/api-reference/referral/leaderboard.md)

### Bug fix: NO picks rejected as thin on liquid books

Pack quoting measured NO picks in the counterparty's dollars, so a NO leg on a genuinely liquid book could be rejected as "top-of-book too thin" while the book showed ample NO liquidity.

* `POST /parlay/quote` and pack leg pricing now measure each outcome in the dollars its buyer pays. Liquid NO legs that previously came back ineligible now quote.
* NO leg prices moved by single-digit basis points; no visible price jumps.
* When a leg is ineligible, `ineligibleReasons` now lists every failed check instead of only the first.
* No action required.

**Documentation:** [Packs](https://docs.limitless.exchange/user-guide/packs.md)

### Bug fix: pack quotes ignore liquidity far above the best price

Pack leg pricing swept the entire order book, so orders resting far above the best price could distort a quoted leg price. A leg with only a few dollars of real asks could quote at a badly wrong price.

* `POST /parlay/quote` and pack leg pricing now only count liquidity within 10 cents of the best usable price.
* Books that are genuinely thin near the best price now reject with an explicit thin-book reason in `ineligibleReasons` instead of quoting a distorted price.
* Liquidity resting more than 10 cents above the best price no longer counts toward depth, so a small number of previously quotable legs now reject.
* No action required.

**Documentation:** [Packs](https://docs.limitless.exchange/user-guide/packs.md)

### Bug fix: missing tennis player photos on rescheduled matches

Tennis moneyline markets created after a reschedule could permanently show placeholder avatars and missing player names on match cards, pack legs, and homepage portraits. The event detail page showed the players correctly.

* Affected markets now pick up player photos and names on the next refresh.
* Display only; markets traded and resolved normally throughout. No action required.

## Aug 26, 2026

### Public pack positions endpoint

`GET /parlay/{account}/positions` returns a wallet's pack (parlay) positions for public profile views, newest first. No authentication required.

* Only `ACTIVE`, `WON`, and `LOST` positions appear. An optional `status` query parameter narrows the list to one of those three; other values return `400`.
* Each position includes its stake, multiplier, claim state (`isClaimed`), full leg details, and the source pack it was bought from. The public payload deliberately excludes wallet, token, and transaction fields.
* Pagination uses `limit` (1-50, default 20) and `offset` (default 0, capped at 10,000). `totalRows` reports the full matching count while `totalPages` is capped at the last browsable page.
* Responses are CDN-cached with `max-age=5, s-maxage=15`, so public status and claim state can trail the database by roughly 30 seconds.

**Documentation:** [Get User Pack Positions (Public)](https://docs.limitless.exchange/api-reference/public-portfolio/pack-positions.md)

### Profile ids on PnL leaderboard entries

Entries on `GET /leaderboard/pnl`, `GET /leaderboard/pnl/lifetime`, and `GET /leaderboard/pnl/me` now include `profileId`.

* It is the same id the follow endpoints use. Clients can resolve follow state for leaderboard rows from `GET /follow/ids` in one call instead of one lookup per row.
* Additive field. No action required.

### ATP and WTA rankings on tennis event views

Tennis event-view responses from `GET /sports/events` now carry the players' singles rankings in the match header.

* `generalInfo.teams.home` and `generalInfo.teams.away` gain a nullable `rank` field: the player's current-season ATP or WTA singles ranking.
* `rank` is `null` when no current-season ranking exists; a stale prior-season ranking is never shown.
* Football and esports event views carry the field as `null`. Additive change, no action required.

### Bug fix: grouped market titles on biggest positions

Biggest-positions entries for markets inside a group previously showed only the child market title with no outcome label, so rows like a team-total market read ambiguously.

* `GET /leaderboard/pnl/unrealized/biggest-positions` now returns the group title as the market title, with the child market shown as the entry's `outcomeLabel`.
* Named-outcome markets now carry their proper outcome labels instead of `null`.
* Display only. No action required.

**Documentation:** [Biggest open positions](https://docs.limitless.exchange/api-reference/leaderboard/biggest-positions.md)

### Bug fix: AMM volume in market search

AMM markets returned by `GET /markets/search` were missing their volume figures, so search results showed AMM markets without activity numbers alongside fully populated orderbook markets.

* Search results now include volume figures for AMM markets again.
* No parameter or shape changes. No action required.

**Documentation:** [Search markets](https://docs.limitless.exchange/api-reference/markets/search.md)

### Bug fix: CS2 final-map round scores after settlement

On CS2 event views, a match that settled within minutes of its final map could show the decisive map with a missing round score. In the worst case, the gap lasted up to 7 days.

* `GET /sports/events` now keeps re-reading a finished CS2 map until its round score lands. Settled matches with an incomplete final-map score refresh within about an hour instead of staying stale for days.
* Display only; market settlement was never affected. No action required.

## Aug 25, 2026

### Category leaderboards and PnL-ranked biggest positions

Leaderboards can now be scoped to a category, and the biggest-positions board can rank by unrealized PnL instead of position size.

* `GET /leaderboard/pnl` accepts `scope=category` with a required `marketPageId` (the category's page id); category scope supports the `24h` window.
* `GET /leaderboard/pnl/unrealized/biggest-positions` gains a `metric` param: `position_size` (default, unchanged behavior) or `pnl`, plus an optional `marketPageId` to rank within one category when using `pnl`.
* Responses echo `metric` and `marketPageId`, entries gain `avgEntry`, and each entry's market carries an `imageUrl` for linking.
* Existing calls keep working unchanged.

**Documentation:** [Biggest open positions](https://docs.limitless.exchange/api-reference/leaderboard/biggest-positions.md)

### Higher parlay limits

Parlays now allow larger stakes, more legs, and higher multipliers.

* The maximum stake on `POST /parlay/quote` and `POST /parlay/create` is now $70, up from $50. The maker-funded flow keeps its separate \$100 ceiling.
* Parlays now accept 2 to 5 legs, up from a maximum of 3. Packs can also carry 4 or 5 legs.
* The maximum offered multiplier is now about 20x, up from about 14.4x. Baskets previously rejected for exceeding the multiplier cap can now quote.
* Clients hard-coding the old \$50, 3-leg, or multiplier limits should update.

**Documentation:** [Packs](https://docs.limitless.exchange/user-guide/packs.md)

### Match and prop markers on parlay outcomes

Parlay surfaces now say explicitly whether an outcome is the match itself or a prop, so clients no longer render esports map-winner props as duplicate match cards.

* Each outcome on `GET /parlay/markets` gains `isMatch`: `true` for the event or match market, `false` for a typed prop.
* Parlay position legs and pack legs gain a nullable `esportsPropType`: `map_winner`, `map_handicap`, or `total_maps`; `null` for match winners and non-esports markets.
* Additive fields. No action required.

**Documentation:** [Packs](https://docs.limitless.exchange/user-guide/packs.md)

### Daily top-trades digest in Telegram and Discord

Group chats subscribed to a category via `/topics` now receive one digest a day listing the biggest positions opened in that category on Limitless.

* Sent daily at 16:00 UTC, covering positions opened in the last 24 hours.
* Up to 10 positions per category, each at least \$25, with the market, side, amount, and payout multiplier.
* The digest names each trader by their public username, or a shortened address when they have none.
* Uses existing `/topics` subscriptions; no new commands.

### Bug fix: manage your orders from esports match pages without a market group

`GET /sports-markets/:slug/user-orders` and `DELETE /sports-markets/:slug/user-orders` now work for esports matches that have a standalone match-winner market instead of a NegRisk group (odd best-of and first-to formats). Both routes previously returned `404` for these slugs, and cancelling per market could leave prop orders live.

* Pass the standalone match-winner market slug. Your match-winner orders fill the `groups` section and your prop orders (map winner, total maps, handicaps) fill `props`; `offThePitch` stays empty for esports.
* `DELETE` cancels every open order you have across all markets of that match in one call, matching the football and tennis flow.
* Even best-of matches keep resolving through their group slug. This mirrors the Aug 20 tennis fix. Authentication required, as before.

### Market description limit raised to 10,000 characters

Market descriptions now accept up to 10,000 plain-text characters, up from 6,000.

## Aug 24, 2026

### Esports payload on the unified event view

`GET /sports/events` now serves the full esports match-page payload for all four videogames: `cs-go`, `dota-2`, `league-of-legends`, and `valorant`. Query with `esportType` (a videogame slug) plus the provider event id from the market's metadata, as introduced in the Aug 14 unified event view. The response echoes the provider's canonical videogame slug, not the request string.

* **Score** uses an esports shape: series score (maps won per side), a `games` array with per-game status, winner, length, and current game position. CS2 games also carry the map name and finished-map round scores, updated live each minute. League of Legends games carry the final kill score shortly after each game ends.
* **Streams** is a new top-level response section: broadcast embeds (for example Twitch and Kick) with `embedUrl`, `rawUrl`, language, and `main`/`official` flags. The main and official streams are listed first. The section is `null` for football and tennis.
* **General info** gains three fields: `serieName` (the tournament serie label for the page header), `tier` (`s` | `a` | `b` | `c` | `d`), and `eventKind` (`online` | `offline` | `online/offline`). `bestOf` is now populated for esports as the best-of map count. All three new fields are `null` for other sports.
* **Lineups** carry team rosters with per-title player roles.
* **Match stats** (League of Legends only) list per-team rows for each finished game: kills, gold, towers, dragons, and barons.
* Head-to-head history, per-team recent form, and team stats (series and map win rates) are populated for all four titles.

### Public accuracy endpoint

`GET /user-stats/accuracy/{account}` returns a wallet's accuracy score for public profile views: markets `won`, `lost`, `total` resolved, and `since` (the earliest resolved date tracked). No authentication required.

* The `200` body is nullable: expect `null` when no accuracy data is available for the address yet.
* The address is normalized server-side (EIP-55 or lowercase both work). A malformed address returns `400`.
* Successful responses are CDN-cached for up to 15 seconds; errors are not cached.
* The endpoint is feature-flagged and returns `404` while accuracy scoring is disabled.

**Documentation:** [Get User Accuracy (Public)](https://docs.limitless.exchange/api-reference/public-portfolio/accuracy.md)

### Bug fix: filter tab counts on market pages

Market page listings previously omitted the `counts` object when an active filter matched zero markets, so clients fell back to unscoped page totals next to an empty list.

* `GET /market-pages/:id/markets` and the by-path variant now always include `counts` while a filter is active, even when every value is `0`.
* An absent `counts` now reliably means no filter is active.
* No new fields or parameters. No action required.

**Documentation:** [List page markets](https://docs.limitless.exchange/api-reference/navigation/list-page-markets.md)

### Bug fix: selecting a whole filter group respects its configured options

Selecting a filter group's parent row (the `__all__` value) on market pages previously matched every market carrying that property, surfacing values outside the curated set for that group.

* `__all__` now expands only over the options configured for the group, in both the market list and the tab counters, so lists and counts agree.
* It falls back to matching any value only when the group has no configured option subset.
* Same parameters and response shape; only the returned set changes.

**Documentation:** [List page markets](https://docs.limitless.exchange/api-reference/navigation/list-page-markets.md)

### Bug fix: your own PnL chart refreshes when you view it

Viewing your own PnL chart previously never triggered a data catch-up, so your chart could lag behind recent trading activity.

* `GET /portfolio/:account/pnl-chart` now accepts optional authentication. When the caller and the requested address resolve to the same profile, the chart data refreshes on read.
* Owner responses are returned uncached.
* Anonymous and non-owner requests are unchanged, including caching. No action required.

**Documentation:** [PnL chart](https://docs.limitless.exchange/api-reference/public-portfolio/pnl-chart.md)

## Aug 22, 2026

### Bug fix: settlement failures and wrongful blocks for smart-contract wallets

Some matched trades that delivered outcome tokens to smart-contract wallets could fail to settle. A wallet that hit this failure could also be wrongly auto-blocked, which cancelled its resting orders and stopped it from trading.

* Trades of the affected shape now settle successfully.
* This settlement failure mode no longer triggers an automatic block; only genuine rejection by the receiving wallet does.
* A small number of trades and wallets were affected in production.

## Aug 21, 2026

### Following feed

`GET /feed/following` returns recent activity from the profiles you follow, covering the last 24 hours. Authentication required.

* Query params: `limit` (1-100, default 30) and `cursor` (opaque string from the previous page).
* `400` for a malformed cursor; `409` when your follow list changed since the cursor was issued (restart pagination); `503` when the feed is temporarily unavailable, never a silently empty response.
* Responses are per-viewer and not cached.
* The public `GET /feed` is unchanged.

### Browser alerts for a trader's trades

New endpoints under `/profile-notifications` let you receive browser push alerts when a chosen trader's trades finalize, covering both AMM and orderbook trades.

* `GET /profile-notifications/vapid-public-key` is public; registering or removing a browser subscription (`POST` / `DELETE /profile-notifications/browser-subscriptions`) requires authentication, with up to 5 browsers per profile.
* Manage per-trader subscriptions via `GET | PUT | DELETE /profile-notifications/users/:account`, with a `tradeAmountFilter` of `ALL` or `GTE_100_USD`.
* Alerts deep-link to the market and include the trader, market, side, and outcome. Trades on hidden markets are excluded.
* Alerts are sampled: subscribers receive a portion of a trader's finalized trades, not every one.
* Alert subscriptions are independent of the social follow feature.

### Tennis parlays

Tennis matchups and props are now first-class parlay legs on `GET /parlay/markets`.

* Tennis cards carry the tournament label; previously they showed no league.
* Player headshots now populate `outcomeImageUrls` on tennis matchup cards instead of a placeholder avatar.
* A match's moneyline and prop cards share one event grouping, so they cluster together instead of appearing unrelated.
* Tennis prop markets (total sets, total games) are offered alongside the match winner.

**Documentation:** [Packs](https://docs.limitless.exchange/user-guide/packs.md)

### Esports parlay league labels and pre-kickoff cutoff

Esports parlay cards now show the actual league (for example "EWC 2026") instead of the game title, and matches that have already started no longer appear as offerable legs.

* League labels resolve to the most specific league tag first, with the game discipline as last fallback.

### Bug fix: Telegram account-link confirmation in DMs

After you completed account linking on limitless.exchange from a Telegram group, the bot's DM conversation went silent. The confirmation posted only in the group chat, making the flow look stalled.

* The bot now sends you a private confirmation naming the group you linked for.
* Discord behavior is unchanged.

## Aug 20, 2026

### Tennis props and tournament matches on match-page routes

The match-page routes now work for tennis market slugs. Previously they only resolved via market group slugs, which tennis markets don't have, so tennis pages returned `404`.

* `GET /sports-markets/:slug/props` returns tennis ladders keyed by market type: `total_sets` and `total_games`, each sorted by threshold, including open and resolved markets.
* `GET /sports-markets/:slug/league-matches` returns other open match-winner markets from the same tournament, sorted by volume descending, with the tournament name as the label.
* Both routes are public with a 60-second shared cache. Football and esports behavior is unchanged.

### Manage your orders from tennis match pages

`GET /sports-markets/:slug/user-orders` and `DELETE /sports-markets/:slug/user-orders` now work for tennis market slugs; both previously returned `404` for tennis.

* The response groups your match-winner orders and totals-market orders for the whole match.
* `DELETE` cancels every open order you have across all markets of that tennis match in one call, matching the football flow.
* Authentication required, as before.

### Tennis round metadata

Tennis market metadata gains a `roundShort` field, and the tournament round now fills in reliably on match pages.

* `roundShort` uses a closed vocabulary: `1/64`, `1/32`, `1/16`, `1/8`, `1/4`, `1/2`, `final`; unrecognized round wording (qualifying, round-robin) stays `null`.
* The round is re-checked until the tournament annotates it, so `league.round` no longer stays `null` forever when the data arrives late.

### Parlay card metadata for outcomes, artwork, and classification

Parlay market cards, pack legs, and position legs now carry server-owned display metadata, so clients no longer derive labels and artwork locally.

* `outcomeLabels`: outcome button labels for named-outcome markets (home/away team names); `null` for plain Yes/No markets.
* `outcomeImageUrls`: team or side artwork as a home/away pair; `null` when unavailable.
* `properties`: league and discipline tags for classifying cards, plus `marketType` (`single` or `group`) and raw prop facts (`fixtureKey`, `propType`, `propLine`) for grouping fixture cards.
* Bug fix: confirming a claim on a parlay bought from a pack now returns the parlay with its `sourcePack` populated.

**Documentation:** [Packs](https://docs.limitless.exchange/user-guide/packs.md)

### Market description limit raised to 6,000 characters

Market descriptions now accept up to 6,000 plain-text characters (previously 4,000). The title limit is unchanged at 120 characters.

* Applies to all market, group, and ladder create and update paths.
* Description length is measured against visible text; HTML markup and entities are stripped before counting.
* No action required.

## Aug 18, 2026

### Public profile realized PnL endpoint

`GET /portfolio/{account}/realized-pnl` returns a wallet's realized PnL timeline for public profile views, with a category breakdown grouped by navigation section (e.g. sport, crypto) and a cumulative timeline series.

* Query with an optional `timeframe` of `1d`, `1w`, or `1m` (default `1w`). Unknown values return `400`.
* Response includes `windowStart`, a `current` snapshot, `categories` (sorted by realized PnL descending, with a synthetic `other` bucket for uncategorized markets), and `data` (per-point cumulative realized PnL).
* Figures are best-effort for the most recent minutes until the current aggregation window closes.
* The legacy `GET /portfolio/{account}/pnl-chart` is now marked deprecated. It still responds; migrate to `/realized-pnl` when convenient.

**Documentation:** [Realized PnL (Public)](https://docs.limitless.exchange/api-reference/public-portfolio/realized-pnl.md)

### Current season points on `/portfolio/points`

The `/portfolio/points` response gains a `currentSeason` field alongside the existing `currentMonth`. Points months are 28-day windows, so `currentMonth` reads as zero for most accounts immediately after a month rollover. Use `currentSeason` for a live running total across the season in progress.

* New field: `currentSeason` on `GET /portfolio/points`.
* `currentMonth` is unchanged and still returned.
* No action required.

**Documentation:** [Get Points Breakdown](https://docs.limitless.exchange/api-reference/portfolio/points.md)

### Larger market title and description limits

Market titles now accept up to 120 characters (previously 70) and descriptions up to 4,000 plain-text characters (previously 3,000). The limits are enforced consistently across markets, groups, and ladders.

* Applies to all market, group, and ladder create and update paths.
* Description length is measured against visible text; HTML markup and entities are stripped before counting.
* Duplicating a title at the new maximum no longer silently truncates it.
* No action required.

### Tennis fixtures on `GET /sports/events`

Tennis fixtures now return a full tennis-shaped payload from `GET /sports/events`. Football and esports responses are unchanged.

* `generalInfo` carries players, tournament, series, `bestOf`, and a strict `clay | grass | hard` surface parse with a fallback to the raw tournament name when unset.
* Top-level `score` uses a tennis shape: sets, games, points, and server.
* Head-to-head, per-player recent form, and per-player season averages (with latest-season surface win rates) are populated from the stats provider.
* Player photos are populated when available and omitted otherwise.

### Football postponed and never-played match copy

Football Result (1X2), BTTS, and total-goals markets now carry updated description copy that matches how these markets actually resolve.

* Postponed matches are waited out with no fixed deadline. An officially recognized result (abandoned, cancelled, awarded) is honored when returned.
* For a match that will never be played: team legs resolve NO, the Draw leg resolves YES (preserving the one-winner invariant), and the CLOB props resolve 50-50.
* Corners, cards, spreads, player props, and user-created templates keep their existing copy.

### NYSE-aware scheduling for equity and FX markets

Equity and FX market scheduling now follows the NYSE trading calendar instead of pure arithmetic, closing gaps where markets could appear outside trading sessions.

* Equity markets are only scheduled for whole NYSE sessions; intraday markets align to the top-of-hour grid anchored at midnight ET, and daily equity markets run close-to-close.
* Weekly equity markets resolve on the last session of the week, with Thursday used when the following Friday is an NYSE holiday.
* FX markets whose deadline falls on a UTC Saturday or Sunday are not created; a Sunday 23:00 UTC market survives because it resolves on Monday.
* Crypto and commodities keep the round-the-clock grid.
* No trades or funds were affected. No action required.

## Aug 17, 2026

### TWAP resolution coming to 5-minute and 15-minute crypto markets

Scheduled for **Wednesday, August 19**: short-cadence crypto up/down markets begin resolving on a **Chainlink time-weighted average price (TWAP)** instead of a single instantaneous price. Advance notice for builders: if you trade or quote these markets programmatically, review your assumptions about how the boundary price is determined.

* **What changes:** both the Price to Beat (captured at open) and the closing value come from the same Chainlink TWAP stream — an average over a fixed window — rather than one price tick. The closing TWAP greater than or equal to the Price to Beat resolves **Up**; otherwise **Down**.
* **Why:** an average over the window means a momentary spike at the market boundary does not decide the outcome on its own.
* **Detection:** TWAP markets carry `streamType: "twap"` and `twapWindowSeconds` on `metadata.chainlinkDataStream` in market responses; existing spot-resolved markets carry `streamType: "spot"`. Each market's description names the exact feed, window, and tolerance.
* **Unchanged:** market cadence, slugs, trading, order flow, and settlement. This is a resolution-source change only, applied per market. Read the market's description and `metadata.chainlinkDataStream` to see which rule applies.

**Documentation:** [Market resolution — Chainlink TWAP](https://docs.limitless.exchange/user-guide/market-resolution.md#chainlink-twap-resolution) | [Get Market](https://docs.limitless.exchange/api-reference/markets/get-market.md)

## Aug 14, 2026

### Unified event view for sports and esports match pages

`GET /sports/events` returns the match-page context for a fixture in one call: the event header, head-to-head history, and recent team form, for football, tennis, and esports fixtures.

* Query with `sportType` or `esportType` (a videogame slug such as `cs-go`), which are mutually exclusive, plus the provider event id carried on the market's metadata.
* One response replaces the separate lookups clients previously stitched together for match pages.
* No changes to market, orderbook, or trading endpoints.

## Aug 13, 2026

### Market properties on public responses

Public market responses now include the market's property assignments as `properties` — pairs of `propertyKeySlug` and `value`. The field appears on market details, group details (including child markets), and the feed and navigation listings that power cards and market lists.

* Also present on sports and esports props, specials, and tournament bracket responses that can initiate trades.
* The field is empty when a market has no properties, and responses degrade to empty properties rather than failing when enrichment is unavailable.
* No action required.

**Documentation:** [Get Market](https://docs.limitless.exchange/api-reference/markets/get-market.md)

## Aug 12, 2026

### All four SDKs: v1.1.0

The TypeScript, Python, Go, and Rust SDKs are released as v1.1.0. Non-breaking upgrades across the board; existing method signatures are unchanged.

* AMM trading: typed buy and sell plus allowance check/approve workflows, for direct wallets and partner-owned server wallets (the programmatic AMM surface shipped Aug 3).
* Cancel-replace: single and batch variants with typed request and response models, including the delegated partner path.
* Opt-in raw HTTP responses: every API-backed service method gains a variant returning the status, headers, and original body alongside the typed result.
* Plus per-SDK fixes and enhancements. See each SDK's changelog for the full list.
* Packages: `@limitless-exchange/sdk` 1.1.0 on npm, `limitless-sdk` 1.1.0 on PyPI, Go and Rust at v1.1.0.

**Documentation:** [SDK orders](https://docs.limitless.exchange/developers/sdk/typescript/orders.md), [AMM Trading guide](https://docs.limitless.exchange/developers/amm-trading.md), [Cancel and Replace Order](https://docs.limitless.exchange/api-reference/trading/cancel-replace.md)

## Aug 11, 2026

### Filter portfolio history by market

`GET /portfolio/history` now accepts an optional `market=<slug>` query parameter. When set, the response only includes activity for that market across every source: CLOB and AMM trades, splits/merges, NegRisk conversions, claims, and resolutions. Use it to verify a single market's activity without walking your full account history.

* An unknown `market` slug returns `404`.
* Cursors are market-scoped: a `nextCursor` issued for one `market` value is only valid when replayed with the same `market` value on the next page. Mixing a filtered cursor with a different or missing `market` produces incorrect pagination.
* Requests without `market` behave exactly as before.

**Documentation:** [Get History](https://docs.limitless.exchange/api-reference/portfolio/history.md)

## Aug 10, 2026

### Richer identifiers on `/portfolio/history` rows

CLOB rows in `GET /portfolio/history` now carry the identifiers needed to reconcile a history entry back to the trade and order that produced it.

* Response items may now include `tradeEventId`, `orderId`, and `makerMatchId` on CLOB-sourced rows.
* Existing fields (`operation`, `blockTimestamp`, `collateralAmount`, and the rest) are unchanged.
* All three new fields are optional. No action required.

**Documentation:** [Get History](https://docs.limitless.exchange/api-reference/portfolio/history.md)

### Bug fix: `/portfolio/history` pages past source limits

Long account histories now paginate cleanly across every data source that backs `/portfolio/history`. Previously a single `nextCursor` could stop advancing once one underlying source hit its internal window, leaving the reader with an incomplete history and no way to resume.

* Affects `GET /portfolio/history` for accounts with activity spanning long time ranges.
* Cursor walks now continue until all matching rows are returned.
* No trades, positions, or funds were affected. Re-page from the first page to backfill any gap that was previously unreachable.

**Documentation:** [Get History](https://docs.limitless.exchange/api-reference/portfolio/history.md)

## Aug 7, 2026

### Public trading history endpoint

A new public `GET /portfolio/{account}/history` endpoint returns the trading history of any wallet address with the same cursor-based pagination as the authenticated `/portfolio/history` route. Profile pages and third-party read integrations can now surface a wallet's history without an authenticated session.

* Path: `GET /portfolio/{account}/history`. Accepts `cursor` and `limit` query parameters; default `limit` is `20`.
* Address is normalized to EIP-55 checksum form. Invalid addresses return `400`; addresses with no associated Limitless profile return `404`.
* Response shape matches the authenticated `/portfolio/history` route, including cursors and the new CLOB identifier fields.

**Documentation:** [Get User History (Public)](https://docs.limitless.exchange/api-reference/public-portfolio/history.md)

### Clearer resolution rules on esports match-winner markets

Standalone CLOB match-winner descriptions on esports markets now spell out the fallback rules that were previously implicit. Traders can see exactly how mid-match forfeits, walkovers, and late cancellations resolve before entering a position.

* Applies to standalone CLOB `MATCH_WINNER` markets on esports fixtures. NegRisk 3-way markets and prop descriptions are unchanged.
* Descriptions now spell out: match not played or delayed beyond 7 days resolves 50-50; mid-match forfeit, disqualification, or walkover resolves to the team that wins; a forfeit before the start resolves 50-50.
* No API or payload changes. No action required.

## Aug 6, 2026

### Cancel and replace an order in one call

New `POST /orders/cancel-replace` and `POST /orders/cancel-replace/batch` endpoints let a trader cancel a resting order and submit its replacement in a single request. Useful for repricing quotes without maintaining two client-side steps.

* The two actions are non-atomic. Each of the cancellation and replacement returns its own outcome (`SUCCESS`, `FAILURE`, or `UNKNOWN`; the replacement can also be `NOT_ATTEMPTED`).
* Choose behavior with `mode`: `STOP_ON_FAILURE` skips the replacement when the cancel fails; `ALLOW_FAILURE` attempts the replacement regardless.
* Batch endpoint runs up to the standard batch size sequentially, returning per-operation results with their original `index`. Full success returns `200`; partial success returns `207` (batch) or `409` (single).
* Cancellation identifies the target by `orderId` or `clientOrderId`. Replacement uses the standard signed order body and must be EIP-712 signed by the profile that owns the cancelled order.
* Authentication matches the existing cancel route: HMAC (`apiToken`), Privy, and session are accepted. Partners can target a sub-account with `onBehalfOf` at the operation level (not inside `replacement`).

**Documentation:** [SDK orders](https://docs.limitless.exchange/developers/sdk/typescript/orders.md)

## Aug 5, 2026

### Embed Limitless markets on any site

You can now embed a live Limitless market widget on external sites. The builder at [embed.limitless.exchange](https://embed.limitless.exchange) turns any market or category link into a copy-paste snippet. Each snippet renders real-time odds, a price chart, and buy buttons in a sandboxed iframe, with layout, theme, and size controls.

* Three snippet formats: Default (styled iframe with SEO markup), Script (auto-sizing height), and Minimal (bare iframe for platforms like Notion).
* Category embeds rotate through the category's top live markets and replace resolved markets automatically; rotation speed, pool size, and sort are configurable.
* Crypto price markets show a live asset-price line with an Odds ↔ Price toggle; sports fixtures render as a live scoreboard.
* Every snippet carries a referral code. Use the code from your Limitless account to earn a share of referred users' trading fees (10–40% by tier, in USDC, paid daily) through the referral program.
* Embedding is free and requires no account; a Limitless account is needed only to collect referral rewards.

**Documentation:** [Embed Limitless Markets](https://docs.limitless.exchange/user-guide/embed-markets.md), [Referral Program](https://docs.limitless.exchange/user-guide/referral-program.md)

### Faster automated resolution for football score markets

Football markets that resolve from the final score are now eligible for automated resolution at kickoff plus 105 minutes, roughly regulation full time. This covers 1X2 group markets and BTTS, TOTAL\_GOALS, and SPREADS solo markets. Previously these markets waited until deadline minus 21 hours, about kickoff plus 3 hours. Stats-based props and team-to-advance markets still use the earlier gate.

* Applies to score-derived football markets only. Other sports and market types are unchanged.
* Resolution never fires before the fixture reaches FT, AET, or PEN. The earlier window only starts polling.
* No API or payload changes. No action required.

**Documentation:** [Market resolution](https://docs.limitless.exchange/user-guide/market-resolution.md)

### Bug fix: `subscribe_positions` ignores empty payloads

Emitting `subscribe_positions` over the WebSocket API with no `marketAddresses` and no `marketSlugs` now returns an empty stream without touching any existing subscription. Previously, the server accepted the empty payload, cancelled the client's prior position subscription, and then returned nothing, so updates stopped silently.

* Affects the WebSocket `subscribe_positions` event only.
* A previous non-empty subscription on the same connection continues to receive updates.
* Include at least one market address or slug to open a subscription. The same payload shape and replace-on-resubscribe behavior otherwise apply.

**Documentation:** [WebSocket events](https://docs.limitless.exchange/developers/websocket/overview.md)

### Bug fix: positions refresh immediately when an order rests

Placing a limit order that rests on the orderbook now refreshes your cached portfolio positions right away. A follow-up read reflects the new open exposure without waiting for a fill. Previously, positions could only refresh when an order matched, so a resting-only order left stale values until the next trade.

* Applies to `GET /portfolio/positions` and to the positions view in the app.
* No positions, orders, or funds were affected. No action required.

**Documentation:** [Positions](https://docs.limitless.exchange/api-reference/portfolio/positions.md), [Create Order](https://docs.limitless.exchange/api-reference/trading/create-order.md)

## Aug 4, 2026

### Paginated Unrealized PnL market leaderboard

The market-scoped Unrealized PnL leaderboard now supports page-based pagination, matching the realized-PnL leaderboard convention. Existing clients keep working unchanged: an omitted `page` is treated as `page=1` and the `limit` default remains `100`.

* `GET /leaderboard/pnl/unrealized/markets/{marketId}` accepts a new `page` query parameter (integer, `1..100`, defaults to `1`); `limit` is unchanged (`1..100`, defaults to `100`).
* Responses now include `page`, `totalRows`, and `totalPages`. `totalRows` reflects the committed Top-100 generation for that market.
* `rank` remains absolute across pages — with `limit=10`, page 2 starts at rank `11`.
* The `ETag` is page-scoped, so `If-None-Match` validators cannot cross pages.
* The `biggest-positions` route is unchanged.

**Documentation:** [Unrealized PnL leaderboard by market](https://docs.limitless.exchange/api-reference/leaderboard/unrealized-pnl-market.md)

### More packs stay quotable in thin orderbooks

Pack quoting now applies a consistent depth requirement across every leg side, so more packs price and stay available when orderbook depth is thinner.

* The quote response contract is unchanged (`eligible`, `ineligibleReasons`, `multiplier`, `potentialPayout`, `collateralRequired`, `legs`); only which quotes come back as `eligible: true` changes.
* No action required for existing integrations.

**Documentation:** [Packs](https://docs.limitless.exchange/user-guide/packs.md)

### Bug fix: Unrealized PnL leaderboard omits entries without a valuation

Live Unrealized PnL leaderboard responses now skip entries whose mark is temporarily unavailable, so ranking pages return only rows with a computable Unrealized PnL. Previously, a missing mark could leave a row in the response with an unusable valuation.

* Affects `GET /leaderboard/pnl/unrealized/markets/{marketId}` and `GET /leaderboard/pnl/unrealized/biggest-positions`.
* Rows with a valid `mark`, `marketValue`, and `unrealizedPnl` are returned as before; rows without an available valuation are excluded from that snapshot and reappear once a mark is available.
* Ranks remain absolute across the returned page. No positions, orders, or funds were affected. No action required.

**Documentation:** [Unrealized PnL leaderboard by market](https://docs.limitless.exchange/api-reference/leaderboard/unrealized-pnl-market.md), [biggest open positions](https://docs.limitless.exchange/api-reference/leaderboard/biggest-positions.md)

## Aug 3, 2026

### Programmatic AMM trading for server wallets

Partners can now execute AMM buy and sell trades — and manage the underlying token approvals — through the Programmatic API using a Privy server-managed wallet. This closes the gap between CLOB (already supported) and AMM markets for delegated trading flows.

* New endpoints: `POST /amm/buy`, `POST /amm/sell`, `POST /amm/allowances/check`, `POST /amm/allowances/approve`.
* Requires an HMAC-signed API token with both the `trading` and `delegated_signing` scopes. Legacy API keys are not accepted.
* Partners target an owned sub-account with `onBehalfOf` in the request body, matching the existing portfolio write endpoints.
* Only AMM markets in `FUNDED` state with a future deadline are tradable. Amounts are positive integer strings in the market's collateral base units; buy takes `collateralAmount`, sell takes `collateralReturnAmount`. Outcome `0` is YES, `1` is NO.
* Slippage defaults to 100 bps and is capped at 1000 bps. Execution bounds are computed from a fresh on-chain quote at submission time.
* Allowances are explicit and one-time per wallet/market/side: buy needs a collateral ERC-20 approval to the market, sell needs a CTF `setApprovalForAll`. `approve` returns `200` when already ready or `202` immediately after submission; poll `check` until confirmed. Buy and sell do not auto-approve.
* Each trade requires a partner `idempotencyKey` bound to the trade fingerprint for 24 hours. Replays of the same key return the original submission; mismatched reuse returns `409`.
* Successful submissions return Privy `transactionId`, `userOperationHash`, and/or `txHash` (sponsored user operations may not have a synchronous `txHash`).
* Rate limit: 10 requests per 10 seconds per caller.

**Documentation:** [AMM Trading guide](https://docs.limitless.exchange/developers/amm-trading.md), [Programmatic API](https://docs.limitless.exchange/developers/programmatic-api.md), [Derive API token](https://docs.limitless.exchange/api-reference/api-tokens/derive-token.md)

### Bug fix: manual LP reward distribution records paid rewards correctly

Manual LP reward distribution now records paid rewards and the linked on-chain payout after the transaction confirms. Previously, the API returned an error and marked the payout as failed even after the Base transaction had confirmed, leaving reward rows without their payout link.

* Affects the manual LP reward distribution endpoint only.
* After a payout transaction confirms, the associated reward rows are now marked paid and linked to the payout in the same request.
* If the payout update does not affect exactly one row, distribution stops before rewards are marked paid and before any success event is published, so state stays consistent.
* No funds were lost. On-chain payouts that already confirmed prior to this fix are reconciled separately.
* No action required from traders or integrators.

**Documentation:** [LP Rewards](https://docs.limitless.exchange/user-guide/lp-rewards.md)

### Bug fix: LP reward distribution reliability restored

Daily LP reward distribution runs are reliable again. The scheduled distribution job had started failing on backlogs of unpaid rewards because a single aggregation query could time out against the database. The job now processes the same rewards across smaller bounded pages, so distributions complete within the request timeout even with large backlogs.

* Affects the scheduled LP reward payout job; no API contract, authentication, or payout-math changes.
* No funds were lost — unpaid rewards remained queued and are paid out on the next successful run.
* No action required from traders or integrators.

**Documentation:** [LP Rewards](https://docs.limitless.exchange/user-guide/lp-rewards.md)

## Aug 1, 2026

### Bug fix: Unrealized PnL leaderboard degrades gracefully under backpressure

The live Unrealized PnL leaderboard now isolates backpressure incidents to the leaderboard itself, so other endpoints stay unaffected. Clients continue to receive a response for `GET /leaderboard/pnl/unrealized/markets/{marketId}` and `GET /leaderboard/pnl/unrealized/biggest-positions`; the snapshot reports its recovery state until fresh data is available.

* Under pressure, incoming mark and position updates are dropped rather than written as partial state, so ranking data can go stale but never corrupt.
* Snapshots that haven't fully rebuilt continue to return `state: DEGRADED` with a `staleReason` (or `BUILDING` when there is no snapshot yet) instead of being promoted to `READY`. Existing clients that already branch on `state` need no changes.
* No positions, orders, or funds were affected. No action required.

**Documentation:** [Unrealized PnL leaderboard by market](https://docs.limitless.exchange/api-reference/leaderboard/unrealized-pnl-market.md), [biggest open positions](https://docs.limitless.exchange/api-reference/leaderboard/biggest-positions.md)

## Jul 31, 2026

### Live unrealized PnL leaderboard

A new live leaderboard ranks traders by unrealized PnL across their open positions, updating in real time as marks move.

* A dedicated live projection, fed by finalized CLOB, AMM, split/merge, conversion, and resolution events, maintains open-position state and leaderboard generations
* The API exposes new leaderboard read routes (market-scoped rankings and biggest positions), and the WebSocket layer sends lightweight invalidation hints so clients know when to refetch

### Live markets on a whole team

User-created live markets can now target a **team**, not only the match or a single named player — for example "any Chelsea player to score, get a yellow, or get a red in the next 5, 10, or 15 minutes." Another user takes the other side, and the market settles from the same match events as existing live windows.

* Market types now form a grid: four event kinds (goal, card, yellow card, red card) across three scopes (match, team, player) — twelve types in total
* Own goals are excluded on every scope

### Live windows settle after full time

Live-window markets now settle once the match is **over**, not when the window's half ends. A market like "goal between 24' and 28'" previously settled at half time; it now settles roughly an hour after the final whistle.

* Why: the data provider keeps amending match events after the whistle (e.g. a late VAR reversal). Settling at the half could pay out on events that later changed; waiting for full time plus a delay means settlement reads the final record
* Suspended or interrupted matches retry until play resumes; matches that end with no result (postponed, cancelled, abandoned, awarded) settle on the events recorded in-window, after the same post-match delay

### Esports: `videogameSlug` on every market response

Esports market responses now expose the videogame slug (`cs-go`, `league-of-legends`, …) under a single key, `videogameSlug`, in the public market metadata — for both match groups and solo props. Previously groups carried the value only as `esportTitle` while solo props used `videogameSlug`, forcing consumers to branch on market kind. Additive change; `esportTitle` is untouched.

### Bug fix: fee-module wallet excluded from holder lists

Market holder lists and top-holder queries no longer include the venue's fee-module contract wallet, which could previously appear as a large "holder" on fee-bearing markets. Display-only fix; no positions or funds were affected.

## Jul 30, 2026

### Tennis: total sets and total games markets

Tennis matches now get automatically created solo CLOB prop markets, following the same pattern as the football props:

* **Total Sets** — over/under (e.g. 2.5)
* **Total Games** — over/under lines (e.g. 21.5 / 22.5 / 23.5)
* Created automatically per match and resolved from official settlement data; carry `metadata.externalSlug` where a matching Polymarket market exists

### Bug fix: league-scoped tab counts on sport pages

On sport pages, the Matches/Props tab counts now reflect the league filter the visitor picked instead of whole-sport totals (e.g. filtering to one tennis league previously kept showing all-tennis counts).

### X account connections now brokered through the platform

The X-account connect flow now runs on the platform's own OAuth handshake instead of being brokered through Privy. This removes a case where users who had signed in with X on any other Limitless account could not connect that same X account to a new profile.

* Connecting an X account that is already active on another profile now transfers it. The previous profile is marked disconnected in the same operation, and the new profile owns the connection.
* One active X connection per profile and one active profile per X account are still enforced. Simultaneous connect attempts return `409`; the losing caller is asked to retry.
* The connect and disconnect endpoints require a Privy or session-authenticated user. Machine API tokens cannot manage the X identity.
* Disconnect immediately clears stored credentials and best-effort revokes the refresh token at X; the connection row is retained so the account can be reconnected later.

## Jul 29, 2026

### Connect an X account to your Limitless profile

Profiles can now be linked to an X account. Once connected, the handle is exposed on the public profile connection resource so anyone can jump from a Limitless profile to the linked X profile.

* New endpoints on `/profiles`: `POST /x/connection/authorize` returns an `x.com/i/oauth2/authorize` URL to redirect the user to, `POST /x/connection` exchanges the returned `{ code, state }` for a stored connection, and `DELETE /x/connection` disconnects.
* Public read: `GET /profiles/:account/x-connection` returns `{ connected, xHandle }` for any caller, including logged-out visitors, and is CDN-cached.
* Owner-only fresh read: `GET /profiles/:account/x-connection/handle` returns the handle for the profile owner without CDN caching, so a user sees their own connect/disconnect immediately.
* Rate limits: 5 mutations per minute per profile, 120 public reads per minute per IP, 60 owner reads per minute per account.

### Partner-restricted market pages

You can now gate a market page to a specific partner and their sub-accounts, so a partner can preview hidden markets on a dedicated page before announcing them publicly. Public pages are unchanged.

* New `restrictedToProfileIds` allowlist on market page create and update. `null` or empty means the page stays public.
* A caller gets access when their own profile ID or `partnerId` appears in the allowlist. Listing the partner root admits existing and future sub-accounts automatically.
* Works for any authenticated caller, including HMAC API tokens and app sessions.
* Unauthorized or anonymous callers get a `404`, the same response as a nonexistent page.
* Restricted pages must be active, `navPlacement=hidden`, root-level, and childless, and list standalone hidden markets only (no groups, no `includeNextMarket=true`).
* Authorized responses are served with `private, no-store`; public pages keep their existing CDN caching.

**Documentation:** [Get Market Page by Path](https://docs.limitless.exchange/api-reference/navigation/get-page-by-path.md), [List Page Markets](https://docs.limitless.exchange/api-reference/navigation/list-page-markets.md)

### Direct-link pages for hidden partner markets

The market detail and historical-prices endpoints now return hidden markets when you request them by exact slug. Partners can share deep links to markets that aren't listed in public feeds (private launches, embedded surfaces, previews) without first flipping them to public.

* Applies to both AMM markets and CLOB markets fetched by slug.
* Slugs must match exactly; hidden markets still don't appear in search, category, or navigation feeds.
* Group-level pages continue to hide their non-visible child markets.
* This is separate from partner-restricted pages above: fetching a hidden market by slug works for any caller who has the exact slug. A restricted page, by contrast, gates a whole curated page to an allowlist.

**Documentation:** [Get market details](https://docs.limitless.exchange/api-reference/markets/get-market.md)

### AMM market stats degrade gracefully during indexer downtime

Market detail and page listings no longer fail when upstream AMM indexing data is temporarily unavailable. Affected AMM markets return zero volume, liquidity, and open interest instead of an error, and real values come back automatically once indexing recovers.

* Applies to both direct market lookups and page-market listings.
* Failed enrichment reads are not cached, so recovery propagates as soon as the response cache expires.

### Split market resolution now supports manual AMM markets

Binary split resolution now works for manual standalone binary AMM markets, in addition to CLOB binary markets. A split resolves the market at a payout ratio (for example 70/30) instead of winner-take-all, and both sides remain redeemable at the split ratio in a single call. Existing integrations keep working.

* On a `RESOLVED` manual AMM market, a split is signaled the same way as on CLOB: `winningOutcomeIndex: null` with the ratio in `payoutNumerators`.
* Detect a split by reading `payoutNumerators` on resolved markets and redeem as usual — the redeem endpoint handles both sides at the ratio.
* Oracle-automated AMM markets continue to resolve winner-take-all and reject split payloads.
* Unrealized and realized PnL account for the split ratio automatically on both sides.

**Documentation:** [Get Market](https://docs.limitless.exchange/api-reference/markets/get-market.md) | [Positions](https://docs.limitless.exchange/api-reference/portfolio/positions.md) | [Redeem](https://docs.limitless.exchange/api-reference/portfolio/redeem.md)

### More resilient real-time streams during upstream latency

Ordered real-time publishes now ride out transient upstream latency instead of failing fast. Short latency blips on the messaging backbone briefly pause per-market ordering rather than dropping the handoff and forcing WebSocket clients into a reconnect/replay loop. Order and orderbook events keep their exactly-once, per-market ordering guarantees.

* No API or payload changes — the fix improves reliability under load only.
* Per-message send deadlines are unchanged; only the retry window around a stalled backbone is extended.
* Unordered publishes are unaffected.

**Documentation:** [WebSocket Events](https://docs.limitless.exchange/developers/websocket/overview.md)

### Faster live order and orderbook updates under load

The real-time pipeline that drives order events and orderbook updates now scales further before it queues. Under heavy trading, live-order and orderbook WebSocket messages arrive with less delay, and per-market updates no longer stall behind a single busy market.

* Order and orderbook events flow through the same WebSocket channels — no API or payload changes.
* Bursts on one market no longer slow updates for other markets: each market has its own update lane.
* Order events keep exactly-once delivery.

**Documentation:** [WebSocket Events](https://docs.limitless.exchange/developers/websocket/overview.md)

### Bug fix: per-parlay PnL attribution on shared positions

When two or more parlays in the same pack shared a position and one redeemed first, the remaining parlays could be recorded at \$0, under-reporting their charted PnL. Each parlay's share is now credited only after the shared redemption is confirmed on-chain; if confirmation hasn't landed yet, attribution is deferred and retried automatically instead of being finalized too early.

* Display-level accounting only: pack-level payouts were always correct, and no funds were affected.
* Extends the earlier fix that covered NegRisk parlays to CLOB parlays, which now behave the same way.
* No API or client changes, and no action required.

## Jul 28, 2026

### Esports markets: Polymarket slug auto-sync for MM and arb

Esports markets now carry the matching Polymarket market slug on `metadata.externalSlug`, and Limitless populates it automatically. Previously the field was populated for football and tennis markets only.

* Applies to esports match-winner groups (both team markets share the event slug) and the new solo prop markets — map winner, total maps, and map handicap.
* Handicap markets are only synced when the favored side can be unambiguously aligned with Polymarket's team ordering; anything ambiguous is skipped rather than guessed.
* Live in v1 for CS2. Other titles are skipped until their Polymarket slug convention is verified against a live event.
* Sync runs hourly and only writes when the corresponding Polymarket event actually lists the expected market — no unverified slugs are emitted.
* Cross-venue market makers and arb integrations can read `metadata.externalSlug` on esports markets to resolve the Polymarket counterpart without extra lookups.

### Esports slug sync: Dota 2, League of Legends, and Valorant match moneylines

The Polymarket `externalSlug` sync for esports now covers Dota 2, League of Legends, and Valorant match moneylines, in addition to CS. Cross-venue market makers and arb integrations can read `metadata.externalSlug` on these markets to resolve the Polymarket counterpart without extra lookups.

* Applies to match moneylines only. Prop-market sync (map winner, total maps, map handicap) stays CS-only.
* Dota 3-way moneylines resolve to their per-team Polymarket sub-markets; the CS/LoL/Valorant binary path is unchanged.
* The matcher now handles Polymarket's trailing instance digits (`100t1`, `g21`, `kru1`) and diacritics (e.g. `KRÜ`) when aligning team abbreviations.
* Ambiguous matches are skipped rather than guessed. Existence-gated: no slug is written unless the Polymarket event actually lists the expected market.

### Esports solo prop markets: map winner, total maps, map handicap

Esports match pages now surface standalone binary prop markets alongside the main match-winner group. Limitless derives these props from the match structure rather than mirroring third-party betting feeds, so coverage is uniform across every supported league. Live in v1 for CS2.

* **Map winner** — one market per guaranteed-played map in odd-format series (a best-of-3 spawns maps 1 and 2), so every market is decidable with no void path.
* **Total maps** — over/under lines strictly inside the achievable series total (e.g. 2.5 for a best-of-3).
* **Map handicap** — margin lines strictly inside the achievable margin range (e.g. 1.5 for a best-of-3).
* Props trade through the same CLOB stack as the match-winner group, with a 24-hour trading window from match start. Live updates flow over the existing WebSocket streams.
* Settlement uses per-game results from the match data provider, and markets only resolve once the provider marks the match fully settled — interim finished states are not trusted.

**Documentation:** [WebSocket Events](https://docs.limitless.exchange/developers/websocket/overview.md)

### Realized PnL: split/merge accounting and partition retries

Realized PnL now records qualifying split and merge activity that was previously skipped. The values returned by the public PnL endpoint reflect that activity going forward. Distant future partition maintenance timeouts now defer to the next hourly run instead of failing.

* No API changes — the fix affects data completeness only.
* Applies to new activity going forward; historical replay is not included.

**Documentation:** [Get PnL Chart (Public)](https://docs.limitless.exchange/api-reference/public-portfolio/pnl-chart.md)

### Unrealized PnL: fee-aware accounting

Unrealized PnL now consistently accounts for fees across the platform, so the open-position value you see reflects what you would actually walk away with. Portfolio and public-portfolio positions responses use the same shared calculation, keeping the app, API, and downstream analytics aligned.

* No response-shape changes — the same `unrealizedPnl` field is returned; only its value is adjusted to include fees.
* Applies going forward to all open positions across binary, split, and grouped markets.

**Documentation:** [Positions](https://docs.limitless.exchange/api-reference/portfolio/positions.md), [Public Positions](https://docs.limitless.exchange/api-reference/public-portfolio/positions.md)

## Jul 27, 2026

### Referral tier floors: `customTier` field

A referrer's USDC referral tier can now include a minimum floor assigned by Limitless. The floor acts as a minimum: if the referrer's trading volume later clears a higher tier, volume wins and they are promoted; if it falls back, the floor holds.

* `GET /referral/usdc/me` now returns an optional `customTier` field with the floor's ladder name when one is active. The response shape is unchanged when no floor exists, so existing clients keep working.
* Ladder widgets can read `customTier` to render the floor above the volume-derived tier.
* There is no public endpoint to set or remove a tier floor.

### Split market resolution for binary markets

Binary markets can now resolve to a payout split (for example 50/50) instead of a single winner. Both sides remain redeemable at the split ratio in a single call — no new endpoint, and existing integrations keep working.

* On a `RESOLVED` market, `winningOutcomeIndex: null` no longer means "not yet resolved" — it can also indicate a split, with the ratio carried in `payoutNumerators`.
* Integrators should detect a split by reading `payoutNumerators` on resolved markets and redeem as usual; the redeem endpoint handles both sides at the ratio.
* Applies to CLOB binary markets. AMM and NegRisk flows are unchanged.

**Documentation:** [Get Market](https://docs.limitless.exchange/api-reference/markets/get-market.md) | [Positions](https://docs.limitless.exchange/api-reference/portfolio/positions.md) | [Redeem](https://docs.limitless.exchange/api-reference/portfolio/redeem.md) | [Programmatic API](https://docs.limitless.exchange/developers/programmatic-api.md)

### WebSocket orderEvent: new timestamp fields

The WebSocket `orderEvent` payload now carries three additive timestamp fields — `matchedAt`, `occurredAt`, and `publishedAt` — across the EXECUTION, MATCHED, and MINED/FAILED lifecycle stages. The legacy `timestamp` field still ships on every event but is now marked deprecated.

* `matchedAt`: when the match occurred in the order matching engine.
* `occurredAt`: when the lifecycle event (execution, mine, fail) was produced.
* `publishedAt`: when the event was published to the WebSocket stream, useful for measuring stream latency.
* No changes required — new fields are additive. Migrate off `timestamp` at your own pace.

**Documentation:** [WebSocket Events](https://docs.limitless.exchange/developers/websocket/overview.md)

### Maker rebates: current rates now on the rewards page

The Maker Rebates docs no longer hardcode a "current program parameters" table. Rates are per-market and change over time (recent example: BTC/ETH 15m and 5m tuned separately). The docs now defer to the rewards dashboard as the source of truth and explain the mechanism only.

* Current rates: [limitless.exchange/rewards?view=rebates](https://limitless.exchange/rewards?view=rebates).
* The illustrative 100 percent example on the page is clearly labeled as an assumption for the walkthrough, not a live rate.

**Documentation:** [Maker Rebates](https://docs.limitless.exchange/user-guide/maker-rebates.md)

### Starter referral rate returns to 10 percent

The one-week Starter tier promo has ended. The Starter referral rate is back to 10 percent, and the tier ladder is now 10/18/25/32/40. Higher tiers are unchanged.

* New referral fills on the Starter tier earn 10 percent from the deploy onward.
* Promo-week fills that are still unresolved will be restamped at 10 percent when their markets resolve, so pending referral earnings on those positions will shrink. Already-resolved fills are not affected.
* No action is required from referrers or referred users.

### Settlement hardening against ERC-1155 receiver-griefing wallets

Wallets that deliberately reject settlement transfers are now identified and blocked automatically, keeping CLOB settlement reliable for everyone else.

* No action is required from legitimate traders — safe wallets are never affected.

### Bug fix: Realized PnL stalled on standalone AMM markets

Realized-PnL updates for standalone AMM (binary) markets could stall when outcome-token mapping was incomplete, causing the PnL chart to fall behind for affected accounts. New events now flow through as expected.

* Applies to standalone AMM binary markets only. CLOB, NegRisk, and grouped markets are unaffected.
* The fix restores forward progress from the point of deploy; it does not automatically replay historical events that stalled before the fix.

**Documentation:** [PnL Chart](https://docs.limitless.exchange/api-reference/portfolio/pnl-chart.md)

### Bug fix: extra-time corners could flip sports YES resolutions

Sports corners markets on fixtures that went to extra time or penalties could resolve YES using inflated regular-time counts. This happened when the stats provider had not yet split extra-time corners out of the regular-time bucket. Affected YES resolutions on such fixtures now route to the Limi Oracle for verification against sources like FIFA and ESPN.

* Only YES outcomes on corners markets for fixtures ending in AET or PEN are re-verified. NO outcomes and full-time fixtures settle as before.
* Cards markets are unaffected — the provider splits cards per period correctly.
* Expected volume of extra Oracle checks is on the order of one per month.

## Jul 23, 2026

### Time-based LP reward schedules

A market's daily LP rewards budget can now be scaled up or down at specific hours or days of the week, evaluated in Eastern Time. Defaults are unchanged — markets without a schedule still pay a flat rate.

* Per-market boosts are applied within the market's daily cap, so total daily payout is bounded.
* Platform-wide dimming (a global multiplier) can also apply on top of the per-market schedule.
* The applied multiplier is recorded per minute for auditability.

**Documentation:** [LP Rewards](https://docs.limitless.exchange/user-guide/lp-rewards.md)

### Market listing endpoints: `includeNextMarket` for upfront-scheduled rounds

Market listing and search endpoints now accept an opt-in `includeNextMarket=true` query parameter. When set, each upfront-scheduled market includes a `navigation.nextMarket` object describing the successor round. Clients can then prefetch or subscribe to it before the current round expires.

* Response gains a `navigation.nextMarket` field with the next round's slug and metadata. Cursor pagination still walks the primary result set — `nextMarket` is attached to each item, not injected as extra rows.
* The `tradable` flag on `nextMarket` is intentionally conservative: it stays `false` until the successor is actually live.
* Opt-in only — omit the parameter and responses are unchanged.

**Documentation:** [Browse Active Markets](https://docs.limitless.exchange/api-reference/markets/browse-active.md) | [Browse Active by Category](https://docs.limitless.exchange/api-reference/markets/browse-active-category.md) | [Search Markets](https://docs.limitless.exchange/api-reference/markets/search.md) | [List Page Markets](https://docs.limitless.exchange/api-reference/navigation/list-page-markets.md)

## Jul 16, 2026

### SDK authentication: scoped API tokens (HMAC) are now the default path

Every SDK getting-started flow — TypeScript, Python, Go, and Rust — now leads with scoped API tokens (HMAC) as the recommended authentication path. The legacy `X-API-Key` / `LIMITLESS_API_KEY` path still works, but the docs now mark it as legacy and not recommended for new integrations.

* New integrations should authenticate with a scoped API token, configured on the SDK client via `hmacCredentials` / `hmac_credentials` / `WithHMACCredentials` / `HmacCredentials`, typically loaded from `LMTS_TOKEN_ID` and `LMTS_TOKEN_SECRET`.
* Existing API-key integrations are unaffected — no forced migration, no removal timeline.
* Scoped tokens give you granular scopes (`trading`, `account_creation`, `delegated_signing`, `withdrawal`) and are required for partner flows like delegated signing and sub-accounts.

**Documentation:** [Authentication](https://docs.limitless.exchange/developers/authentication.md) | [TypeScript SDK](https://docs.limitless.exchange/developers/sdk/typescript/getting-started.md) | [Python SDK](https://docs.limitless.exchange/developers/sdk/python/getting-started.md) | [Go SDK](https://docs.limitless.exchange/developers/sdk/go/getting-started.md) | [Rust SDK](https://docs.limitless.exchange/developers/sdk/rust/getting-started.md)

## Jul 13, 2026

### Trading restricted for Ontario and Alberta

Users in the Canadian provinces of Ontario (ON) and Alberta (AB) can no longer trade on the Platform. Ontario and Alberta now join the trading blocklist alongside the United States and the Republic of China. You can still browse markets, but you cannot place or fill orders.

* If you're located in ON or AB, you'll see a restriction when attempting to trade.
* Fully blocked jurisdictions (Russia, Belarus, Cuba, Iran, North Korea, Syria, and the Crimea, Donetsk, and Luhansk regions) are unchanged.

**Documentation:** [Terms of Service](https://docs.limitless.exchange/user-guide/terms-of-service.md)

## Jul 7, 2026

### Get market details: full response schema in the API reference

`GET /markets/{addressOrSlug}` now publishes its complete response schema, so the API playground renders a real example (instead of `<unknown>`) and integrators can generate clients directly from the spec.

* Covers all three market shapes returned by the endpoint — CLOB markets, NegRisk groups, and AMM markets — plus every nested object (venue, settings, tokens, resolution, creator, and more).
* No behavior change on the endpoint itself: fields returned in production are unchanged; this is a spec-completeness fix.
* If you generate types or clients from `openapi.json`, regenerate to pick up the concrete response types.

**Documentation:** [Get Market Details](https://docs.limitless.exchange/api-reference/markets/get-market.md)

## Jul 1, 2026

### Predictable, second-precision slugs for scheduled and recurring markets

Going live Wednesday, July 1. Recurring and upfront-scheduled CLOB market slugs become predictable, so market makers can precompute a slug before its market exists. This aligns the slug timestamp with Polymarket's convention and was driven by multiple MM requests.

* **Format change:** on recurring and scheduled markets, the slug timestamp suffix moves from a 13-digit millisecond value (set at creation time, carrying no real information) to a 10-digit Unix-second value taken from the slot's scheduled open time.
  * Before: `eth-up-or-down-5-min-1782716420095`
  * After: `eth-up-or-down-5-min-1782717300` (Polymarket parity: `eth-updown-5m-1782717300`)
* **Cadences:** applies to every recurring up/down series — 5-min, 15-min, hourly, daily, and weekly — plus upfront-scheduled markets. The suffix is the slot start in Unix seconds, so it aligns to the slot boundary (e.g. a multiple of `300` for 5-min, `3600` for hourly, `86400` for daily).
* **Ladder markets:** same second-precision suffix, taken from the market's start point (`openPriceAt`).
* **UGM markets:** still use a full millisecond timestamp (not precomputable), but now carry a dedicated `-ugm-` marker so they can be identified, e.g. `btc-above-dollar6024331-on-jun-28-1218-utc-ugm-1782648136065`.
* **Unchanged:** manually-launched markets and AMM markets keep the millisecond suffix.
* **Action:** if you parse or hardcode slug timestamps, switch to the seconds-based format. To fetch upcoming slot slugs without computing them, use the timeline endpoints.

**Documentation:** [Market Timeline](https://docs.limitless.exchange/api-reference/markets/timeline.md) | [Get Active Market Slugs](https://docs.limitless.exchange/api-reference/markets/active-slugs.md)

## Jun 29, 2026

### Market status values and `orderbookUpdate` payload documented

Two reference gaps closed for integrators reading market state and real-time orderbooks.

* `GET /markets/{slug}`: the market `status` enum is now documented — `FUNDED` (live and tradeable), `LOCKED` (a legacy value that appears only if an operator manually overrides a market's status; not tradeable), `RESOLVED` (outcome known, winners can redeem), and `CREATED` / `DRAFTED` (not yet funded, not tradeable). Treat any unrecognized future value defensively rather than assuming the market is tradeable.
* WebSocket `orderbookUpdate`: the payload is now spelled out with the concrete `bids`/`asks` schema and a field table, plus a precision/snapshot note pointing at `GET /markets/{slug}/orderbook`.

**Documentation:** [Get Market](https://docs.limitless.exchange/api-reference/markets/get-market.md) | [WebSocket Events](https://docs.limitless.exchange/developers/websocket/overview.md)

## Jun 25, 2026

### Maintenance mode: detecting trading pauses

Production integrations can now detect and handle platform maintenance windows. During maintenance, trading can become post-only, cancel-only, or fully disabled, and trading endpoints may return `425 Too Early` with a trading-mode `code`.

* New `GET /maintenance/status` endpoint to check whether trading is currently restricted or a future maintenance notice is scheduled
* New **Maintenance Mode** developer guide covering when to check status, the trading modes, and `425` handling (do not retry a blocked action in a tight loop — refresh status and wait until the mode allows it)

**Documentation:** [Maintenance Mode](https://docs.limitless.exchange/developers/maintenance-mode.md) | [Maintenance Status](https://docs.limitless.exchange/api-reference/system/maintenance-status.md)

### Public portfolio: PnL chart endpoint

A public, read-only endpoint exposes an account's realized PnL over a timeframe — no authentication required for the read.

* `GET /portfolio/{account}/pnl-chart` returns a realized PnL series plus the current realized snapshot for the given account address, selected by a `timeframe` query (e.g. `1w`)
* Part of the public-portfolio read surface (alongside public positions and traded-volume); served read-only with caching, and the `account` address is normalized

**Documentation:** [Get PnL Chart (Public)](https://docs.limitless.exchange/api-reference/public-portfolio/pnl-chart.md)

### `/portfolio/orders`: cursor pagination

The authenticated `/portfolio/orders` read now supports keyset (cursor) pagination.

* Responses carry `nextCursor` (`null` on the last page) and an exact `total`
* Pass the returned cursor back along with `limit` to page forward — the cursor is opaque and resumes exactly where the previous page ended, with no duplicates across pages even when many orders share the same timestamp
* The legacy non-projection fallback is not paginated (returns the first `limit` orders with `nextCursor: null`) and is being retired

### Market creator: `username` and trade wallet

The `creator` object on market and group responses now includes the creator's `username` (alongside display name, image, and social link). The creator `address` resolves to the creator's trade wallet (their smart wallet, or the signer EOA when the trade wallet is set to EOA).

**Documentation:** [Get Market](https://docs.limitless.exchange/api-reference/markets/get-market.md)

## Jun 24, 2026

### Packs: on-chain mechanics documented

The Packs guide now explains how a pack works on-chain. Each pack is a single Conditional Token (CTF) held in the user's own wallet, redeemable only if every leg resolves their way (otherwise it expires worthless). Buying a pack signs an EIP-712 intent covering the chosen pack, stake, and deadline, and winners claim permissionlessly on Base — there is no dependency on Limitless to release winnings. Risk is fixed to the stake.

**Documentation:** [Packs](https://docs.limitless.exchange/user-guide/packs.md#under-the-hood)

## Jun 22, 2026

### Market data clarifications and market pages discoverability

* Confirmed there is **no testnet or sandbox** — all integrations run against Base mainnet with real USDC. Rehearse a flow with small live orders on a low-volume market.
* Clarified that reported user volume is **lifetime** volume, and the fee difference between **claiming** a resolved win and **selling** a position before resolution.
* The **Market Pages** endpoints (category- and property-based filtering) are now surfaced in the API Reference navigation, and `GET /markets/active` points to them for structured filtering.

**Documentation:** [For Developers](https://docs.limitless.exchange/developers/introduction.md) | [Market Resolution](https://docs.limitless.exchange/user-guide/market-resolution.md)

## Jun 17, 2026

### Orderbook: deriving the NO book

`GET /markets/{slug}/orderbook` returns a single, YES-side book. The reference now documents the complementary-pricing identity — `price(YES) + price(NO) = 1` — so integrators can mirror the YES book into the NO book (flip bids and asks, replace each price `p` with `1 - p`) instead of assuming NO liquidity is missing. Native NO orders are already merged into the returned YES book. Multi-outcome (NegRisk) markets are covered too: each outcome has its own book and is derived independently.

**Documentation:** [Get Orderbook](https://docs.limitless.exchange/api-reference/trading/orderbook.md)

## Jun 14, 2026

### SDK WebSocket: authenticated subscriptions on HMAC

All four SDK WebSocket pages (TypeScript, Python, Go, Rust) now document authenticated subscriptions — positions, order events, and transactions — via `hmacCredentials` passed to the WebSocket client, which signs the handshake automatically. The Python page gained full authenticated-subscription examples to match the others. No `X-API-Key` is used on the WebSocket handshake.

**Documentation:** [TypeScript](https://docs.limitless.exchange/developers/sdk/typescript/websocket.md) | [Python](https://docs.limitless.exchange/developers/sdk/python/websocket.md) | [Go](https://docs.limitless.exchange/developers/sdk/go/websocket.md) | [Rust](https://docs.limitless.exchange/developers/sdk/rust/websocket.md)

## Jun 12, 2026

### Authentication docs standardized on HMAC

Active code examples across the developer docs now standardize on scoped API tokens with HMAC-SHA256 request signing (`lmts-api-key`, `lmts-timestamp`, `lmts-signature`). The legacy `X-API-Key` header has been removed from active examples. Existing API-key integrations continue to work, but new integrations should use HMAC scoped tokens.

**Documentation:** [Authentication](https://docs.limitless.exchange/developers/authentication.md)

## Jun 10, 2026

### Documentation accuracy pass

A sweep fixed copy-paste-breaking inaccuracies across the API and SDK references: scoped-token field names, SDK retry-timing units, WebSocket symbol and event names, and signing-payload details. It also clarified that `expiration` and `nonce` must both be `0` for standard CTF orders.

**Documentation:** [EIP-712 Signing](https://docs.limitless.exchange/developers/eip712-signing.md) | [Authentication](https://docs.limitless.exchange/developers/authentication.md)

## Jun 9, 2026

### Self-trade prevention on `POST /orders`

`POST /orders` now accepts an optional top-level `stpPolicy` for clients that want explicit self-trade handling. Available across the TypeScript, Python, Rust, and Go SDKs.

* Existing integrations keep the default `cancel_maker` behavior when `stpPolicy` is omitted.
* Supported values: `cancel_maker`, `cancel_taker`, `cancel_both`.
* `stpPolicy` sits outside the EIP-712 signed order payload (top-level request field).
* `cancel_taker` / `cancel_both` reject the incoming order with `execution.settlementStatus: "CANCELED"` and `execution.reason: "STP_TAKER_REJECTED"` on the `POST /orders` response.
* `cancel_maker` / `cancel_both` list the cancelled resting order IDs in `execution.stpMakerCancels`; each cancelled maker emits a `CANCELLATION` order-event with `reason: "STP_MAKER_CANCELLED"`.
* Scope: blocks same-profile self-matches on the same token only; cross-token orders on the same profile are unaffected.

**Documentation:** [Create Order — Self-Trade Prevention](https://docs.limitless.exchange/api-reference/trading/create-order.md#self-trade-prevention)

## Jun 8, 2026

### Taker delay: async submission for marketable orders

Markets can now apply a **taker delay** — a short, per-market hold on marketable (taker) orders before the matching engine fills them. When a market has it enabled, order submission becomes asynchronous.

**What changes for integrators on a delay-enabled market:**

* A marketable order's `POST /orders` returns immediately with `execution.settlementStatus: "DELAYED"` and an `eligibleAt` timestamp — it no longer blocks until the trade is mined. Track the fill asynchronously over `subscribe_order_events` (provisional `MATCHED` → terminal `MINED` / `FAILED`), correlating by `clientOrderId` / `tradeEventId`.
* **`postOnly` orders are not affected** — maker quotes rest immediately, as today.
* Read a market's current delay from `settings.takerDelayMs` (milliseconds; `0` = none) on the market response.

**Documentation:** [WebSocket Events](https://docs.limitless.exchange/developers/websocket/order-events.md#subscribing-to-order-events)

## Jun 7, 2026

### Packs

A new product on Limitless. **Packs** are curated bundles of 2 to 3 predictions from different markets, presented as ready-made offers with a clear multiplier and a single buy-in window. A user wins only if every leg lands.

**What's live:**

* USDC collateral on Base, stake range \$1 to \$10, multiplier capped at 15x before vig
* 4% vig on crypto and sports packs, already baked into the displayed multiplier
* Pack listing states: Active, Hidden (no new buys; existing positions continue to resolve), Closed (terminal)
* User-held pack status: Active, Won, Lost; Won packs expose a Claim button until winnings are collected
* External wallets sign a one-time USDC approval for \$100 (covers up to 10 max-stake packs); each pack purchase needs a confirmation
* Limitless Safe wallets do not need ETH for gas; external EOA wallets need a small Base ETH balance when claiming

**Documentation:** [Packs](https://docs.limitless.exchange/user-guide/packs.md)

## Jun 5, 2026

### WebSocket order events: FAK/FOK terminal (`EXECUTION`) frame

Authenticated `subscribe_order_events` clients now receive a terminal `EXECUTION` frame the moment an immediate-or-cancel (FAK/FOK) order reaches its final state — no polling needed.

**What changed:**

* `source: "OME"` now carries a fourth `type`, `EXECUTION`, with a `status` of `FILLED`, `PARTIALLY_FILLED`, or `KILLED`
* `eventId` uses the string form `terminal:<orderId>`
* Delivered once, to the order owner; it carries no fee fields — read the `MINED` settlement frame or the `POST /orders` response for the realized fee
* A FOK that cannot fill is rejected with HTTP 400 and emits no terminal frame, so a FOK only ever appears as `FILLED`

**Documentation:** [WebSocket Events](https://docs.limitless.exchange/developers/websocket/order-events.md#subscribing-to-order-events)

## Jun 3, 2026

### WebSocket order events: pre-settlement `MATCHED` frame

Authenticated `subscribe_order_events` clients now receive a provisional `MATCHED` settlement frame the moment the matching engine fills an order — **before** the on-chain settlement transaction. This is the earliest "your order will be matched for N" signal. It is emitted per participant (the taker and each maker), each carrying its own side, token, fill size, and a fee **estimate** (`isEstimate: true`).

**What changed:**

* `source: "SETTLEMENT"` now carries three `type`s: provisional `MATCHED`, then terminal `MINED` or `FAILED`
* `MATCHED` uses its own `eventId` namespace `matched:<tradeEventId>:<orderId>`, distinct from the terminal `settlement:<tradeEventId>:<orderId>`, so the two never dedup-collide
* Correlate provisional → terminal by `tradeEventId` + `orderId`; settle accounting on `MINED` (realized fee + `txHash`), never on the `MATCHED` estimate

**Documentation:** [WebSocket Events](https://docs.limitless.exchange/developers/websocket/order-events.md#subscribing-to-order-events)

### Polymarket migration guide: updated for CLOB V2

Polymarket cut over to CLOB V2 around May 2026, deprecating the V1 SDKs and endpoints the original migration guide was built on. The entire **Migrate from Polymarket** page has been reframed against V2.

**What changed in the guide:**

* Polymarket collateral updated from USDC.e to pUSD
* New host `data-api.polymarket.com` documented for positions, trades, activity, and price history
* Cancel semantics, `/data/*` order endpoints, public search, and slug paths corrected to V2 conventions
* The Limitless side of every comparison table remains classic CTF (taker, expiration, nonce, feeRateBps)
* Getting Started navigation reordered to surface the migration guide earlier

**Documentation:** [Migrate from Polymarket](https://docs.limitless.exchange/developers/migrate-from-polymarket.md)

## Jun 2, 2026

### User-generated markets

Limitless now lets users propose and fund their own markets. A new user-guide page covers the flow end-to-end, and the Maker Rebates page has been updated alongside to reflect the current rebate eligibility surface.

**Documentation:** [User-Generated Markets](https://docs.limitless.exchange/user-guide/user-generated-markets.md) | [Maker Rebates](https://docs.limitless.exchange/user-guide/maker-rebates.md)

### Authentication: UI flow for scoped API tokens

The "Getting a Scoped API Token" section now documents the UI derivation flow (connect wallet, open the API token modal, derive) alongside the existing programmatic `POST /auth/api-tokens/derive` path. Most builders should use the UI; the programmatic path is for fully automated partner integrations that need to mint tokens on behalf of end users.

**Documentation:** [Authentication](https://docs.limitless.exchange/developers/authentication.md)

## Jun 1, 2026

### Markets: `winningOutcomeIndex` outcome mapping

The `winningOutcomeIndex` field on resolved markets is now explicitly documented as `0` = YES, `1` = NO. Integrators previously had to verify this convention empirically. The mapping is added to the `GET /markets/{slug}` reference, the Programmatic API guide, and the OpenAPI description for `winning_index`.

**Documentation:** [Get Market](https://docs.limitless.exchange/api-reference/markets/get-market.md) | [Programmatic API](https://docs.limitless.exchange/developers/programmatic-api.md)

## May 29, 2026

### Cross-market market making quickstart

A new dedicated quickstart for the agents-starter `cross-market-mm` strategy: quote on Limitless, hedge fills on Polymarket to stay delta-neutral. The page covers the one-key wallet model (EOA plus key-less ERC-1271 deposit wallet, pUSD held in it), a no-money dry-run flow that takes under 10 minutes, an honest 20 to 30 minute go-live path, the lifecycle commands, safety rails, and the economics.

**Economics callout:** Limitless charges takers only, so the maker bot pays no Limitless fee. Revenue is the cross-venue spread plus maker rebates (100% of eligible taker fees on Daily/Hourly Crypto and 15-min Crypto, fill-gated) plus LP rewards for resting orders near midpoint. Cost is the Polymarket hedge taker fee.

**Documentation:** [Cross-Market Market Making](https://docs.limitless.exchange/developers/cross-market-market-making.md) | [Build a Trading Agent](https://docs.limitless.exchange/developers/build-a-trading-agent.md)

### SDK retirement: Java quickstart removed

The Java quickstart has been removed from the developer documentation. It was unmaintained and out of line with current API behavior. The four supported developer quickstarts are now TypeScript, Python, Go, and WebSocket.

### Small audit fixes

* `GET /auth/api-tokens/capabilities`: profiles with no capability row return `tokenManagementEnabled: true` and `allowedScopes: ["trading"]`, not `false` and an empty array. The docs now match the backend handler.
* TypeScript SDK markets reference: `group.submarkets` corrected to `group.markets` (the field is `markets?: Market[]`). The previous samples would throw at runtime.

## May 28, 2026

### Market timeline endpoints

Two new endpoints let integrators pre-fetch upcoming recurring-market slots (5-minute crypto, hourly, etc.) before they open:

* `GET /markets/{slug}/timeline` for the schedule on a single recurring market
* `GET /markets/timeline` for the global upcoming schedule

**Documentation:** [Market Timeline](https://docs.limitless.exchange/api-reference/markets/timeline.md)

### Cancel authentication clarifications

`POST /orders/cancel` is not EIP-712 signed. It requires the `trading` scope. Cancels on behalf of sub-accounts via `onBehalfOf` additionally require the `delegated_signing` scope. The reference page now spells this out so partner integrations can scope their tokens correctly the first time.

**Documentation:** [Cancel Order](https://docs.limitless.exchange/api-reference/trading/cancel.md)

## May 27, 2026

### SDK update: current profile and partner account listing

All four official SDKs now expose helpers for authenticated current-profile reads and partner-owned sub-account listing/recovery.

**Current profile:**

* `GET /profiles/me` returns the authenticated caller's private profile without passing a wallet address
* SDK helpers:
  * TypeScript: `client.portfolio.getProfile()`
  * Python: `client.portfolio.get_current_profile()`
  * Go: `client.Portfolio.GetCurrentProfile(ctx)`
  * Rust: `client.portfolio.get_current_profile()`

**Partner account listing:**

* `GET /profiles/partner-accounts` lists child accounts owned by the authenticated partner or recovers one by `account`
* Requires HMAC authentication with the `account_creation` scope
* Do not send `x-on-behalf-of`; results are always scoped to the partner behind the HMAC token
* SDK helpers:
  * TypeScript: `client.partnerAccounts.listAccounts()`
  * Python: `client.partner_accounts.list_accounts()`
  * Go: `client.PartnerAccounts.ListAccounts(ctx, ...)`
  * Rust: `client.partner_accounts.list_accounts(...)`

**Documentation:** [Get Current Profile](https://docs.limitless.exchange/api-reference/portfolio/get-current-profile.md) | [List Partner Sub-Accounts](https://docs.limitless.exchange/api-reference/partner-accounts/list-partner-accounts.md) | [Programmatic API](https://docs.limitless.exchange/developers/programmatic-api.md) | [TypeScript SDK](https://docs.limitless.exchange/developers/sdk/typescript/partner-accounts.md) | [Python SDK](https://docs.limitless.exchange/developers/sdk/python/partner-accounts.md) | [Go SDK](https://docs.limitless.exchange/developers/sdk/go/partner-accounts.md) | [Rust SDK](https://docs.limitless.exchange/developers/sdk/rust/partner-accounts.md)

## May 25, 2026

### Pyth markets: full-precision open price and descriptions

New Pyth-resolved markets now expose the full oracle precision in `metadata.openPrice` and the auto-generated market description text. Chainlink-resolved markets are not affected.

* `metadata.openPrice` for new Pyth markets returns the full decimal value (e.g. `2132.21000000` instead of `2132.21`). Pyth crypto feeds typically use 8 decimal places.
* The strike price quoted inside the auto-generated market `description` text uses the same full-precision value.
* Chainlink markets continue to return the 18-decimal padded string in both `metadata.openPrice` and the description.
* No backfill — only Pyth markets created or activated after the cutover get the new shape. Existing markets remain as-is.

**Action for partners:** if you parse `openPrice` as a number, no change is needed. If you display it verbatim or regex-match against the rounded value inside descriptions, expect longer strings for new Pyth markets.

**Documentation:** [Market Resolution](https://docs.limitless.exchange/user-guide/market-resolution.md)

### Sports markets: updated titles and resolution wording

Football match markets get cleaner titles and more explicit resolution language. Existing markets are not affected; the changes apply to newly created markets.

* **Group titles** no longer include the match date. The scheduled date and time appears in the description body.
* **Solo market titles** are reformatted (e.g. "Both Home and Away score on Feb 17?" → "Home and Away both to score?"). Affects BTTS, TOTAL\_GOALS, CORNERS\_MATCH, CARDS\_MATCH, and SPREADS.
* **Descriptions** are expanded to a 3-paragraph format with explicit branches for: match completed on the pitch, match abandoned after kickoff (solo markets resolve based on official data recorded up to that point), and match cancelled before kickoff or postponed beyond the resolution window.
* **Team-outcome markets** now explicitly recognize wins awarded by the competition authority when the match itself is not completed.

**Action for partners:** if you parse market titles for the match date, switch to the `deadline` field on the market object. If you regex-match descriptions for resolution wording, expect the new 3-paragraph format on newly created markets.

## May 20, 2026

### Receive window on `POST /orders`

`POST /orders` now accepts optional top-level `timestamp` (Unix ms) and `recvWindow` (ms) fields for clients that want order freshness checks. Both fields sit outside the EIP-712 signed order payload.

* Existing integrations are unchanged unless they send `recvWindow`.
* `recvWindow` must be between `1` and `10000` ms.
* A stale or future-dated timestamp returns HTTP `425 Too Early`. Build and sign a fresh order before retrying.

**Documentation:** [Create Order — Receive Window](https://docs.limitless.exchange/api-reference/trading/create-order.md#receive-window)

## May 7, 2026

### SDK update: partner withdrawal allowlist and expanded WebSocket coverage

All four official SDKs (TypeScript, Python, Go, Rust) now expose helpers for the partner withdrawal-address allowlist and a typed WebSocket subscription surface for the public real-time channels.

**Partner withdrawal-address allowlist:**

* `PartnerAccountService.addWithdrawalAddress()` — `POST /portfolio/withdrawal-addresses`
* `PartnerAccountService.deleteWithdrawalAddress()` — `DELETE /portfolio/withdrawal-addresses/:address`
* Both use a Privy identity token (`identity: Bearer <token>`), not API-token/HMAC auth
* `HttpClient.deleteWithIdentity()` exposed for identity-token authenticated DELETE requests
* `POST /portfolio/withdraw` continues to use HMAC auth with the `withdrawal` scope; `destination` is optional for child server-wallet withdrawals and defaults to the partner smart wallet (or partner account)
* Unit coverage added for identity-auth allowlist calls and explicit server-wallet withdrawal destinations

**WebSocket subscription / event surface:**

* Typed subscriptions for order events, live sports/esports, market lifecycle, oracle price data, and system messages
* Mirrors the `subscribe_*` channels documented on the WebSocket reference

**Documentation:** [TypeScript Partner Accounts](https://docs.limitless.exchange/developers/sdk/typescript/partner-accounts.md#withdrawal-address-allowlist) | [Python Partner Accounts](https://docs.limitless.exchange/developers/sdk/python/partner-accounts.md) | [Go Partner Accounts](https://docs.limitless.exchange/developers/sdk/go/partner-accounts.md) | [Rust Partner Accounts](https://docs.limitless.exchange/developers/sdk/rust/partner-accounts.md) | [Add Withdrawal Address](https://docs.limitless.exchange/api-reference/portfolio/add-withdrawal-address.md) | [Delete Withdrawal Address](https://docs.limitless.exchange/api-reference/portfolio/delete-withdrawal-address.md) | [WebSocket Events](https://docs.limitless.exchange/developers/websocket/overview.md)

## May 5, 2026

### Combined cancel endpoints (orderIds + clientOrderIds)

A new `POST /orders/batch-cancel` endpoint accepts either internal `orderIds` or `clientOrderIds` (the value supplied at order creation time) in a single call. Provide exactly one identifier array — requests with both, or with neither, return `400 Bad Request`.

* `POST /orders/cancel-batch` remains supported for existing integrations and continues to accept `orderIds` only
* `clientOrderId` is also surfaced on the `subscribe_order_events` payload so partners can correlate WebSocket events to their own client-side IDs

**Documentation:** [Batch Cancel Orders (Combined)](https://docs.limitless.exchange/api-reference/trading/batch-cancel.md) | [Cancel Orders (Batch)](https://docs.limitless.exchange/api-reference/trading/cancel-batch.md) | [WebSocket Events](https://docs.limitless.exchange/developers/websocket/order-events.md#subscribing-to-order-events)

## May 4, 2026

### Withdrawal address whitelisting

Explicit treasury destinations for server-wallet withdrawals must now be allowlisted on the authenticated partner profile. Withdrawals to the partner account or partner smart wallet do not require allowlisting.

* `POST /portfolio/withdrawal-addresses` — add an allowlisted destination (Privy identity token)
* `DELETE /portfolio/withdrawal-addresses/:address` — remove an allowlisted destination (Privy identity token)
* `POST /portfolio/withdraw` — `destination` field now references allowlisted addresses for child server-wallet withdrawals; HMAC auth with the `withdrawal` scope unchanged

**Documentation:** [Add Withdrawal Address](https://docs.limitless.exchange/api-reference/portfolio/add-withdrawal-address.md) | [Delete Withdrawal Address](https://docs.limitless.exchange/api-reference/portfolio/delete-withdrawal-address.md) | [Withdraw](https://docs.limitless.exchange/api-reference/portfolio/withdraw.md)

## Apr 30, 2026

### Partner account allowance helpers

Server-wallet sub-accounts need delegated-trading approvals before they can trade. Two new endpoints (and matching helpers across all four SDKs) make the recovery flow explicit:

* `GET /profiles/partner-accounts/:profileId/allowances` — inspect approval state per target
* `POST /profiles/partner-accounts/:profileId/allowances/retry` — re-run any `missing` or `failed` retryable targets
* Both require HMAC credentials with `account_creation` and `delegated_signing`
* `409 Conflict` indicates a retry is already running; `429` returns `retryAfterSeconds`

Recommended flow: poll `checkAllowances` → if not ready and any target is retryable, call `retryAllowances` → on `submitted`, poll again after a short delay.

**Documentation:** [Check Allowances](https://docs.limitless.exchange/api-reference/partner-accounts/check-allowances.md) | [Retry Allowances](https://docs.limitless.exchange/api-reference/partner-accounts/retry-allowances.md) | [Programmatic API](https://docs.limitless.exchange/developers/programmatic-api.md)

### Restricted regions update

Russia and Belarus added to the list of restricted jurisdictions in the Terms of Service.

**Documentation:** [Terms of Service](https://docs.limitless.exchange/user-guide/terms-of-service.md)

## Apr 27, 2026

### Rust SDK v1.0.7: initial stable release

The official Rust SDK is now documented with full coverage for individual traders, bot builders, and partner integrations.

**Highlights:**

* Typed async client for CLOB and NegRisk markets
* Root `Client` entrypoint for markets, portfolio, market pages, API tokens, partner accounts, delegated orders, server wallets, and WebSockets
* Built-in EIP-712 order building and signing on Base
* API key and HMAC authentication support
* Async WebSocket streaming with reconnect handling
* Pluggable logging, retry helpers, and builder-style HTTP configuration

**Documentation:** [Rust SDK](https://docs.limitless.exchange/developers/sdk/rust/getting-started.md)

### Order execution: FAK orders added to signing and SDK docs

Fill-and-kill (FAK) orders are now documented across the developer guides. FAK orders use the same `price` and `size` inputs as GTC limit orders, match immediately against available liquidity, and cancel any unmatched remainder instead of resting on the book.

**Updated docs:**

* EIP-712 signing now includes FAK in the order type reference and amount-calculation guidance
* TypeScript SDK order docs include FAK examples and parameter reference
* Programmatic API delegated orders now show GTC, FAK, and FOK flows

**Documentation:** [EIP-712 Signing](https://docs.limitless.exchange/developers/eip712-signing.md) | [TypeScript SDK Orders](https://docs.limitless.exchange/developers/sdk/typescript/orders.md) | [Programmatic API](https://docs.limitless.exchange/developers/programmatic-api.md)

### WebSocket order events

Authenticated WebSocket clients can now subscribe to the CLOB order lifecycle with `subscribe_order_events`.

**New real-time stream:**

* Emits `orderEvent` messages for both off-chain matching-engine updates and on-chain settlement results
* OME events cover placement, updates, and cancellations
* Settlement events cover mined and failed transaction outcomes
* Auth failures are surfaced on the `exception` channel
* Clients should resubscribe on reconnect and treat OME and settlement events as independent streams

**Documentation:** [WebSocket Events](https://docs.limitless.exchange/developers/websocket/order-events.md#subscribing-to-order-events)

### Portfolio history cursor contract and partner position headers

Portfolio and partner account docs were updated for integrations that page through account activity or query positions on behalf of managed accounts.

**API documentation updates:**

* `GET /portfolio/history` now reflects the cursor-based pagination contract
* Position reads now document partner `onBehalfOf` usage for managed account flows
* Server-wallet redemption docs clarify the difference between API resolution state and on-chain conditional-token settlement

**Documentation:** [Portfolio History](https://docs.limitless.exchange/api-reference/portfolio/history.md) | [Get Positions](https://docs.limitless.exchange/api-reference/portfolio/positions.md) | [Programmatic API](https://docs.limitless.exchange/developers/programmatic-api.md#lifecycle-after-a-trade)

### Developer onboarding and partner flow updates

Developer onboarding now more clearly separates the individual trader/bot path from the platform/partner path.

**Updated guidance:**

* Individual traders and bot builders can use API keys or self-service scoped trading tokens without applying for partner access
* Platform partners should use backend-held HMAC credentials, sub-accounts, and delegated signing
* Programmatic API docs now include the partner application link and updated signing guidance

**Documentation:** [For Developers](https://docs.limitless.exchange/developers/introduction.md) | [Authentication](https://docs.limitless.exchange/developers/authentication.md) | [Programmatic API](https://docs.limitless.exchange/developers/programmatic-api.md)

### Brand assets and support contact

Brand assets were refreshed and the docs support link now points to `help@limitless.network`.

## Apr 14, 2026

### SDK v1.0.6: server wallet claim and full maker rebates

**Server wallet claim (all SDKs):**

* All three SDKs (TypeScript, Python, Go) now include helper methods for server wallet redemption and withdrawal
* `redeem` — claim resolved conditional-token positions from managed sub-accounts
* `withdraw` — transfer ERC20 funds from managed sub-accounts to partner wallets
* Previously these operations required direct REST calls; now fully supported in the SDK

**Maker Rebates program update:**

* Rebate rate increased to **100%** across all market types (daily, hourly crypto, 15-minute crypto)

**Documentation:** [Programmatic API](https://docs.limitless.exchange/developers/programmatic-api.md) | [TypeScript SDK](https://docs.limitless.exchange/developers/sdk/typescript/getting-started.md) | [Python SDK](https://docs.limitless.exchange/developers/sdk/python/getting-started.md) | [Go SDK](https://docs.limitless.exchange/developers/sdk/go/getting-started.md) | [Maker Rebates](https://docs.limitless.exchange/user-guide/maker-rebates.md)

## Apr 2, 2026

### Programmatic API: partner integrations, delegated signing, and FOK orders

Major new capability for partners building on Limitless. The Programmatic API enables platform integrations with sub-account management, server-side order signing, and both GTC and FOK order types — all through HMAC-authenticated scoped tokens.

**New API endpoints:**

* `POST /auth/api-tokens/derive` — Create scoped HMAC tokens with granular permissions (`trading`, `account_creation`, `delegated_signing`)
* `GET /auth/api-tokens/capabilities` — Check partner capability configuration
* `GET /auth/api-tokens` — List active tokens
* `DELETE /auth/api-tokens/:tokenId` — Revoke a token
* `POST /profiles/partner-accounts` — Create sub-accounts with server-managed wallets or EOA verification

**Delegated signing:**

* Partners with the `delegated_signing` scope can submit unsigned orders on behalf of sub-accounts
* The server signs orders using Privy-managed wallets — no private key management needed on the partner side
* Both **GTC** (limit) and **FOK** (market) order types are supported for delegated orders
* FOK orders use `makerAmount` (USDC to spend for BUY, shares to sell for SELL) instead of `price` + `size`

**Recommended architecture:**

* Store HMAC credentials on your backend — never expose them to frontends
* Use the SDK server-side to sign partner-authenticated requests
* Expose only your own app-specific endpoints to the frontend

**Documentation:** [Programmatic API guide](https://docs.limitless.exchange/developers/programmatic-api.md) | [Authentication](https://docs.limitless.exchange/developers/authentication.md#scoped-api-tokens-hmac) | [API Tokens reference](https://docs.limitless.exchange/api-reference/api-tokens/derive-token.md)

### SDK v1.0.4–1.0.5: programmatic API support (TypeScript, Python, Go)

All three official SDKs now include full support for the Programmatic API:

**New services across all SDKs:**

* `ApiTokenService` — Derive, list, and revoke scoped HMAC tokens
* `PartnerAccountService` — Create sub-accounts with server wallets or EOA verification
* `DelegatedOrderService` — Place GTC and FOK orders on behalf of sub-accounts, cancel orders

**New root `Client` entrypoint:**

* Composes all domain services (markets, portfolio, orders, API tokens, partner accounts, delegated orders) behind a single constructor
* HMAC credentials are configured once and applied to all requests automatically

**TypeScript SDK:**

* `Client` with `hmacCredentials` option
* `client.apiTokens`, `client.partnerAccounts`, `client.delegatedOrders`
* WebSocket HMAC authentication support
* [TypeScript SDK docs](https://docs.limitless.exchange/developers/sdk/typescript/getting-started.md)

**Python SDK:**

* `Client` with `hmac_credentials` option
* `client.api_tokens`, `client.partner_accounts`, `client.delegated_orders`
* WebSocket HMAC handshake support
* [Python SDK docs](https://docs.limitless.exchange/developers/sdk/python/getting-started.md)

**Go SDK:**

* `NewClient(limitless.WithHMACCredentials(...))`
* `client.ApiTokens`, `client.PartnerAccounts`, `client.DelegatedOrders`
* WebSocket HMAC authentication support
* [Go SDK docs](https://docs.limitless.exchange/developers/sdk/go/getting-started.md)

## Mar 23, 2026

### SDK v1.0.3: market pages navigation

All three SDKs now support the market pages navigation API for browsing markets by category.

**New capabilities:**

* Navigation tree discovery
* Market page resolution by path with automatic redirect handling
* Market listing with filters, pagination, and cursor support
* Property keys and options for dynamic filtering

**TypeScript:** [Market Pages](https://docs.limitless.exchange/developers/sdk/typescript/market-pages.md) | **Python:** [Market Pages](https://docs.limitless.exchange/developers/sdk/python/market-pages.md) | **Go:** [Market Pages](https://docs.limitless.exchange/developers/sdk/go/market-pages.md)

### Go SDK v1.0.3: initial stable release

First stable, production-ready release of the Go SDK with full feature parity.

**Highlights:**

* EIP-712 order signing with private key (Base mainnet)
* GTC and FOK order support
* WebSocket streaming with Socket.IO protocol, auto-reconnect, and typed event handlers
* Configurable retry with exponential backoff
* Functional options pattern throughout (`WithBaseURL`, `WithAPIKey`, `WithLogger`, etc.)
* Zero external dependencies beyond `go-ethereum` and `gorilla/websocket`

**Documentation:** [Go SDK](https://docs.limitless.exchange/developers/sdk/go/getting-started.md)

## Mar 2026

### WebSocket market lifecycle events

New WebSocket events for market creation and resolution, enabling real-time monitoring of market lifecycle changes.

* `market.created` — Fires when a new market is created
* `market.resolved` — Fires when a market resolves

**Documentation:** [WebSocket Events](https://docs.limitless.exchange/developers/websocket/overview.md)

## Feb 2026

### SDK v1.0.2: stable LTS release (TypeScript and Python)

First stable, long-term support releases of the TypeScript and Python SDKs.

**Core features across both SDKs:**

* API key authentication with `X-API-Key` header
* EIP-712 order signing with venue-aware contract resolution
* GTC and FOK order creation with automatic signing
* Market data fetching with intelligent venue caching
* Portfolio and position tracking
* WebSocket streaming with auto-reconnect
* Retry mechanisms with configurable backoff strategies
* NegRisk market support with dual approval system

**TypeScript SDK highlights:**

* Full TypeScript type safety with comprehensive type definitions
* 17 production-ready code samples
* `@retryOnErrors` decorator and `withRetry` wrapper
* [TypeScript SDK docs](https://docs.limitless.exchange/developers/sdk/typescript/getting-started.md)

**Python SDK highlights:**

* Async-first architecture built on aiohttp
* Pydantic models for type-safe request/response handling
* `@retry_on_errors` decorator
* [Python SDK docs](https://docs.limitless.exchange/developers/sdk/python/getting-started.md)

### Python SDK v1.0.2: float precision fix

Fixed IEEE 754 float precision issues in order pricing that could cause incorrect `makerAmount`/`takerAmount` calculations (e.g., `0.95` scaling to `949999` instead of `950000`).

## Dec 2025

### API: cookie-based authentication removed

Cookie-based session authentication has been removed. All programmatic access now requires API keys (`X-API-Key` header) or scoped API tokens (HMAC).

**Action required:** If you were using cookie-based authentication, migrate to API key authentication. Generate keys at [limitless.exchange](https://limitless.exchange) under profile menu → API keys.

**Documentation:** [Authentication](https://docs.limitless.exchange/developers/authentication.md)

## Nov 2025

### Initial SDK releases (pre-release)

Pre-release versions of the TypeScript (v0.0.1) and Python (v0.1.0) SDKs launched with core trading functionality including market data access, GTC/FOK order creation, and portfolio tracking.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.