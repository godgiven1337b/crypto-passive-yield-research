> ## Documentation Index
> Fetch the complete documentation index at: https://docs.limitless.exchange/llms.txt
> Use this file to discover all available pages before exploring further.

# Market Lifecycle

> Subscribe to market creation, schedule, and resolution events, optionally filtered by category, and read the marketCreated, marketUpdated, and marketResolved payloads

This page covers subscribing to market lifecycle events with `subscribe_market_lifecycle`, filtering them by category, and the `marketCreated`, `marketUpdated`, and `marketResolved` payloads that subscription delivers.

## Subscribing to market lifecycle events

Subscribe to market lifecycle events by emitting `subscribe_market_lifecycle`. No authentication required. The server acknowledges with a `system` message.

```typescript theme={null}
socket.on('connect', () => {
  socket.emit('subscribe_market_lifecycle');
});

socket.on('marketCreated', (data) => {
  console.log('New market:', data.slug, data.title);
});

socket.on('marketUpdated', (data) => {
  console.log('Schedule changed:', data.slug, data.startMatchTimestampInUTC, data.matchStatus);
});

socket.on('marketResolved', (data) => {
  console.log('Market resolved:', data.slug, data.winningOutcome);
});
```

> [!NOTE]
>
> `marketResolved` is also emitted to existing per-market room subscribers automatically (CLOB: `market:{slug}`, AMM: `market:{address}`). You don't need a separate lifecycle subscription to receive resolution events for markets you're already watching.

To unsubscribe:

```typescript theme={null}
socket.emit('unsubscribe_market_lifecycle');
```

### Filtering by category

Pass `categoryIds` to receive only events for markets in those categories:

```typescript theme={null}
socket.emit('subscribe_market_lifecycle', { categoryIds: [1, 49] });
```

* An event is delivered when any ID you pass appears in the event's `categoryIds`. You receive each event once, even when several of your IDs match.
* `categoryIds` must be an array of at most 32 positive integers. An invalid value is rejected with an `error` event carrying a `message`, and your existing lifecycle subscription is left unchanged.
* Omitting `categoryIds`, or passing an empty array, subscribes to every lifecycle event.
* Emitting `subscribe_market_lifecycle` again replaces your previous filter. It does not add to it.
* The filter applies to `marketCreated`, `marketUpdated`, and the lifecycle copy of `marketResolved`. Per-market room subscribers still receive `marketResolved` for markets they watch, whatever the filter.

## Event payloads

### `marketCreated`

Emitted when a new market is funded and visible. Hidden markets are excluded.

```json theme={null}
{
  "slug": "btc-above-110k-apr-2026",
  "title": "$BTC above $110,000 on Apr 5, 2026?",
  "type": "CLOB",
  "categoryIds": [1, 5],
  "createdAt": "2026-04-02T12:00:00.000Z"
}
```

| Field | Type | Description |
| - | - | - |
| `slug` | `string` | Market slug identifier |
| `title` | `string` | Market title |
| `type` | `'AMM' \| 'CLOB'` | Market type |
| `groupSlug` | `string?` | Present only when the event is for a market group; then `groupSlug` equals `slug`. Submarkets do not emit their own `marketCreated`. |
| `categoryIds` | `number[]` | Category IDs (always present, may be empty) |
| `createdAt` | `string` | ISO-8601 creation timestamp |

### `marketUpdated`

Emitted when a sports or esports match's schedule changes: a new start time or deadline, or a match status such as postponed or cancelled. Each frame carries the current schedule, so you can replace what you hold rather than apply a diff. Only funded, visible markets and groups with a match start time emit it.

A market group emits one frame for the whole group; its submarkets do not emit their own. Standalone markets for the same match, such as player props, each emit their own frame.

```json theme={null}
{
  "slug": "arsenal-vs-chelsea-oct-18-2026",
  "groupSlug": "arsenal-vs-chelsea-oct-18-2026",
  "type": "CLOB",
  "matchStatus": "RESCHEDULED",
  "categoryIds": [49],
  "deadline": "2026-10-18T16:00:00.000Z",
  "startMatchTimestampInUTC": 1792339200
}
```

| Field | Type | Description |
| - | - | - |
| `slug` | `string` | Market or group slug |
| `groupSlug` | `string?` | Present only when the event is for a market group; then `groupSlug` equals `slug` |
| `type` | `'AMM' \| 'CLOB'` | Market type. Always `CLOB` for groups. |
| `matchStatus` | `'POSTPONED' \| 'RESCHEDULED' \| 'CANCELLED' \| 'ABANDONED' \| null` | Match status from the data provider, or `null` when there is none |
| `categoryIds` | `number[]` | Category IDs (always present, may be empty) |
| `deadline` | `string \| null` | ISO-8601 market deadline |
| `startMatchTimestampInUTC` | `number` | Match start time as a Unix timestamp in seconds |

### `marketResolved`

Emitted when a market resolves to a single winner. Sent to both `market_lifecycle` subscribers and existing `market:{slug}` room subscribers.

```json theme={null}
{
  "slug": "btc-above-110k-apr-2026",
  "type": "CLOB",
  "winningOutcome": "YES",
  "winningIndex": 0,
  "resolutionDate": "2026-04-05T14:00:00.000Z"
}
```

| Field | Type | Description |
| - | - | - |
| `slug` | `string` | Market slug identifier |
| `type` | `'AMM' \| 'CLOB'` | Market type |
| `winningOutcome` | `'YES' \| 'NO'` | The winning outcome |
| `winningIndex` | `0 \| 1` | Index of the winning outcome (0 = YES, 1 = NO) |
| `resolutionDate` | `string` | ISO-8601 resolution timestamp |

> [!WARNING]
>
> `marketResolved` is not emitted for a split resolution, such as a [50-50 resolution](https://docs.limitless.exchange/user-guide/market-resolution.md#50-50-resolution), on either the lifecycle stream or the per-market room. Detect splits over REST with [`GET /markets/{slug}`](https://docs.limitless.exchange/api-reference/markets/get-market): the market has `status: "RESOLVED"`, `winningOutcomeIndex: null`, and `payoutNumerators` with two positive values.

## Related

* [WebSocket overview](https://docs.limitless.exchange/developers/websocket/overview.md): connection details, handshake authentication, and the full event reference


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.